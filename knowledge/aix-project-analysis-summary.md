# AIX项目关联分析汇总

> 2026-05-09 讨论的所有开源项目完整分析
> 最后更新：2026-05-10

---

## 项目总览表（14个项目）

| # | 项目名称 | Stars | GitHub地址 | AIX关联度 | 核心用途 |
|---|---------|-------|-----------|----------|---------|
| 1 | Browser Harness | 11717 | github.com/browser-use/browser-harness | ⭐⭐⭐⭐⭐ | 软件层Harness标杆 |
| 2 | Composio | - | composio.dev | ⭐⭐⭐⭐⭐ | 800+工具连接器 |
| 3 | Tavily | - | tavily.com | ⭐⭐⭐⭐⭐ | AI专用搜索 |
| 4 | Playwright-MCP | - | - | ⭐⭐⭐⭐ | 网页确定性执行 |
| 5 | Self-Improving | - | - | ⭐⭐⭐⭐⭐ | Agent自进化核心 |
| 6 | ms-swift | 14042 | github.com/modelscope/ms-swift | ⭐⭐⭐⭐⭐ | 600+模型训练框架 |
| 7 | deep-comedy-pro | - | github.com/yuanzhongqiao/deep-comedy-pro | ⭐⭐⭐⭐⭐ | AI短剧全链路 |
| 8 | EverOS | 4511 | github.com/EverMind-AI/EverOS | ⭐⭐⭐⭐⭐ | 自进化Agent记忆OS |
| 9 | Arnis | 15496 | github.com/louis-e/arnis | ⭐⭐⭐⭐⭐ | 真实地理→Minecraft |
| 10 | Memvid | 15372 | github.com/memvid/memvid | ⭐⭐⭐⭐⭐ | 单文件记忆层 |
| 11 | Rowboat | 13520 | github.com/rowboatlabs/rowboat | ⭐⭐⭐⭐⭐ | YC验证的一人公司Agent |
| 12 | Skills Manager | 641 | github.com/jiweiyeah/Skills-Manager | ⭐⭐⭐⭐⭐ | 跨平台技能同步 |
| 13 | Feynman | 6948 | github.com/getcompanion-ai/feynman | ⭐⭐⭐⭐ | 四智能体Deep Research |
| 14 | Awareness-Local | 217 | github.com/edwin-hao-ai/Awareness-Local | ⭐⭐⭐⭐⭐ | OpenClaw原生记忆 |
| 15 | Skill Graphs 2.0 | - | x.com/shivsakhuja (方法论) | ⭐⭐⭐⭐⭐ | 技能分层设计框架 |
| 16 | cmux | - | github.com/manifoldai/cmux | ⭐⭐⭐⭐ | Agent多并行工作台 |

---

## 分类汇总

### 记忆层（5个方案）

| 项目 | Stars | 特点 | 选择建议 |
|------|-------|------|---------|
| **Awareness-Local** | 217 | OpenClaw原生，一行安装 | **首选** |
| EverOS | 4511 | 企业级完整系统，自进化 | 企业场景 |
| Memvid | 15372 | 单文件便携，0.025ms检索 | 备份/边缘设备 |
| Graphify | 39436 | 知识图谱，71.5x降成本 | 结构化知识 |
| Rowboat | 13520 | Obsidian vault，人机共用 | 参考实现 |

### 工具层（6个核心）

| 类别 | 项目 | Stars | 一人公司用途 |
|------|------|-------|------------|
| 搜索 | Tavily | - | 信息摄入器官 |
| API连接 | Composio | - | 万能接口中台 |
| 浏览器 | Browser Harness | 11717 | Self-healing探索 |
| 浏览器 | Playwright-MCP | - | 确定性稳定执行 |
| 内容生成 | deep-comedy-pro | - | 短剧全链路 |
| 元宇宙 | Arnis | 15496 | 真实地理复刻 |

### 训练层（3个方案）

