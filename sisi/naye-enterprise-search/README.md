# 那耶村企业搜索 (Naye Enterprise Search)

Anthropic Claude Enterprise Search 的那耶村定制版 - 连接AIX本地知识库。

## 快速开始

### 安装

```bash
# 进入AIX工作区
cd ~/.openclaw/workspace

# 添加插件
openclaw plugin add sisi/naye-enterprise-search

# 自动索引
/openclaw plugin run naye-enterprise-search --index
```

### 使用

```bash
# 搜索那耶村知识库
/naye:search 梁越的作品

# 指定来源
/naye:search from:memory CH分配方案
/naye:search from:knowledge 短剧平台

# 时间过滤
/naye:search after:2026-05-01 项目进度

# 生成日报
/naye:digest --daily
```

## 架构

```
naye-enterprise-search/
├── .aix/
│   ├── plugin.json          # 插件清单
│   └── mcp.json             # 数据源配置
├── commands/
│   └── search.py            # 搜索命令实现
├── connectors/
│   ├── memory.py            # MEMORY.md连接器
│   ├── knowledge.py         # knowledge/连接器
│   └── workspace.py         # 工作区连接器
├── skills/
│   └── search-strategy.md   # 搜索策略技能
└── README.md                # 本文件
```

## 数据源

| 源 | 路径 | 内容 |
|----|------|------|
| **memory** | `memory/*.md` | 每日日志、会议记录 |
| **knowledge** | `knowledge/*.md` | 知识库、方案文档 |
| **workspace** | `sisi/`, `files/` | 工作文档 |
| **feishu** | 飞书导出 | 群聊历史 |
| **codegraph** | `.codegraph/` | 代码索引 |

## 搜索语法

### 基础搜索
```
/naye:search 关键词
```

### 高级过滤
```
/naye:search from:memory 梁越        # 只搜MEMORY
/naye:search from:knowledge category:project  # 按分类
/naye:search after:2026-05-01        # 时间之后
/naye:search before:2026-05-28       # 时间之前
/naye:search tag:urgent              # 按标签
```

### 组合查询
```
/naye:search from:memory after:2026-05-01 CH预算
/naye:search from:knowledge tag:urgent project:那耶IP出海
```

## 与Anthropic原版对比

| 特性 | Anthropic版 | 那耶村版 |
|------|------------|---------|
| **数据源** | Slack/Gmail/Notion | MEMORY.md/knowledge/本地文件 |
| **部署** | 云端SaaS | AIX Box本地 |
| **隐私** | 上传云端 | 完全本地 |
| **计费** | 订阅制 | Coin Hour按次 |
| **定制化** | 通用 | 那耶村专属优化 |

## 性能

- **索引速度**: ~100文件/秒
- **搜索延迟**: <100ms
- **内存占用**: ~50MB基础 + 10MB/千文件

## 路线图

### v1.0 (本周)
- [x] memory连接器
- [x] knowledge连接器  
- [x] 基础搜索命令
- [x] 时间过滤

### v1.1 (下周)
- [ ] workspace连接器
- [ ] 飞书对话集成
- [ ] 自然语言查询优化

### v1.2 (下月)
- [ ] 语义搜索（向量索引）
- [ ] 图像OCR搜索
- [ ] 知识图谱集成

## 贡献

基于 Anthropic Knowledge Work Plugins，MIT协议。

**主要修改**：
- 替换云端SaaS连接为本地文件系统
- 添加那耶村专属实体识别
- 适配Coin Hour计费
- 中文搜索优化

## 许可证

MIT - 与上游保持一致
