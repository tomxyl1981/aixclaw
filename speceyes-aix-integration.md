# SpecEyes 框架与 AIX 融合分析

> 研究来源：厦门大学、罗切斯特大学、俄亥俄州立大学
> 核心概念：快慢思考 + 投机加速
> 生成日期：2026-04-19

---

## SpecEyes 解决什么问题？

### 痛点：状态化瓶颈（Stateful Bottleneck）

**传统代理式多模态大模型的问题**：

```
用户提问 → 模型调用视觉工具（放大、裁剪、OCR）→ 
分析结果 → 再次调用工具 → ... → 
最终答案

问题：调用深度↑ → 延迟线性爆炸 → GPU闲置 → 并发能力崩溃
```

| 问题 | 后果 |
|------|------|
| 串行处理 | 延迟爆炸 |
| 状态依赖 | 并发崩溃 |
| 工具调用深度增加 | GPU大量闲置 |

### 解决方案：快慢思考架构

**灵感来源**：人类大脑的"快慢思考"（Daniel Kahneman《思考，快与慢》）

| 系统 | 特点 | 角色 |
|------|------|------|
| **系统1（快思考）** | 直觉、快速、无意识 | 轻量级小模型，快速预判 |
| **系统2（慢思考）** | 分析、缓慢、有意识 | 大模型深度处理 |

---

## SpecEyes 核心架构

### 三大组件

```
┌─────────────────┐
│   用户请求      │
└────────┬────────┘
         ↓
┌─────────────────┐
│  认知门控机制   │ ← 答案可分性评估
│  (Gate)        │
└────┬───────┬───┘
     │       │
     ↓       ↓
┌───────┐ ┌───────┐
│快系统 │ │慢系统 │
│小模型 │ │大模型 │
└───┬───┘ └───┬───┘
    │         │
    ↓         ↓
  投机答案   深度推理
    │         │
    └────┬────┘
         ↓
┌─────────────────┐
│    最终答案     │
└─────────────────┘
```

### 组件1：快思考系统（小模型）

**特点**：
- 轻量级、无工具依赖
- 快速直觉判断
- 投机生成答案

**作用**：
- 80%简单问题直接解决
- 不调用外部工具
- 延迟极低

### 组件2：慢思考系统（大模型）

**特点**：
- 重量级、依赖工具
- 深度推理
- 多步交互

**作用**：
- 20%复杂问题深度处理
- 调用视觉工具
- 准确率高

### 组件3：认知门控机制

**关键创新**：答案可分性（Answer Separability）

```python
class CognitiveGate:
    def evaluate_confidence(self, quick_answer, context):
        """
        评估快系统答案的自信度
        无需真实标签，基于答案可分性
        """
        # 检查答案是否边界清晰
        separability_score = self.compute_separability(quick_answer)
        
        if separability_score > threshold:
            return quick_answer  # 自信，直接采用
        else:
            return slow_system.process(context)  # 不自信，回退大模型
```

---

## 性能提升

| 指标 | 结果 |
|------|------|
| 推理速度 | 1.1x - 3.35x 提升 |
| 准确率 | 最高提升 6.7% |
| 幻觉问题 | 显著减少 |
| GPU利用 | 大幅改善 |

---

## 与 AIX 的契合点分析

### 契合1："LLM打工，代码做主"的完美落地

**SpecEyes 的逻辑**：
- 快系统 = 确定性规则（类似代码）
- 慢系统 = LLM深度推理

**AIX 的理念**：
- 确定性逻辑 → 代码层
- 语义理解 → LLM层

**融合**：SpecEyes 的快系统可以是 AIX 的 "代码层"，慢系统才是 LLM

### 契合2：本地推理的分层架构

**AIX Box 可以借鉴 SpecEyes**：

```
┌──────────────────────────────┐
│     AIX Box 本地推理架构      │
├──────────────────────────────┤
│                              │
│  ┌────────────────────┐     │
│  │  快系统（本地规则）    │     │
│  │  • 确定性逻辑         │     │
│  │  • Skill规则执行      │     │
│  │  • 无需LLM参与        │     │
│  └─────────┬──────────┘     │
│            │                │
│      自信？│                │
│            │                │
│  ┌─────────┴──────────┐     │
│  │  慢系统（本地LLM）    │     │
│  │  • Pico Claw推理     │     │
│  │  • 7B-13B模型        │     │
│  │  • 消耗Coin Hour     │     │
│  └─────────────────────┘     │
│                              │
└──────────────────────────────┘
```

**优势**：
- 80%请求走快系统 → 零Coin Hour消耗
- 20%复杂请求走慢系统 → 消耗Coin Hour
- 用户成本大幅降低

### 契合3：避坑门控 = Harness 机制

**SpecEyes 的认知门控**：
- 评估答案可分性
- 决定快系统 vs 慢系统

**AIX 的 Harness 机制**：
- 评估操作合规性
- 决定允许 vs 拦截

**融合**：认知门控可以成为 Harness 的一个子模块

```python
class SpecEyesHarness:
    def process_request(self, user_input):
        # 第一步：Harness安全检查
        if not self.safety_check(user_input):
            return "操作被拦截"
        
        # 第二步：认知门控评估
        separability = self.evaluate_separability(user_input)
        
        if separability > threshold:
            # 快系统：规则执行
            return self.fast_system.execute(user_input)
        else:
            # 慢系统：LLM推理
            return self.slow_system.reason(user_input)
```

---

## 具体融合方案

### 方案一：Pico Claw 快慢架构

**实现**：

