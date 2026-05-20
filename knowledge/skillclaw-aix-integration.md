# SkillClaw与AIX整合分析

> 高德地图开源的技能集体进化框架
> 原生支持OpenClaw
> 最后更新：2026-05-10

---

## 一、SkillClaw核心价值

### 1.1 定位

**Let Skills Evolve Collectively with Agentic Evolver**

| 维度 | 数据 |
|------|------|
| Stars | 1267 |
| 开发者 | **高德地图（AMAP-ML，阿里系）** |
| 论文 | arXiv 2604.08377 |
| License | MIT |
| 支持框架 | Hermes, OpenClaw, Codex, Claude Code, QwenPaw... |

### 1.2 核心架构

```
两组件架构：

┌─────────────────────────────────────┐
│  Client Proxy（本地代理）             │
│  ├── 拦截Agent请求                   │
│  ├── 记录会话artifacts               │
│  └── 管理本地技能库                  │
└─────────────────────────────────────┘
          ↕ Shared Storage
┌─────────────────────────────────────┐
│  Evolve Server（进化服务器）          │
│  ├── workflow引擎（3阶段LLM管道）     │
│  │   └── Summarize → Aggregate → Execute │
│  └── agent引擎（OpenClaw驱动）       │
└─────────────────────────────────────┘
```

---

## 二、集体技能进化机制

### 2.1 单用户场景

```
Hermes任务循环 + SkillClaw进化循环

用户对话 → Hermes执行任务 → SkillClaw后台进化技能
    ↑                              ↓
    └────── 下次任务更聪明 ←───────┘

关键：技能进化在后台自动发生，零额外努力
```

### 2.2 多Agent场景

```
多个Hermes Agents共享技能库：

Frontend Agent → 学习React模式 ──┐
Backend Agent → 学习API设计   ──┼→ SkillClaw统一技能库
DevOps Agent → 学习K8s配置    ──┘
                    ↓
        所有Agent共享彼此经验
```

### 2.3 多设备场景

```
同一用户，不同设备：

Home Hermes → 学习React ──┐
School Hermes → 学习ML    ──┼→ SkillClaw跨设备统一
Work Hermes → 学习K8s     ──┘
                    ↓
    技能跟随用户，不跟随机器
```

### 2.4 团队共享场景

```
N用户，一个Skill，持续进化：

User A → 调试数据库问题 → 技能进化 ──┐
User B → 受益（从未遇到此问题）     │
User C → 受益                       ├→ 团队技能库
User D → 受益                      ──┘
                ↓
    每个人的经验都让所有人受益
```

---

## 三、与AIX一人公司Agent的整合

### 3.1 替代Skills Manager？

| 维度 | Skills Manager | SkillClaw |
|------|---------------|-----------|
| 定位 | 跨平台技能同步 | 技能集体进化 |
| 进化能力 | ❌ 无 | ✅ 自动进化 |
| 去重 | ❌ 无 | ✅ 自动去重 |
| 质量优化 | ❌ 无 | ✅ 自动改进 |
| 跨设备 | ✅ 有 | ✅ 有 |
| 团队共享 | ⚠️ Community Hub计划 | ✅ 已实现 |
| OpenClaw支持 | ✅ 有 | ✅ 原生 |

**判断**：SkillClaw是**Skills Manager的升级版**，增加了进化能力。

### 3.2 与Self-Improving的关系

| Self-Improving概念 | SkillClaw实现 |
|--------------------|--------------|
| 任务执行 → 失败分析 | ✅ 会话记录 |
| 改进原子任务 | ✅ 技能进化 |
| 所有组合受益 | ✅ 集体共享 |
| 自动化程度 | ✅ 后台自动 |

**判断**：SkillClaw是**Self-Improving的技能版实现**。

### 3.3 与那耶村DAO的关系

```
那耶村DAO技能共享：

村民A → 学习梯田导览技能 → 技能进化 ──┐
村民B → 学习民宿服务技能 → 技能进化 ──┼→ 那耶村技能库
村民C → 学习美食推荐技能 → 技能进化 ──┘
                    ↓
    所有村民共享彼此经验
    Coin Hour结算技能使用
```

---

## 四、技术整合方案

### 4.1 AIX技术栈整合

```
SkillClaw（技能进化层）
    ├── 替代：Skills Manager
    ├── 增强：Self-Improving技能版
    └── 实现：DAO技能共享

    ↓ 整合到

AIX技术栈：
├── OpenClaw Agent运行时（原生支持）
├── Awareness-Local记忆层
├── Coin Hour计费
└── AIX Box硬件治理
```

### 4.2 部署架构

```
那耶村SkillClaw部署：

每个AIX Box：
├── Client Proxy（本地代理）
└── 本地技能库

云端（可选）：
├── Evolve Server（进化服务器）
├── 共享存储（OSS/S3/本地）
└── 那耶村技能库

工作流：
村民使用Agent → Client Proxy记录会话
                     ↓
              Evolve Server进化技能
                     ↓
              共享存储同步
                     ↓
              所有AIX Box获得进化技能
```

### 4.3 Coin Hour整合

```
SkillClaw技能进化 + Coin Hour结算：

技能使用 → Coin Hour消费
技能进化 → Coin Hour奖励（贡献者）
技能共享 → Coin Hour分成（DAO成员）
```

---

## 五、核心功能详解

### 5.1 自动去重

**问题**：技能库混乱，重复、过时、半成品堆积

