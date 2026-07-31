#!/usr/bin/env python3
"""evidence_ledger.py — 证据溯源清单渲染 (A3, 2026-07-31 张红批准)

独立模块: 从证据行提取可溯源信息, 生成 Markdown 清单表格,
自动为 PMID / GWAS / Ensembl / ChEMBL / NCT 生成可点击链接。

原则 (2026-07-25): 每个结论可追溯到具体 PMID/数据集; 无溯源信息的行不进清单。
"""

from __future__ import annotations

from typing import List, Sequence


def _attr(row, name, default=""):
    """宽松读取属性 (兼容 EvidenceRow / dict / SimpleNamespace)。"""
    if isinstance(row, dict):
        return row.get(name, default)
    return getattr(row, name, default)


def _enum_value(v):
    """枚举成员 → 值; 其他原样返回。"""
    if v is None:
        return ""
    return v.value if hasattr(v, "value") else str(v)


def infer_link(source_id: str, source_url: str = "") -> str:
    """优先 source_url; 否则按 ID 模式推断公共数据库链接。"""
    sid = (source_id or "").strip()
    if source_url and source_url.strip().startswith("http"):
        return source_url.strip()
    if not sid:
        return ""
    up = sid.upper()
    # PMID:  "PMID:31247652" 或 "31247652" (纯数字且 ≥5 位)
    pmid = up.replace("PMID:", "").replace("PMID", "").strip()
    if pmid.isdigit() and len(pmid) >= 5:
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    if up.startswith("GCST"):
        return f"https://www.ebi.ac.uk/gwas/studies/{up}"
    if up.startswith("ENSG"):
        return f"https://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={up}"
    if up.startswith("CHEMBL"):
        return f"https://www.ebi.ac.uk/chembl/target_report_card/{up}/"
    if up.startswith("NCT"):
        return f"https://clinicaltrials.gov/study/{up}"
    return ""


def render_evidence_ledger(evidence_rows: Sequence, strength_label=None, direction_label=None) -> List[str]:
    """渲染证据溯源清单章节 (返回 Markdown 行列表, 不含章节标题)。

    Args:
        evidence_rows: 证据行序列 (EvidenceRow / dict / SimpleNamespace)
        strength_label: 强度枚举 → 中文标签函数 (可选)
        direction_label: 方向枚举 → 中文标签函数 (可选)
    """
    from typing import List, Sequence  # noqa: F401 (保留签名可读性)

    def _sec(title):
        return "\n## " + title + "\n"

    def _tbl(headers, rows):
        lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for r in rows:
            lines.append("| " + " | ".join(str(c) for c in r) + " |")
        return "\n".join(lines)

    sl = strength_label or (lambda s: _enum_value(s))
    dl = direction_label or (lambda d: _enum_value(d))

    out: List[str] = []
    out.append(_sec("附录、证据溯源清单（可核验）"))
    out.append("> 本清单列出简报引用的全部证据行及其原始来源。每个结论均可点击链接回溯到")
    out.append("> 发表论文或公共数据库记录 —— 不信任模型，信任数据源头（2026-07-25 原则）。")
    out.append("")

    ledger_rows: List[List[str]] = []
    seen: set = set()

    for row in evidence_rows:
        dim = _enum_value(_attr(row, "dimension"))
        sub = str(_attr(row, "sub_dimension", ""))
        st = _enum_value(_attr(row, "strength"))
        di = _enum_value(_attr(row, "direction"))
        sid = str(_attr(row, "source_id", "")).strip()
        surl = str(_attr(row, "source_url", "")).strip()
        sname = str(_attr(row, "source_name", "")).strip()
        raw = str(_attr(row, "raw_stat", "")).strip()
        n = _attr(row, "sample_size", None)
        es = _attr(row, "effect_size", None)

        if not sid and not surl:
            continue  # 无溯源信息 → 不进清单 (诚实原则)
        key = f"{dim}|{sid}" if sid else f"{dim}|{surl}"
        if key in seen:
            continue  # 同源同维去重（同一来源ID只保留一条，跨子维度）
        seen.add(key)

        link = infer_link(sid, surl)
        link_md = f"[🔗]({link})" if link else "—"

        stat_parts = []
        if raw:
            stat_parts.append(raw)
        if es is not None:
            stat_parts.append(f"ES={es:.3f}" if isinstance(es, float) else f"ES={es}")
        if n:
            stat_parts.append(f"n={n}")
        stat = " ".join(stat_parts) if stat_parts else "—"
        src_disp = sid or sname or "—"

        ledger_rows.append([
            sl(st), sub or "—", dl(di), stat, src_disp, link_md,
        ])

    if ledger_rows:
        out.append(f"共 {len(ledger_rows)} 条可溯源证据（同源同维去重后）：")
        out.append("")
        out.append(_tbl(["强度", "子维度", "方向", "统计/效应", "来源ID", "链接"], ledger_rows))
        out.append("")
    else:
        out.append("（当前无带溯源信息的证据行）")
        out.append("")

    return out


if __name__ == "__main__":
    from types import SimpleNamespace as NS
    rows = [
        NS(dimension="GWAS", sub_dimension="GWAS Catalog", strength="p<5e-8",
           direction="up", effect_size=1.28, sample_size=184305, raw_stat="p=3.1e-9, OR=1.28",
           source_id="GCST003116", source_url="", source_name="GWAS Catalog"),
        NS(dimension="EQTL", sub_dimension="GTEx", strength="p<1e-5",
           direction="up", effect_size=0.42, sample_size=838, raw_stat="p=2.2e-6",
           source_id="PMID:31247652", source_url="", source_name="Nature Genetics"),
        NS(dimension="ANIMAL", sub_dimension="KO mouse", strength="log2FC>1",
           direction="down", effect_size=-1.8, sample_size=None, raw_stat="log2FC=-1.8",
           source_id="PMID:28892040", source_url="", source_name="Cell"),
        NS(dimension="EXPR", sub_dimension="scRNA-seq", strength="nominal",
           direction="up", effect_size=0.31, sample_size=12000, raw_stat="p=0.02",
           source_id="", source_url="https://gtexportal.org/home/gene/ENSG00000121989",
           source_name="GTEx Portal"),
        NS(dimension="PATHWAY", sub_dimension="Reactome", strength="weak",
           direction="up", effect_size=None, sample_size=None, raw_stat="",
           source_id="", source_url="", source_name=""),  # 无溯源 → 跳过
        NS(dimension="GWAS", sub_dimension="FinnGen", strength="p<1e-5",
           direction="up", effect_size=0.95, sample_size=377277, raw_stat="p=8.4e-7",
           source_id="GCST003116", source_url="", source_name="GWAS Catalog"),  # 重复 → 去重
    ]
    md = "\n".join(render_evidence_ledger(rows))
    with open("/tmp/ledger_demo.md", "w") as f:
        f.write(md)
    print("demo written")