```python
class PicoClawFastSlow:
    def __init__(self):
        self.fast_system = RuleEngine()  # 快系统：Skill规则
        self.slow_system = LLMEngine()   # 慢系统：本地LLM
        self.gate = CognitiveGate()      # 认知门控
    
    def process(self, user_input):
        # 1. 快系统先尝试
        quick_answer = self.fast_system.execute(user_input)
        
        # 2. 认知门控评估
        if self.gate.is_confident(quick_answer):
            # 自信，直接返回（零Coin Hour）
            return quick_answer
        else:
            # 不自信，慢系统推理（消耗Coin Hour）
            return self.slow_system.reason(user_input)
```

**Coin Hour 优化**：

| 场景 | 传统Pico Claw | 快慢架构Pico Claw |
|------|---------------|------------------|
| 简单查询（80%） | 10 CH | 0 CH（快系统） |
| 复杂推理（20%） | 50 CH | 50 CH（慢系统） |
| 平均消耗 | 18 CH | 10 CH |
| **节省** | - | **44%** |

### 方案二：SpecEyes Skill 化

**将认知门控打包成 Skill**：

```yaml
---
name: speceyes-gate
description: 认知门控机制，评估答案可分性，决定快慢系统切换
---

# SpecEyes Gate Skill

## 使用场景
- 判断用户的请求是否需要LLM深度推理
- 评估快速规则是否能给出足够准确的答案

## 输入
- 用户请求
- 快速答案（如果有）
- 上下文信息

## 输出
- 决策：使用快系统 OR 慢系统
- 置信度分数（0-1）
- 推荐策略
```

### 方案三：那耶村场景应用

**农产品价格查询**：

```
用户："梯田米现在多少钱？"

快系统：
├── 查询本地缓存（最近1小时数据）
├── 如果有数据 → 直接返回
└── 自信度：高 → 采用

用户："帮分析梯田米未来3个月价格趋势"

快系统：
├── 无法用缓存数据回答
└── 自信度：低 → 回退

慢系统：
├── 调用Firecrawl抓取市场数据
├── Pico Claw分析趋势
├── 消耗Coin Hour
└── 返回深度分析
```

---

## 技术实现路径

### 阶段一：规则引擎（快系统）

**目标**：搭建基于 Skill 的规则引擎

```python
class RuleEngine:
    def __init__(self):
        self.skill_store = SkillStore()
        self.cache = IPFS()  # 本地存储
    
    def execute(self, user_input):
        # 1. 检查缓存
        if cached := self.cache.get(user_input):
            return cached
        
        # 2. 加载匹配的Skill
        skill = self.skill_store.match_skill(user_input)
        
        # 3. 执行规则
        return skill.execute(user_input)
```

### 阶段二：认知门控

**目标**：实现答案可分性评估

```python
class CognitiveGate:
    def is_confident(self, quick_answer):
        """
        评估答案可分性
        无需真实标签的自信度评估
        """
        # 方法1：答案边界清晰度
        if self.is_clear_boundary(quick_answer):
            return True
        
        # 方法2：历史准确率
        if self.history_accuracy(quick_answer.type) > 0.95:
            return True
        
        # 方法3：问题复杂度评估
        if self.complexity_score(quick_answer.context) < threshold:
            return True
        
        return False
```

### 阶段三：慢系统优化

**目标**：优化 LLM 推理效率

```python
class SlowSystem:
    def reason(self, user_input):
        # 1. 分解复杂问题
        sub_tasks = self.decompose(user_input)
        
        # 2. 并行处理
        results = parallel_execute(sub_tasks)
        
        # 3. 聚合答案
        final_answer = self.aggregate(results)
        
        # 4. 消耗Coin Hour
        deduct_coin_hour(len(sub_tasks))
        
        return final_answer
```

---

## 与其他项目的协同

| 项目 | SpecEyes 融合方式 |
|------|------------------|
| **Karpathy Guidelines** | 快系统遵循规则，慢系统遵循行为指南 |
| **Firecrawl MCP** | 慢系统调用Firecrawl获取数据 |
| **预测市场** | 快系统返回缓存数据，慢系统深度分析 |
| **DESIGN.md** | 快系统生成简单UI，慢系统复杂交互 |
| **百万美元架构师** | 快系统执行日常任务，慢系统深度创意 |

---

## 孵化项目方向

### 项目20：SpecEyes 认知门控系统

**问题**：80%的请求不需要LLM深度推理，浪费时间浪费钱

**解决方案**：
- 快系统：规则引擎 + Skill执行
- 慢系统：Pico Claw LLM推理
- 认知门控：答案可分性评估

**Coin Hour 节省**：平均44%

**适合背景**：AI架构、系统优化、规则引擎

---

## 金句

> "SpecEyes 让 80% 的简单请求快如闪电，20% 的复杂请求慢得精准。"

> "快系统是代码层，慢系统是LLM层——SpecEyes 是 AIX 理念的完美落地。"

> "认知门控是天生的 Harness，决定让谁思考、让谁打工。"

---

## 总结

**SpecEyes 与 AIX 的契合度**：★★★★★

| 维度 | 契合点 |
|------|--------|
| 架构哲学 | 快慢系统 = 代码做主+LLM打工 |
| 本地推理 | 80%请求零Coin Hour，20%请求LLM推理 |
| Harness | 认知门控天然是安全+效率门控 |
| 经济优化 | 用户成本降低44% |
| Skill生态 | 认知门控、快系统都可Skill化 |

**一句话**：SpecEyes 让 AIX Box 更聪明——知道什么时候该快、什么时候该慢，知道什么时候该省钱、什么时候该深度思考。

---

*生成时间：2026-04-19（UTC）*