| 项目 | Stars | 特点 | 用途 |
|------|-------|------|------|
| MiniMind | 48673 | 2小时64M模型 | 快速原型 |
| ms-swift | 14042 | 600+模型，GRPO | 生产级训练 |
| ML Intern | 7847 | 自动化训练智能体 | 无ML专家训练 |

### 技能管理层（2个）

| 项目 | Stars | 特点 |
|------|-------|------|
| Skills Manager | 641 | 跨平台同步，写一次全平台用 |
| Skill Graphs 2.0 | 方法论 | 原子→分子→复合，100x杠杆 |

### Agent运行时/工作台（3个）

| 项目 | Stars | 特点 |
|------|-------|------|
| OpenClaw | - | 官方运行时 |
| OpenOcta | 2504 | 中国企业优化版 |
| cmux | - | macOS多Agent并行工作台 |

### 参考实现（2个）

| 项目 | Stars | 特点 |
|------|-------|------|
| Rowboat | 13520 | YC S24，一人公司Agent原型 |
| Feynman | 6948 | 四智能体Deep Research模式 |

---

## 每个项目与AIX的具体关联

### 1. Browser Harness（11717 stars）

**关联**：
- 软件层Harness标杆，验证"LLM打工，代码做主"理念
- 和AIX Box硬件层治理互补
- 可纳入一人公司Agent技术栈作为浏览器自动化组件

**应用场景**：
- 客服Agent在网页上回复
- 内容Agent发布到各平台
- 数据Agent爬取信息

**Coin Hour定价**：10-50 CH/任务

---

### 2. Composio（800+工具）

**关联**：
- 一人公司Agent的"API中台"
- 统一接口连接飞书/钉钉/微信/银行API

**应用场景**：
- 客服Agent → 飞书/企业微信
- 财务Agent → 用友/金蝶/银行API
- 营销Agent → 微信公众号/抖音

**Coin Hour定价**：1-5 CH/任务

---

### 3. Tavily（AI专用搜索）

**关联**：
- 一人公司Agent的"信息摄入器官"
- 直接返回结构化答案，不是链接列表

**应用场景**：
- 市场调研Agent → 行业报告
- 竞品分析Agent → 实时监控
- 新闻Agent → 每日摘要

**Coin Hour定价**：0.5-2 CH/搜索

---

### 4. ms-swift（14042 stars）

**关联**：
- AIX一人公司Agent的本地训练→部署完整链路
- Mac MPS支持，Mac mini M4可直接训练
- GRPO强化学习，Agent技能优化

**应用场景**：
- 那耶村专属模型训练（方言/行业术语）
- Agent技能强化学习
- Agentic RL训练（多轮工具调用）

**Coin Hour定价**：20-100 CH/训练任务

---

### 5. deep-comedy-pro

**关联**：
- AIX一人公司内容Agent的核心工具
- MIT协议可商用
- 本地部署符合数据主权理念

**应用场景**：
- 那耶村短剧生成（梯田文化/民宿故事）
- Coin Hour结算创作者收益
- 一人公司品牌宣传

**Coin Hour定价**：10-50 CH/部

**待确认**：硬件要求、模型协议

---

### 6. EverOS（4511 stars）

**关联**：
- AIX一人公司Agent的"记忆大脑"
- 提供长期记忆OS、自进化评估、记忆治理框架

**应用场景**：
- Agent长期记忆管理
- EvoAgentBench自进化评估
- 和Graphify/Avatar NFT/Coin Hour/AIX Box形成闭环

**Coin Hour定价**：记忆治理服务

---

### 7. Arnis（15496 stars）

**关联**：
- AIX那耶村元宇宙沙盘的"地理引擎"
- OpenStreetMap真实数据生成梯田Minecraft世界
- Apache 2.0可商用

**应用场景**：
- 那耶村梯田数字孪生
- 游客虚拟探索→实体转化
- AIX Box本地托管私有元宇宙

