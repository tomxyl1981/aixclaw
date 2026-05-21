# Spec Kit 分析 - 对AIX项目的帮助

> 分析时间：2026-05-21 | 项目：github/spec-kit | Stars: 104,456

---

## 一、Spec Kit 是什么

**GitHub官方出品**的规范驱动开发工具包，核心理念：

```
传统开发：代码为王，规范只是脚手架
Spec-Driven Development：规范可执行，直接生成实现
```

### 核心流程

```
/speckit.constitution → 定义项目原则
/speckit.specify      → 描述要建什么（需求和用户故事）
/speckit.clarify      → 澄清模糊区域
/speckit.plan         → 技术实现计划
/speckit.tasks        → 生成任务列表
/speckit.implement    → 执行任务，构建功能
```

### 关键特性

- 支持30+ AI编码Agent（Claude/Copilot/Codex等）
- Extensions扩展系统 + Presets预设系统
- 开源（MIT），GitHub官方维护
- Python CLI工具

---

## 二、对AIX项目的直接帮助

### 帮助1：AIX九层架构规范化

| 痛点 | Spec Kit解决方案 |
|------|------------------|
| 九层架构描述分散 | 用constitution定义全局原则 |
| 各层实现随意 | 用specify定义每层需求 |
| Agent之间接口不清 | 用plan定义技术规范 |
| 开发任务无追踪 | 用tasks生成+GitHub Issues追踪 |

**具体操作**：
```
/speckit.constitution → AIX五层架构原则（数据主权、代码做主、硬件级治理）
/speckit.specify      → 每层组件需求（记忆层、技能层、钩子层...）
/speckit.plan         → 技术栈选择（OpenClaw/Coin Hour/UTXO）
/speckit.tasks        → 开发任务分解
/speckit.implement    → Agent自动执行
```

### 帮助2：ViMax漫剧平台开发

| 痛点 | Spec Kit解决方案 |
|------|------------------|
| 15个Agent协作无规范 | constitution定义Agent行为边界 |
| 创作/校验/生成流程随意 | specify定义每个Agent职责 |
| 质量不可控 | checklist生成质量检查清单 |

### 帮助3：Coin Hour经济模型

| 痛点 | Spec Kit解决方案 |
|------|------------------|
| 支付流程定义模糊 | specify精确描述支付场景 |
| UTXO账本规则不清 | constitution定义账本原则 |
| 测试覆盖不足 | tasks+implement自动生成测试 |

### 帮助4：那耶米产品开发

| 痛点 | Spec Kit解决方案 |
|------|------------------|
| 溯源体系无技术规范 | specify定义溯源需求 |
| CH支付集成随意 | plan定义支付接口规范 |

---

## 三、与AIX理念契合度

| AIX理念 | Spec Kit对应 |
|---------|-------------|
| "LLM打工，代码做主" | 规范驱动，AI执行 ✅ 完全一致 |
| 数据主权 | constitution定义数据不出村原则 ✅ |
| 硬件级治理 | spec可写入硬件约束 ✅ |
| 一人公司 | spec让一人也能管大项目 ✅ |

**核心理念完全一致**：
- AIX说"LLM打工，代码做主"
- Spec Kit说"规范先行，AI执行"
- 本质相同：**人定义规则，AI负责实现**

---

## 四、行动建议

### 立即执行（0-1周）

1. **安装Spec Kit**
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

2. **初始化AIX项目**
```bash
specify init aix-core --integration copilot
```

3. **创建AIX Constitution**
```
/speckit.constitution Create principles for AIX:
- Data sovereignty: data never leaves the community
- Code rules: deterministic logic in code, LLM only for semantic understanding
- Hardware governance: physical enforcement of rules
- Coin Hour economy: internal economic loop
- One-person company: minimal team, maximum automation
```

### 短期计划（1-4周）

| 项目 | 使用方式 |
|------|----------|
| Coin Hour支付 | specify定义支付流程 + plan定义UTXO接口 |
| 那耶米溯源 | specify定义溯源需求 + tasks分解开发 |
| ViMax编排 | specify定义15个Agent职责 |

### 长期计划

- 建立AIX专属Preset（定制模板）
- 贡献Extension（Coin Hour验证、AIX Box部署）
- 社区共建AIX规范生态

---

## 五、结论

**Spec Kit与AIX理念100%契合**，核心都是"规范先行，AI执行"。

| 评估维度 | 评分 | 说明 |
|----------|------|------|
| 理念契合 | ⭐⭐⭐⭐⭐ | "LLM打工，代码做主"vs"规范先行，AI执行" |
| 即用性 | ⭐⭐⭐⭐⭐ | CLI安装，30+Agent集成 |
| AIX定制 | ⭐⭐⭐⭐ | 需创建AIX专属Constitution |
| 社区生态 | ⭐⭐⭐⭐⭐ | GitHub官方，10万+Stars |

**建议：立即安装，用constitution定义AIX核心原则。**
