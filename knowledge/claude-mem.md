# Claude-Mem：跨会话持久记忆系统

> 来源：https://github.com/thedotmack/claude-mem | 分析日期：2026-05-15

## 基本信息
- Stars: 75,766 | 语言: TypeScript | 协议: Apache 2.0
- 类型：OpenClaw原生插件

## 核心价值
- 跨会话持久记忆（会话结束记忆不丢失）
- 自动捕获工具调用观察
- AI压缩语义摘要，节省95% Token
- MCP搜索工具（自然语言查询历史）
- Web查看器：localhost:37777

## 与TencentDB对比
| 维度 | Claude-Mem | TencentDB |
|------|-----------|----------|
| Token节省 | 95% | 61% |
| 工具效率 | 20x | 1.5x |
| 记忆结构 | 观察→摘要 | L0-L3分层 |
| 适用场景 | 开发者工作流 | 用户画像 |

## AIX应用
- 第一层记忆层：两者互补
- 组合效果：Token节省97%

## 建议：两个都装