**Coin Hour定价**：
- 虚拟梯田入场：10 CH
- 导览NPC服务：5 CH

---

### 8. Memvid（15372 stars）

**关联**：
- AIX一人公司Agent的"轻量记忆文件"
- 单文件、无数据库、0.025ms检索
- 完美适配AIX Box边缘设备

**应用场景**：
- 一人公司Agent轻量记忆
- AIX Box边缘记忆
- Avatar NFT记忆载体（.mv2文件）

**Coin Hour定价**：记忆存储服务

---

### 9. Rowboat（13520 stars）

**关联**：
- 一人公司Agent的YC验证参考实现
- 本地运行、Obsidian知识图谱、全语音交互

**学习点**：
- Obsidian vault作为人机共用透明记忆载体
- Deepgram/ElevenLabs语音闭环
- Composio工具集成模式

**Coin Hour定价**：参考其定价模式

---

### 10. Skills Manager（641 stars）

**关联**：
- 一人公司Agent的"技能中台"
- 写一次，全平台同步，节省80%维护时间

**应用场景**：
- 统一管理一人公司10大能力技能
- 那耶村专属技能库
- DAO成员技能共享（Community Hub）

**Coin Hour定价**：
- 基础技能：免费
- 那耶村专属：10-20 CH

---

### 11. Feynman（6948 stars）

**关联**：
- Deep Research四智能体协作参考实现
- 找论文→挑问题→写报告→核引用

**学习点**：
- 四智能体分工模式可迁移到一人公司Agent
- 复杂任务自动分解架构
- 引用追溯和UTXO理念一致

**Coin Hour定价**：50-100 CH/调研报告

---

### 12. Awareness-Local（217 stars）

**关联**：
- **OpenClaw Agent官方记忆插件**
- 一行安装，本地优先，95.6%基准第一梯队

**核心优势**：
- 原生支持OpenClaw ✅
- 无需云端 ✅
- 零LLM推理成本 ✅

**应用场景**：
- OpenClaw Agent记忆层首选
- 那耶村知识库本地存储

**安装**：`npx @awareness-sdk/setup`

---

### 13. Skill Graphs 2.0（方法论）

**关联**：
- 一人公司Agent技能分层设计方法论
- 原子→分子→复合三层，系统级杠杆100x

**公式**：
```
杠杆 = 原子任务复用次数 × 组合路径数
```

**应用场景**：
- 一人公司10大能力拆解
- Coin Hour定价梯度设计
- Skills Manager原子任务库

---

### 14. cmux

**关联**：
- AIX一人公司Agent的"多Agent并行工作台"
- 智能通知环、垂直标签、内置浏览器

**应用场景**：
- 10个Agent同时跑，状态一目了然
- Browser Harness网页操作可视化
- Coin Hour状态扩展通知环

---

## 那耶村MVP应用组合

### 梯田导览Agent

| 层级 | 工具 | 用途 |
|------|------|------|
| 记忆 | Awareness-Local | 梯田知识库 |
| 地理 | Arnis | Minecraft虚拟梯田 |
| 语音 | ElevenLabs | 方言讲解 |
| 记忆辅助 | Graphify | 景点关系图谱 |

**Coin Hour**：50-100 CH/全程导览

### 短剧生成Agent

| 层级 | 工具 | 用途 |
|------|------|------|
| 内容 | deep-comedy-pro | 短剧生成 |
| 发布 | Browser Harness | 自动发布抖音/快手 |
| 记忆 | Rowboat模式 | 知识图谱记忆 |

**Coin Hour**：100-200 CH/短剧制作

### 一人公司Agent完整栈

| 层级 | 工具 |
|------|------|
| 工作台 | cmux |
| 运行时 | OpenClaw Agent |
| 技能管理 | Skills Manager |
| 记忆 | Awareness-Local |
| 工具 | Composio + Tavily + Browser Harness |
| 训练 | ms-swift + MiniMind |
| 硬件 | AIX Box + Mac mini M4 |

