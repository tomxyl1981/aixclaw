#!/usr/bin/env python3
"""
ChEMBL 药物-靶点亲和力连接器 (P0+)。

通过 EMBL-EBI ChEMBL REST API 检索靶点的已知药物、化合物活性、
pChEMBL 评分、FDA 批准适应症，补充可药性证据维度。

API: https://chembl.gitbook.io/chembl-interface-documentation/web-services
用法:
    python3 chembl_connector.py ACVR2A
"""

import json, sys, urllib.request, urllib.error, urllib.parse, ssl
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))

API_BASE = "https://www.ebi.ac.uk/chembl/api/data"


def _tem():
    import target_evidence_matrix as tm
    return tm


# ── 基因→UniProt 映射（ChEMBL 目标查找需要） ──
GENE_UNIPROT: Dict[str, str] = {
    "ACVR2A": "Q13705",
    "ACVR2B": "P27037",
    "KRAS": "P01116",
    "NRAS": "P01111",
    "HRAS": "P01112",
    "TP53": "P04637",
    "PCSK9": "Q8NBP7",
    "EGFR": "P00533",
    "ERBB2": "P04626",
    "MET": "P08581",
    "BRAF": "P15056",
    "ALK": "Q9UM73",
    "VEGFA": "P15692",
    "PD1": "Q15116",
    "PDL1": "Q9NZQ7",
    "CTLA4": "P16410",
    "CD19": "P15391",
    "ACE2": "Q9BYF1",
    "FTO": "Q9C0B1",
    "APOE": "P02649",
    "APP": "P05067",
    "LDLR": "P01130",
}

# 别名（ChEMBL 中机制描述）
MOA_KEYWORDS = {
    "ANTAGONIST": "拮抗剂",
    "AGONIST": "激动剂",
    "INHIBITOR": "抑制剂",
    "MODULATOR": "调节剂",
    "BLOCKER": "阻断剂",
    "ACTIVATOR": "激活剂",
    "PARTIAL AGONIST": "部分激动剂",
    "INVERSE AGONIST": "反向激动剂",
    "BINDING": "结合剂",
}
STANDARD_TYPE_LABELS = {
    "IC50": "IC₅₀",
    "Kd": "Kd",
    "Ki": "Ki",
    "EC50": "EC₅₀",
    "Potency": "效能",
}
POTENCY_BANDS = {
    "nM": {
        (0, 1): ("picomolar", 1.0),
        (1, 10): ("high nM", 0.9),
        (10, 100): ("moderate nM", 0.7),
        (100, 1000): ("low nM", 0.5),
        (1000, 10000): ("μM", 0.3),
        (10000, 1e9): ("weak", 0.1),
    },
}


