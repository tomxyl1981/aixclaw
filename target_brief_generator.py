#!/usr/bin/env python3
"""
Phase 5: AI 靶点简报生成器 (Target Brief Generator) — 中文版 v1.1

整合七维证据矩阵 + 可编辑性评分 → 结构化靶点简报（中文）。
模板化渲染，不依赖 LLM，支持扩展 LLM 润色。

输出: Markdown（可直接写入飞书文档/HTML/微信）
"""

import os, sys, json, datetime
from typing import Optional, List, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_ALL_OK = True
try:
    from target_evidence_matrix import (
        TargetEvidenceMatrix, EvidenceRow, EvidenceDimension,
        EvidenceStrength, EvidenceDirection, InterpretabilityLevel,
        ReasoningStep
    )
except ImportError:
    _ALL_OK = False

try:
    from editableity_connector import score_editableity, get_global_scores, recommend_strategy
except ImportError:
    _ALL_OK = False

try:
    from evidence_editableity_bridge import editableity_to_rows, build_editableity_safety
except ImportError:
    _ALL_OK = False
# ── 熵态分析（邓煜框架 / P0 2026-07-31）──
try:
    from entropy_section import compute_entropy, render_entropy_section
    _HAS_ENTROPY = True
except Exception:
    _HAS_ENTROPY = False


REPORT_VERSION = "1.1.0"
REPORT_DATE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")


# ── 评分标签翻译 ──

def _rating_label(score: float) -> str:
    if score >= 0.8:
        return "💚 极高可编辑性"
    elif score >= 0.6:
        return "🟢 高可编辑性"
    elif score >= 0.4:
        return "🟡 中等可编辑性"
    elif score >= 0.2:
        return "🟠 低可编辑性"
    else:
        return "🔴 不可编辑"


def _strength_label(s: str) -> str:
    labels = {
        "p<5e-8": "🟢 全基因组显著",
        "p<1e-5": "🟢 暗示性关联",
        "p<0.01": "🟡 一般显著",
        "AUC>0.8": "🟢 高区分度",
        "AUC>0.6": "🟡 中等区分度",
        "log2FC>1": "🟢 表达显著",
        "log2FC>0.5": "🟡 表达中等",
        "nominal": "🟠 名义显著",
        "weak": "🟠 弱信号",
        "not_significant": "⚪ 不显著",
        "unknown": "❓ 未知",
    }
    return labels.get(s.lower(), s)


def _direction_label(d: str) -> str:
    labels = {
        "upregulated": "⬆️ 上调/激活/促进",
        "downregulated": "⬇️ 下调/抑制/保护",
        "gain_of_function": "🔺 功能获得",
        "loss_of_function": "🔻 功能缺失",
        "supportive": "✅ 支持",
        "contradictory": "❌ 矛盾",
        "unknown": "❓ 未知",
    }
    return labels.get(d.lower(), d)


def _section(title: str, level: int = 2) -> str:
    return "\n" + ("#" * level) + f" {title}\n"


