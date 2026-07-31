#!/usr/bin/env python3
"""verify_formula.py — 校验 confidence_formula.md 与代码实现的一致性"""
import ast, sys, os

errors = []
ok = []

# ── 1. 提取 target_evidence_matrix.py 的关键常量 ──
src = open('/home/xiaoyao/.openclaw/workspace-dev/target_evidence_matrix.py').read()
tree = ast.parse(src)

strength_weights = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == '_STRENGTH_WEIGHT':
                # 键是 EvidenceStrength.X 枚举属性, 不是字面量 → 提取属性名
                strength_weights = {}
                for key, val in zip(node.value.keys, node.value.values):
                    if isinstance(key, ast.Attribute):
                        strength_weights[key.attr] = ast.literal_eval(val)
                    else:
                        strength_weights[ast.literal_eval(key)] = ast.literal_eval(val)

# 文档中声称的权重表
doc_weights = {
    'P_VALUE_LT_5E8': 0.08, 'AUC_GT_0_8': 0.07, 'LOG2FC_GT_1': 0.07,
    'P_VALUE_LT_1E5': 0.06, 'AUC_GT_0_6': 0.05, 'LOG2FC_GT_0_5': 0.05,
    'P_VALUE_LT_0_01': 0.04, 'NOMINAL': 0.03, 'WEAK': 0.02,
    'UNKNOWN': 0.02, 'NOT_SIGNIFICANT': 0.01,
}
if strength_weights is None:
    errors.append("无法提取 _STRENGTH_WEIGHT")
else:
    for k, v in doc_weights.items():
        actual = strength_weights.get(k)
        if actual is None:
            errors.append(f"文档权重 {k} 不在代码中")
        elif abs(actual - v) > 1e-9:
            errors.append(f"{k}: 文档={v} 代码={actual}")
    ok.append(f"_STRENGTH_WEIGHT: {len(doc_weights)} 项全部一致")

# 提取双因子系数 0.80 / 0.20 / 4.0
src_text = src
checks = [
    ("coverage /4.0 封顶", "min(n_present / 4.0, 1.0)" in src_text),
    ("0.80 覆盖权重", "0.80 * coverage_score" in src_text),
    ("0.20 强度权重", "0.20 * intensity_score" in src_text),
    ("矛盾扣分 0.10", "contradiction_penalty += 0.10" in src_text),
    ("缺失扣分 0.1", "missing_penalty += 0.1" in src_text),
    ("一致性 boost 0.05", "consistency_boost += 0.05" in src_text),
]
for name, passed in checks:
    (ok if passed else errors).append(f"{name}: {'✅' if passed else '❌'}")

# ── 2. row_weight.py 关键公式 ──
rw = open('/home/xiaoyao/.openclaw/workspace-dev/row_weight.py').read()
rw_checks = [
    ("logN 公式 /7", "max_log_n" in rw and "7.0" in rw),
    ("pval 5e-8 基准", "5e-8" in rw or "5e-8" in rw.lower()),
    ("时效 7年衰减", "0.5 + 0.5" in rw),
    ("安全折扣 0.7", "*= 0.7" in rw),
]
for name, passed in rw_checks:
    (ok if passed else errors).append(f"row_weight {name}: {'✅' if passed else '❌'}")

# ── 3. entropy_section.py 关键逻辑 ──
es = open('/home/xiaoyao/.openclaw/workspace-dev/entropy_section.py').read()
es_checks = [
    ("compute_entropy 存在", "def compute_entropy" in es),
    ("render_entropy_section 存在", "def render_entropy_section" in es),
    ("H0 < 0.3 → 绿", "ne < 0.3" in es),
    ("H0 < 0.6 → 黄", "ne < 0.6" in es),
]
for name, passed in es_checks:
    (ok if passed else errors).append(f"entropy {name}: {'✅' if passed else '❌'}")

# ── 输出 ──
out = []
out.append(f"=== 校验结果: {len(ok)} 通过 / {len(errors)} 失败 ===")
out.extend(ok)
if errors:
    out.append("--- 失败项 ---")
    out.extend(errors)
# 无论成败都写文件，再决定退出码
open('/tmp/formula_verify_out.txt', 'w').write("\n".join(out))
if errors:
    sys.exit(1)
print("done")
