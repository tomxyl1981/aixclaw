"""
靶点证据矩阵 — 真实数据源适配器

对接 PubMed (NCBI EUtils) 和用户提供的差异表达数据。
"""

import json
import re
import socket
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote_plus
from urllib.error import URLError, HTTPError

import urllib.request

from target_evidence_matrix import (
    EvidenceMatrixBuilder,
    EvidenceDirection,
    EvidenceStrength,
    EvidenceDimension,
    TargetEvidenceMatrix,
)

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = "aixclaw@aixbox.ai"  # NCBI 要求提供邮箱


def _safe_urlopen(req: urllib.request.Request, timeout: int = 30):
    """带异常处理的 urlopen：将 URLError/HTTPError/超时统一转为可捕获的异常。"""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except HTTPError as e:
        raise ConnectionError(f"PubMed HTTP {e.code}: {e.reason}") from e
    except (URLError, socket.timeout, TimeoutError) as e:
        raise ConnectionError(f"PubMed 网络错误: {e}") from e


def search_pubmed(query: str, max_results: int = 10) -> list[str]:
    """搜索 PubMed 返回 PMID 列表"""
    encoded = quote_plus(query)
    url = f"{PUBMED_BASE}/esearch.fcgi?db=pubmed&term={encoded}&retmax={max_results}&retmode=json&tool=AIXClaw&email={EMAIL}"
    req = urllib.request.Request(url, headers={"User-Agent": "AIXClaw/1.0"})
    with _safe_urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_abstracts(pmids: list[str]) -> list[dict[str, Any]]:
    """获取 PMID 对应的文章信息和摘要"""
    ids = ",".join(pmids)
    url = f"{PUBMED_BASE}/efetch.fcgi?db=pubmed&id={ids}&retmode=xml&rettype=abstract&tool=AIXClaw&email={EMAIL}"
    req = urllib.request.Request(url, headers={"User-Agent": "AIXClaw/1.0"})
    with _safe_urlopen(req, timeout=30) as resp:
        xml_data = resp.read()

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        raise ConnectionError(f"PubMed 返回非 XML 内容: {e}") from e
    articles = []
    
    for article_elem in root.findall(".//PubmedArticle"):
        pmid_elem = article_elem.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else ""
        
        # 标题
        title_elem = article_elem.find(".//ArticleTitle")
        title = "".join(title_elem.itertext()) if title_elem is not None else ""
        
        # 摘要
        abstract_parts = []
        for abs_text in article_elem.findall(".//AbstractText"):
            label = abs_text.get("Label", "")
            text = "".join(abs_text.itertext())
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        abstract = "\n".join(abstract_parts)
        
        # 期刊+年份
        journal_elem = article_elem.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else ""
        year_elem = article_elem.find(".//PubDate/Year")
        year = year_elem.text if year_elem is not None else ""
        
        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
        })
    
    return articles