def _table(headers: list, rows: list) -> str:
    sep = "|" + "|".join("---" for _ in headers) + "|"
    hdr = "| " + " | ".join(headers) + " |"
    lines = [hdr, sep]
    for r in rows:
        cells = [str(c) if c is not None else "" for c in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _score_bar(score: float, width: int = 20) -> str:
    filled = int(score * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {score:.3f}"


# ══════════════════════════════════════════════════════════════

def generate_brief(
    gene_symbol: str,
    ensembl_id: str = "",
    disease: str = "",
    editableity_data: Optional[dict] = None,
    global_scores: Optional[dict] = None,
    evidence_rows: Optional[list] = None,
    llm_summary: Optional[str] = None,
) -> str:
    """
    生成中文靶点简报 (Markdown).
    """
    g_up = gene_symbol.upper()

    # 数据获取
    if editableity_data is None:
        try:
            editableity_data = score_editableity(g_up, ensembl_id) or {}
        except Exception:
            editableity_data = {}

    if global_scores is None:
        try:
            global_scores = get_global_scores(g_up) or {}
        except Exception:
            global_scores = {}

    if evidence_rows is None:
        try:
            from evidence_editableity_bridge import editableity_to_rows
            evidence_rows = editableity_to_rows(g_up, ensembl_id, editableity_data, global_scores)
        except Exception:
            evidence_rows = []

    editableity = editableity_data.get("editableity", {})
    overall = editableity.get("overall_score", 0.0)
    comp_scores = editableity_data.get("component_scores", {})
    struct = editableity.get("gene_structure", {})
    span = struct.get("genomic_span", {})
    pam = editableity.get("pam_availability", {})
    gno = editableity.get("editing_evidence", {}).get("gnomad_lof", {})
    dep = editableity.get("editing_evidence", {}).get("depmap", {})
    strategy_rec = editableity.get("strategy_recommendation", {})
    top_strat = editableity.get("top_strategy", "未知")
    gs_gnomad = global_scores.get("gnomad", {})
    gs_dep = global_scores.get("depmap", {})
    gno_show = gs_gnomad if gs_gnomad else gno
    dep_show = gs_dep if gs_dep else dep

        # ── UK Biobank + FinnGen 队列证据 ──
    try:
        from ukb_finngen_connector import ClinicalEvidenceConnector as _FinngenConnector
        _ukb_fn = _FinngenConnector()
        _ukb_result = _ukb_fn.query_by_gene(g_up, disease)
        _ukb_rows = _ukb_fn.to_evidence_rows(g_up, disease, _ukb_result)
    except Exception:
        _ukb_result = {"n_datasets": 0, "overall_support": "none",
                       "evidence_summary": "UKB+FinnGen 连接器加载失败"}
        _ukb_rows = []

    # 可编辑性评级
    rating = _rating_label(overall)

    # ── 开始构建报告 ──
    brief = []

    brief.append(f"# 🧬 靶点简报: {g_up}")
    brief.append("")
    brief.append(f"> **生成时间**: {REPORT_DATE} | **报告版本**: v{REPORT_VERSION}")
    brief.append(f"> **基因ID**: {ensembl_id or gs_gnomad.get('ensembl_id', '?')}")
    brief.append(f"> **关联疾病**: {disease or '待定'}")

    # ── 熵态速览徽章（p0 entropy badge）──
    try:
        from entropy_section import compute_entropy
        _entropy = compute_entropy(matrix)
        ne = _entropy.get('natural_entropy', 0.5)
        ct = _entropy.get('consensus_type', 'no_data')
        pr = _entropy.get('pressure_ratio', 0)
        _ctx_badge = "🟢" if ct == "full_consensus" else ("🟡" if ct == "majority" else "🔴")
        _ent_badge = "🟢" if ne < 0.3 else ("🟡" if ne < 0.5 else "🔴")
        brief.append(f"> {_ctx_badge} 共识: {ct} | {_ent_badge} 熵: {ne:.3f} | 压熵: {pr*100:.1f}%")
    except Exception:
        pass
    brief.append("")

    # ═══════ 1. 执行摘要 ═══════
    brief.append(_section("一、执行摘要", 2))

    if llm_summary:
        brief.append(llm_summary)
    else:
        brief.append(f"**{g_up}**: {rating}（综合评分 **{overall:.3f}**）")
        brief.append("")

        oeu = gno_show.get("oe_upper", "?")
        lof_desc = "不耐受（敲除风险高）" if isinstance(oeu, (int, float)) and oeu < 0.35 else "耐受（可敲除）"
        dep_eff = dep_show.get("depmap_effect", dep_show.get("gene_effect", "?"))
        ess_desc = "必需" if isinstance(dep_eff, (int, float)) and dep_eff <= -1.0 else \
                   "可能必需" if isinstance(dep_eff, (int, float)) and dep_eff <= -0.5 else "非必需"

        brief.extend([
            f"- **基因结构**: {comp_scores.get('gene_structure', 0):.1f} — {struct.get('exon_count','?')} 个外显子, CDS {struct.get('cds_length','?')}bp",
            f"- **PAM 可及性**: {comp_scores.get('pam_availability', 0):.1f} — SpCas9 有 {pam.get('SpCas9_NGG',{}).get('count','?')} 个 NGG 位点",
            f"- **CRISPR 耐受性**: {comp_scores.get('tolerability', 0):.1f} — gnomAD pLoF o/e 上限 = {oeu}（{lof_desc}）",
            f"- **基因必需性**: {comp_scores.get('essentiality', 0):.1f} — DepMap 效应值 {dep_eff}（{ess_desc}）",
            f"- **推荐策略**: **{top_strat}**",
            "",
        ])

    # ═══════ 2. 评分总览 ═══════
    brief.append(_section("二、可编辑性评分总览", 3))
    score_rows = [
        ["基因结构", f"{comp_scores.get('gene_structure',0):.3f}", _score_bar(comp_scores.get('gene_structure',0))],
        ["PAM 可及性", f"{comp_scores.get('pam_availability',0):.3f}", _score_bar(comp_scores.get('pam_availability',0))],
        ["CRISPR 耐受性", f"{comp_scores.get('tolerability',0):.3f}", _score_bar(comp_scores.get('tolerability',0))],
        ["基因必需性", f"{comp_scores.get('essentiality',0):.3f}", _score_bar(comp_scores.get('essentiality',0))],
        ["策略适配", f"{comp_scores.get('strategy_fit',0):.3f}", _score_bar(comp_scores.get('strategy_fit',0))],
        ["━━━━━━━━", "━━━━━━━", "━━━━━━━━━━━━"],
        ["**综合评分**", f"**{overall:.3f}**", _score_bar(overall)],
    ]
    brief.append(_table(["维度", "评分", ""], score_rows))
    brief.append("")

    # ═══════ 3. 基因结构 ═══════
    brief.append(_section("三、基因结构", 3))
    brief.append(_table(
        ["属性", "值"],
        [
            ["染色体", span.get("chr", "?")],
            ["基因组范围", f"{span.get('start','?')} - {span.get('end','?')} ({span.get('strand','?')})"],
            ["外显子数", str(struct.get("exon_count", "?"))],
            ["编码区长度", f"{struct.get('cds_length','?')} bp"],
            ["数据来源", struct.get("_source", "Ensembl")],
        ]
    ))
    brief.append("")

    # ═══════ 4. PAM ═══════
    brief.append(_section("四、PAM 位点分析", 3))
    pam_rows = []
    for cas in ["SpCas9_NGG", "SpCas9_NG", "SaCas9", "AsCas12a"]:
        info = pam.get(cas, {})
        count = info.get("count", 0)
        sg_ok_str = info.get("sg_ok_count", 0)
        score_str = info.get("spacing_score", f"{sg_ok_str}/{count}")
        pam_rows.append([cas.replace("_", "-"), str(count), str(score_str)])
    brief.append(_table(["核酸酶", "PAM 位点数", "间距评分"], pam_rows))
    brief.append(f"\n> 数据来源: {pam.get('_source', 'Ensembl + 本地索引')}\n")

    # ═══════ 5. gnomAD 约束 ═══════
    brief.append(_section("五、群体遗传约束（gnomAD）", 3))
    if gno_show:
        brief.append(_table(
            ["指标", "值", "说明"],
            [
                ["pLoF o/e 比值", f"{gno_show.get('oe','?'):.4f}" if isinstance(gno_show.get('oe'), (int, float)) else str(gno_show.get('oe', '?')),
                 "观测/期望 Loss-of-Function 变异数比"],
                ["pLoF o/e 上限", f"{gno_show.get('oe_upper','?'):.3f}" if isinstance(gno_show.get('oe_upper'), (int, float)) else str(gno_show.get('oe_upper', '?')),
                 "≤0.35=不耐受, ≤0.15=极不耐受"],
                ["约束评分", f"{gno_show.get('score','?'):.1f}" if isinstance(gno_show.get('score'), (int, float)) else str(gno_show.get('score', '?')),
                 "1.0=最大约束"],
                ["期望 LoF", f"{gno_show.get('exp','?'):.1f}" if isinstance(gno_show.get('exp'), (int, float)) else str(gno_show.get('exp', '?')),
                 ""],
                ["观测 LoF", f"{gno_show.get('obs','?'):.1f}" if isinstance(gno_show.get('obs'), (int, float)) else str(gno_show.get('obs', '?')),
                 ""],
            ]
        ))
    else:
        brief.append("（无 gnomAD 数据）\n")

    # ═══════ 6. DepMap ═══════
    brief.append(_section("六、基因必需性（DepMap）", 3))
    if dep_show:
        eff = dep_show.get("gene_effect", dep_show.get("depmap_effect", "?"))
        is_ess = dep_show.get("is_essential", dep_show.get("significance") == "essential")
        brief.append(_table(
            ["指标", "值"],
            [
                ["基因效应 (Gene Effect)", f"{eff:.4f}" if isinstance(eff, (int, float)) else str(eff)],
                ["推断", "⚠️ 必需（敲除有毒性）" if is_ess else "✅ 非必需（可安全敲除）"],
                ["细胞系数", str(dep_show.get("cell_line_count", dep_show.get("n_cell_lines", "?")))],
            ]
        ))
    else:
        brief.append("（无 DepMap 数据）\n")

    # ═══════ 7. 编辑策略 ═══════
    brief.append(_section("七、编辑策略推荐", 3))
    strategies = strategy_rec.get("strategies", [])
    if strategies:
        strat_rows = []
        for s in strategies[:3]:
            strat_rows.append([
                s.get("type", "?"),
                f"{s.get('score', 0):.2f}",
                s.get("reason", ""),
            ])
        brief.append(_table(["策略", "评分", "理由"], strat_rows))
        brief.append(f"\n**推荐**: {strategy_rec.get('recommended', top_strat)}\n")
    else:
        brief.append("（策略推荐不可用，系统未返回）\n")

    # ═══════ 8. 证据矩阵 ═══════
    if evidence_rows:
        brief.append(_section("八、证据矩阵摘要", 3))
        brief.append(f"共 {len(evidence_rows)} 条证据行：\n")
        ev_rows = []
        for r in evidence_rows:
            dim = r.dimension.value if hasattr(r.dimension, 'value') else r.dimension
            sub = r.sub_dimension if hasattr(r, 'sub_dimension') else ""
            st = r.strength.value if hasattr(r.strength, 'value') else r.strength
            di = r.direction.value if hasattr(r.direction, 'value') else r.direction
            es = f"{r.effect_size:.3f}" if hasattr(r, 'effect_size') and isinstance(getattr(r, 'effect_size', 0), (int, float)) else "—"
            ev_rows.append([_strength_label(st), sub, _direction_label(di), es])
        if ev_rows:
            brief.append(_table(["强度", "子维度", "方向", "效应值"], ev_rows))
        brief.append("")

    # ═══════ 8.5. 人群队列证据 (UK Biobank + FinnGen) ═══════
    if _ukb_result.get("n_datasets", 0) > 0:
        brief.append(_section("八·五、人群队列证据（UK Biobank + FinnGen）", 3))
        support = _ukb_result.get("overall_support", "none")
        support_label = {"strong": "🟢 强", "moderate": "🟡 中", "weak": "🟠 弱", "none": "⚪ 无"}.get(support, support)
        brief.extend([
            f"- **队列覆盖**: {_ukb_result['n_datasets']} 个 GWAS 数据集",
            f"  - UK Biobank: {_ukb_result.get('n_ukb', 0)} 个",
            f"  - FinnGen: {_ukb_result.get('n_finn', 0)} 个",
            f"- **人群跨度**: {', '.join(_ukb_result.get('populations', []))}",
            f"- **总体证据**: {support_label}",
            f"- **摘要**: {_ukb_result.get('evidence_summary', '')}",
            "",
        ])
        if _ukb_result.get("datasets"):
            ds_rows = []
            for ds in _ukb_result["datasets"]:
                ds_rows.append([ds["id"], ds["cohort"], ds["trait"][:40], ds.get("population", "?"), str(ds.get("n", 0))])
            brief.append(_table(["数据集ID", "队列", "性状", "人群", "样本量"], ds_rows))
            brief.append("")
    else:
        brief.append(_section("八·五、人群队列证据（UK Biobank + FinnGen）", 3))
        brief.append("（无可用的 UK Biobank / FinnGen 队列数据）\n")

    # ═══════ 八·六. 临床试验证据 (ClinicalTrials.gov) ═══════
    try:
        from clinicaltrials_connector import ClinicalTrialsConnector as _CTConnector2
        _ct_conn2 = _CTConnector2()
        _ct_summary = _ct_conn2.summarize_by_gene(g_up)
        _ct_rows = _ct_conn2.to_evidence_rows(g_up, _ct_summary)
    except Exception as _ct_err:
        _ct_summary = {"n_studies": 0, "max_phase_label": "查询失败",
                       "conditions": [], "summary": f"ClinicalTrials.gov 查询异常: {_ct_err}"}
        _ct_rows = []

    if _ct_summary.get("n_studies", 0) > 0:
        brief.append(_section("八·六、临床试验证据（ClinicalTrials.gov）", 3))
        _ct_n = _ct_summary["n_studies"]
        _ct_max = _ct_summary.get("max_phase_label", "?")
        _ct_active = "🟢 有活跃试验" if _ct_summary.get("has_active_trials") else "⚪ 无活跃试验"
        _ct_conds = "；".join(_ct_summary.get("conditions", [])[:4])
        _ct_intervs = "；".join(_ct_summary.get("interventions", [])[:4])
        _ct_by_phase = _ct_summary.get("by_phase", {})
        _ct_phase_str = " | ".join(f"{k} {v}项" for k, v in _ct_by_phase.items() if v > 0)
        brief.extend([
            f"- **试验总数**: {_ct_n} 项",
            f"- **最高阶段**: {_ct_max}",
            f"- **活跃状态**: {_ct_active}",
            f"- **阶段分布**: {_ct_phase_str}",
            f"- **适应症**: {_ct_conds}",
            f"- **干预药物**: {_ct_intervs}",
            f"- **摘要**: {_ct_summary.get('summary', '')}",
            "",
        ])
        # 按阶段列出代表性试验
        _ct_detail = _ct_summary.get("phase_details", {})
        for _ct_phase_lbl, _ct_infos in _ct_detail.items():
            if not _ct_infos:
                continue
            _ct_short = _ct_infos[:3]
            for _ct_info in _ct_short:
                brief.append(f"  - NCT{_ct_info['nct_id']}: {_ct_info['title'][:60]}")
                brief.append(f"    {_ct_info['overall_status']} | {_ct_info['phase_label']} | 适应症: {'; '.join(_ct_info['conditions'][:2])}")
            if len(_ct_infos) > 3:
                brief.append(f"    ... 还有 {len(_ct_infos)-3} 项")
            brief.append("")
    else:
        brief.append(_section("八·六、临床试验证据（ClinicalTrials.gov）", 3))
        brief.append("（ClinicalTrials.gov 中未查到该靶点的临床试验记录）\n")

    # ═══════ 八·七. ChEMBL 药物-靶点亲和力 ═══════
    try:
        from chembl_connector import ChEMBLConnector as _ChChConn
        _chch = _ChChConn()
        _chch_info = _chch.sum_by_gene(g_up)
    except Exception as _chch_err:
        _chch_info = {"found": False, "summary": f"ChEMBL 查询异常: {_chch_err}"}

    if _chch_info.get("found"):
        brief.append(_section("八·七、药物-靶点亲和力（ChEMBL）", 3))
        _chch_dist = "; ".join(f"{k}:{v}" for k,v in _chch_info.get("pchembl_distribution",{}).items() if v>0)
        brief.extend([
            f"- **ChEMBL ID**: {_chch_info.get('chembl_id','?')}",
            f"- **靶向化合物**: {_chch_info.get('n_activities',0)} 条高置信度活性数据",
            f"- **靶向药物/化合物**: {_chch_info.get('n_drugs',0)} 个",
            f"- **最佳 pChEMBL**: {_chch_info.get('best_pchembl','N/A')}",
            f"- **最高临床阶段**: {_chch_info.get('max_phase_label','?')}",
            f"- **批准药物**: {'✅ 有已批准药物' if _chch_info.get('has_approved_drug') else '❌ 无批准药物'}",
            f"- **作用机制**: {'; '.join(_chch_info.get('action_types', []))}",
            f"- **pChEMBL 分布**: {_chch_dist}",
            "",
        ])
        dl = _chch_info.get("drug_list", [])
        if dl:
            dr = [[d.get("molecule_name", d.get("molecule_chembl_id","?"))[:25], d.get("action_type","?"), str(d.get("max_phase",0))] for d in dl[:8]]
            brief.append(_table(["化合物", "作用类型", "最高Phase"], dr))
            brief.append("")
    else:
        brief.append(_section("八·七、药物-靶点亲和力（ChEMBL）", 3))
        brief.append("（ChEMBL 中未查到该靶点的药物亲和力数据）\n")

    # ═══════ 八·八. UniPert-G2CP AI 预测证据 ═══════
    try:
        from unipert_connector import generate_evidence_rows as _up_gen, check_env as _up_env
        _up_rows = _up_gen(g_up, disease=disease, run_inference=False)
        _up_env_info = _up_env()
    except Exception as _up_err:
        _up_rows = []
        _up_env_info = {"error": str(_up_err)}

    _up_dim = "AI_prediction"
    if _up_rows:
        brief.append(_section("八·八、AI 预测证据（UniPert-G2CP）", 3))
        brief.extend([
            f"- **模型**: UniPert-G2CP (腾讯生命科学实验室 × 中南大学, Cell 2026)",
            f"- **许可证**: GPL-3.0 (已开源)",
            f"- **仓库**: https://github.com/lynn-1998/UniPert",
            f"- **Zenodo 检查点**: https://zenodo.org/doi/10.5281/zenodo.20355906",
            f"- **环境**: device={_up_env_info.get('device','?')}, "
            f"UniPert={'✅' if _up_env_info.get('unipert_installed') else '❌'}, "
            f"模型={'✅' if _up_env_info.get('model_downloaded') else '❌'}",
            f"- **可解释性**: 深度嵌入级 (0.1/1.0) — 不替代实验验证",
            "",
        ])
        for r in _up_rows:
            d = r if isinstance(r, dict) else (r.to_dict() if hasattr(r, 'to_dict') else {})
            dim = d.get('sub_dimension', '?')
            finding = (d.get('key_finding', '') or '')[:120]
            notes = (d.get('notes', '') or '')[:80]
            brief.append(f"  - **[{dim}]** {finding}")
            if notes:
                brief.append(f"    📎 {notes}")
        brief.append("")
    else:
        brief.append(_section("八·八、AI 预测证据（UniPert-G2CP）", 3))
        err = _up_env_info.get('error', '查询失败')
        brief.append(f"（UniPert-G2CP AI 预测证据生成异常: {err}）\n")

    # ═══════ 八·九. MR 因果证据 ═══════
    try:
        from mr_connector import generate_evidence_rows as _mr_gen
        _mr_rows = _mr_gen(g_up, disease=disease)
    except Exception as _mr_err:
        _mr_rows = []
        _mr_err_str = str(_mr_err)

    if _mr_rows:
        brief.append(_section("八·九、MR 因果证据（孟德尔随机化）", 3))
        brief.extend([
            f"- **方法**: IVW (主) / MR-Egger (多效性检测) / 加权中位数 (鲁棒) / 数据源: IEU OpenGWAS",
            f"- **暴露**: {g_up} (cis-eQTL 工具变量) / **结局**: {disease or '（未指定）'}",
            "",
        ])
        for r in _mr_rows:
            d = r if isinstance(r, dict) else (r.to_dict() if hasattr(r, 'to_dict') else {})
            dim = d.get('sub_dimension', '?')
            finding = (d.get('key_finding', '') or '')[:120]
            notes = (d.get('notes', '') or '')[:80]
            brief.append(f"  - **[{dim}]** {finding}")
            if notes:
                brief.append(f"    📎 {notes}")
        brief.append("")
    else:
        brief.append(_section("八·九、MR 因果证据（孟德尔随机化）", 3))
        e = _mr_err_str if '_mr_err_str' in dir() else '查询失败'
        brief.append(f"（MR 因果证据生成异常: {e}）\n")

    # ═══════ 八·十. 安全性证据 ═══════
    try:
        from safety_connector import generate_evidence_rows as _saf_gen
        _saf_rows = _saf_gen(g_up, disease=disease)
    except Exception as _saf_err:
        _saf_rows = []
        _saf_err_str = str(_saf_err)

    if _saf_rows:
        brief.append(_section("八·十、安全性证据（ON-target 风险评估）", 3))
        brief.extend([
            f"- **方法**: GTEx 组织表达 (心/脑/肝/肾/肺/胰/肌) + 已知安全性信号 + 基因必需性",
            f"- **评估范围**: ON-target ON-tissue 毒性风险 (不覆盖 OFF-target)",
            "",
        ])
        for r in _saf_rows:
            d = r if isinstance(r, dict) else (r.to_dict() if hasattr(r, 'to_dict') else {})
            dim = d.get('sub_dimension', '?')
            finding = (d.get('key_finding', '') or '')[:120]
            if dim.startswith("Safety:"):
                brief.append(f"  - **[{dim}]** {finding}")
        brief.append("")
    else:
        brief.append(_section("八·十、安全性证据（ON-target 风险评估）", 3))
        e = _saf_err_str if '_saf_err_str' in dir() else '查询失败'
        brief.append(f"（安全性证据生成异常: {e}）\n")

    # ═══════ 八·十一. 临床遗传证据 ═══════
    try:
        from clinical_genetics_connector import generate_evidence_rows as _cg_gen
        _cg_rows = _cg_gen(g_up, disease=disease)
    except Exception as _cg_err:
        _cg_rows = []
        _cg_err_str = str(_cg_err)

    if _cg_rows:
        brief.append(_section("八·十一、临床遗传证据（ClinVar 致病变异）", 3))
        _cg_info = next((r for r in _cg_rows if r.get('sub_dimension') == 'ClinicalGenetics:summary'), {})
        _cg_finding = (_cg_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_cg_finding}")
        _cg_plp = [r for r in _cg_rows if r.get('sub_dimension','').startswith('ClinicalGenetics:P/LP:')]
        for r in _cg_plp[:5]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十一、临床遗传证据（ClinVar 致病变异）", 3))
        e = _cg_err_str if '_cg_err_str' in dir() else '查询失败'
        brief.append(f"（临床遗传证据生成异常: {e}）\n")

    # ═══════ 八·十二. 基因必需性 ═══════
    try:
        from essentiality_connector import generate_evidence_rows as _es_gen
        _es_rows = _es_gen(g_up, disease=disease)
    except Exception as _es_err:
        _es_rows = []
        _es_err_str = str(_es_err)

    if _es_rows:
        brief.append(_section("八·十二、基因必需性（DepMap + MGI）", 3))
        _es_info = next((r for r in _es_rows if r.get('sub_dimension') == 'Essentiality:summary'), {})
        _es_finding = (_es_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_es_finding}")
        _es_other = [r for r in _es_rows if r.get('sub_dimension','').startswith('Essentiality:') \
                      and r.get('sub_dimension') != 'Essentiality:method' \
                      and r.get('sub_dimension') != 'Essentiality:summary']
        for r in _es_other[:3]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十二、基因必需性（DepMap + MGI）", 3))
        e = _es_err_str if '_es_err_str' in dir() else '查询失败'
        brief.append(f"（基因必需性证据生成异常: {e}）\n")

    # ═══════ 八·十三. 群体遗传耐受性 ═══════
    try:
        from gnomad_connector import generate_evidence_rows as _gn_gen
        _gn_rows = _gn_gen(g_up, disease=disease)
    except Exception as _gn_err:
        _gn_rows = []
        _gn_err_str = str(_gn_err)

    if _gn_rows:
        brief.append(_section("八·十三、群体遗传耐受性（gnomAD）", 3))
        _gn_info = next((r for r in _gn_rows if r.get('sub_dimension') == 'PopulationTolerance:summary'), {})
        _gn_finding = (_gn_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_gn_finding}")
        _gn_detail = [r for r in _gn_rows if 'PopulationTolerance:pLI' in r.get('sub_dimension','') or 'PopulationTolerance:LOEUF' in r.get('sub_dimension','')]
        for r in _gn_detail[:2]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十三、群体遗传耐受性（gnomAD）", 3))
        e = _gn_err_str if '_gn_err_str' in dir() else '查询失败'
        brief.append(f"（群体遗传耐受性异常: {e}）\n")

    # ═══════ 八·十四. PPI 网络中心性 ═══════
    try:
        from string_connector import generate_evidence_rows as _st_gen
        _st_rows = _st_gen(g_up, disease=disease)
    except Exception as _st_err:
        _st_rows = []
        _st_err_str = str(_st_err)

    if _st_rows:
        brief.append(_section("八·十四、蛋白互作网络中心性（STRING）", 3))
        _st_info = next((r for r in _st_rows if r.get('sub_dimension') == 'PPI:summary'), {})
        _st_finding = (_st_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_st_finding}")
        _st_inter = [r for r in _st_rows if r.get('sub_dimension','').startswith('PPI:interactor:')]
        for r in _st_inter[:3]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十四、蛋白互作网络中心性（STRING）", 3))
        e = _st_err_str if '_st_err_str' in dir() else '查询失败'
        brief.append(f"（PPI 网络中心性异常: {e}）\n")

    # ═══════ 八·十五. 进化保守性 ═══════
    try:
        from conservation_connector import generate_evidence_rows as _cv_gen
        _cv_rows = _cv_gen(g_up, disease=disease)
    except Exception as _cv_err:
        _cv_rows = []
        _cv_err_str = str(_cv_err)

    if _cv_rows:
        brief.append(_section("八·十五、进化保守性（phyloP）", 3))
        _cv_info = next((r for r in _cv_rows if r.get('sub_dimension') == 'Conservation:summary'), {})
        _cv_finding = (_cv_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_cv_finding}")
        brief.append("")
    else:
        brief.append(_section("八·十五、进化保守性（phyloP）", 3))
        e = _cv_err_str if '_cv_err_str' in dir() else '查询失败'
        brief.append(f"（进化保守性异常: {e}）\n")

    # ═══════ 八·十六. 免疫微环境互作 ═══════
    try:
        from immune_microenv_connector import generate_evidence_rows as _im_gen
        _im_rows = _im_gen(g_up, disease=disease)
    except Exception as _im_err:
        _im_rows = []
        _im_err_str = str(_im_err)

    if _im_rows:
        brief.append(_section("八·十六、免疫微环境互作（TISIDB）", 3))
        _im_info = next((r for r in _im_rows if r.get('sub_dimension') == 'ImmuneMicroenv:summary'), {})
        _im_finding = (_im_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_im_finding}")
        # 检查点/细胞类型详情
        _im_detail = [r for r in _im_rows if 'ImmuneMicroenv:cell:' in r.get('sub_dimension','') or 'ImmuneMicroenv:checkpoint:' in r.get('sub_dimension','')]
        for r in _im_detail[:3]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十六、免疫微环境互作（TISIDB）", 3))
        e = _im_err_str if '_im_err_str' in dir() else '查询失败'
        brief.append(f"（免疫微环境互作异常: {e}）\n")

    # ═══════ 八·十七. 表型相似性关联 ═══════
    try:
        from phenotype_connector import generate_evidence_rows as _ph_gen
        _ph_rows = _ph_gen(g_up, disease=disease)
    except Exception as _ph_err:
        _ph_rows = []
        _ph_err_str = str(_ph_err)

    if _ph_rows:
        brief.append(_section("八·十七、表型相似性关联（HPO）", 3))
        _ph_info = next((r for r in _ph_rows if r.get('sub_dimension') == 'Phenotype:summary'), {})
        _ph_finding = (_ph_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_ph_finding}")
        _ph_dz = [r for r in _ph_rows if 'Phenotype:disease:' in r.get('sub_dimension','')]
        for r in _ph_dz[:3]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十七、表型相似性关联（HPO）", 3))
        e = _ph_err_str if '_ph_err_str' in dir() else '查询失败'
        brief.append(f"（表型相似性关联异常: {e}）\n")

    # ═══════ 八·十八. 三维结构可药性 ═══════
    try:
        from structure_connector import generate_evidence_rows as _st2_gen
        _st2_rows = _st2_gen(g_up, disease=disease)
    except Exception as _st2_err:
        _st2_rows = []
        _st2_err_str = str(_st2_err)

    if _st2_rows:
        brief.append(_section("八·十八、三维结构可药性（AlphaFold）", 3))
        _st2_info = next((r for r in _st2_rows if r.get('sub_dimension') == 'Structure:summary'), {})
        _st2_finding = (_st2_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_st2_finding}")
        _st2_dom = [r for r in _st2_rows if 'Structure:domain:' in r.get('sub_dimension','')]
        for r in _st2_dom[:2]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·十八、三维结构可药性（AlphaFold）", 3))
        e = _st2_err_str if '_st2_err_str' in dir() else '查询失败'
        brief.append(f"（三维结构可药性异常: {e}）\n")

    # ═══════ 八·二十. 泛癌全景 ═══════
    try:
        from pancancer_connector import generate_evidence_rows as _pc_gen
        _pc_rows = _pc_gen(g_up, disease=disease)
    except Exception as _pc_err:
        _pc_rows = []
        _pc_err_str = str(_pc_err)

    if _pc_rows:
        brief.append(_section("八·二十、泛癌全景（cBioPortal）", 3))
        _pc_info = next((r for r in _pc_rows if r.get('sub_dimension') == 'Pancancer:summary'), {})
        _pc_finding = (_pc_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_pc_finding}")
        brief.append("")
    else:
        brief.append(_section("八·二十、泛癌全景（cBioPortal）", 3))
        e = _pc_err_str if '_pc_err_str' in dir() else '查询失败'
        brief.append(f"（泛癌全景异常: {e}）\n")

    # ═══════ 八·二十一. 单细胞全图谱 ═══════
    try:
        from cellxgene_connector import generate_evidence_rows as _cx_gen
        _cx_rows = _cx_gen(g_up, disease=disease)
    except Exception as _cx_err:
        _cx_rows = []
        _cx_err_str = str(_cx_err)

    if _cx_rows:
        brief.append(_section("八·二十一、单细胞全图谱（CELLxGENE）", 3))
        _cx_info = next((r for r in _cx_rows if r.get('sub_dimension') == 'Cellxgene:summary'), {})
        _cx_finding = (_cx_info.get('key_finding', '') or '')[:120]
        brief.append(f"  - {_cx_finding}")
        _cx_tissue = [r for r in _cx_rows if 'Cellxgene:tissue:' in r.get('sub_dimension','')]
        for r in _cx_tissue[:3]:
            f = (r.get('key_finding', '') or '')[:100]
            if f:
                brief.append(f"    • {f}")
        brief.append("")
    else:
        brief.append(_section("八·二十一、单细胞全图谱（CELLxGENE）", 3))
        e = _cx_err_str if '_cx_err_str' in dir() else '查询失败'
        brief.append(f"（单细胞全图谱异常: {e}）\n")

    # ═══════ 9. 安全约束 ═══════
    brief.append(_section("九、安全约束", 3))
    try:
        safeties = build_editableity_safety(global_scores or {})
        if safeties:
            for s in safeties:
                txt = s.contraindication if hasattr(s, 'contraindication') else str(s)
                brief.append(f"- ⚠️ {txt}\n")
        else:
            brief.append("（无安全约束提醒）\n")
    except Exception:
        brief.append("（安全约束检查跳过了）\n")

    # ═══════ 10. sgRNA 候选 ═══════
    sg_candidates = editableity_data.get("sg_rna_candidates", [])
    if sg_candidates:
        brief.append(_section("十、sgRNA 候选序列", 3))
        brief.append(f"共 {len(sg_candidates)} 条候选（按效率降序排列前10条）：\n")
        sg_rows = []
        for sg in sg_candidates[:10]:
            guide = sg.get("guide_seq", sg.get("seq", ""))
            score = sg.get("on_target_score", sg.get("score", sg.get("efficiency_score", "?")))
            model = sg.get("model_used", sg.get("model", "?"))
            sg_rows.append([
                f"`{guide[:20]}...`" if len(guide) > 20 else f"`{guide}`",
                f"{score:.4f}" if isinstance(score, (int, float)) else str(score),
                model,
            ])
        if sg_rows:
            brief.append(_table(["sgRNA 序列", "效率评分", "模型"], sg_rows))
            if len(sg_candidates) > 10:
                brief.append(f"\n> ... 还有 {len(sg_candidates) - 10} 条，完整列表见 JSON\n")
    else:
        brief.append("（sgRNA 候选未生成）\n")

    # ═══════ 11. 中文数据源 ═══════
    brief.append(_section("十一、中文数据源信息", 3))
    try:
        from cn_source_connector import query_target_summary
        zh_summary = query_target_summary(g_up)
        if zh_summary:
            brief.append(zh_summary + "\n")
    except Exception:
        brief.append("（中文数据连接器未加载）\n")

    # ═══════ 脚注 ═══════
    brief.append("---\n")
    brief.append(f"> _本报告由 AIXBox 靶点评级管线 v{REPORT_VERSION} 自动生成_")
    brief.append("> _数据来源: Open Targets Platform / gnomAD v4 / DepMap 24Q2 / Ensembl / 万方/药智/ChiCTR_")
    brief.append("> _注意: 所有评分均为计算预测结果，最终编辑方案需湿实验验证_")
    brief.append("> _AIXBox 智能体网关 · AIXClaw_\n")

    # ════════════════════════════════════════════
    # Phase III-D: 新增临床数据源 (2026-07-29)
    # ════════════════════════════════════════════

    # ── 八·二十二、ChiCTR 中国临床试验 ──
    try:
        from chictr_connector import ChiCTRConnector
        _chictr = ChiCTRConnector()
        _chictr_data = _chictr.query_by_gene(g_up, disease)
        if _chictr_data.get("n_studies", 0) > 0:
            brief.append(_section("八·二十二、中国临床试验（ChiCTR）", 3))
            brief.append(f"  - {_chictr_data.get('summary', 'ChiCTR 查询完成')}")
            brief.append("")
        else:
            brief.append(_section("八·二十二、中国临床试验（ChiCTR）", 3))
            brief.append("> 暂无 ChiCTR 相关试验记录\n")
    except Exception as _e_chictr:
        brief.append(_section("八·二十二、中国临床试验（ChiCTR）", 3))
        brief.append(f"> ⚠ ChiCTR 连接器异常: {_e_chictr}\n")

    # ── 八·二十三、NMPA/CDE 药品审批 ──
    try:
        from cde_connector import CDEConnector
        _cde = CDEConnector()
        _cde_data = _cde.query_by_gene(g_up, disease)
        if _cde_data.get("has_approved_drug", False):
            brief.append(_section("八·二十三、中国药监局审批（NMPA/CDE）", 3))
            brief.append(f"  - {_cde_data.get('summary', 'NMPA/CDE 查询完成')}")
            _inds = _cde_data.get("indications", [])
            if _inds:
                brief.append(f"  - 已获批适应症: {'; '.join(_inds[:5])}")
            brief.append("")
        else:
            brief.append(_section("八·二十三、中国药监局审批（NMPA/CDE）", 3))
            brief.append("> 暂无 NMPA/CDE 获批药物记录\n")
    except Exception as _e_cde:
        brief.append(_section("八·二十三、中国药监局审批（NMPA/CDE）", 3))
        brief.append(f"> ⚠ CDE 连接器异常: {_e_cde}\n")

    # ── 八·二十四、CKB 中国人群队列 ──
    try:
        from ckb_connector import CKBConnector
        _ckb = CKBConnector()
        _ckb_data = _ckb.query_by_gene(g_up, disease)
        if _ckb_data.get("associations", []):
            brief.append(_section("八·二十四、中国人群队列（CKB）", 3))
            brief.append(f"  - {_ckb_data.get('summary', 'CKB 查询完成')}")
            brief.append("")
        else:
            brief.append(_section("八·二十四、中国人群队列（CKB）", 3))
            brief.append("> 暂无 CKB 数据\n")
    except Exception as _e_ckb:
        brief.append(_section("八·二十四、中国人群队列（CKB）", 3))
        brief.append(f"> ⚠ CKB 连接器异常: {_e_ckb}\n")

    # ── 八·二十五、BioBank Japan ──
    try:
        from bbj_connector import BBJConnector
        _bbj = BBJConnector()
        _bbj_data = _bbj.query_by_gene(g_up, disease)
        if _bbj_data.get("associations", []):
            brief.append(_section("八·二十五、日本人群队列（BioBank Japan）", 3))
            brief.append(f"  - {_bbj_data.get('summary', 'BBJ 查询完成')}")
            brief.append("")
        else:
            brief.append(_section("八·二十五、日本人群队列（BioBank Japan）", 3))
            brief.append("> 暂无 BioBank Japan 数据\n")
    except Exception as _e_bbj:
        brief.append(_section("八·二十五、日本人群队列（BioBank Japan）", 3))
        brief.append(f"> ⚠ BBJ 连接器异常: {_e_bbj}\n")

    # ── 八·二十六、Orphanet 罕见病 ──
    try:
        from orphanet_connector import OrphanetConnector
        _orph = OrphanetConnector()
        _orph_data = _orph.query_by_gene(g_up, disease)
        if _orph_data.get("associations", []):
            brief.append(_section("八·二十六、罕见病关联（Orphanet）", 3))
            brief.append(f"  - {_orph_data.get('summary', 'Orphanet 查询完成')}")
            brief.append("")
        else:
            brief.append(_section("八·二十六、罕见病关联（Orphanet）", 3))
            brief.append("> 暂无 Orphanet 罕见病关联\n")
    except Exception as _e_orph:
        brief.append(_section("八·二十六、罕见病关联（Orphanet）", 3))
        brief.append(f"> ⚠ Orphanet 连接器异常: {_e_orph}\n")

    # ── 八·二十七、PheWAS 表型组关联 ──
    try:
        from phewas_connector import PheWASConnector
        _phewas = PheWASConnector()
        _phewas_data = _phewas.query_by_gene(g_up, disease)
        if _phewas_data.get("associations", []):
            brief.append(_section("八·二十七、表型组关联（PheWAS Catalog）", 3))
            brief.append(f"  - {_phewas_data.get('summary', 'PheWAS 查询完成')}")
            brief.append("")
        else:
            brief.append(_section("八·二十七、表型组关联（PheWAS Catalog）", 3))
            brief.append("> 暂无 PheWAS 数据\n")
    except Exception as _e_phewas:
        brief.append(_section("八·二十七、表型组关联（PheWAS Catalog）", 3))
        brief.append(f"> ⚠ PheWAS 连接器异常: {_e_phewas}\n")

    # ── 八·二十八、跨维度信号嵌入分析（P1b PCA 可视化） ──
    try:
        from cross_dim_p1 import DimEmbedder, ConditionalSignalDetector
        # 从证据行构建维度列表
        _cross_dims = []
        for _rw in evidence_rows:
            _s = getattr(_rw, 'score', None)
            if _s is not None:
                class _DimDummy:
                    pass
                _d = _DimDummy()
                _d.name = getattr(_rw, 'dimension', '?').replace('_', ' ').title()
                _d.score = _s
                _d.note = getattr(_rw, 'interpretation', '')
                _cross_dims.append(_d)
        # 也加入可编辑性组件评分
        _comp_map = {
            '基因结构': comp_scores.get('gene_structure', 0),
            'PAM可及性': comp_scores.get('pam_availability', 0),
            'CRISPR耐受性': comp_scores.get('tolerability', 0),
            '基因必需性': comp_scores.get('essentiality', 0),
        }
        for _cn, _cs in _comp_map.items():
            class _DimDummy:
                pass
            _d = _DimDummy()
            _d.name = _cn
            _d.score = _cs
            _d.note = ''
            _cross_dims.append(_d)

        if len(_cross_dims) >= 3:
            brief.append(_section('八·二十八、跨维度信号嵌入分析（PCA 2D）', 3))
            _embedder = DimEmbedder()
            _result = _embedder.embed_pca(_cross_dims)
            _ev_parts = ', '.join(f'PC{i+1}={v*100:.0f}%' for i, v in enumerate(_result.get('explained_var', [])))
            brief.append(f'> 降维方法: {_result.get("method", "pca").upper()}')
            brief.append(f'> 解释方差: {_ev_parts}')
            brief.append(f'> 参与维度: {_result.get("dims_used", 0)} 个')
            brief.append('')

            # 嵌入坐标表
            _emb = _result.get('embeddings', [])
            _hdr = ['维度', '原始分', 'PC1', 'PC2', '聚类', '异常']
            _rows = []
            for _e in _emb:
                _rows.append([
                    _e.get('name', '?'),
                    str(_e.get('original_score', '?')),
                    f"{_e.get('x', 0):.3f}",
                    f"{_e.get('y', 0):.3f}",
                    str(_e.get('cluster', -1)),
                    '⚠ 是' if _e.get('is_outlier') else '否',
                ])
            brief.extend(_table(_hdr, _rows))
            brief.append('')

            # 聚类汇总
            _clusters = _result.get('clusters', {})
            brief.append('**聚类分布**:')
            for _cid in sorted(_clusters.keys(), key=lambda k: len(_clusters[k]), reverse=True):
                _label = '噪声' if _cid == '-1' else f'簇 {_cid}'
                _members = ', '.join(_clusters[_cid])
                brief.append(f'- **{_label}**: {_members}')
            brief.append('')

            # 条件显著信号检测
            _detector = ConditionalSignalDetector()
            _signals = _detector.detect(_cross_dims)
            if _signals:
                brief.append('**跨维信号分析**:')
                for _sig in _signals[:5]:
                    brief.append(f'- {_sig.interpretation}')
                brief.append('')

            # 自动解读
            _rec = _result.get('recommendation', '')
            if _rec:
                brief.append(f'**自动解读**: {_rec}')
                brief.append('')

            # ASCII '散点图'（字符近似）
            if len(_emb) >= 3:
                _xs = [e.get('x', 0) for e in _emb]
                _ys = [e.get('y', 0) for e in _emb]
                _xmin, _xmax = min(_xs), max(_xs)
                _ymin, _ymax = min(_ys), max(_ys)
                _xr = max(_xmax - _xmin, 1e-6)
                _yr = max(_ymax - _ymin, 1e-6)
                _grid_w, _grid_h = 30, 12
                _grid = [[' ' for _ in range(_grid_w)] for _ in range(_grid_h)]
                _labels = {}
                for _e in _emb:
                    _xi = int((_e.get('x', 0) - _xmin) / _xr * (_grid_w - 1))
                    _yi = int((_e.get('y', 0) - _ymin) / _yr * (_grid_h - 1))
                    _xi = max(0, min(_grid_w - 1, _xi))
                    _yi = max(0, min(_grid_h - 1, _yi))
                    _ch = '⚠' if _e.get('is_outlier') else str(_e.get('cluster', '?'))[0]
                    _grid[_grid_h - 1 - _yi][_xi] = _ch
                    _labels[f'({_xi},{_grid_h-1-_yi})'] = _e.get('name', '?')[0]
                brief.append('**信号嵌入空间（字符近似）**:')
                brief.append('```')
                brief.append(f'PC2 ↑')
                for _row in _grid:
                    brief.append(''.join(_row))
                brief.append(f'PC1 →')
                brief.append('```')
                brief.append('') if False else None  # noop
                _legend = {}
                for _e in _emb:
                    _c = str(_e.get('cluster', -1))
                    _n = _e.get('name', '?')
                    if _c not in _legend:
                        _legend[_c] = []
                    _legend[_c].append(_n)
                brief.append('**图例**:')
                for _c in sorted(_legend.keys()):
                    _label = '噪声(⚠)' if _c == '-1' or (_c == '-1:') else f'簇{_c}'
                    brief.append(f'- [{_label}] {", ".join(_legend[_c])}')
                brief.append('')

    except Exception as _e_cross:
        pass  # 跨维度嵌入分析为非关键特性，静默跳过

    brief.append('')
    return '\n'.join(brief)

# ── CLI 入口 ──

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=f"AI靶点简报生成器 v{REPORT_VERSION}（中文版）"
    )
    parser.add_argument("target", help="基因符号（如 ACVR2A, KRAS, TP53）")
    parser.add_argument("--ensembl", default="", help="Ensembl 基因 ID（可选）")
    parser.add_argument("--disease", default="", help="关联疾病（中文，如 肺癌/2型糖尿病）")
    parser.add_argument("--output", "-o", default="", help="输出文件路径（默认 stdout）")
    parser.add_argument("--json", action="store_true", help="同时输出 JSON 数据")
    args = parser.parse_args()

    if not _ALL_OK:
        print("[WARN] 部分依赖模块未加载，但仍可尝试生成。")

    brief = generate_brief(args.target, args.ensembl, args.disease)

    if args.output:
        with open(args.output, "w") as f:
            f.write(brief)
        print(f"✅ 简报已写入: {args.output}")
    else:
        print(brief)

    if args.json:
        from editableity_connector import score_editableity, get_global_scores
        data = score_editableity(args.target, args.ensembl) or {}
        gs = get_global_scores(args.target) or {}
        of = args.output.replace(".md", ".json") if args.output else f"/tmp/{args.target}_brief.json"
        with open(of, "w") as f:
            json.dump({"brief": data, "global_scores": gs}, f, indent=2, default=str)
        print(f"✅ JSON 数据已导出: {of}")


if __name__ == "__main__":
    main()
