# MEMORY.md - 长期记忆（精简版）

> 最后更新：2026-05-14 | 已清理：归档旧日志，详细分析移至knowledge/

---

## 👤 关于Jane

- AIX项目创始人
- 时区：中国（UTC+8）
- 飞书User ID：ou_0f69829f208490a428d5cdede9e508bc
- 主要沟通平台：飞书

## 🏗️ AIX项目

### 核心理念（一句话）
**"LLM打工，代码做主"** + 数据主权 + Coin Hour内循环

### 关键产品
- AIX Box（边缘节点：硬件钱包+分布式计算+存储+广告）
- Coin Hour（算法稳定币，锚定1元人民币）
- UTXO无共识账本 + Avatar NFT

### 硬件生态
- Mac mini M4 = 推理中枢（7B-13B本地模型）
- AIX Box = 边缘执行节点 + 经济主权载体

### 经济闭环
```
囤AIX → 产出Coin Hour → 那耶村消费 → 不需要法币
持有 = 免费AI推理 + 稳定产出 + 资本增值
```

## 📅 关键时间线

| 日期 | 事件 |
|------|------|
| 2026-04-18 | Jane确认我为私人助理，开始建立知识库 |
| 2026-05-01 | 技术栈九层架构完整版 |
| 2026-05-14 | 清理MEMORY.md，归档旧日志 |

## 💡 核心洞察索引
- `cli-anything.md` - GUI→CLI转换（34K星，18+款软件）
- `claude-mem.md` - 跨会话持久记忆（75K星，节省95% Token）✅与TencentDB互补
- `unividx-video-generation.md` - 统一多模态视频生成（SIGGRAPH 2026）
- `tencentdb-agent-memory.md` - Agent分层记忆系统（Token降61%）✅建议立即安装

详细分析已移至 `knowledge/` 目录：

- `aix-competitive-analysis.md` - Mac Studio/TsingWin/QoderWake对比
- `aix-one-person-agent-tech-stack.md` - 一人公司技术栈
- `aix-multi-agent-orchestration.md` - Agent编排设计
- `aix-agent-error-handling.md` - 工具失败处理机制
- `aix-hayek-perspective.md` - 哈耶克视角分析

## 🔧 一人公司Agent技术栈（九层）

```
第八层：应用层（Rowboat/OCT-Agent + OfficeCLI）
第七层：营销层（AiToEarn）
第六层：Agent编排层（PraisonAI + ProactiveAgent）
第五层：技能管理层（Skills Manager + Agent Skills）
第四层：Agent运行时层（OpenClaw/OpenOcta）
第三层：工作流层（Skill Graphs 2.0）
第二层：工具层（Tavily/Composio/SourcingGPT等）
第一层：记忆层（Awareness-Local/Graphify等）
第零层：训练层（MiniMind/ms-swift/ML Intern）
负一层：硬件治理层（AIX Box + Mac mini M4）
```

## 🌟 那耶村MVP

- 数字主权宣言已完成
- Coin Hour真实消费场景（吃喝拉撒）
- 云海素材已存档（knowledge/naye-village/media-assets.md）

## ⚠️ 紧迫窗口

- Naval预言"18个月"
- TsingWin二代5月14日发布
- 那耶村MVP需快速验证

## 👥 关键人物

- 刘威（ou_9a5a03d4a7e8838781f747a4c2e51141）：AIX Box原型开发者

---