---

## 行动优先级

### P0（立即执行）

1. 安装Awareness-Local：`npx @awareness-sdk/setup`
2. 安装Skills Manager：统一管理技能
3. 安装cmux：macOS多Agent工作台

### P1（1周内）

1. 创建50个核心原子任务库
2. 训练那耶村方言MiniMind模型
3. Arnis生成那耶村Minecraft世界

### P2（1月内）

1. 完整实现10大能力复合任务
2. Coin Hour计费系统对接
3. 那耶村实地部署测试

---

## 总Stars统计

| 类别 | Stars总和 |
|------|----------|
| 记忆层 | ~58,000 |
| 工具层 | ~27,000 |
| 训练层 | ~63,000 |
| 技能管理 | ~641 |
| 运行时/工作台 | ~2,500 |

**总计**：~150,000+ stars（所有开源项目）

---

*最后更新：2026-05-10*

---

### 17. OPC方法论（15488 stars）

**GitHub**：github.com/easychen/opc-methodology
**官网**：opc-skills.ft07.com

**定位**：《一人企业方法论》的可执行Agent版本

| 特性 | 说明 |
|------|------|
| Stars | 15488 |
| Skills数量 | 9个Agent Skills |
| 核心价值 | 从资源盘点到转化闭环完整流程 |
| 案例 | 设计师林夏3000底薪→副业稳定闭环 |

**9个Agent Skills**：

| # | Skill | 功能 | AIX对应 |
|---|-------|------|---------|
| 01 | opc-resource-audit | 资源盘点（8类别） | 创始人能力盘点 |
| 02 | opc-niche-positioning | 利基定位（三环叠加） | 那耶村赛道选择 |
| 03 | opc-value-proposition | 价值主张 | Coin Hour价值设计 |
| 04 | opc-business-model-design | 商业模式（Lean Canvas） | AIX经济闭环 |
| 06 | opc-mvp-designer | MVP设计 | 那耶村MVP验证 |
| 07 | opc-conversion-loop | 转化闭环 | Coin Hour转化 |
| 08 | opc-asset-ops | 资产沉淀 | Avatar NFT资产化 |
| 09 | opc-dashboard-review | 经营复盘 | Self-Improving |
| orchestrator | opc-orchestrator | 总编排 | Agent流程编排 |

**资源盘点8类别**：

| 类别 | 内容 | 那耶村应用 |
|------|------|----------|
| 经验资源 | 行业经验 | 梯田运营经验 |
| 人群资源 | 最懂哪类人 | 懂游客/民宿客群 |
| 能力资源 | 专业能力 | 数字化运营能力 |
| 关系资源 | 客户关系 | 村民网络、游客关系 |
| 渠道资源 | 社交账号 | 微信公众号、抖音 |
| 资产资源 | 案例、素材 | 梯田照片、民宿案例 |
| 约束资源 | 时间、现金流 | 季节性约束 |
| 硬性边界 | 不能碰的事 | 数据不上云 |

**流程架构**：

```
建盘期（线性）
├── 战略层：01→02→03→04
└── 验证层：06→07

运营循环（可触发）
├── 08 资产沉淀
└── 09 经营复盘
```

**关键原则**：
- 阶段边界严格管控（不越界）
- 对话先行、文件随后
- 一次只问一个问题
- 给3个备选方案+自定义

**Coin Hour定价**：

| OPC服务 | Coin Hour |
|---------|----------|
| 资源盘点 | 50 CH |
| 利基定位 | 100 CH |
| 商业模式设计 | 150 CH |
| MVP验证辅导 | 200 CH |
| 经营复盘 | 80 CH |

**一句话**：OPC方法论是AIX一人公司Agent的"业务流程方法论"，和Skill Graphs（技能分层）形成"方法论+技术栈"闭环。

---

### 18. PersonaVLM（95 stars）

