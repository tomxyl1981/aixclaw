# Codex /goal 源码解析：长周期 Agent 的状态机设计

> 来源：用户377861 分享 | 日期：2026-05-17

---

## 核心洞见

**从"别停下来"到"目标在多轮之间还认得自己"**

普通 loop 解决的是"持续性"；/goal 更关心"一个目标在多轮之间还认不认得自己"。

---

## /goal 的三层设计

```
第一层：目标持久化
  - 自然语言目标 → thread 上的持久对象
  - 进入 state-db，有自己的状态、预算、token 记账
  - 状态：active / paused / complete / budget_limited

第二层：运行时生命周期
  - GoalRuntimeEvent：TurnStarted / ToolCompleted / TurnFinished
  - MaybeContinueIfIdle / TaskAborted / ExternalSet / ExternalClear
  - ThreadResumed

第三层：完成审计与预算收束
  - continuation 模板：继续可以，但不能重新定义目标
  - budget_limit 模板：到点了，别开新工作，整理现场
```

---

## Goal vs Loop 对照

| 维度 | 普通 loop | Codex /goal |
|------|-----------|-------------|
| 目标位置 | prompt、脚本或文件里 | thread goal 和 state-db |
| 续跑方式 | 结束后再喂同一目标 | 空闲时触发 continuation turn |
| 状态边界 | 通常靠脚本约定 | active/paused/complete/budget_limited |
| 完成判断 | 模型自报或脚本约定 | completion audit 后 update_goal complete |
| 预算控制 | 外部粗略限制 | token 和 wall clock accounting |
| 中断恢复 | 依赖脚本和临时文件 | runtime event 同步状态 |

---

## 关键工程细节

### 1. `update_goal` 只接受 `complete`

```rust
// 模型可以宣布"做完了"，但没法自己宣布"超预算了"或"差不多了"
// 退路被运行时收掉了
```

### 2. continuation prompt 的完成审计

- 目标会跨 turn 持续存在
- 不要把完整目标缩小成当前容易完成的小目标
- 要基于当前 worktree 和外部状态
- 每个要求都要找到证据
- 证据弱、不完整、间接，都不能算完成

### 3. budget_limit.md 模板

```
当前 goal 已经达到 token budget：
- 不要再为这个 goal 开始新的实质工作
- 尽快收束本轮
- 总结有用进展、剩余工作或阻塞
- 给用户留下清楚的下一步
```

---

## Agent 工作现场六件事

| 事项 | 说明 | /goal 的位置 |
|------|------|-------------|
| 目标 | 不是愿望，是范围、约束、验收、停止条件 | thread 上的状态对象 |
| 上下文 | 当前推理的工作集 | Harness 层 |
| 工具 | Agent 接触真实系统的接口 | update_goal 参数被收紧 |
| 状态 | 计划、进度、预算、完成标记 | state-db |
| 验证 | 测试、构建、lint、PR 状态 | continuation 模板约束 |
| 收束 | 暂停、预算耗尽、中断、交接 | budget_limit 模板 |

---

## 三个可迁移的工程思路

### 1. 目标做成对象，不是 prompt

让"目标"在系统里有名字、有状态机，不只是 prompt 拼接的副产品。

### 2. 完成做成审计，不是开关

只暴露一个开关，但拉高门槛——逼模型把"差不多"翻译成"哪些要求、哪些证据"。

### 3. 专门给"停"留一份模板

停下来，本身也是一种状态，要有自己的协议。

---

## 与 AIX 的关联

- **硬件化 Harness**：AIX Box 把拦截机制写入硬件钱包，物理锁死禁止违规操作
- **"LLM打工，代码做主"**：/goal 的 `update_goal` 设计是这个理念的工程实现
- **可接管性**：长任务不能只看能跑多久，更要看跑完或停下后现场能不能被接手

---

## 金句

> "可以把很多执行交给 Agent，但别把工作现场交给运气。"

> "目标一旦变成 thread 上的状态，运行时至少可以开始处理：当前目标是不是 active、是否被 paused、消耗了多少 token 和时间、是否到了 budget limit。"

> "长任务里，Agent 很容易给自己找一个看起来合理的结束点。系统需要不断把模型从'讲一个完成故事'，拉回'拿出完成证据'。"

---

*归档日期：2026-05-17*
