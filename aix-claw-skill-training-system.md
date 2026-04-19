# AIX Claw Skill 训练系统

> 基于 Andrej Karpathy 的 65 行规则文件
> 项目：https://github.com/forrestchang/andrej-karpathy-skills（61,130 Star）
> 生成日期：2026-04-19

---

## Karpathy Guidelines Skill 是什么？

### 核心定位

> "行为指南，减少 LLM 编码常见错误"

这不是教AI写代码，而是教AI**如何思考、如何做决策、如何避免过度设计**。

### 四大核心规则

| 规则 | 核心 | 避免 |
|------|------|------|
| **Think Before Coding** | 不假设、不隐藏困惑、表面权衡 | 假设默认值、过度解读 |
| **Simplicity First** | 最少代码解决问题 | 过度抽象、不存在的需求 |
| **Surgical Changes** | 只改必须改的 | 重构无关代码、"顺便优化" |
| **Goal-Driven Execution** | 定义成功标准、循环验证 | "让它工作"这种弱目标 |

### 关键洞察（Karpathy 原话）

> "LLM 会写 200 行代码，其实 50 行就够了。"

> "LLM 会假设、会隐藏困惑、会过度设计。"

> "这不是技术问题，是行为问题。"

---

## 如何用 Karpathy Skill 训练 Pico Claw

### 方案一：直接嵌入 CLAUDE.md

**最简单的方式**：把 `CLAUDE.md` 放到项目根目录，Pico Claw 自动遵循

```
你的项目/
├── CLAUDE.md          ← Karpathy 规则（或合并你的规则）
├── AGENTS.md          ← 项目特定指令
└── DESGIN.md          ← 设计系统（可选）
```

**Pico Claw 读取优先级**：
1. 项目级 `CLAUDE.md`（最高优先）
2. 用户级 `~/.claude/CLAUDE.md`
3. 默认行为

### 方案二：打包成 Skill Store 的 Skill

**Skill 格式**（已标准化）：

```yaml
---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes
license: MIT
---

# Karpathy Guidelines

[规则内容...]
```

**上架 Skill Store**：
- 用户购买 → 自动注入 Pico Claw
- Coin Hour 支付（如 100 CH）
- 一次性购买，永久使用

### 方案三：动态加载（MCP 协议）

```python
# Pico Claw 启动时加载 Skills
class PicoClaw:
    def load_skills(self):
        skills = [
            "karpathy-guidelines",  # 编码行为规则
            "design-md-reader",     # DESIGN.md 读取
            "firecrawl-mcp",        # 网页抓取
        ]
        
        for skill in skills:
            skill_content = skill_store.get(skill)
            self.system_prompt += skill_content
```

---

## 创建你自己的 "_style" Skill

### 为什么需要个性化 Skill？

**问题**：Karpathy 规则是通用编码行为，但每个人都有自己的偏好：
- 编码风格（函数式 vs OOP）
- 注释习惯（详细 vs 极简）
- 测试策略（TDD vs 后补测试）
- 文档偏好（英文 vs 中文）

**解决**：创建个人 "风格 Skill"

### 个人风格 Skill 模板

```yaml
---
name: my-coding-style
description: 个人编码风格偏好，合并到 Karpathy Guidelines
author: your-name
license: MIT
---

# My Coding Style

## 语言偏好
- 默认使用中文注释（除非是 API 文档）
- 变量名用英文，注释用中文
- 函数名遵循 snake_case（Python）或 camelCase（JS）

## 代码风格
- 函数不超过 30 行，如果超过就拆分
- 优先使用纯函数，避免副作用
- 类型注解必须完整（Python: Type Hints）

## 测试策略
- 先写测试（TDD）
- 测试覆盖核心逻辑，不测 trivial 代码
- 测试名称描述预期行为（test_should_xxx）

## 注释策略
- 不写"做什么"（代码已经说明了）
- 写"为什么这么做"（解释原因）
- 复杂逻辑加注释，简单逻辑不加

## 禁止行为
- 禁止未请求的"顺便优化"
- 禁止假设默认值（必须问）
- 禁止超过 50 行的函数（除非我明确说可以）

## 成功标准
- Diff 不超过 100 行（除非大重构）
- 每个改动都能追溯到我的请求
- 测试全部通过
```

### 如何训练你的"龙虾"

```python
class ClawTraining:
    def train_your_claw(self):
        # 1. 加载基础规则（Karpathy）
        base_rules = skill_store.get("karpathy-guidelines")
        
        # 2. 加载个人风格
        personal_style = skill_store.get("my-coding-style")
        
        # 3. 合并规则
        combined_rules = f"""
# Pico Claw System Prompt

{base_rules}

---

# Personal Style

{personal_style}

---

⚠️ 优先级：当 Karpathy 规则和个人风格冲突时，遵循个人风格。
"""
        
        # 4. 写入 Pico Claw 配置
        self.save_to_claude_md(combined_rules)
```

