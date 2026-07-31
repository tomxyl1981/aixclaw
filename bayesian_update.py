#!/usr/bin/env python3
"""bayesian_update.py — 贝叶斯后验更新模块 (A2, 2026-07-31 张红批准)

核心: P(靶点有效 | 证据) ∝ P(靶点有效) × P(证据 | 靶点有效)
实现: 序贯贝叶斯 (sequential Bayes) — 每条独立证据产生一个贝叶斯因子,
      后验作为下一条证据的先验, 依次更新。

与 A1 confidence_formula.md 的关系:
  - A1 的置信度是启发式评分 (0.80 覆盖 + 0.20 强度 + 调整)
  - A2 提供概率论意义上的后验更新, 输入可复用证据行的结构化字段
  - 两者并存: A1 打分用于排序/展示, A2 用于"这个靶点值不值得投"的决策

设计原则 (张红 2026-07-25 教条):
  - 大模型是提取工具, 不是发现工具 → 本模块只做概率更新, 不做"判断"
  - 每个结论可追溯到具体证据行 → 输出保留每条证据的贡献明细
  - 多独立源不一致时降级, 不强行调和 → 矛盾证据自然拉低后验

实现: 纯 stdlib (math), 无外部依赖。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Union

# ─────────────────────────────────────────────────────────────
# 1. 证据类型的先验校准 (敏感性 se / 特异性 sp)
#    se = P(证据阳性 | 靶点真实有效)   — 真阳性率
#    sp = P(证据阴性 | 靶点真实无效)   — 真阴性率
#    贝叶斯因子 LR = se / (1 - sp)
#
#    取值依据 (保守校准, 参考流行病学文献常用范围):
#    - 人类遗传学证据 (GWAS 全基因组显著) 是靶点因果性最强信号
#    - 动物模型 KO 表型因果性高, 但跨物种外推有损耗
#    - eQTL/表达/通路是支持性证据, 特异性有限
#    默认值可被调用方覆盖 (证据行自带 se/sp 时优先)。
# ─────────────────────────────────────────────────────────────

DEFAULT_CALIBRATION: Dict[str, Dict[str, float]] = {
    # 证据类型           se     sp    说明
    "gwas":              {"se": 0.80, "sp": 0.90},   # 全基因组显著, 因果性最强
    "eqtl":              {"se": 0.60, "sp": 0.70},   # 顺式调控, 中等
    "pwas":             {"se": 0.60, "sp": 0.70},   # 蛋白质组学关联 (同 eQTL 档)
    "scrna":             {"se": 0.50, "sp": 0.60},   # 单细胞表达, 支持性
    "animal":            {"se": 0.70, "sp": 0.75},   # KO 表型, 因果但跨物种
    "expression":        {"se": 0.45, "sp": 0.55},   # 表达差异, 弱支持
    "pathway":           {"se": 0.40, "sp": 0.50},   # 通路注释, 弱
    "clinical":          {"se": 0.65, "sp": 0.70},   # 临床队列/试验
    "chembl":            {"se": 0.55, "sp": 0.65},   # 可药性/亲和力, 支持性
    "druggability":      {"se": 0.50, "sp": 0.60},   # 结构/口袋预测
    "default":           {"se": 0.50, "sp": 0.50},   # 未知类型 → LR=1, 不改变信念
}


@dataclass
class EvidenceInput:
    """一条证据的最小输入 (与 EvidenceRow 字段兼容, duck typing)。

    也可直接传 dict 或任何带以下属性的对象。
    """
    evidence_type: str = "default"
    direction: Optional[str] = None          # up/down 或 None
    consistent: Optional[bool] = None        # 与主流方向一致?
    se: Optional[float] = None               # 覆盖默认校准
    sp: Optional[float] = None

    @classmethod
    def from_row(cls, row) -> "EvidenceInput":
        """从 EvidenceRow / dict 宽松转换。"""
        if isinstance(row, dict):
            return cls(
                evidence_type=str(row.get("evidence_type", row.get("type", "default"))),
                direction=row.get("direction"),
                consistent=row.get("consistent"),
                se=row.get("se"),
                sp=row.get("sp"),
            )
        return cls(
            evidence_type=str(getattr(row, "evidence_type", getattr(row, "type", "default"))),
            direction=getattr(row, "direction", None),
            consistent=getattr(row, "consistent", None),
            se=getattr(row, "se", None),
            sp=getattr(row, "sp", None),
        )


# ─────────────────────────────────────────────────────────────
# 2. 核心计算
# ─────────────────────────────────────────────────────────────

def bayes_factor(se: float, sp: float) -> float:
    """贝叶斯因子 LR = se / (1 - sp)。LR>1 支持有效, LR<1 反对。"""
    if not (0 < se < 1 and 0 < sp < 1):
        raise ValueError(f"se/sp 必须在 (0,1) 开区间: se={se}, sp={sp}")
    return se / (1.0 - sp)


def _apply_direction_penalty(lr: float, ev: EvidenceInput) -> float:
    """方向/一致性调整:
    - 明确标注与主流方向矛盾 → 证据反对靶点 → LR 取倒数 (转为反对证据)
    - consistent=False 同理
    - 方向未知 → 不调整
    """
    if ev.consistent is False:
        return 1.0 / lr if lr > 0 else lr
    if ev.consistent is True:
        return lr
    # consistent 未标注, 看 direction 无法判断矛盾 → 原样返回
    return lr


def odds(p: float) -> float:
    """概率 → 优势比。"""
    if not 0 < p < 1:
        raise ValueError(f"概率必须在 (0,1) 开区间: {p}")
    return p / (1.0 - p)


def prob(o: float) -> float:
    """优势比 → 概率。"""
    return o / (1.0 + o)


@dataclass
class UpdateStep:
    """单条证据的更新记录 (可追溯)。"""
    evidence_type: str
    se: float
    sp: float
    lr: float
    prior: float
    posterior: float


@dataclass
class PosteriorResult:
    """后验更新结果。"""
    prior: float
    posterior: float
    steps: List[UpdateStep] = field(default_factory=list)
    n_evidence: int = 0
    n_supporting: int = 0
    n_against: int = 0

    def summary(self) -> Dict[str, float]:
        return {
            "prior": round(self.prior, 4),
            "posterior": round(self.posterior, 4),
            "bayes_factor_total": round(odds(self.posterior) / odds(self.prior), 3),
            "n_evidence": self.n_evidence,
            "n_supporting": self.n_supporting,
            "n_against": self.n_against,
        }


def compute_posterior(
    prior: float,
    evidence: Sequence[Union[EvidenceInput, dict, object]],
) -> PosteriorResult:
    """序贯贝叶斯更新。

    Args:
        prior: 先验概率 P(靶点有效), 0~1 开区间。建议:
               - 未知靶点: 0.01 (保守)
               - 有生物学先验 (通路/家族): 0.05~0.10
               - Open Targets 高置信: 0.10~0.20
        evidence: 证据列表, 每项为 EvidenceInput / dict / EvidenceRow 兼容对象

    Returns:
        PosteriorResult (含每步明细)
    """
    if not (0 < prior < 1):
        raise ValueError(f"先验必须在 (0,1) 开区间: {prior}")

    cur = prior
    steps: List[UpdateStep] = []
    n_support = 0
    n_against = 0

    for raw in evidence:
        ev = raw if isinstance(raw, EvidenceInput) else EvidenceInput.from_row(raw)
        cal = DEFAULT_CALIBRATION.get(ev.evidence_type, DEFAULT_CALIBRATION["default"])
        se = ev.se if ev.se is not None else cal["se"]
        sp = ev.sp if ev.sp is not None else cal["sp"]
        lr = bayes_factor(se, sp)
        lr = _apply_direction_penalty(lr, ev)

        if lr > 1.0:
            n_support += 1
        elif lr < 1.0:
            n_against += 1

        new_odds = odds(cur) * lr
        new_p = prob(new_odds)
        steps.append(UpdateStep(
            evidence_type=ev.evidence_type,
            se=se, sp=sp, lr=round(lr, 3),
            prior=round(cur, 4), posterior=round(new_p, 4),
        ))
        cur = new_p

    return PosteriorResult(
        prior=prior,
        posterior=cur,
        steps=steps,
        n_evidence=len(steps),
        n_supporting=n_support,
        n_against=n_against,
    )


# ─────────────────────────────────────────────────────────────
# 3. 决策辅助 (不替代人, 只给颜色提示)
# ─────────────────────────────────────────────────────────────

def decision_hint(posterior: float, prior: float) -> str:
    """基于后验/先验比给出提示色。阈值保守, 最终决策权在人。"""
    ratio = posterior / prior if prior > 0 else float("inf")
    if ratio >= 10.0 and posterior >= 0.3:
        return "🟢 证据大幅提升后验 (≥10×), 建议进入验证管线"
    if ratio >= 3.0 and posterior >= 0.15:
        return "🟡 证据中等支持 (3-10×), 建议补充独立证据"
    if ratio < 0.33:
        return "🔴 证据整体反对 (≤1/3×), 建议降级或放弃"
    return "⚪ 证据不足或矛盾, 维持观察"


# ─────────────────────────────────────────────────────────────
# 4. 自测 (python3 bayesian_update.py)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 场景: 未知靶点先验 0.01, 收集到 5 条独立证据
    demo = [
        {"evidence_type": "gwas", "consistent": True},        # 强支持
        {"evidence_type": "eqtl", "consistent": True},        # 支持
        {"evidence_type": "animal", "consistent": True},      # 支持
        {"evidence_type": "expression", "consistent": True},  # 弱支持
        {"evidence_type": "pathway", "consistent": None},     # 中性偏弱
    ]
    r = compute_posterior(0.01, demo)
    print("=== 演示: 先验 0.01 + 5 条支持证据 ===")
    for s in r.steps:
        print(f"  {s.evidence_type:>10}  LR={s.lr:>6.2f}  {s.prior:.4f} → {s.posterior:.4f}")
    print("  后验:", round(r.posterior, 4), "| 总贝叶斯因子:", round(odds(r.posterior) / odds(r.prior), 1))
    print("  提示:", decision_hint(r.posterior, r.prior))

    print("\n=== 演示2: 加入 2 条矛盾证据 ===")
    demo2 = demo + [
        {"evidence_type": "gwas", "consistent": False},       # 矛盾 → LR 取倒数
        {"evidence_type": "expression", "consistent": False},
    ]
    r2 = compute_posterior(0.01, demo2)
    for s in r2.steps:
        print(f"  {s.evidence_type:>10}  LR={s.lr:>6.2f}  {s.prior:.4f} → {s.posterior:.4f}")
    print("  后验:", round(r2.posterior, 4), "| 提示:", decision_hint(r2.posterior, r2.prior))
    print("  (矛盾证据把后验拉回, 符合'不强行调和'原则)")
