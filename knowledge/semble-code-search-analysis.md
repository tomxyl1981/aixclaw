# Semble 代码搜索分析

> 最后更新：2026-05-20 | 来源：用户377861

---

## 项目信息

- **项目**：MinishLab/semble
- **Stars**：3,115
- **核心能力**：98% Token节省（vs grep+read）| CPU运行 | MCP一行集成
- **GitHub**：https://github.com/MinishLab/semble

---

## 安装结果（2026-05-20）

### 组件状态

| 组件 | 状态 |
|------|------|
| Semble CLI | ✓ 已安装到 `~/.venv/bin/semble` |
| MCP Server | ✓ 已配置到 `~/.hermes/config.yaml` |
| 嵌入模型 | ✓ potion-code-16M (63MB, 已缓存) |
| Tree-sitter 解析器 | ✓ 306 语言包已安装 |

### 性能测试结果

**GBrain 项目（约500文件）：**
- 首次索引：13.10 秒
- 查询延迟：~10ms

**查询示例：**
```
"skill resolver dispatch" → check-resolvable.ts:243
"MCP server tools"        → mcp/server.ts:30
"knowledge graph link"    → operations.ts:717
"minion queue"            → minions/queue.ts:1
```

---

## 中国环境镜像配置（关键）

### 问题背景
HuggingFace 和 GitHub 在中国访问受限。

### 解决方案

**环境变量：**
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

**镜像站地址：**
- HuggingFace 镜像：`https://hf-mirror.com`
- Tree-sitter 解析器：已手动下载到 `~/.cache/tree-sitter-language-pack/v1.6.2/libs/`

---

## 使用方式

### CLI 模式

```bash
# 中国环境必须设置
export HF_ENDPOINT=https://hf-mirror.com

# 搜索代码
semble search "your query" ./your-project --top-k 5
```

### MCP 模式

**工具列表：**
- `semble_search` - 代码搜索
- `semble_find_related` - 查找相关代码

**特点：**
- 自动缓存索引
- 本地路径监听文件变化自动重建
- 重启 Hermes 即可生效

---

## 对 AIX 的帮助

| 场景 | 应用 |
|------|------|
| Coding Agent 优化 | 本地代码搜索，零 API 成本 |
| AgentMemory.dev 协同 | 与 RAG-Anything 形成三件套 |
| AIX Box 本地部署 | 代码知识库本地存储 |

**三件套组合：**
1. **AgentMemory.dev** - Agent 持久记忆
2. **RAG-Anything** - 多模态知识图谱
3. **Semble** - 代码搜索

---

## 技术细节

### 嵌入模型
- **名称**：potion-code-16M
- **大小**：63MB
- **特点**：轻量级，CPU 友好

### 语言支持
- **Tree-sitter 解析器**：306 种语言
- **覆盖**：主流编程语言全支持

---

*维护者：AIX 项目*
