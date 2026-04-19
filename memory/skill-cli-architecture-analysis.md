# Skill vs CLI 三层架构分析

## 核心观点

Skill是自然语言层的"连接器"，CLI是确定性执行的"地基"。二者在三层架构中各司其职。

## 三层架构模型

### Layer 3: 自然语言层 (Skill)
- 意图理解、语义连接、任务编排
- 把人类模糊意图映射到可执行结构
- 灵活、容错、上下文感知

### Layer 2: 逻辑编排层 (Orchestration)
- 工作流引擎、API编排、状态管理
- 将Skill意图转换为系统调用序列
- 半确定性、可回滚、可观测

### Layer 1: 确定性执行层 (CLI)
- 系统调用、硬件操作、文件IO
- 精确、可靠、幂等的底层执行
- 确定性、原子性、不可变

## AI开发"重顶层轻底层"误区

| 误区 | 后果 |
|------|------|
| 让LLM直接生成Shell命令 | 命令错误、系统损坏 |
| Skill直接调用系统无校验 | 状态不一致 |
| 把CLI封装成Skill | 失去精确性也没获得灵活性 |
| 自然语言直接翻译为系统调用 | 状态丢失无法回滚 |

## AIX Box 在三层架构中的定位

### Layer 3: Skill生态层
- 那耶村艺术家创作的Skill
- Skill Store购买/销售
- MemPalace记忆增强
- Pico Claw AI Agent

### Layer 2: AIX编排层 (OpenClaw)
- 任务调度
- Coin Hour经济结算
- 分布式任务编排
- 状态一致性管理

### Layer 1: AIX Box执行层
- 硬件钱包 (AIX Token)
- 分布式计算 (边缘节点)
- 分布式存储
- 广告终端

## 关键结论

1. Skill负责"做什么"（What）— 灵活、创意
2. CLI负责"怎么做"（How）— 精确、可靠
3. 编排层负责"协调"（Orchestrate）— 连接、管理
4. AIX Box通过Coin Hour将三层与经济模型绑定

## 那耶村基地实践

- Layer 3: 音乐人自然语言创作
- Layer 2: OpenClaw编排资源
- Layer 1: AIX Box确定性执行
- 经济纽带: Coin Hour精准计费