**GitHub**：github.com/MiG-NJU/PersonaVLM
**会议**：CVPR 2026 Highlight
**团队**：南京大学 + 字节跳动

**定位**：长期个性化多模态LLM

| 特性 | 说明 |
|------|------|
| Stars | 95 |
| 基座模型 | Qwen2.5-VL |
| 基准 | Persona-MME超GPT-4o 5.2% |
| 核心能力 | Remembering + Reasoning + Response Alignment |

**四种记忆类型**：

| 记忆类型 | 内容 | AIX应用 |
|---------|------|---------|
| Core Memory | 用户核心特征 | Avatar NFT身份 |
| Semantic Memory | 知识、概念 | Graphify知识图谱 |
| Episodic Memory | 具体事件 | Awareness-Local历史 |
| Procedural Memory | 技能、流程 | Skills Manager技能 |

**PEM机制**：Momentum-based Personality Evolving Mechanism
- 动态推断用户最新潜在特征
- 确保响应与用户演化特征对齐

**那耶村应用**：
- 游客个性化导览（记住偏好）
- 民宿回头客识别（入住历史）
- 短剧内容个性化推荐

**一句话**：PersonaVLM是AIX的"个性化大脑"，四类型记忆+PEM性格演化，不只是存储，而是理解用户。

---

## 今日分析项目汇总（18个）

| # | 项目 | Stars | AIX关联度 |
|---|------|-------|----------|
| 1 | Browser Harness | 11717 | ⭐⭐⭐⭐⭐ |
| 2 | Composio | - | ⭐⭐⭐⭐⭐ |
| 3 | Tavily | - | ⭐⭐⭐⭐⭐ |
| 4 | Playwright-MCP | - | ⭐⭐⭐⭐ |
| 5 | Self-Improving | - | ⭐⭐⭐⭐⭐ |
| 6 | ms-swift | 14042 | ⭐⭐⭐⭐⭐ |
| 7 | deep-comedy-pro | - | ⭐⭐⭐⭐⭐ |
| 8 | EverOS | 4511 | ⭐⭐⭐⭐⭐ |
| 9 | Arnis | 15496 | ⭐⭐⭐⭐⭐ |
| 10 | Memvid | 15372 | ⭐⭐⭐⭐⭐ |
| 11 | Rowboat | 13520 | ⭐⭐⭐⭐⭐ |
| 12 | Skills Manager | 641 | ⭐⭐⭐⭐⭐ |
| 13 | Feynman | 6948 | ⭐⭐⭐⭐ |
| 14 | Awareness-Local | 217 | ⭐⭐⭐⭐⭐ |
| 15 | Skill Graphs 2.0 | 方法论 | ⭐⭐⭐⭐⭐ |
| 16 | cmux | - | ⭐⭐⭐⭐ |
| 17 | OPC方法论 | 15488 | ⭐⭐⭐⭐⭐ |
| 18 | PersonaVLM | 95 | ⭐⭐⭐⭐⭐ |

**总Stars**：~150,000+


---

### 19. Ruflo（47880 stars）

**GitHub**：github.com/ruvnet/ruflo
**官网**：flo.ruv.io, goal.ruv.io

**定位**：Multi-agent AI orchestration for Claude Code

| 特性 | 说明 |
|------|------|
| Stars | 47880 |
| Agents数量 | 100+ specialized agents |
| Plugins | 32 native plugins |
| 核心能力 | Swarm coordination + Self-learning + RAG + Federation |

**核心架构**：

```
User → Ruflo (CLI/MCP) → Router → Swarm → Agents → Memory → LLM Providers
                          ^                           |
                          +---- Learning Loop <-------+
```

**32个Plugins分类**：

