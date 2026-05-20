# MTP/Lookahead Decoding：并行推理加速

> 来源：LMSYS 2023-11 | 分析日期：2026-05-15

## 核心概念
MTP（Multi-Token Prediction）= Lookahead Decoding

使用Jacobi迭代方法打破自回归解码的串行依赖，实现并行token生成。

## 技术原理
传统：token1 → token2 → token3（串行）
Lookahead：同时生成多个n-gram → 并行验证 → 接受正确的

关键参数：
- W=15（lookahead window）
- N=5（n-gram size）
- G=15（verification n-grams）

## 性能提升
- LLaMA-2-7B: 1.5-2.3x加速
- Qwen27B: 40%提速（24→34 Tps）
- 万字文档：10秒→6秒

## 实现路径
LLaMA.cpp完整支持：
```bash
llama-lookahead -hf Qwen-27B -p "prompt" -ngl 99 -kvu
```

## 与AIX关系
- 部署位置：Mac mini M4推理中枢
- 经济影响：推理提速40% = Coin Hour边际成本降28%
- 升级路径：Qwen-7B → Qwen-27B → exo集群

## 优势对比
| 方案 | 草稿模型 | 加速比 | 复杂度 |
|------|---------|--------|--------|
| MTP | 不需要 | 1.5-2.3x | 低 |
| Speculative | 需要 | 2-3x | 中 |
| Medusa | 训练 | 2-3x | 高 |

## 注意事项
- ✅ 长文本生成最佳
- ✅ 零额外成本
- ⚠️ 显存开销增加
