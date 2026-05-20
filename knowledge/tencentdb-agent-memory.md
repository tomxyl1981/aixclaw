# TencentDB Agent Memory：Agent分层记忆系统

> 来源：https://github.com/Tencent/TencentDB-Agent-Memory | 分析日期：2026-05-15

## 基本信息
- Stars: 882 | 语言: TypeScript | 协议: MIT
- 类型：OpenClaw原生插件
- 安装：`openclaw plugins install @tencentdb-agent-memory/memory-tencentdb`

## 核心价值
- 分层记忆：L0对话→L1原子事实→L2场景→L3用户画像
- 符号化记忆：Mermaid图替代冗长文本
- Token消耗降61%，任务通过率提升51%
- 完全本地（SQLite+sqlite-vec），零外部API依赖

## 与AIX关系
- = AIX五层架构第一层（记忆层）的现成实现
- 符号化记忆="LLM打工，代码做主"理念验证
- Token降61% = Coin Hour边际成本降61%
- 数据完全本地 = 数字主权

## 那耶村MVP
- 安装后自动记住游客偏好（L3 Persona）
- 下次对话更精准，Token更少
- 边际成本持续下降

## 配置
```jsonc
{
  "memory-tencentdb": {
    "enabled": true,
    "config": {
      "offload": { "enabled": true },
      "recall": { "strategy": "hybrid", "maxResults": 5 },
      "bm25": { "language": "zh" }
    }
  }
}
```

## 建议：立即安装
