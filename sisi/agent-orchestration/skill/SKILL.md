---
name: agent_orchestrator
description: Multi-pattern agent orchestration supporting ReAct, Pipeline, Plan-Execute, Reflection, and Multi-Agent modes for AIX ecosystem.
version: 1.0.0
author: AIX Team
license: MIT
---

# Agent Orchestrator Skill

统一编排五种 Agent 工作模式，根据任务特性自动/手动选择最优执行策略。

## 五种模式总览

| 模式 | 适用场景 | 核心特性 | 那耶村示例 |
|------|---------|----------|-----------|
| **ReAct** | 开放探索 | 思考→行动→观察→再思考 | "有哪些IP可以出海？" |
| **Pipeline** | 标准化流程 | 固定步骤、错误处理、重试 | "制作第5集短剧" |
| **Plan-Execute** | 复杂项目 | 先规划后执行、里程碑检查 | "那耶村全年内容计划" |
| **Reflection** | 质量敏感 | 自我纠错、迭代优化 | "审查版权合规性" |
| **Multi-Agent** | 超复杂协作 | 多专家并行、分工协作 | "制作电影级纪录片" |

## 核心 API

### 1. auto_select_mode(task: str) → ModeRecommendation

分析任务特性，推荐最适合的模式。

**示例**：
```json
// 输入: "分析那耶村有哪些可以数字化的文化资产"
{
  "recommended_mode": "react",
  "confidence": 0.92,
  "reason": "开放探索任务，需要多轮信息收集和推理"
}

// 输入: "制作10集短剧并发布到抖音快手红果"
{
  "recommended_mode": "plan_execute",
  "confidence": 0.88,
  "reason": "复杂多步骤任务，需要规划和里程碑检查"
}
```

### 2. run_react(task: str, max_iterations: int = 10)

ReAct 模式执行 - 开放式探索与推理。

**流程**：
```
Thought 1: 分析任务 → Action 1: 查询版权 → Observation 1: 结果
Thought 2: 评估结果 → Action 2: 检查余额 → Observation 2: 结果
Thought 3: 决策 → Action 3: 执行购买 → 完成
```

### 3. run_pipeline(task: str, config: PipelineConfig)

Pipeline 模式执行 - 标准化工作流。

**配置示例**：
```yaml
pipeline:
  name: "短剧制作流程"
  steps:
    - id: verify
      skill: copyright_manager
      function: verify_license
      error_action: stop
    - id: generate
      skill: vimax
      function: generate_video
      error_action: retry
      max_retries: 2
    - id: upload
      skill: storage
      function: upload_ipfs
      error_action: continue
```

### 4. run_plan_execute(task: str, config: PlanConfig)

Plan-Execute 模式执行 - 复杂项目规划与执行。

**阶段示例**：
```yaml
plan:
  task: "那耶IP出海"
  phases:
    - name: "版权准备"
      tasks: [查询版权, 购买改编权]
      milestone: "版权就绪"
    - name: "内容制作" 
      tasks: [翻译剧本, 生成视频]
      milestone: "内容完成"
      dependencies: ["版权准备"]
    - name: "平台分发"
      tasks: [申请账号, 上传内容]
      milestone: "上线运营"
  checkpoints:
    - after: "版权准备"
      action: "用户确认继续"
```

### 5. run_reflection(task: str, config: ReflectionConfig)

Reflection 模式执行 - 自我纠错与质量优化。

**质量检查**：
```yaml
reflection:
  checks:
    - name: "版权合规"
      criteria: {valid: true, remaining: "> 0"}
    - name: "内容质量"  
      criteria: {completeness: ">= 0.8"}
      auto_fix: true
      max_iterations: 3
```

### 6. run_multi_agent(task: str, config: CrewConfig)

Multi-Agent 模式执行 - 多专家协作。

**配置示例**：
```yaml
crew:
  agents:
    - name: "文化顾问"
      role: "那耶村文化专家"
      skills: [naye_culture]
    - name: "剧本专家"  
      role: "短剧编剧"
      skills: [screenwriting]
    - name: "分发经理"
      role: "平台运营专家"  
      skills: [distribution]
  workflow:
    - phase: "策划"
      agents: ["文化顾问", "剧本专家"]
    - phase: "制作"
      agents: ["技术制片"]
      dependencies: ["策划"]
    - phase: "分发"
      agents: ["分发经理"]
      dependencies: ["制作"]
```

## 智能模式选择

### 决策逻辑

```python
def select_mode(task):
    if match_preset_pipeline(task):
        return "pipeline"
    if domain_count(task) >= 4:
        return "multi_agent"
    if quality_critical(task) and complexity(task) == "high":
        return "reflection"
    if complexity(task) == "high":
        return "plan_execute"
    if complexity(task) == "low" and openness(task) == "low":
        return "pipeline"
    return "react"
```

### 评估维度

| 维度 | 触发条件 | 推荐模式 |
|------|---------|----------|
| 复杂度>10步 | 多阶段依赖 | plan_execute |
| 领域跨度>=4 | 需多专家 | multi_agent |
| 质量必须达标 | 合规敏感 | reflection |
| 目标明确<3步 | 标准化 | pipeline |
| 开放探索 | 信息收集 | react |

## 定价

| 模式 | Coin Hour |
|------|----------|
| auto_select_mode | 免费 |
| run_react | 0.5 CH / 10 iterations |
| run_pipeline | 1 CH / execution |
| run_plan_execute | 2 CH + 0.5 CH/phase |
| run_reflection | 1 CH + 0.5 CH/iteration |
| run_multi_agent | 3 CH + 1 CH/agent |

## 限制

- ReAct: max 50 iterations
- Pipeline: max 20 steps
- Plan-Execute: max 10 phases
- Reflection: max 5 iterations
- Multi-Agent: max 10 agents

**Last Updated**: 2026-05-28
**Compatible**: OpenClaw 2.0+
