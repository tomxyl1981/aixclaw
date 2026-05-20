# AIX智能体五层架构

> 基于 CLAUDE 智能体开发工具包架构，适配 OpenClaw + AIX 项目

---

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│                    第五层：插件层                      │
│              PLUGINS (扩展包管理)                      │
├─────────────────────────────────────────────────────┤
│                 第四层：智能体组件层                    │
│           COMPONENTS (委员会、审查、测试)               │
├─────────────────────────────────────────────────────┤
│                   第三层：钩子层                        │
│              HOOKS (生命周期拦截)                      │
├─────────────────────────────────────────────────────┤
│                   第二层：技能层                        │
│              SKILLS (能力模块化)                       │
├─────────────────────────────────────────────────────┤
│                   第一层：记忆层                        │
│              MEMORY (持久化知识)                       │
└─────────────────────────────────────────────────────┘
```

---

## 第一层：记忆层 (MEMORY)

### 功能定位
**持久化知识存储，跨会话记忆复用**

### 当前实现

| 组件 | 文件 | 状态 |
|------|------|------|
| 长期记忆 | `MEMORY.md` | ✅ 已有 |
| 每日笔记 | `memory/YYYY-MM-DD.md` | ✅ 已有 |
| 用户画像 | `USER.md` | ✅ 已有 |
| 身份定义 | `IDENTITY.md` | ✅ 已有 |
| 知识库 | `knowledge/*.md` | ✅ 已有 |

### 增强计划

| 组件 | 描述 | 优先级 |
|------|------|--------|
| `CLAUDE.md` | 全局指令文件（类似 `.clauderc`） | 🔴 高 |
| `knowledge/` 结构化 | 按主题分类的知识索引 | 🔴 高 |
| 记忆检索优化 | 语义搜索 + 向量索引 | 🟡 中 |
| 记忆压缩 | 归档旧日志，保持 MEMORY.md 精简 | 🟢 低 |

### 命名规范

```
memory/
├── 2026-05-14.md          # 每日笔记
├── archive/               # 归档
│   └── 2026-04-*.md
knowledge/
├── aix-*.md               # AIX 项目相关
├── naye-village/          # 那耶村专题
├── competitors/           # 竞品分析
└── tech-stack/            # 技术栈
```

---

## 第二层：技能层 (SKILLS)

### 功能定位
**能力模块化，描述匹配 + 自动调用**

### 当前实现

| 技能 | 路径 | 状态 |
|------|------|------|
| coding-agent | `~/openclaw/skills/coding-agent/` | ✅ |
| healthcheck | `~/openclaw/skills/healthcheck/` | ✅ |
| node-connect | `~/openclaw/skills/node-connect/` | ✅ |
| security-best-practices | `~/openclaw/skills/security-best-practices/` | ✅ |
| skill-creator | `~/openclaw/skills/skill-creator/` | ✅ |
| tmux | `~/openclaw/skills/tmux/` | ✅ |
| weather | `~/openclaw/skills/weather/` | ✅ |
| 自定义技能 | `~/.openclaw/workspace/skills/` | ✅ |

### 增强计划

| 技能 | 描述 | 优先级 |
|------|------|--------|
| `coin-hour` | Coin Hour 管理/结算/查询 | 🔴 高 |
| `naye-village` | 那耶村场景专用技能 | 🔴 高 |
| `avatar-nft` | Avatar 语料资产管理 | 🟡 中 |
| `trade-net` | 交易网络操作 | 🟡 中 |
| `compute-bank` | 算力银行接口 | 🟡 中 |

### 技能结构规范

```
skill-name/
├── SKILL.md              # 技能描述（描述匹配用）
├── scripts/              # 可执行脚本
├── references/           # 参考资料
└── templates/            # 模板文件
```

---

## 第三层：钩子层 (HOOKS)

### 功能定位
**生命周期拦截，工具调用前后处理**

### 钩子类型

| 钩子 | 触发时机 | 用途 |
|------|----------|------|
| `PreToolUse` | 工具调用前 | 权限检查、参数验证 |
| `PostToolUse` | 工具调用后 | 结果处理、日志记录 |
| `PreSession` | 会话开始前 | 加载上下文、初始化 |
| `PostSession` | 会话结束后 | 保存状态、清理资源 |
| `OnError` | 错误发生时 | 错误处理、重试逻辑 |
| `OnApproval` | 需要审批时 | 通知用户、等待确认 |

### 当前实现

| 钩子 | 状态 | 说明 |
|------|------|------|
| 内存检索 | ✅ | `memory_search` 在回答前自动调用 |
| 技能匹配 | ✅ | 根据描述自动选择技能 |
| 审批流程 | ✅ | 敏感操作需要用户确认 |

### 增强计划

| 钩子 | 描述 | 优先级 |
|------|------|--------|
| `CoinHourTracker` | 记录每次调用的 token 成本 | 🔴 高 |
| `AuditLogger` | 操作审计日志 | 🟡 中 |
| `RateLimiter` | API 调用频率限制 | 🟡 中 |
| `DataSovereignty` | 数据流出拦截（AIX 核心安全） | 🔴 高 |

---

## 第四层：智能体组件层 (COMPONENTS)

### 功能定位
**多智能体协作，委员会/审查/测试**

### 组件类型

| 组件 | 功能 | 描述 |
|------|------|------|
| **委员会派** | 多Agent协作 | 多个专家Agent并行处理 |
| **审查委员** | 质量把关 | 输出审核、安全检查 |
| **测试运行器** | 验证能力 | 自动化测试、回归验证 |
| **调度器** | 任务编排 | 任务队列、优先级管理 |
| **监控器** | 状态追踪 | 实时监控、告警通知 |

### 当前实现

| 组件 | 状态 | 说明 |
|------|------|------|
| Sub-agents | ✅ | OpenClaw 支持子智能体 |
| Session 管理 | ✅ | 多会话并行 |
| 背景任务 | ✅ | 后台执行长任务 |

### 增强计划

| 组件 | 描述 | 优先级 |
|------|------|--------|
| `ReviewAgent` | 输出审核Agent（检查敏感信息） | 🔴 高 |
| `TestRunner` | 自动化测试（技能回归测试） | 🟡 中 |
| `CoinHourAccountant` | 成本核算Agent | 🔴 高 |
| `NayeVillageCoordinator` | 那耶村场景协调器 | 🟡 中 |

---

## 第五层：插件层 (PLUGINS)

### 功能定位
**扩展包管理，技能/智能体打包分发**

### 插件结构

```
plugin-name/
├── skills/              # 包含的技能
├── agents/              # 包含的智能体
├── hooks/               # 包含的钩子
├── config/               # 配置文件
├── manifest.json        # 插件清单
└── README.md            # 说明文档
```

### 当前实现

| 插件 | 状态 | 说明 |
|------|------|------|
| AIX Skills | 🟡 | 规划中，部分技能已实现 |
| ClawHub | ✅ | 技能市场已上线 |

### 增强计划

| 插件 | 描述 | 优先级 |
|------|------|--------|
| `aix-core` | AIX 核心技能包 | 🔴 高 |
| `naye-village-bundle` | 那耶村场景完整包 | 🔴 高 |
| `compute-bank-plugin` | 算力银行对接插件 | 🟡 中 |
| `avatar-marketplace` | Avatar NFT 市场插件 | 🟢 低 |

---

## 与 AIX 项目的对接

### 数据主权保障

```
第一层（记忆）→ AIX Box 本地存储
第二层（技能）→ 本地 Skills + 云端补充
第三层（钩子）→ 数据流出拦截
第四层（组件）→ 多Agent本地协作
第五层（插件）→ ClawHub + 自建市场
```

### Coin Hour 结算

```
每次工具调用 → 钩子记录成本
                ↓
        累计到 CoinHourAccountant
                ↓
        定期结算（那耶村内循环）
```

### 硬件层（负一层）

```
Mac mini M4 = 推理中枢（本地7B-13B模型）
AIX Box = 边缘节点（UTXO账本 + 硬件钱包）
```

---

## 实施路线图

### Phase 1: 记忆层完善（1周）

- [ ] 创建 `CLAUDE.md` 全局指令
- [ ] 整理 `knowledge/` 结构
- [ ] 建立归档机制

### Phase 2: 技能层扩展（2周）

- [ ] 创建 `coin-hour` 技能
- [ ] 创建 `naye-village` 技能
- [ ] 技能自动化测试

### Phase 3: 钩子层增强（1周）

- [ ] 实现 `CoinHourTracker` 钩子
- [ ] 实现 `DataSovereignty` 拦截器

### Phase 4: 组件层建设（2周）

- [ ] 实现 `ReviewAgent`
- [ ] 实现 `CoinHourAccountant`

### Phase 5: 插件层发布（1周）

- [ ] 打包 `aix-core` 插件
- [ ] 发布到 ClawHub

---

## 文档架构规则

### 命名规范

- `MEMORY.md` - 长期记忆（索引式）
- `memory/YYYY-MM-DD.md` - 每日笔记
- `knowledge/topic-name.md` - 专题知识
- `skills/skill-name/SKILL.md` - 技能描述

### 测试要求

- 每个技能必须有 `scripts/test.sh`
- 钩子必须有单元测试
- 插件发布前需要集成测试

---

*创建时间：2026-05-14*
*来源：用户分享的 CLAUDE 智能体开发工具包架构图*
