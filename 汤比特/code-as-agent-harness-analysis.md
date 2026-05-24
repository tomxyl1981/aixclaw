# Code as Agent Harness 论文分析

**论文**：arXiv 2605.18747
**标题**：Code as Agent Harness
**作者**：Xuying Ning + 41位作者（Cornell/UIUC等）
**时间**：2026-05-18
**GitHub**：https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers
**来源**：用户377861分享

---

## 核心观点

> **Code is no longer only a target output. It increasingly serves as an operational substrate for agent reasoning, acting, environment modeling, and execution-based verification.**

**中心思想**：代码不再只是输出目标，而是Agent基础设施的基础。

---

## 三层架构

### 第一层：Harness Interface（接口层）

代码连接Agent到：
- **Reasoning**（推理）
- **Action**（行动）
- **Environment Modeling**（环境建模）

### 第二层：Harness Mechanisms（机制层）

| 机制 | 说明 |
|------|------|
| Planning | 规划（长周期执行） |
| Memory | 记忆（状态持久化） |
| Tool Use | 工具使用 |
| Feedback-driven Control | 反馈驱动控制 |
| Optimization | 优化（自适应） |

### 第三层：Multi-Agent Scaling（多Agent扩展）

- 共享代码artifact
- 多Agent协调
- Review机制
- Verification机制

---

## 应用场景

- Coding assistants
- GUI/OS automation
- Embodied agents
- Scientific discovery
- Personalization and recommendation
- DevOps
- Enterprise workflows

---

## Harness Engineering六大挑战

| 挑战 | 说明 |
|------|------|
| 评估 | 不能只看最终任务成功 |
| 验证 | 不完整反馈下的验证 |
| 无回归 | Harness改进不能破坏已有功能 |
| 共享状态 | 多Agent间一致状态 |
| 人监督 | 安全关键动作需要人类监督 |
| 多模态 | 扩展到多模态环境 |

---

## 与AIX的关系

### 直接验证"LLM打工，代码做主"

| AIX理念 | 论文对应 |
|---------|----------|
| "代码做主" | Code as Agent Harness |
| Harness | Harness Mechanisms |
| 硬件级Harness | 人监督 + 无回归 |
| UTXO账本 | Memory + Verification |
| OpenHarness | Tool Use + Interface |

### 三层架构映射

```
论文                        AIX
第一层：Interface      →    OpenHarness API
第二层：Mechanisms     →    Skill/Memory/Tool
第三层：Multi-Agent   →    AIX DAO多Agent协作
```

### 六大挑战 → AIX解决方案

| 挑战 | AIX方案 |
|------|---------|
| 评估 | Coin Hour计费 = 效果量化 |
| 验证 | UTXO原子记录 |
| 无回归 | 硬件级锁死 |
| 共享状态 | 本地知识图谱 |
| 人监督 | Harness二次确认 |
| 多模态 | ViMax视频生成 |

---

## 关键引用

> **"By centering code as the harness of agentic AI, this survey provides a unified roadmap toward executable, verifiable, and stateful AI agent systems."**

**一句话**：把代码作为Agent Harness的中心 → 可执行、可验证、有状态的AI系统

---

## 对AIX的启发

### 验证AIX路线的正确性

这篇论文是学术界对"代码做主"的系统化阐述：
- 代码不只是输出 → Harness基础设施
- 三层架构 → AIX九层架构的理论支撑
- 六大挑战 → AIX Box设计问题清单

### OpenHarness设计参考

论文的Harness Mechanisms可以直接映射到OpenHarness设计：
1. **Planning** → 任务调度层
2. **Memory** → 本地知识图谱 + AgentMemory.dev
3. **Tool Use** → Skills Manager
4. **Feedback-driven Control** → Coin Hour反馈
5. **Optimization** → 自适应Harness（按任务调整）

### Multi-Agent场景

第三层的多Agent扩展 → AIX DAO的Agent协作：
- 共享代码artifact → Skills Store共享
- Review机制 → ReviewAgent组件
- Verification → UTXO审计

---

## 下一步行动

1. 把论文PDF存到知识库
2. 结合上一篇"Agent安全"论文，形成完整Harness理论框架
3. 给刘威：OpenHarness设计参考这两篇论文

---

*存档时间：2026-05-24*