---

## Skill 训练的四个层次

### 层次 1：行为规则（Karpathy）

**解决问题**：LLM 的行为偏差（过度设计、假设、隐藏困惑）

| 规则 | 训练效果 |
|------|----------|
| Think Before Coding | AI 会先问，不假设 |
| Simplicity First | AI 写 50 行，不写 200 行 |
| Surgical Changes | AI 只改必须改的，不"顺便优化" |
| Goal-Driven Execution | AI 定义成功标准，循环验证 |

### 层次 2：个人风格（_style）

**解决问题**：编码风格偏好、语言偏好、注释习惯

| 维度 | 示例 |
|------|------|
| 语言偏好 | 中文注释 vs 英文注释 |
| 代码风格 | snake_case vs camelCase |
| 测试策略 | TDD vs 后补测试 |
| 类型注解 | 必须完整 vs 可选 |

### 层次 3：项目特定（AGENTS.md）

**解决问题**：项目架构、技术栈、约定

```markdown
# 项目特定规则

## 技术栈
- Python 3.11 + FastAPI + PostgreSQL
- 前端：React + TypeScript

## 约定
- API 路由遵循 RESTful
- 数据库迁移用 Alembic
- 环境变量用 .env

## 禁止
- 禁止使用 Django ORM（只用 SQLAlchemy）
- 禁止前端使用 class 组件（只用 Hooks）
```

### 层次 4：领域知识（知识库 Skill）

**解决问题**：行业知识、业务逻辑、最佳实践

```yaml
---
name: fintech-domain-knowledge
---

# 金融科技领域知识

## 风控规则
- 交易金额 > 10万触发人工审核
- 同 IP 多账号标记风险

## 合规要求
- 用户数据保留 5 年
- 日志必须包含审计轨迹
```

---

## 完整训练流程

```
输入请求
    ↓
检查是否有足够的上下文
    ├── 有 → 执行
    └── 无 → 提问（遵循 Think Before Coding）
    ↓
选择最简方案（遵循 Simplicity First）
    ↓
只改必须改的（遵循 Surgical Changes）
    ↓
定义成功标准（遵循 Goal-Driven Execution）
    ↓
循环验证直到成功
    ↓
检查是否符合个人风格（_style Skill）
    ├── 符合 → 完成
    └── 不符合 → 调整
```

---

## Skill Store 架构

### 基础技能包

| Skill | 说明 | 价格 |
|-------|------|------|
| **Karpathy Guidelines** | 编码行为规则 | 50 CH（一次性）|
| **Design.md Reader** | 设计系统读取 | 30 CH |
| **Firecrawl MCP** | 网页抓取 | 100 CH/月 |
| **Git Best Practices** | Git 提交规范 | 20 CH |

### 个人风格包

| Skill | 说明 | 价格 |
|-------|------|------|
| **Python Style** | Python 编码风格 | 30 CH |
| **JS/TS Style** | JavaScript/TypeScript 风格 | 30 CH |
| **TDD Enforcer** | 测试驱动开发强制 | 40 CH |
| **中文优先** | 中文注释偏好 | 免费 |

### 领域知识包

| Skill | 说明 | 价格 |
|-------|------|------|
| **Fintech Domain** | 金融科技知识 | 100 CH |
| **E-commerce Domain** | 电商领域知识 | 80 CH |
| **Game Dev Domain** | 游戏开发知识 | 80 CH |

---

## 与其他项目的协同

| 项目 | 协同方式 |
|------|----------|
| **DESIGN.md** | Pico Claw 读取 DESIGN.md + Karpathy 规则 |
| **Firecrawl MCP** | Claw 调用 Firecrawl → 遵循 Surgical Changes |
| **百万美元架构师** | 个人风格 Skill + 品牌定位 Skill 叠加 |
| **那耶村艺术家** | 艺术家创建自己的编码风格 Skill |

---

## 金句

> "Karpathy 规则让 LLM 少写 150 行废话，个人风格 Skill 让 LLM 写出你的味儿。"

> "不是教 AI 写代码，是教 AI 如何思考、如何做决策。"

> "Skill Store 让每个开发者都能把自己的编码哲学打包上架。"

> "四层训练：行为规则 → 个人风格 → 项目特定 → 领域知识。"

---

## 总结

**Karpathy Guidelines + AIX Box = 可训练的"龙虾"**

| 维度 | 传统 AI | Pico Claw + Skills |
|------|---------|-------------------|
| 行为 | 默认行为（过度设计） | Karpathy 规则约束 |
| 风格 | 统一风格 | 个人风格 Skill 定制 |
| 项目 | 无项目上下文 | AGENTS.md 项目特定 |
| 领域 | 通用知识 | 领域知识 Skill 注入 |

**核心理念**：
- LLM 打工（执行）
- Skill 做主（规则）
- 用户控制（风格）

---

*生成时间：2026-04-19（UTC）*
