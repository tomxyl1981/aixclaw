# exo：分布式本地推理集群

> 来源：https://github.com/exo-explore/exo | 分析日期：2026-05-14

## 基本信息
- Stars: 44,616 | Forks: 3,141
- 语言: Python | 协议: Apache 2.0
- 创建: 2024-06-24 | 最新: v1.0.71

## 核心能力
- 多设备自动发现，零配置组集群
- Thunderbolt 5 RDMA（延迟降低99%）
- 拓扑感知张量并行（4设备3.2x加速）
- MLX后端 + 多API兼容（OpenAI/Claude/Ollama）
- 标杆：4×M3 Ultra Mac Studio跑DeepSeek v3.1 671B

## 与AIX关系
- 互补：exo=推理层，AIX=经济层
- 可直接组合：exo集群推理 → AIX Box Coin Hour结算
- 那耶村升级路径：单M4 → exo集群 → 大模型

## 局限
- RDMA依赖TB5直连
- Linux GPU支持未完成
- 无经济层
