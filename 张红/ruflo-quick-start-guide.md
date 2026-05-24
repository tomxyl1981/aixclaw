# Ruflo 快速上手手册

> 多智能体编排引擎 | GitHub: ruvnet/ruflo | Stars: 54K

---

## 一、5分钟安装

```bash
# 安装Ruflo
npx ruflo@latest init

# 验证安装
ruflo --version
```

---

## 二、核心命令

### 2.1 启动智能体群

```bash
# 启动默认蜂群（3个Agent）
ruflo start

# 启动指定数量
ruflo start --agents 10

# 启动指定拓扑
ruflo start --topology pipeline
ruflo start --topology mesh
ruflo start --topology hierarchical
ruflo start --topology clustered
ruflo start --topology star
```

### 2.2 任务分配

```bash
# 给蜂群分配任务
ruflo task "写一个Python爬虫"

# 指定认知模式
ruflo task "设计产品架构" --mode systems
ruflo task "头脑风暴营销方案" --mode divergent
ruflo task "修复这个Bug" --mode convergent
ruflo task "代码审查" --mode critical
```

### 2.3 监控与控制

```bash
# 查看蜂群状态
ruflo status

# 查看单个Agent
ruflo agent list
ruflo agent info <agent-id>

# 暂停/恢复
ruflo pause
ruflo resume

# 停止蜂群
ruflo stop
```

---

## 三、五种拓扑结构

### 3.1 Pipeline（流水线）

**适用：顺序工作流**

```
Agent A → Agent B → Agent C → Agent D
```

**命令：**
```bash
ruflo start --topology pipeline --agents 5
ruflo task "制作AI短剧：剧本→分镜→图像→配音→剪辑"
```

**场景：**
- AI短剧制作
- 文档处理流程
- 数据清洗管道

---

### 3.2 Mesh（网状）

**适用：头脑风暴、研究**

```
    Agent A
   ↙    ↘
Agent B ← Agent C
   ↘    ↙
    Agent D
```

**命令：**
```bash
ruflo start --topology mesh --agents 6
ruflo task "头脑风暴音乐节创意方案" --mode divergent
```

**场景：**
- 创意策划会
- 技术调研
- 问题诊断

---

### 3.3 Hierarchical（层级）

**适用：大型项目管理**

```
        总指挥Agent
       ↙    ↓    ↘
   组长A  组长B  组长C
    ↓      ↓      ↓
  成员群  成员群  成员群
```

**命令：**
```bash
ruflo start --topology hierarchical --agents 20
ruflo task "开发那耶村知识图谱系统"
```

**场景：**
- 九层架构开发
- 音乐节筹备（分组协作）
- 企业级项目

---

### 3.4 Clustered（集群）

**适用：专门团队协作**

```
    ┌─────┬─────┬─────┐
    ↓     ↓     ↓     ↓
 音响组 舞美组 安保组 后勤组
    ↓     ↓     ↓     ↓
   5个   5个   5个   5个
```

**命令：**
```bash
ruflo start --topology clustered --agents 30
ruflo task "音乐节各组并行筹备"
```

**场景：**
- 音乐节/电影节筹备
- 多部门协作
- 多渠道营销

---

### 3.5 Star（星型）

**适用：中心化控制**

```
      中心Agent
     ↙↓↘↓↙↓↘
  A B C D E F
```

**命令：**
```bash
ruflo start --topology star --agents 10
ruflo task "民宿运营：前台调度各服务Agent"
```

**场景：**
- 民宿运营管理
- 院子咖啡店
- 直播带货调度

---

## 四、六种认知模式

| 模式 | 用途 | 触发词 |
|------|------|--------|
| **convergent** | Bug修复、问题解决 | "修复"、"诊断"、"解决" |
| **divergent** | 创意策划、头脑风暴 | "创意"、"策划"、"头脑风暴" |
| **lateral** | 跨领域创新 | "跨界"、"类比"、"创新" |
| **systems** | 架构设计、整体优化 | "架构"、"系统"、"整体" |
| **critical** | 代码审查、风险评估 | "审查"、"评估"、"检查" |
| **abstract** | 模式识别、通用化 | "抽象"、"模式"、"通用" |

---

## 五、实战案例

### 案例1：AI短剧制作（Pipeline）

