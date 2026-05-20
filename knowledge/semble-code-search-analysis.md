# Semble代码搜索分析

> 项目：MinishLab/semble
> Stars：3,115 | 创建：2026-04-06 | 更新：2026-05-20
> 来源：Jane推送

---

## 一、核心能力

| 维度 | 数据 |
|------|------|
| **Token节省** | 98%（vs grep+read） |
| **索引速度** | 218x快于CodeRankEmbed |
| **查询速度** | 10x快于transformer |
| **检索质量** | 99% NDCG@10 |
| **召回率** | 94% @ 2k tokens（grep需100k） |
| **硬件需求** | 仅CPU，无GPU/API key |

---

## 二、技术架构

```
代码文件
    ↓
tree-sitter分块（代码感知）
    ↓
双检索器并行：
  ├── Model2Vec静态embedding（potion-code-16M）
  └── BM25词汇匹配
    ↓
RRF融合 + 代码感知重排序
    ↓
Top-K结果返回
```

### 重排序信号

| 信号 | 作用 |
|------|------|
| **自适应权重** | 符号查询→词汇权重↑，自然语言→平衡 |
| **定义boost** | 定义chunk > 引用chunk |
| **标识符stem** | `parse config` → `parseConfig`, `ConfigParser` |
| **文件一致性** | 同文件多匹配 → 文件级boost |
| **噪音惩罚** | test/compat/legacy → 降权 |

---

## 三、对AIX项目的帮助

### 1. 本地开发闭环

```
Mac mini M4（推理中枢）
    +
AIX Box（边缘节点）
    +
Semble（本地代码搜索）
    =
完全无云依赖的开发环境
```

**数据主权**：代码不离开本地，符合AIX核心理念

### 2. 一人公司技术栈集成

| 层级 | 组件 | 与Semble协同 |
|------|------|-------------|
| **第五层：技能层** | Semble | 代码搜索技能 |
| **第四层：Agent运行时** | OpenClaw | MCP集成 |
| **第一层：记忆层** | AgentMemory.dev | 持久记忆 + 代码知识 |
| **工具层** | RAG-Anything | 多模态RAG + 代码检索 |

### 3. 具体应用场景

| 场景 | 应用 |
|------|------|
| **Coding Agent优化** | OpenClaw集成Semble → Token成本降98% |
| **那耶村MVP开发** | 本地代码搜索 → 快速迭代 |
| **AIX Box SDK** | 内置Semble → 开发者友好 |
| **知识库构建** | 代码 → 知识图谱（RAG-Anything） |

---

## 四、与现有组件对比

| 组件 | 功能 | 与Semble关系 |
|------|------|-------------|
| **AgentMemory.dev** | 持久记忆（对话/决策） | 互补：记忆层 vs 代码层 |
| **RAG-Anything** | 多模态RAG（PDF/图像/视频） | 互补：文档层 vs 代码层 |
| **Claude-mem** | 跨会话记忆 | 替代：更轻量（12K vs 75K stars） |
| **grep+read** | 传统代码搜索 | 替代：98% Token节省 |

---

## 五、部署建议

### Phase 1（立即）
```bash
# OpenClaw MCP集成
claude mcp add semble -s user -- uvx --from "semble[mcp]" semble
```

### Phase 2（那耶村MVP）
- AIX Box内置Semble
- 本地代码库索引
- Coin Hour计费（搜索次数）

### Phase 3（知识库）
- 代码 → RAG-Anything知识图谱
- ViMax创作时检索相关代码片段

---

## 六、一句话总结

> **Semble = 代码版的AgentMemory.dev**
> 
> 本地、无依赖、98% Token节省，完美契合AIX数据主权理念。

---

*分析日期：2026-05-20*

---

## 七、实测数据验证（2026-05-20补充）

> 来源：用户377861实测
> 测试场景：GBrain代码库（~300个TypeScript文件）

### 测试结果

| 指标 | grep + read_file | Semble |
|------|-----------------|--------|
| **首次搜索** | 即时（<1s） | 首次需下载模型（~2min） |
| **二次搜索** | 即时 | 10秒（索引已缓存） |
| **Token消耗** | ~63,600 | ~500 |
| **节省比例** | 基准 | **98%** |
| **结果质量** | 184个匹配 | 5个语义相关片段 |
| **理解能力** | ❌ 无语义 | ✅ 自然语言意图 |

### 典型案例

**查询**："vector indexing for semantic search"

**Semble返回**：
1. `src/core/search/vector.ts` - 向量搜索核心
2. `src/core/search/hybrid.ts` - 混合搜索缓存
3. `src/core/search/query-cache.ts` - 语义查询缓存
4. `src/core/migrate.ts` - 缓存表迁移
5. `src/core/types.ts` - 类型定义

### 注意事项

| 问题 | 解决方案 |
|------|----------|
| 首次下载模型（~100MB） | 国内配置 `HF_ENDPOINT=https://hf-mirror.com` |
| MCP集成 | 需要 `/reload-mcp` 才能生效 |
| 适用场景 | 理解代码库、探索性搜索、大型项目导航 |
| 不适用场景 | 精确字符串匹配、简单查找（如TODO注释） |

---

*实测日期：2026-05-20*