*维护原则：MEMORY.md只保留索引，详细内容移至knowledge/*

## 🆕 新增项目索引（2026-05-14）

- `mtp-lookahead-decoding.md` - 并行推理加速（40%提速）
- `exo-distributed-inference.md` - Mac集群分布式推理
- `praisonai-agent-orchestration.md` - Agent编排框架
- `paperclip-agent-orchestration.md` - Agent编排层（公司治理）

## 📐 智能体架构（2026-05-14 新增）

### 五层架构

```
第五层：插件层 (PLUGINS) - 扩展包管理
第四层：组件层 (COMPONENTS) - 多Agent协作
第三层：钩子层 (HOOKS) - 生命周期拦截
第二层：技能层 (SKILLS) - 能力模块化
第一层：记忆层 (MEMORY) - 持久化知识
```

详见：`knowledge/aix-agent-five-layer-architecture.md`

### 全局指令

- `CLAUDE.md` - 全局行为配置（2026-05-14 创建）

### 增强计划

| 组件 | 状态 |
|------|------|
| `coin-hour` 技能 | 待建 |
| `naye-village` 技能 | 待建 |
| `CoinHourTracker` 钩子 | 待建 |
| `ReviewAgent` 组件 | 待建 |
| `aix-core` 插件 | 待建 |


### AI原生开发三大转变（2026-05-15新增）
- **写代码 → 表达意图**：LLM打工，代码做主
- **静态系统 → 自演化系统**：Agent自进化框架
- **工程驱动 → 智能体协作**：多Agent编排层

**企业IT瘦身：** 5人团队 → 1人+Agent，成本降90%

### AIX园区战略（2026-05-15新增）
- 定位：AI原生基础设施 + 数字主权经济实验场
- 收入：30%租金 + 30%Coin Hour + 20%Token + 20%服务
- 复制：那耶村MVP x 园区规模 x 企业密度

## 🧠 记忆引擎（2026-05-18新增）

### AgentMemory.dev
- `knowledge/agentmemory-dev-analysis.md` - 专为Coding Agent设计的持久记忆引擎
- Stars：12,018 | 检索准确率：95.2% | Token降92%
- ✅ OpenClaw原生支持 | ✅ 零外部依赖 | ✅ 12个自动Hooks
- 与AIX Box本地存储理念完全一致，即用


### 个人AI工作台（2026-05-18新增）
- `knowledge/personal-ai-workbench-18-actions.md` - 若飞《用好Claude的18个动作》
- 六层架构：工作区→身份→任务入口→输出标准→上下文治理→反馈回路
- 18个动作形成闭环：事实源→行为契约→任务入口→验收标准→复盘更新
- ✅ 与AIX九层架构完全对应
- 核心理念：**环境工程 > 提示词工程**

## 🌾 那耶村经济发展策略（2026-05-19 新增）

详见：`knowledge/naye-village-economy-strategy.md`

### 三层经济架构

```
基础经济层：农业 + AIX Box数据采集 + 团长带货
增量经济层：安缦式酒店 + 音乐节 + 电影节（线上+线下）
杠杆经济层：AI村（学AI创作）+ AI创业创新大赛 + 项目路演
```

### 核心定位

**那耶村 = AI原生乡村实验场**

### 人群与经济流动

- 创作者：学费/消费 → AI技能/NFT收入
- 投资者：投资/住宿 → 项目股权/回报
- 消费者：购买农产品 → 溯源产品
- 本地村民：劳动/数据采集 → Coin Hour收入

### 发展三阶段

| Phase | 时间 | 里程碑 |
|-------|------|--------|
| 验证期 | 0-6月 | AIX Box部署、团长试运行、首期AI工坊 |
| 增长期 | 6-18月 | 酒店运营、音乐节/电影节、创业大赛 |
| 复制期 | 18月+ | 标准化输出、第二村落、全球AI村网络 |


### AI漫剧电影平台（2026-05-20 新增）

**内容来源**：村长梁越的书作为原创IP

**变现方式**：
- AIX Box内置广告点击赚钱
- 平台广告分成（每万次10-40元）
- Coin Hour付费观看
- 品牌定制合作
- IP衍生（Avatar NFT）
- 出海分发

**创作者吸引**：来村里和村长一起做，驻村共创

**策略**：用村长的书降低内容风险，用AI工具降低成本，靠量取胜（100部短剧 → 1-2部爆款）


### 投资结构（2026-05-20 新增）

**那耶村AI漫剧电影平台由AIX基金会投资**

治理架构：
- 基金会：资金注入 + IP授权管理 + Coin Hour发行
- 村集体：土地入股 → Coin Hour分红
- 村长梁越：IP授权 → Coin Hour分成
- 创作者：驻村共创 → 作品分成
- 本地村民：服务劳动 → Coin Hour工资


### AIX漫剧电影AI创作平台架构（2026-05-20 新增）

详见：`knowledge/aix-manga-movie-platform-architecture.md`

**核心定位**：本地化部署的AI漫剧电影工厂，Coin Hour结算，数据主权归属创作者

**技术栈**：
- 编排引擎：ViMax（15个Agent）
- 本地推理：AIX Box + Ollama（7B-13B）
- 云端溢出：Runway/Pika/OpenAI API
- 结算工具：Coin Hour + UTXO账本
- IP确权：Avatar NFT

**算力分配**：
- 剧本/校验：本地优先
- 图像/视频：云端溢出
- Coin Hour按消耗计费

**开发路径**：
- Phase 1（0-3月）：MVP + Coin Hour集成
- Phase 2（3-6月）：图像/视频生成 + 村长IP导入
- Phase 3（6-12月）：商业化 + 多村复制


### 多平台分发+多语言翻译（2026-05-20 新增）

**一键上传**：红果短剧、抖音、快手、视频号、YouTube Shorts、TikTok

**多语言翻译**：
- 中文（原生）
- 英语（全球市场）
- 俄语（俄罗斯/中亚）
- 哈萨克语（哈萨克斯坦/新疆）

**闭环**：一部漫剧 → 4种语言 → 6+平台 → 各平台结算 → UTXO汇总 → 智能分账


## 🎬 梁越IP Token商业模式（2026-05-20 新增）

详见：`knowledge/liang-yue-ip-token-model.md` + `knowledge/liang-yue-ip-works-detail.md`

### 梁越作品IP库

| 作品 | 类型 | AI改编潜力 |
|------|------|-----------|
| 《西去的使节》 | 历史小说（张骞） | ⭐⭐⭐⭐⭐ 丝路大IP |
| 《陆荣廷评传》 | 史学传记 | ⭐⭐⭐ 人物传记片 |
| 《百战名将陆荣廷》 | 史学传记 | ⭐⭐⭐⭐ 战争片 |
| 《隐没的战象》 | 长篇历史小说（50万字） | ⭐⭐⭐⭐⭐ 史诗级 |
| 《痕》 | 当代艺术展 | ⭐⭐⭐ 实验影像 |

### IP Token商业模式

```
梁越作品IP → IP Token → 出售给创作者
                            ↓
创作者购买Token → 用AIX设备+平台创作
                            ↓
作品产出 → 多平台分发 → 收益分账（创作者50% + IP池20% + 平台20% + 基金会10%）
```

### Token分类

| 类型 | 价格 | 适合人群 |
|------|------|----------|
| 单集Token | 100-500 CH | 个人创作者 |
| 系列Token | 1000-5000 CH | 工作室 |
| 全IP Token | 10000-50000 CH | 影视公司 |
| 独占Token | 面议 | 大型制作方 |

### 那耶AI影视平台

**定位**：买Token → 用设备 → 做影视 → 赺Coin Hour

**四重收益**：
1. IP Token销售（一次性）
2. 设备/平台租用（持续）
3. 作品分分成（长期）
4. AIX Box广告（被动）


### MemEye多模态记忆评估（2026-05-20 新增）
详见：`knowledge/memeye-multimodal-memory-analysis.md`

**论文**：arxiv 2605.15128 | 来源：罗格斯/圣母/普林斯顿/AMD
**核心发现**：双重瓶颈 — 文本派记不住细节（X轴），视觉派理不清时间（Y轴）
**架构建议**：混合架构 = 原生图像 + 结构化状态 + 时间感知
**AIX应用**：AIX Box记忆模块设计 + Coin Hour计费场景


### Semble代码搜索分析（2026-05-20 新增）
详见：`knowledge/semble-code-search-analysis.md`

**项目**：MinishLab/semble | Stars: 3,115 | ✅ 已部署
**核心能力**：98% Token节省（vs grep+read）| CPU运行 | MCP已集成到Hermes | 查询延迟~10ms
**对AIX帮助**：本地代码搜索 → Coding Agent优化 → 与AgentMemory.dev/RAG-Anything形成三件套


### RAG-Anything分析（2026-05-20 新增）

详见：`knowledge/rag-anything-analysis.md`

**项目**：港大DS实验室多模态RAG框架（Stars: 20,405）

**核心能力**：
- PDF/Office/图片全格式解析
- 自动提取文本、图表、表格、公式
- 跨模态知识图谱构建

**对AIX的帮助**：

| 场景 | 应用 |
|------|------|
| 梁越50万字作品解析 | 构建人物/时间线/地理知识图谱 |
| ViMax创作支撑 | 提供一致性保证的知识检索 |
| AIX Box本地部署 | 知识图谱本地存储，数据主权 |

**与ViMax协同**：同实验室项目，天然集成。知识库 → ViMax Agent调用 → 一致性保证的AI漫剧


### 音乐节策划（2026-05-20新增）

详见：`knowledge/naye-village-music-festival-plan.md`

**核心理念**：民族音乐（壮族/苗族）+ 非遗传承 + 西洋交响形式 + AI音乐制作

**AI工具选择**：
- Suno/Udio：AI编曲（10-50 CH/曲目）
- MusicGen：本地生成（AIX Box，免费）
- Stable Audio：环境音效（5-20 CH/音效）

**商业模式**：票务40% + 直播20% + NFT 15% + 赞助15% + 非遗衍生10%


## 👥 关键人物

### 顾超
- **User ID**: ou_8cbbc7b13c76a75bc1ad0e0e0aaabc3e
- **专属文件夹**: `sisi/`
- **服务定位**: 本群优先服务对象，所有文件存放在 sisi/ 文件夹

---

*更新时间: 2026-05-21 | 战略已调整*

## 🎯 战略定位调整（2026-05-21）

### 大模型市场结构性分化

**DeepSeek V4成本降至第三方云1/40**，市场非零和博弈而是增量爆发期：
- 40倍成本优势源于硬件适配+缓存机制，非价格战
- 日均token调用量两年增长千倍至140万亿
- 三大运营商9.9元套餐推动公用事业化
- 市场双层分化：成本敏感型 vs 质量优先型

### AIX战略调整

**奥卡姆剃刀：大模型竞争只剩两条路**
1. 成本压到别人做不到 ❌ AIX不选这条路
2. 质量做到别人不可替代 ✅ AIX走这条路

**云厂商做不到的四件事：**
| 能力 | AIX独占 | 云端限制 |
|------|---------|----------|
| 数据主权 | 物理级隔离，数据不出村 | 数据必须上传 |
| Coin Hour内循环 | 本地经济闭环 | 云端插不进手 |
| 硬件级治理 | 物理锁死违规操作 | 软约束可绕过 |
| 社区信任 | 看得见摸得着 | 黑箱不可信 |

**定位调整：**
```
原定位：本地推理 + 数据主权
新定位：数据主权 + 本地治理 + Coin Hour闭环
         （推理由云端DeepSeek补充，成本更低）
```

### 行动计划

| 时间 | 动作 |
|------|------|
| 7月前 | 完成DeepSeek API接口迁移 |
| 8月 | 验证"降价扩容"逻辑（那耶村MVP数据） |
| 园区招商 | 话术调整：AI时代的数字主权基础设施 |

### 新增工具评估

**Next AI Draw.io**（Stars: 29,522）
- 自然语言 → draw.io图表
- ✅ MCP Server已就绪，可集成OpenClaw
- ✅ 支持Ollama本地部署
- 应用：那耶村经济架构图、ViMax流程图、AIX九层架构图

---

### 关键人物更新

**金晶（Jessie）**
- User ID: ou_e0adf0ab5d2012fe4b87ce9d218c23aa
- 加入时间: 2026-05-21

---

*更新时间: 2026-05-21*


### 那耶村文化+金融+产业整体方案（2026-05-22新增）

**核心公式**：文化艺术 × 金融属性 × 产业生态

- 文化艺术：音乐节+电影节+夏令营+战象IP+盲盒IP
- 金融属性：Token融资+IP资产化+季度分红+二级市场
- 产业生态：院落创业+AI创作基地+Skills Store+全球发行

**第一年营收预测：1,058万元**

**Token体系**：基础500CH / 赞助5000CH / VIP 5万CH / 创始50万CH

**详细文档**：`sisi/naye-village-culture-finance-industry-master-plan.md`


### AIX DAO会员制模型（2026-05-22新增）

**核心**：付1万元 → 获得AIX Token → 每日产出Coin Hour → 那耶村消费

| 等级 | 入会费 | CH日产出 |
|------|--------|----------|
| 普通 | 1万 | 10 CH |
| 银卡 | 3万 | 30 CH |
| 金卡 | 5万 | 50 CH |
| 创始 | 10万 | 100 CH |

**三重身份**：会员+股东+消费者

**详细文档**：`sisi/aix-dao-membership-model.md`


### 夏令营Graphify实战课程（2026-05-23新增）

**7天课程**：实地采集→Graphify知识图谱→Skill封装→上架变现

**三导师**：梁越（IP）+Jane（AI）+用户377861（技术）

**安装**：`pip install graphifyy && graphify install`

**详细文档**：`files/naye-summer-camp-graphify-course-design.md`


### 夏令营定位升级：DAO精神股东（2026-05-23新增）

**核心转变**：学员→DAO成员，学费→投资，消费→分红

**10000元** = 10000 AIX Token → 每日10 CH永续产出

**权益**：分红权+投票权+收益权

**新文案**："不是花钱，是投资；不是学员，是股东"

**完整方案**：`files/naye-dao-member-summer-camp-master-plan.md`


### YourChannel案例+那耶村AI影视平台（2026-05-23新增）

**核心验证**：1人创作，72小时50万美金，创作者分成90%

**双轨制**：外循环（美金）+ 内循环（Coin Hour）

**那耶村优势**：梁越IP + 实体社区 + 导师孵化

**详细方案**：`knowledge/naye-ai-film-platform-yourchannel-analysis.md`

### 梁越《隐没的战象》创作背景（2026-05-23存档）
详见：`knowledge/liang-yue-hidden-war-elephants-creation-background.md`
- 创作时长：15年积淀+2年那耶村驻村
- 字数：50万字
- 历史背景：侬智高"特磨道"秘史（北宋壮族首领）
- 精神内核：战象隐于稻田=那文化精神
- 核心理念："艺术长在乡村"
- 那耶村定位：《隐没的战象》诞生地+侬智高历史现场

---

## 📤 文件上传工作流（2026-05-24新增）

### GitHub仓库

**仓库地址**：https://github.com/tomxyl1981/aixclaw

**上传规则**：
1. 每个飞书用户的文件存放在独立文件夹（文件夹名 = 飞书用户名）
2. 使用提供的GitHub Token进行认证
3. 文件命名：英文、小写、连字符分隔

**Token**：已存储于系统记忆

**目录结构**：
```
aixclaw/
├── 用户377861/     # 用户377861的文件
├── 顾超/           # 顾超的文件
├── 张红老师/       # 张红老师的文件
├── Jane/           # Jane的文件
└── ...
```

**操作流程**：
1. 收到飞书用户上传请求
2. 识别用户飞书名称
3. 创建/使用对应用户文件夹
4. 上传文件到GitHub
5. 返回GitHub文件链接

---

*更新时间: 2026-05-24 | 新增GitHub上传工作流*

### AIX商业模式：训练Agent作为资产（2026-05-25新增）

**核心**：训练好的Agent = 有价值观的数字资产，可复制可销售

**三层模式**：
1. 卖龙虾 — 预训练Agent，带AIX价值观，开箱即用
2. 龙虾Party — 线下定制+社区裂变
3. 参与创业 — 买Agent=买合伙人身份，Coin Hour分润

**差异化**：云厂商=通用API | AIX=有人格+立场+记忆的专属Agent

**裂变**：每个用户=活广告，龙虾Party=裂变场


### 光邮星空星地激光通信项目（2026-05-27新增）

详见：`knowledge/laserposts-business-plan-20250728-summary.md`

**公司**：北京光邮星空科技有限公司（LaserPosts）
**成立**：2024年11月
**核心技术**：
- 模式分集接收(MDR) - 全球首创
- SpaceDSP算法 - 2.5~200Gbps自适应
- 高轨+低轨双验证（国内唯一）

**团队**：
- 伍剑（董事长/首席科学家）：北邮教授，15年+星地激光通信
- 张傲（CEO）：20年+央企经验，营收超100亿

**市场**：星地激光通信，5-10年数百亿元

**对AIX的协同**：
- 边缘计算场景：解决AIX Box数据上传瓶颈
- 数字主权延伸：空天地一体化
- Coin Hour场景：遥感数据传输消费

---

*更新时间: 2026-05-27 | 新增光邮星空项目*


### 那耶村品牌定位（2026-05-27新增）

**核心理念**：吸引奇奇怪怪的人，来那耶村躲避旧世界，和同类一起建立新世界。

**目标人群**：
- 技术极客（拒绝大厂规训）
- 数字游民（拒绝平台收割）
- 艺术家（拒绝算法埋没）
- 创业者（拒绝VC绑架）
- 思考者（拒绝信息茧房）

**文案方向**：
> 来那耶村，不是逃避，是选择。
> 和一群奇奇怪怪的人，在旧世界之外，搭一个新世界。

**与AIX的呼应**：数字主权 = 拒绝被旧世界规训的权利

---

*更新时间: 2026-05-27 | 新增那耶村品牌定位*


### 机制设计理论（2026-05-27新增）

详见：`knowledge/mechanism-design-theory-maskin.md`

**来源**：Eric Maskin等2007年诺贝尔经济学奖获奖研究

**核心概念**：
- 机制设计 = 经济学的"工程学"（先定目标，再设计规则）
- 激励相容 = 让诚实成为最优策略
- Maskin单调性 = 社会目标可实现的必要条件
- 显示原理 = 简化分析的核心工具

**对那耶村的应用**：
- 三方博弈：投资人（资金）+ 操盘人（运营）+ 村集体（土地/劳动）
- 机制设计步骤：定义社会目标 → 识别私人信息 → 设计激励相容机制
- 代码化实现：UTXO账本 + 硬件治理

**核心公式**：机制设计理论 + 纳什博弈论 = 那耶村机制设计

---

*更新时间: 2026-05-27 | 新增机制设计理论*
