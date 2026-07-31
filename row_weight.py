"""
数据驱动证据行权重计算 (Phase 1)
===================================

基于张红 2026-07-30 授权，替代现有的平权打分。

权重四因子:
  - logN_weight: 样本量
  - pval_weight: p-value 显著性
  - effect_weight: 效应量
  - recency_weight: 时效性

用法:
  from row_weight import compute_data_weight
  row.data_weight = compute_data_weight(row)
"""

from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any

CURRENT_YEAR = datetime.now().year


def _parse_pval(raw_stat: str) -> float | None:
    """从 raw_stat 中提取 p-value。"""
    if not raw_stat:
        return None
    raw = raw_stat.strip().lower().replace(" ", "")
    # "p=2.3e-8" / "pvalue=1e-5" / "p-val=0.01"
    m = re.search(r"p(?:[-_]?value|val)?\s*[=:≈]\s*([0-9]+\\.?[0-9]*(?:e[+-]?[0-9]+)?)", raw)
    if m:
        return float(m.group(1))
    # 纯数字且很小
    try:
        v = float(raw)
        if 0 < v <= 1:
            return v
    except ValueError:
        pass
    return None


def _parse_sample_size(row: Any) -> int | None:
    """获取样本量，支持 int、float、字段多种命名。"""
    for attr in ("sample_size", "n_samples", "n", "sample_count", "num_samples"):
        v = getattr(row, attr, None)
        if v is not None:
            return int(v) if isinstance(v, (int, float)) else None
    return None


def _parse_effect_size(row: Any) -> float | None:
    """获取效应量。"""
    for attr in ("effect_size", "beta", "log2fc", "log2FC", "odds_ratio", "or", "cohens_d"):
        v = getattr(row, attr, None)
        if v is not None:
            return float(v) if isinstance(v, (int, float)) else None
    return None


def _parse_year(row: Any) -> int | None:
    """获取发表年份。"""
    for attr in ("publish_year", "pub_year", "year", "publication_year"):
        v = getattr(row, attr, None)
        if v is not None:
            return int(v)
    return None


def _get_strength_baseline(row: Any) -> float:
    """根据 EvidenceStrength 枚举的值返回基准权重。"""
    s = getattr(row, "strength", None)
    if s is None:
        return 0.5
    sval = str(s.value if hasattr(s, "value") else s)
    score_map = {
        "p<5e-8": 1.0,
        "p<1e-5": 0.85,
        "p<0.01": 0.65,
        "auc>0.8": 0.90,
        "auc>0.6": 0.70,
        "log2fc>1": 0.80,
        "log2fc>0.5": 0.60,
        "nominal": 0.40,
        "weak": 0.25,
        "not_significant": 0.10,
        "unknown": 0.30,
    }
    return score_map.get(sval.lower(), 0.5)


def _get_dimension_name(row: Any) -> str | None:
    """获取维度名称，支持多种属性名和枚举类型。"""
    for attr in ("dimension", "dim", "dim_name", "evidence_dimension"):
        v = getattr(row, attr, None)
        if v is not None:
            if hasattr(v, "value"):
                return str(v.value)
            return str(v)
    return None


