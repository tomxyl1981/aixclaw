"""熵态分析章节生成器 — 供 target_brief_generator.py 调用

基于邓煜(t=0独立→熵增)框架。
证据维度在接入时相互独立(t=0)，交叉验证时自然碰撞产生信息熵增。
靶点筛选是外部压熵过程，不代表自然收敛到真理。
"""

import datetime
from typing import List, Dict

from target_evidence_matrix import (
    TargetEvidenceMatrix, EvidenceRow, EvidenceDimension
)


def compute_entropy(matrix: TargetEvidenceMatrix) -> dict:
    """对单靶点的证据矩阵计算熵态指标"""
    rows = matrix.rows
    if not rows:
        return {
            "natural_entropy": 0.0,
            "processed_confidence": 0.0,
            "pressure_ratio": 0.0,
            "contradiction_count": 0,
            "coherent_pairs": 0,
            "missing_dimensions": [],
            "consensus_type": "no_data",
            "dimension_breakdown": []
        }

    # 按维度聚合
    dim_groups: Dict[str, List[EvidenceRow]] = {}
    for r in rows:
        dim = r.dimension.value if hasattr(r.dimension, 'value') else str(r.dimension)
        dim_groups.setdefault(dim, []).append(r)

    # ── 自然态置信度 ──
    # 从每行的 natural_confidence 取值（t=0 独立状态）
    natural_confidences = []
    for r in rows:
        c = getattr(r, 'natural_confidence', 0.5)
        natural_confidences.append(c)

    avg_natural = sum(natural_confidences) / len(natural_confidences) if natural_confidences else 0.0
    natural_entropy = round(1.0 - avg_natural, 4)

    # ── 压熵后置信度 ──
    # 使用矩阵级的 overall_confidence（经 AI 压熵后的结果）
    avg_processed = getattr(matrix, 'overall_confidence', 0.0)

    # ── 矛盾检测 ──
    contradictions = 0
    coherent_pairs = 0
    dim_directions: Dict[str, set] = {}
    for r in rows:
        d = r.dimension.value if hasattr(r.dimension, 'value') else str(r.dimension)
        direction = r.direction.value if hasattr(r.direction, 'value') else str(r.direction)
        dim_directions.setdefault(d, set()).add(direction)

    for d, dirs in dim_directions.items():
        if len(dirs) > 1:
            contradictions += 1
        else:
            coherent_pairs += 1

    # ── 缺失维度 ──
    try:
        all_dims = {e.value for e in EvidenceDimension}
    except TypeError:
        all_dims = set()
    present_dims = set(dim_groups.keys())
    missing = sorted(all_dims - present_dims)

    # ── 共识类型 ──
    if contradictions == 0 and len(dim_groups) >= 3:
        consensus_type = "full_consensus"
    elif contradictions <= len(dim_groups) // 2:
        consensus_type = "majority"
    elif contradictions > 0:
        consensus_type = "split"
    else:
        consensus_type = "no_consensus"

    # ── 压熵幅度 ──
    # 压熵幅度 = (整体置信度 - 平均自然置信度) / 平均自然置信度
    pressure_ratio = 0.0
    if avg_natural > 0:
        pressure_ratio = round((avg_processed - avg_natural) / avg_natural, 4)

    # ── 维度分解 ──
    dim_breakdown = []
    for d, r_list in sorted(dim_groups.items()):
        nat = [getattr(r, 'natural_confidence', 0.5) for r in r_list]
        n_avg = sum(nat) / len(nat)
        dirs = list(set(
            r.direction.value if hasattr(r.direction, 'value') else str(r.direction)
            for r in r_list
        ))
        dim_breakdown.append({
            "dimension": d,
            "natural_confidence": round(n_avg, 3),
            "row_count": len(r_list),
            "pressure_path": getattr(r_list[0], 'pressure_path', "natural"),
            "directions": dirs
        })

    return {
        "natural_entropy": round(natural_entropy, 4),
        "processed_confidence": round(avg_processed, 4),
        "pressure_ratio": pressure_ratio,
        "contradiction_count": contradictions,
        "coherent_pairs": coherent_pairs,
        "missing_dimensions": missing,
        "consensus_type": consensus_type,
        "dimension_breakdown": dim_breakdown,
        "computed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    }


def render_entropy_section(entropy: dict) -> str:
    """渲染熵态报告 Markdown"""
    lines = []

    lines.append("\n---\n")
    lines.append("## 九、熵态分析\n")
    lines.append(f"> 基于 Deng Yu (t=0独立→熵增) 框架 | {entropy['computed_at']}\n")
    lines.append("> 各证据维度在接入时相互独立 (t₀)，交叉验证时自然碰撞产生信息熵增。")
    lines.append("> 靶点筛选是外部压熵过程，不代表自然收敛到真理。\n")

    # ── 9.1 维度分解 ──
    lines.append("### 9.1 证据自然态（t₀ 独立）\n")
    lines.append("| 维度 | 行数 | 自然置信度 | 压熵路径 | 方向 |")
    lines.append("|------|------|-----------|---------|------|")
    for d in entropy.get("dimension_breakdown", []):
        dir_str = " / ".join(d.get("directions", [])) or "—"
        lines.append(
            f"| {d['dimension']} | {d['row_count']} | "
            f"{d['natural_confidence']:.3f} | "
            f"{d['pressure_path']} | {dir_str} |"
        )
    lines.append("")

    # ── 9.2 碰撞与矛盾 ──
    lines.append("### 9.2 碰撞与矛盾\n")
    cc = entropy.get("contradiction_count", 0)
    if cc > 0:
        lines.append(f"- 🔴 **矛盾维度**: {cc} 个维度的证据方向不一致")
    else:
        lines.append("- 🟢 **方向一致**: 所有有数据的维度方向一致")

    md = entropy.get("missing_dimensions", [])
    if md:
        lines.append(f"- ⚪ **缺失维度**: {len(md)} 维（{'、'.join(md[:6])}{'…' if len(md) > 6 else ''}）")
    else:
        lines.append("- ✅ **维度全覆盖**")
    lines.append(f"- 🤝 **共识类型**: {entropy.get('consensus_type', 'unknown')}\n")

    # ── 9.3 压熵分析 ──
    lines.append("### 9.3 压熵分析\n")
    pr = entropy.get("pressure_ratio", 0)
    if abs(pr) < 0.01:
        pr_note = "🟢 几乎未压熵，自然态即终态"
    elif pr > 0.40:
        pr_note = "⚠️ 大幅压熵，需检查手段是否合理"
    elif pr > 0:
        pr_note = "🟡 适度压熵"
    else:
        pr_note = "🔴 负压熵，系统异常"

    lines.append("| 指标 | 值 | 说明 |")
    lines.append("|------|-----|------|")
    lines.append(f"| 自然态熵 (H₀) | {entropy.get('natural_entropy', 0):.4f} | 0=完全确定, 1=完全不确定 |")
    lines.append(f"| 压熵后置信度 | {entropy.get('processed_confidence', 0):.4f} | 矩阵整体置信度 |")
    lines.append(f"| 压熵幅度 | {pr * 100:.2f}% | {pr_note} |")
    lines.append(f"| 矛盾维度 | {entropy.get('contradiction_count', 0)} | 方向冲突的证据维度数 |")
    lines.append(f"| 缺失维度 | {len(entropy.get('missing_dimensions', []))} | 尚无数据的维度 |")
    lines.append("")

    # ── 9.4 决策建议 ──
    lines.append("### 9.4 决策建议\n")
    ct = entropy.get("consensus_type", "no_consensus")
    ne = entropy.get("natural_entropy", 0.5)
    if ct == "full_consensus" and ne < 0.3:
        lines.append("**✅ 可信区间**: 多源独立证据高度一致，自然态熵低。可直接用于投资决策。")
    elif ct in ("full_consensus", "majority") and ne < 0.6:
        lines.append("**🟡 有条件可信**: 多数维度方向一致，自然态熵适中。建议补充证据后决策。")
    else:
        lines.append("**🔴 高不确定性**: 自然态熵高 / 矛盾多 / 共识弱。优先投入验证，控制仓位。")

    lines.append(
        "\n> ⚠️ 压熵路径: `natural`=未处理, `mom`=MoM多视角共识, "
        "`human`=人工评审, `mixed`=混合路径\n"
    )

    return "\n".join(lines)