**SkillClaw解决**：
- 自动识别重复技能
- 合并相似技能
- 清理过时技能
- 提升技能质量

### 5.2 技能进化流程

```
3阶段LLM管道（workflow引擎）：

Stage 1: Summarize
├── 读取会话记录
└── 提取关键经验

Stage 2: Aggregate
├── 合并相似经验
└── 去重优化

Stage 3: Execute
├── 生成/更新技能
└── 验证技能质量
```

### 5.3 agent引擎

**OpenClaw驱动的技能编辑**：
- 直接编辑技能文件
- 更灵活的进化方式
- 支持复杂技能逻辑

---

## 六、与高德地图的关系

### 6.1 为什么高德开源这个？

**推测**：
- 高德有大量Agent应用场景（导航、地图、出行）
- 需要跨Agent技能共享
- 阿里系的Agent生态布局

### 6.2 AIX可以学到什么？

| 高德经验 | AIX应用 |
|---------|--------|
| 大规模Agent部署 | 那耶村可扩展性 |
| 技能集体进化 | DAO技能共享机制 |
| 跨设备同步 | AIX Box分布式技能 |
| 生产级实现 | 技术架构参考 |

---

## 七、与其他工具的关系

### 7.1 vs Ruflo

| 维度 | SkillClaw | Ruflo |
|------|-----------|-------|
| 定位 | 技能进化 | Agent编排 |
| Stars | 1267 | 47880 |
| OpenClaw支持 | ✅ 原生 | ✅ 有 |
| Self-Learning | ✅ 技能版 | ✅ Agent版 |
| 团队共享 | ✅ 核心 | ⚠️ Federation |

**互补**：Ruflo编排Agent，SkillClaw进化技能。

### 7.2 vs Skills Manager

| 维度 | SkillClaw | Skills Manager |
|------|-----------|----------------|
| 定位 | 技能进化 | 技能同步 |
| 进化能力 | ✅ 有 | ❌ 无 |
| 跨平台 | ⚠️ Agent框架 | ✅ 20+ IDE |

**整合可能**：Skills Manager管理IDE同步，SkillClaw负责进化。

### 7.3 vs EverOS

| 维度 | SkillClaw | EverOS |
|------|-----------|--------|
| 定位 | 技能进化 | 记忆OS |
| 进化对象 | 技能 | 记忆 |
| 共享机制 | ✅ 集体 | ⚠️ 系统 |

**互补**：EverOS管理记忆，SkillClaw进化技能。

---

## 八、那耶村应用场景

### 8.1 村民技能共享

```
那耶村SkillClaw网络：

村民A（导览专家）
├── 学习最优导览路线
└── 技能进化 → 共享

村民B（民宿老板）
├── 学习客户服务技巧
└── 技能进化 → 共享

村民C（美食达人）
├── 学习美食推荐策略
└── 技能进化 → 共享

所有村民共享彼此经验
Coin Hour奖励技能贡献者
```

### 8.2 游客技能积累

```
游客使用服务 → 技能进化：

游客第一次来
├── 导览Agent学习偏好
└── 技能进化（个性化）

游客第二次来
├── 导览Agent记住偏好
└── 更好服务（经验积累）

游客换设备访问
├── 技能跨设备同步
└── 体验连续
```

### 8.3 Coin Hour技能经济

```
技能贡献 → Coin Hour奖励：

村民A贡献导览技能 → 10 CH奖励
村民B使用该技能 → 5 CH消费
                   ↓
            5 CH给技能贡献者
            5 CH给DAO国库

激励机制：贡献越多，收益越多
```

---

## 九、安装与使用

### 9.1 安装

```bash
# macOS/Linux
git clone https://github.com/AMAP-ML/SkillClaw.git
cd SkillClaw
bash scripts/install_skillclaw.sh
source .venv/bin/activate

# 配置
skillclaw setup

# 启动守护进程
skillclaw start --daemon
```

### 9.2 OpenClaw集成

```bash
# SkillClaw自动检测OpenClaw
# 技能目录默认：~/.openclaw/skills/

# 查看技能状态
skillclaw skills list

# 查看进化进度
skillclaw dashboard serve
```

---

## 十、行动建议

### 10.1 立即行动

| 优先级 | 任务 |
|--------|------|
| **P0** | 安装SkillClaw，体验技能进化 |
| **P0** | 测试OpenClaw集成 |
| **P1** | 设计那耶村DAO技能共享机制 |
| **P1** | 设计Coin Hour技能奖励机制 |

### 10.2 整合决策

| 选项 | 说明 |
|------|------|
| **完全替代Skills Manager** | SkillClaw功能更全 |
| **整合使用** | Skills Manager同步IDE，SkillClaw进化技能 |
| **架构参考** | 学习设计，按AIX需求定制 |

---

## 十一、一句话总结

**SkillClaw是高德地图开源的技能集体进化框架，原生支持OpenClaw，实现跨Agent/设备技能共享与自动进化，是AIX Skills生态的核心基础设施。**

**核心价值**：
- 原生支持OpenClaw ✅
- 自动进化技能（后台自动）
- 跨Agent/设备共享
- 团队集体进化
- 自动去重优化

**与AIX关系**：
- 替代Skills Manager（功能更全）
- 实现Self-Improving技能版
- 支持那耶村DAO技能共享
- Coin Hour技能经济基础

---

*最后更新：2026-05-10*