class PubMedToEvidenceBuilder:
    """
    PubMed 搜索结果 → 靶点证据矩阵
    """
    
    def __init__(self, target_gene: str, disease: str):
        self.builder = EvidenceMatrixBuilder(target_gene=target_gene, disease=disease)
        self.pmids_searched: list[str] = []
        self.articles_fetched: list[dict[str, Any]] = []
    
    def search_and_fetch(self, query: str, max_results: int = 10):
        """搜索 PubMed 并获取文章"""
        self.pmids_searched = search_pubmed(query, max_results)
        self.articles_fetched = fetch_abstracts(self.pmids_searched)
        return self.articles_fetched
    
    def extract_gwas_evidence(self, article: dict[str, Any]) -> bool:
        """从摘要中提取 GWAS 证据"""
        abstract = (article.get("abstract") or "").lower()
        title = (article.get("title") or "").lower()
        combined = abstract + " " + title
        
        # 检测 GWAS 关键词
        gwas_keywords = ["gwas", "genome-wide", "genome wide", "association study", "locus", "snps", "p=", "p <"]
        if not any(kw in combined for kw in gwas_keywords):
            return False
        
        # 提取 p 值
        p_matches = re.findall(r'p\s*[=<\s]+\s*([0-9]+(?:\.[0-9]+)?(?:e-?[0-9]+)?)', combined)
        if not p_matches:
            return False
        
        best_p = min(float(p) if not p.startswith("e-") else float("1e" + p[1:]) for p in p_matches)
        
        # 提取方向
        direction = EvidenceDirection.ASSOCIATED
        if "higher" in combined or "increased" in combined or "up" in combined:
            direction = EvidenceDirection.UPREGULATED
        elif "lower" in combined or "decreased" in combined or "reduced" in combined or "protective" in combined:
            direction = EvidenceDirection.DOWNREGULATED
        
        # 强度分级
        if best_p < 5e-8:
            strength = EvidenceStrength.P_VALUE_LT_5E8
        elif best_p < 1e-5:
            strength = EvidenceStrength.P_VALUE_LT_1E5
        elif best_p < 0.01:
            strength = EvidenceStrength.NOMINAL
        else:
            strength = EvidenceStrength.WEAK
        
        row = self.builder.from_gwas(
            p_value=str(best_p),
            direction=direction.value,
            source_id=f"PMID:{article['pmid']}",
            raw_finding=f"GWAS: {article['title'][:100]}",
        )
        row.raw_snippet = article["abstract"][:300] if article.get("abstract") else ""
        row.source_name = article.get("journal", "")
        row.source_date = article.get("year", "")
        self.builder.add(row)
        return True
    
    def extract_expression_evidence(self, article: dict[str, Any]) -> bool:
        """从摘要中提取表达相关证据"""
        abstract = (article.get("abstract") or "").lower()
        title = (article.get("title") or "").lower()
        combined = abstract + " " + title
        
        # 检测表达关键词
        expr_keywords = ["expression", "rna-seq", "transcriptom", "rna seq", "mrna", "differentially expressed"]
        if not any(kw in combined for kw in expr_keywords):
            return False
        
        # 提取细胞类型
        cell_types = re.findall(r'(hepatocyte|stellate cell|kupffer|macrophage|neutrophil|t cell|b cell|endothelial|fibroblast)', combined)
        cell_type = cell_types[0] if cell_types else "肝细胞"
        
        # 检测方向
        direction = EvidenceDirection.UNKNOWN
        if "upregulat" in combined or "higher expression" in combined or "overexpress" in combined:
            direction = EvidenceDirection.UPREGULATED
        elif "downregulat" in combined or "lower expression" in combined or "decreased expression" in combined:
            direction = EvidenceDirection.DOWNREGULATED
        
        # log2FC 检测
        fc_matches = re.findall(r'log2?(?:fc|fold.change)\s*[=:]\s*([-]?[0-9.]+)', combined)
        fc_matches += re.findall(r'fold.change\s*[=:]\s*([-]?[0-9.]+)', combined)
        fc_str = fc_matches[0] if fc_matches else ""
        
        p_matches = re.findall(r'p\s*[=<\s]+\s*([0-9]+(?:\.[0-9]+)?(?:e-?[0-9]+)?)', combined)
        p_str = p_matches[0] if p_matches else ""
        
        try:
            fc = float(fc_str) if fc_str else None
        except ValueError:
            fc = None
        
        row = self.builder.from_scRNA_seq(
            log2fc=fc_str or "n/a",
            p_value=p_str or "n/a",
            cell_type=cell_type,
            direction=direction.value,
            source_id=f"PMID:{article['pmid']}",
            raw_finding=f"表达证据: {article['title'][:100]}",
        )
        row.raw_snippet = article["abstract"][:300] if article.get("abstract") else ""
        self.builder.add(row)
        return True
    
    def extract_animal_evidence(self, article: dict[str, Any]) -> bool:
        """提取动物模型证据"""
        abstract = (article.get("abstract") or "").lower()
        title = (article.get("title") or "").lower()
        combined = abstract + " " + title
        
        model_keywords = ["mouse", "mice", "rat", "murine", "knockout", "ko ", "transgenic", 
                         "animal", "in vivo", "xenograft", "zebrafish"]
        if not any(kw in combined for kw in model_keywords):
            return False
        
        # 检测模型类型
        model_type = "knockout" if any(kw in combined for kw in ["knockout", "ko ", "null"]) else \
                     "transgenic" if "transgenic" in combined else \
                     "xenograft" if "xenograft" in combined else \
                     "model"
        
        # 检测效果方向
        effect = "protective" if any(kw in combined for kw in ["reduced", "suppressed", "decreased", 
                                                                 "ameliorated", "protected", "inhibited"]) else \
                 "harmful" if any(kw in combined for kw in ["increased", "induced", "exacerbated",
                                                            "promoted", "worsened"]) else \
                 "no_effect"
        
        # 提取表型
        phenotype_keywords = ["fibrosis", "inflammation", "steatosis", "cirrhosis", "tumor", 
                            "necrosis", "apoptosis", "proliferation"]
        phenotypes = [kw for kw in phenotype_keywords if kw in combined]
        phenotype = phenotypes[0] if phenotypes else "未明确"
        
        row = self.builder.from_animal_model(
            model_type=model_type,
            phenotype=phenotype,
            effect_direction=effect,
            source_id=f"PMID:{article['pmid']}",
            raw_finding=f"动物模型: {article['title'][:100]}",
        )
        row.raw_snippet = article["abstract"][:300] if article.get("abstract") else ""
        self.builder.add(row)
        return True
    
    def extract_pathway_evidence(self, article: dict[str, Any]) -> bool:
        """提取通路证据"""
        abstract = (article.get("abstract") or "").lower()
        title = (article.get("title") or "").lower()
        combined = abstract + " " + title
        
        pathway_keywords = ["pathway", "signaling", "signal", "tgf", "smad", "wnt", "nf-kb", 
                          "mapk", "pi3k", "akt", "mtor", "jak", "stat"]
        if not any(kw in combined for kw in pathway_keywords):
            return False
        
        # 提取具体的通路名
        pathway_names = {
            "tgf": "TGF-β", "smad": "SMAD", "wnt": "Wnt/β-catenin",
            "nf-kb": "NF-κB", "mapk": "MAPK/ERK", "pi3k": "PI3K/Akt",
            "akt": "PI3K/Akt", "mtor": "mTOR", "jak": "JAK/STAT", "stat": "JAK/STAT",
        }
        found_pathways = [v for k, v in pathway_names.items() if k in combined]
        pathway = found_pathways[0] if found_pathways else "信号通路"
        
        p_matches = re.findall(r'p\s*[=<\s]+\s*([0-9]+(?:\.[0-9]+)?(?:e-?[0-9]+)?)', combined)
        p_str = p_matches[0] if p_matches else "n/a"
        
        row = self.builder.from_pathway(
            pathway_name=pathway,
            pathway_role="activator" if "activate" in combined or "promote" in combined else \
                         "inhibitor" if "inhibit" in combined or "suppress" in combined else \
                         "member",
            enrichment_p=p_str,
            source_id=f"PMID:{article['pmid']}",
            raw_finding=f"通路: {article['title'][:100]}",
        )
        row.raw_snippet = article["abstract"][:300] if article.get("abstract") else ""
        self.builder.add(row)
        return True
    
    def auto_extract(self) -> TargetEvidenceMatrix:
        """自动从获取的文章中提取各类证据"""
        for article in self.articles_fetched:
            # 尝试每种证据类型
            found = False
            
            # GWAS 证据优先级最高
            if self.extract_gwas_evidence(article):
                found = True
            
            # 表达证据
            if self.extract_expression_evidence(article):
                found = True
            
            # 动物模型
            if self.extract_animal_evidence(article):
                found = True
            
            # 通路
            if self.extract_pathway_evidence(article):
                found = True
            
            # 如果文献里什么模式都没匹配到，作为一般文献证据加入
            if not found:
                row = self.builder.from_literature_abstract(
                    source_id=article["pmid"],
                    key_finding=article["title"][:200],
                    strength="nominal",
                )
                row.raw_snippet = article["abstract"][:500] if article.get("abstract") else ""
                self.builder.add(row)
        
        return self.builder.build()


def build_from_pubmed(target_gene: str, disease: str, query: str | None = None, max_results: int = 8) -> TargetEvidenceMatrix:
    """
    一站式函数：搜索 PubMed → 提取证据 → 构建靶点矩阵
    
    参数：
        target_gene: 靶点基因名
        disease: 疾病名
        query: 搜索词（默认 "target_gene disease"）
        max_results: 最多搜索结果数
    """
    if query is None:
        query = f"{target_gene} {disease}"
    
    builder = PubMedToEvidenceBuilder(target_gene=target_gene, disease=disease)
    print(f"[PubMed] 搜索: {query}")
    articles = builder.search_and_fetch(query, max_results)
    print(f"[PubMed] 找到 {len(articles)} 篇文章")
    
    print("[提取] 自动提取各维度证据...")
    matrix = builder.auto_extract()
    print(f"[完成] 构建 {target_gene} → {disease} 证据矩阵")
    print(f"       证据行: {len(matrix.rows)} | 置信度: {matrix.overall_confidence:.2f}")
    
    return matrix
