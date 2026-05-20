# AgentMemory.dev 深度分析

> 来源：https://github.com/rohitg00/agentmemory
> 分析日期：2026-05-18
> Stars：12,018 | Forks：1,020 | License：Apache 2.0

---

## 🎯 一句话定位

**首个专为Coding Agent设计的持久记忆引擎**，基于Karpathy LLM Wiki模式扩展，支持自动捕获上下文，跨会话记忆。

---

## 📊 核心指标

| 指标 | 数值 |
|------|------|
| 检索准确率 | 95.2% (R@5, LongMemEval-S) |
| Token节省 | 92% (从$500/年→$10/年) |
| 自动Hooks | 12个（零手动记录） |
| MCP工具 | 53个 |
| 外部依赖 | 0（纯SQLite） |
| 支持Agent | 16+ |

---

## 🔗 与AIX架构对应

| AgentMemory层 | AIX对应 | 匹配度 |
|----------------|---------|--------|
| SQLite本地存储 | AIX Box本地存储 | ✅ 完全一致 |
| iii-engine | Karpathy Wiki扩展 | ✅ 理念同源 |
| 4层记忆生命周期 | AIX五层架构 | ✅ 高度互补 |
| MCP协议 | OpenClaw原生支持 | ✅ 已集成 |
| 多Agent共享记忆 | Pico Claw + Hermes | ✅ 即用 |
| 零外部DB | AIX Box无依赖 | ✅ 物理+数字对齐 |

---

## 🚀 对AIX的具体价值

### 1. **技术栈补全**
```
AIX九层架构第一层（记忆层）的现成实现：
├── 本地持久化存储 → SQLite（AIX Box可托管）
├── 语义检索 → BM25 + Vector + Graph（RRF融合）
├── 记忆生命周期 → 4层压缩+衰减（与Coin Hour经济激励协同）
└── 多Agent协调 → MCP + REST + leases
```

### 2. **与现有项目互补**
| 项目 | 与AgentMemory关系 |
|------|-------------------|
| TencentDB Agent Memory | Token降61% vs 92%，AgentMemory更强，但TencentDB有云托管优势 |
| claude-mem (75K星) | 功能重叠，但AgentMemory有OpenClaw原生支持 |
| Letta/MemGPT | AgentMemory更轻量，无运行时绑定 |

### 3. **那耶村MVP验证**
```
场景：游客到那耶村，Claw Agent记住偏好
├── 游客说"喜欢酸汤鱼" → AgentMemory自动捕获
├── 下次来，Agent主动推荐相关餐馆
├── Coin Hour结算 → 消费凭证上链
└── Avatar NFT → 语料资产化（与AgentMemory互补）
```

---

## 🛠️ 技术亮点

### 自动捕获机制
```bash
# 12个Hooks自动触发
- Tool call之前/之后
- 文件写入之后
- 命令执行之后
- 错误发生时
- 会话结束时
...
```

### 检索策略
```
BM25（关键词） + Vector（语义） + Graph（关系） → RRF融合
                                    ↓
                              95.2%准确率
```

### 记忆生命周期
```
热记忆（当前会话）→ 温记忆（压缩）→ 冷记忆（归档）→ 删除（衰减）
                    ↓
              Coin Hour可设计写入成本
```

---

## 📋 行动建议

### ✅ 立即可做
1. **安装测试**
   ```bash
   npm install -g @agentmemory/agentmemory
   agentmemory
   ```
   
2. **集成OpenClaw**
   ```bash
   agentmemory connect openclaw
   ```
   （已原生支持）

3. **验证那耶村场景**
   - 测试游客偏好记忆
   - 测试跨会话推荐
   - 测试Coin Hour结算触发

### 📝 中期规划
1. **适配AIX Box**
   - 将SQLite数据目录挂载到Box
   - 与UTXO账本做一致性校验
   - 设计Avatar NFT与记忆的关系

2. **经济层集成**
   - 记忆写入消耗Coin Hour
   - 高价值记忆可获得Coin Hour奖励
   - 删除记忆可回收Coin Hour

### ⚠️ 注意事项
1. **与TencentDB Agent Memory对比**：两者可共存，AgentMemory适合本地，TencentDB适合云端
2. **数据主权**：确保所有记忆数据在本地，不上传云端
3. **成本控制**：本地嵌入模型(all-MiniLM-L6-v2)免费，云端嵌入需API成本

---

## 🔍 竞品对比

| 维度 | AgentMemory | mem0 | Letta | claude-mem |
|------|-------------|------|-------|------------|
| Stars | 12K | 53K | 22K | 75K |
| 检索准确率 | **95.2%** | 68.5% | 83.2% | N/A |
| 自动捕获 | ✅ 12 Hooks | ❌ | ⚠️ 自编辑 | ❌ |
| OpenClaw支持 | ✅ 原生 | ❌ | ❌ | ✅ |
| 本地部署 | ✅ 默认 | ⚠️ 可选 | ⚠️ 可选 | ✅ |
| Token节省 | **92%** | 变化 | N/A | **95%** |

---

## 📚 相关资源

- 官网：https://agent-memory.dev
- GitHub：https://github.com/rohitg00/agentmemory
- iii-engine：https://github.com/iii-hq/iii
- 基准测试：LongMemEval-S (ICLR 2025)

---

*标签：记忆引擎, MCP, OpenClaw原生, 本地部署, Token降本*