class ChEMBLConnector:
    """ChEMBL 药物-靶点亲和力连接器。"""

    def __init__(self, cache_dir: str = "/tmp/hms_chembl_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._ctx = ssl.create_default_context()
        self._headers = {"User-Agent": "AIXBox/1.0"}

    def _request(self, url: str, retries: int = 2, timeout: int = 20) -> Optional[Dict]:
        last_err = None
        for attempt in range(1 + retries):
            try:
                req = urllib.request.Request(url, headers=self._headers)
                resp = urllib.request.urlopen(req, context=self._ctx, timeout=timeout)
                return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                last_err = e
                if attempt < retries:
                    __import__("time").sleep(1.5 ** attempt)
            except Exception as e:
                last_err = e
                break
        if last_err:
            print(f"⚠ ChEMBL {url[:80]} → {last_err}", file=sys.stderr)
        return None

    def _paged(self, base_url: str, max_pages: int = 3) -> List[Dict]:
        """获取分页结果。"""
        all_items = []
        url = base_url
        for _ in range(max_pages):
            data = self._request(url)
            if not data:
                break
            items = data.get("activities", data.get("mechanisms", data.get("drugs",
                       data.get("molecules", data.get("targets", data.get("target_components", []))))))
            if not items:
                break
            all_items.extend(items)
            page_meta = data.get("page_meta", {})
            next_url = page_meta.get("next")
            if not next_url:
                break
            url = urllib.parse.urljoin(API_BASE, next_url)
        return all_items

    def target_id_by_uniprot(self, uniprot: str) -> Optional[str]:
        """通过 UniProt ID 查找 ChEMBL 靶点 ID。"""
        url = f"{API_BASE}/target.json?target_components__accession={uniprot}&limit=5"
        data = self._request(url)
        if not data:
            return None
        targets = data.get("targets", [])
        if not targets:
            return None
        # 优先选 SINGLE PROTEIN
        for t in targets:
            if t.get("target_type") == "SINGLE PROTEIN" and t.get("organism") == "Homo sapiens":
                return t["target_chembl_id"]
        return targets[0].get("target_chembl_id")

    def target_id_by_gene(self, gene: str) -> Optional[str]:
        """通过基因符号查找 ChEMBL 靶点 ID。"""
        gene = gene.upper()
        uniprot = GENE_UNIPROT.get(gene)
        if uniprot:
            tid = self.target_id_by_uniprot(uniprot)
            if tid:
                return tid
        # 备选：通过同义词搜索
        url = f"{API_BASE}/target.json?pref_name__icontains={gene}&organism=Homo%20sapiens&limit=5"
        data = self._request(url)
        if data:
            for t in data.get("targets", []):
                if t.get("target_type") == "SINGLE PROTEIN":
                    return t["target_chembl_id"]
        return None

    def get_target_info(self, chembl_id: str) -> Dict:
        """获取靶点详情。"""
        url = f"{API_BASE}/target/{chembl_id}.json"
        data = self._request(url)
        if not data:
            return {}
        return {
            "chembl_id": chembl_id,
            "pref_name": data.get("pref_name", ""),
            "organism": data.get("organism", ""),
            "target_type": data.get("target_type", ""),
            "uniprot": (data.get("target_components", [{}])[0].get("accession", "") if data.get("target_components") else ""),
        }

    def get_mechanisms(self, chembl_id: str) -> List[Dict]:
        """获取机制（激动剂/拮抗剂等）。"""
        url = f"{API_BASE}/mechanism.json?target_chembl_id={chembl_id}&limit=50"
        data = self._request(url)
        results = []
        for m in (data or {}).get("mechanisms", []):
            results.append({
                "molecule_chembl_id": m.get("molecule_chembl_id", ""),
                "action_type": m.get("action_type", ""),
                "mechanism_of_action": m.get("mechanism_of_action", ""),
                "max_phase": m.get("max_phase_for_ind", 0),
                "molecule_name": m.get("molecule_name", ""),
            })
        return results

    def get_activities(self, chembl_id: str, max_results: int = 50) -> List[Dict]:
        """获取亲和力数据（IC50/Kd/Ki，过滤有 pChEMBL 的）。"""
        # 先获取总数
        url = (f"{API_BASE}/activity.json?target_chembl_id={chembl_id}"
               f"&standard_type__in=IC50,Kd,Ki"
               f"&pchembl_value__isnull=false"
               f"&limit=1&order_by=-pchembl_value")
        data = self._request(url)
        total = (data or {}).get("page_meta", {}).get("total_count", 0)
        if total == 0:
            return []

        # 获取实际数据
        limit = min(max_results, total, 100)
        url = (f"{API_BASE}/activity.json?target_chembl_id={chembl_id}"
               f"&standard_type__in=IC50,Kd,Ki"
               f"&pchembl_value__isnull=false"
               f"&limit={limit}&order_by=-pchembl_value")
        data = self._request(url)
        results = []
        for a in (data or {}).get("activities", []):
            pv = a.get("pchembl_value")
            try:
                pv = float(pv) if pv is not None else None
            except (ValueError, TypeError):
                pv = None
            if pv is None or pv < 5:
                continue
            results.append({
                "molecule_chembl_id": a.get("molecule_chembl_id", ""),
                "standard_type": a.get("standard_type", ""),
                "standard_value": a.get("standard_value"),
                "standard_units": a.get("standard_units", ""),
                "standard_relation": a.get("standard_relation", ""),
                "pchembl_value": pv,
                "assay_description": (a.get("assay_description", "") or "")[:120],
                "document_id": a.get("document_chembl_id", ""),
            })
        return results

    def sum_by_gene(self, gene: str) -> Dict:
        """完整汇总：按基因搜索→获取机制+活性→结构化。"""
        gene = gene.upper()
        chembl_id = self.target_id_by_gene(gene)
        if not chembl_id:
            return {
                "gene": gene,
                "found": False,
                "chembl_id": None,
                "summary": f"ChEMBL 中未找到 {gene} 靶点条目",
            }

        target_info = self.get_target_info(chembl_id)
        mechanisms = self.get_mechanisms(chembl_id)
        activities = self.get_activities(chembl_id)

        # 汇总药物/化合物
        drugs_seen = set()
        drug_list = []
        for m in mechanisms:
            mol_id = m["molecule_chembl_id"]
            if mol_id not in drugs_seen:
                drugs_seen.add(mol_id)
                drug_list.append(m)

        # 最佳活性
        best_act = activities[0] if activities else None
        best_pchembl = best_act["pchembl_value"] if best_act else None

        # pChEMBL 分布
        pchembl_bands = {"9+": 0, "8-9": 0, "7-8": 0, "6-7": 0, "5-6": 0}
        for a in activities:
            pv = a["pchembl_value"]
            if pv >= 9:
                pchembl_bands["9+"] += 1
            elif pv >= 8:
                pchembl_bands["8-9"] += 1
            elif pv >= 7:
                pchembl_bands["7-8"] += 1
            elif pv >= 6:
                pchembl_bands["6-7"] += 1
            else:
                pchembl_bands["5-6"] += 1

        # 机制汇总
        action_types = list(set(m["action_type"] for m in mechanisms if m["action_type"]))

        max_phase = max((m["max_phase"] or 0 for m in mechanisms), default=0)
        phase_label = {0: "临床前", 1: "Phase 1", 2: "Phase 2", 3: "Phase 3", 4: "已上市"}.get(max_phase, str(max_phase))

        has_drug = max_phase >= 4

        return {
            "gene": gene,
            "found": True,
            "chembl_id": chembl_id,
            "target_info": target_info,
            "n_activities": len(activities),
            "n_mechanisms": len(mechanisms),
            "n_drugs": len(drug_list),
            "best_pchembl": best_pchembl,
            "pchembl_distribution": pchembl_bands,
            "action_types": action_types,
            "max_phase": max_phase,
            "max_phase_label": phase_label,
            "has_approved_drug": has_drug,
            "drug_list": drug_list[:15],
            "top_activities": activities[:10],
            "summary": (
                f"ChEMBL {chembl_id}: {len(drug_list)} 个靶向药物/化合物, "
                f"最高 Phase {max_phase} ({phase_label}), "
                f"最佳 pChEMBL={best_pchembl if best_pchembl else 'N/A'}, "
                f"{len(activities)} 条高置信度活性数据"
            ),
        }

    def to_evidence_rows(self, gene: str, summary: Optional[Dict] = None) -> List:
        """映射到 EvidenceRow（可药性维度）。"""
        tem = _tem()
        if summary is None:
            summary = self.sum_by_gene(gene)

        rows = []
        if not summary.get("found"):
            rows.append(tem.EvidenceRow(
                target_gene=gene, disease="",
                dimension=tem.EvidenceDimension.DRUGGABILITY,
                strength=tem.EvidenceStrength.WEAK,
                direction=tem.EvidenceDirection.UNKNOWN,
                sub_dimension="ChEMBL",
                key_finding=f"ChEMBL 中未找到 {gene} 靶点条目",
                source_name="ChEMBL (EMBL-EBI)",
            ))
            return rows

        # 主行
        pv = summary.get("best_pchembl")
        if pv and pv >= 8:
            str_band = tem.EvidenceStrength.P_VALUE_LT_5E8
        elif pv and pv >= 7:
            str_band = tem.EvidenceStrength.P_VALUE_LT_1E5
        elif pv and pv >= 6:
            str_band = tem.EvidenceStrength.P_VALUE_LT_0_01
        elif pv:
            str_band = tem.EvidenceStrength.NOMINAL
        else:
            str_band = tem.EvidenceStrength.WEAK

        rows.append(tem.EvidenceRow(
            target_gene=gene,
            disease="; ".join(summary.get("action_types", [])),
            dimension=tem.EvidenceDimension.DRUGGABILITY,
            strength=str_band,
            direction=tem.EvidenceDirection.ASSOCIATED,
            sub_dimension=f"ChEMBL:{summary['chembl_id']}",
            effect_size=summary.get("best_pchembl", 0),
            key_finding=summary["summary"],
            notes=f"药物: {summary['n_drugs']} | 高置信度活性: {summary['n_activities']} | Phase: {summary['max_phase_label']}",
            source_name="ChEMBL (EMBL-EBI)",
            source_id=summary["chembl_id"],
        ))

        # 按机制分行
        for m in summary.get("drug_list", [])[:5]:
            act = m.get("action_type", "?")
            moa = m.get("mechanism_of_action", "?")
            rows.append(tem.EvidenceRow(
                target_gene=gene,
                disease="",
                dimension=tem.EvidenceDimension.DRUGGABILITY,
                strength=tem.EvidenceStrength.P_VALUE_LT_0_01 if m.get("max_phase", 0) >= 2 else tem.EvidenceStrength.NOMINAL,
                direction=tem.EvidenceDirection.ASSOCIATED,
                sub_dimension=f"ChEMBL:{act}",
                effect_size=m.get("max_phase", 0),
                key_finding=f"{m.get('molecule_name', m['molecule_chembl_id'])} — {MOA_KEYWORDS.get(act, act)} ({moa})",
                notes=f"Phase: {m.get('max_phase', '?')} | ChEMBL: {m['molecule_chembl_id']}",
                source_name="ChEMBL (EMBL-EBI)",
                source_id=m["molecule_chembl_id"],
            ))

        # 最佳活性行
        for a in summary.get("top_activities", [])[:3]:
            std = STANDARD_TYPE_LABELS.get(a["standard_type"], a["standard_type"])
            rel = a.get("standard_relation", "")
            val = a.get("standard_value", "?")
            units = a.get("standard_units", "")
            rows.append(tem.EvidenceRow(
                target_gene=gene, disease="",
                dimension=tem.EvidenceDimension.DRUGGABILITY,
                strength=str_band,
                direction=tem.EvidenceDirection.ASSOCIATED,
                sub_dimension=f"ChEMBL:{std}",
                effect_size=a["pchembl_value"],
                key_finding=f"{std}={rel}{val}{units} | pChEMBL={a['pchembl_value']:.1f}",
                notes=(a.get("assay_description", "") or "")[:100],
                source_name="ChEMBL (EMBL-EBI)",
                source_id=a["molecule_chembl_id"],
            ))

        return rows


def main():
    parser = __import__("argparse").ArgumentParser(description="ChEMBL 药物-靶点亲和力连接器")
    parser.add_argument("gene", help="基因符号")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--best-only", action="store_true", help="仅显示最佳 pChEMBL")
    args = parser.parse_args()

    conn = ChEMBLConnector()
    summary = conn.sum_by_gene(args.gene.upper())

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        return

    print(f"\n{'='*60}")
    print(f"ChEMBL 药物-靶点亲和力证据")
    print(f"基因: {args.gene.upper()}")
    print(f"{'='*60}\n")

    if not summary.get("found"):
        print(f"❌ {summary.get('summary')}")
        return

    t = summary["target_info"]
    print(f"ChEMBL ID: {summary['chembl_id']} ({t.get('pref_name','?')})")
    print(f"化合物体数量: {summary['n_activities']} 条高置信度活性")
    print(f"靶向药物/化合物: {summary['n_drugs']} 个")
    print(f"最高临床阶段: {summary['max_phase_label']}")
    print(f"批准药物: {'✅ 有' if summary.get('has_approved_drug') else '❌ 无'}")
    print(f"最佳 pChEMBL: {summary.get('best_pchembl', 'N/A')}")
    print(f"pChEMBL 分布:")
    for k, v in summary.get("pchembl_distribution", {}).items():
        if v > 0:
            print(f"  {k}: {v}")
    print(f"作用机制: {', '.join(summary.get('action_types', []))}")
    print(f"\n靶向药物/化合物 (前 {len(summary.get('drug_list',[]))}):")
    for m in summary.get("drug_list", []):
        print(f"  {m['molecule_name'] or m['molecule_chembl_id']:30s} | {m['action_type']:12s} | Phase {m.get('max_phase',0)}")
    print(f"\n最佳活性:")
    for a in summary.get("top_activities", [])[:5]:
        print(f"  {a['molecule_chembl_id']} | {a['standard_type']}={a.get('standard_relation','')}{a['standard_value']}{a['standard_units']} | pChEMBL={a['pchembl_value']:.1f}")


if __name__ == "__main__":
    main()

# === Wrapper for validation script ===
def generate_evidence_rows(gene: str, disease: str = "") -> list:
    """Wrapper: generate_evidence_rows → to_evidence_rows."""
    c = ChEMBLConnector()
    summary = c.sum_by_gene(gene)
    return c.to_evidence_rows(gene, summary)