```bash
# 1. 启动Pipeline蜂群
ruflo start --topology pipeline --agents 6

# 2. 分配任务
ruflo task "根据梁越《隐没的战象》第一章，制作3分钟AI短剧：
1. 剧本Agent：提炼关键场景
2. 分镜Agent：设计画面构图
3. 图像Agent：生成场景图
4. 配音Agent：多角色配音
5. 剪辑Agent：合成视频
6. 审核Agent：质量检查"

# 3. 监控进度
ruflo status

# 4. 输出到AIX Box
ruflo export --output /aix-box/projects/drama-01/
```

---

### 案例2：夏令营项目管理（Hierarchical）

```bash
# 1. 启动层级蜂群
ruflo start --topology hierarchical --agents 15

# 2. 定义角色结构
ruflo config set roles:
  - coordinator: "三导师总控"
  - ip-team: "梁越IP文化组"
  - ai-team: "Jane AI创作组"
  - tech-team: "用户377861技术组"

# 3. 分配任务
ruflo task "夏令营第1周任务分配：
- IP组：整理梁越50万字作品
- AI组：设计Graphify课程
- 技术组：部署AIX Box原型"

# 4. 每日汇报
ruflo report daily
```

---

### 案例3：民宿运营（Star）

```bash
# 1. 启动星型蜂群
ruflo start --topology star --agents 8

# 2. 定义服务Agent
ruflo config set agents:
  - front-desk: "前台接待调度"
  - cleaning: "清洁服务"
  - kitchen: "厨房备餐"
  - guide: "导游服务"
  - transport: "接送服务"
  - maintenance: "设施维护"
  - feedback: "顾客反馈收集"
  - billing: "Coin Hour结算"

# 3. 运行模式
ruflo task "民宿日常运营：前台协调各服务Agent，Coin Hour结算"
ruflo mode set auto  # 自动运行模式
```

---

## 六、高级配置

### 6.1 记忆持久化

```bash
# 启用AgentDB（自学习记忆）
ruflo config set memory:
  enabled: true
  type: agentdb
  path: ~/.ruflo/memory/

# 查看记忆状态
ruflo memory stats
```

### 6.2 MCP工具集成

```bash
# 添加MCP工具
ruflo mcp add filesystem
ruflo mcp add github
ruflo mcp add web-search

# 配置飞书写入（可选）
ruflo mcp add feishu --token <your-token>
```

### 6.3 Coin Hour计费

```bash
# 配置Coin Hour计费
ruflo config set coinhour:
  enabled: true
  rate: 10  # 每任务10 CH起
  log: ~/.ruflo/ch-log/

# 查看消耗统计
ruflo coinhour stats --week
```

---

## 七、常见问题

### Q1: Ruflo和Claude Code如何配合？

```bash
# Ruflo自动调用Claude Code工具
ruflo start --claude-integration true

# 在Claude Code中用Ruflo
claude> /ruflo task "..."
```

### Q2: 如何限制Agent数量？

```bash
# 设置最大Agent数
ruflo config set max-agents 50

# 或启动时指定
ruflo start --agents 10 --max 20
```

### Q3: 如何保存任务结果？

```bash
# 导出到文件
ruflo export --format markdown --output ./results/

# 导出到AIX Box
ruflo export --output /aix-box/projects/<name>/
```

### Q4: 如何查看Agent对话？

```bash
# 实时查看
ruflo logs --live

# 查看历史
ruflo logs --task <task-id>
```

---

## 八、快速参考卡

| 常用命令 | 说明 |
|----------|------|
| `ruflo start` | 启动蜂群 |
| `ruflo task "..."` | 分配任务 |
| `ruflo status` | 查看状态 |
| `ruflo stop` | 停止蜂群 |
| `ruflo export` | 导出结果 |
| `ruflo logs` | 查看日志 |

| 拓扑参数 | 适用场景 |
|----------|----------|
| `--topology pipeline` | 流水线工作流 |
| `--topology mesh` | 头脑风暴 |
| `--topology hierarchical` | 大型项目 |
| `--topology clustered` | 团队协作 |
| `--topology star` | 中心调度 |

| 认知模式参数 | 用途 |
|--------------|------|
| `--mode convergent` | 问题解决 |
| `--mode divergent` | 创意策划 |
| `--mode systems` | 架构设计 |
| `--mode critical` | 审查评估 |

---

## 九、系统要求

| 项目 | 最低 | 推荐 |
|------|------|------|
| Node.js | 14.0 | 18.0+ |
| 内存 | 1GB | 4GB+ |
| CPU | 2核 | 4核+ |
| 存储 | 100MB | 1GB |

---

*手册版本：v1.0 | 更新时间：2026-05-23*