def compute_data_weight(
    row: Any,
    *,
    max_log_n: float = 7.0,     # log10(10M) ≈ 7
    effect_threshold: float = 1.0,
    pval_max: float = 5e-8,
    decay_years: float = 7.0,  # 2026-07-30: 收紧时效性 (10→7)
    min_weight: float = 0.10,
) -> float:
    """
    计算单条证据行的数据驱动权重。

    权重公式:
        logN_weight = min(log10(N+1) / max_log_n, 1.0)
        pval_weight = min(-log10(pval) / -log10(pval_max), 1.0)  (pval <= 0.05)
                      else 0.15 (pval > 0.05)
        effect_weight = min(abs(effect) / effect_threshold, 1.0)
        recency_weight = 0.5 + 0.5 * max(0, 1 - age / decay_years)
        data_weight = logN_weight * pval_weight * (0.5 + 0.5*effect_weight) * recency_weight

    参数调优 (2026-07-30):
        - min_weight 从 0.05 提到 0.10，避免间接证据行完全掉地板
        - pathway/druggability 维度额外 0.12 保底
        - sample_size=0 时额外 0.3× 衰减（防止虚高）
    """
    # 1. logN_weight
    n = _parse_sample_size(row)
    if n and n > 0:
        log_n = math.log10(n + 1)
        logN_weight = min(log_n / max_log_n, 1.0)
    else:
        # 无样本量信息时，用 strength 枚举基准估算
        # 2026-07-30 fix: 额外 0.3× 衰减，防止 sample_size=0 时虚高
        logN_weight = _get_strength_baseline(row) * 0.6 * 0.3

    # 2. pval_weight
    pval = _parse_pval(getattr(row, "raw_stat", "") or "")
    if pval is not None and pval > 0:
        if pval <= 0.05:
            pval_weight = min(-math.log10(pval) / -math.log10(pval_max), 1.0)
        else:
            pval_weight = 0.15
    else:
        # 无 p-value 时固定 0.5 回退，不靠 strength 枚举虚高
        pval_weight = 0.5

    # 3. effect_weight
    eff = _parse_effect_size(row)
    if eff is not None:
        eff_abs = abs(eff)
        effect_weight = min(eff_abs / effect_threshold, 1.0)
    else:
        effect_weight = 0.5

    # 4. recency_weight
    year = _parse_year(row)
    if year and year > 1900:
        age = CURRENT_YEAR - year
        recency_weight = 0.5 + 0.5 * max(0.0, 1.0 - age / decay_years)
    else:
        recency_weight = 0.75  # 无年份信息用默认值

    # 5. 组合
    raw_weight = logN_weight * pval_weight * (0.5 + 0.5 * effect_weight) * recency_weight

    # 5. 维度惩罚 (safety ≠ efficacy)
    # 2026-07-30: safety 维度另乘 0.7
    dim_name = _get_dimension_name(row)
    if dim_name and dim_name.lower() == "safety":
        raw_weight *= 0.7

    # 边界保护
    # 2026-07-31 fix: 当所有数值字段缺失时用 strength 枚举区分
    has_numeric = any([
        _parse_sample_size(row) is not None,
        _parse_pval(getattr(row, "raw_stat", "") or "") is not None,
        _parse_effect_size(row) is not None,
        _parse_year(row) is not None,
    ])
    if not has_numeric:
        # 纯枚举权重: 不用 min_weight 杀平, 直接返回枚举基准
        baseline = _get_strength_baseline(row)
        scaled = baseline * 0.35  # 映射到 [0.035, 0.35] 范围
        dim_name = _get_dimension_name(row)
        if dim_name and dim_name.lower() == "safety":
            scaled *= 0.7
        return max(0.03, min(scaled, 1.0))
    # 有数值字段时正常保护
    dim_name = _get_dimension_name(row)
    if dim_name and dim_name.lower() in ("pathway", "druggability", "druggable"):
        min_weight = max(min_weight, 0.12)
    return max(min_weight, min(raw_weight, 1.0))


def compute_batch_weights(
    rows: list[Any],
    *,
    normalize: bool = True,
) -> list[float]:
    """
    批量计算权重，支持归一化到 [0, 1] 区间。

    归一化模式 (normalize=True):
        max_weight = max(all_weights)
        if max_weight > 0:
            weights = [w / max_weight for w in weights]

    返回归一化后的权重列表（不会修改 row.data_weight）。
    """
    weights = [compute_data_weight(r) for r in rows]
    if normalize and weights:
        max_w = max(weights)
        if max_w > 0:
            weights = [w / max_w for w in weights]
    return weights


def update_row_weights(
    rows: list[Any],
    *,
    normalize: bool = False,
) -> float:
    """
    原地更新每条证据行的 data_weight 字段。

    Args:
        rows: 证据行列表（EvidenceRow 或其子类）
        normalize: 是否归一化到 [0,1]

    Returns:
        max_weight: 更新后的最大权重值
    """
    for r in rows:
        if hasattr(r, "data_weight"):
            r.data_weight = compute_data_weight(r)

    weights = [r.data_weight for r in rows if hasattr(r, "data_weight")]
    if not weights:
        return 0.0

    max_w = max(weights)
    if normalize and max_w > 0:
        for r in rows:
            if hasattr(r, "data_weight") and r.data_weight > 0:
                r.data_weight /= max_w

    return max_w