| 类别 | Plugins |
|------|---------|
| **Core & Orchestration** | ruflo-core, ruflo-swarm, ruflo-autopilot, ruflo-federation |
| **Memory & Knowledge** | ruflo-agentdb, ruflo-rag-memory, ruflo-ruvector, ruflo-knowledge-graph |
| **Intelligence & Learning** | ruflo-intelligence, ruflo-daa, ruflo-ruvllm, ruflo-goals |
| **Code Quality** | ruflo-testgen, ruflo-browser, ruflo-jujutsu, ruflo-docs |
| **Security** | ruflo-security-audit, ruflo-aidefence |
| **Architecture** | ruflo-adr, ruflo-ddd, ruflo-sparc |
| **DevOps** | ruflo-migrations, ruflo-observability, ruflo-cost-tracker |
| **Domain** | ruflo-iot-cognitum, ruflo-neural-trader, ruflo-market-data |

**关键特性**：

| 特性 | AIX关联 |
|------|--------|
| **Self-Learning** | ✅ 对应Self-Improving机制 |
| **Swarm Coordination** | ✅ 对应Agent Teams架构 |
| **Vector Memory (AgentDB)** | ✅ 对应Awareness-Local/Memvid |
| **Plugin Marketplace** | ✅ 对应Skills Manager |
| **Federation（跨机器协作）** | ✅ 对应AIX Box分布式架构 |
| **MCP Server** | ✅ 标准协议，OpenClaw兼容 |

**安装方式**：

```bash
# Claude Code Plugin（轻量）
/plugin install ruflo-core@ruflo
/plugin install ruflo-swarm@ruflo

# CLI完整安装（生产）
npx ruflo@latest init

# MCP Server
claude mcp add ruflo -- npx ruflo@latest mcp start
```

**一句话**：Ruflo是Multi-Agent编排的生产级实现，47,880 stars验证，100+ agents + 32 plugins + Self-learning + Federation，是AIX一人公司Agent编排的参考实现和技术基础。


---

### 20. SkillClaw（1267 stars）

**GitHub**：github.com/AMAP-ML/SkillClaw
**开发者**：高德地图（AMAP-ML）
**论文**：arXiv 2604.08377

**定位**：Let Skills Evolve Collectively with Agentic Evolver

| 特性 | 说明 |
|------|------|
| Stars | 1267 |
| 开发者 | **高德地图（阿里系）** |
| 核心能力 | 跨Agent/设备技能共享与自动优化 |
| 支持框架 | Hermes, **OpenClaw**, Codex, Claude Code, QwenPaw, IronClaw, PicoClaw... |
| License | MIT |

**核心架构**：

```
两组件架构：
├── Client Proxy（本地代理）
│   ├── 拦截请求
│   ├── 记录会话
│   └── 管理本地技能库
└── Evolve Server（进化服务器）
    ├── workflow引擎（3阶段LLM管道）
    └── agent引擎（OpenClaw驱动）
```

**核心价值**：

| 能力 | AIX对应 |
|------|--------|
| **集体技能进化** | ✅ Self-Improving的社区版 |
| **跨Agent共享** | ✅ Skills Manager的升级版 |
| **跨设备同步** | ✅ AIX Box分布式技能共享 |
| **自动去重优化** | ✅ 解决技能碎片化问题 |
| **OpenClaw原生支持** | ✅ 直接整合 |

**支持的Agent框架**：

| 框架 | 状态 |
|------|------|
| Hermes | ✅ 支持 |
| **OpenClaw** | ✅ **原生支持** |
| Codex | ✅ 支持 |
| Claude Code | ✅ 支持 |
| QwenPaw | ✅ 支持 |
| IronClaw | ✅ 支持 |
| PicoClaw | ✅ 支持 |

**关键特性**：

1. **Just Chat**：技能进化在后台自动发生，零额外努力
2. **跨Agent共享**：多个Agent统一技能库
3. **跨设备同步**：家里/学校/公司技能统一
4. **团队共享**：N用户，一个Skill，持续进化

**一句话**：SkillClaw是高德地图开源的技能集体进化框架，原生支持OpenClaw，实现跨Agent/设备技能共享与自动优化，是AIX Skills生态的核心基础设施。

