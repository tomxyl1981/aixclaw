# 每日定时任务清单

## ⏰ 每日 09:00 北京时间 - 工作摘要播报

### 任务配置
- **Job ID**: `9188ae92-5313-4f57-af2e-2a516e923fe1`
- **名称**: `daily-summary-feishu`
- **时间**: 每天 UTC 01:00 (北京时间 09:00)
- **目标**: 飞书群 `oc_f444fe5f779e84223fee89a008340a57`
- **状态**: ✅ 已启用

### 执行内容
1. 读取 `memory/YYYY-MM-DD.md` (昨天的记录)
2. 汇总：完成任务、生成文档、重要讨论、待办事项
3. 发送到飞书群

### 管理命令
```bash
# 查看任务状态
openclaw cron list

# 手动触发
openclaw cron run 9188ae92-5313-4f57-af2e-2a516e923fe1

# 禁用任务
openclaw cron disable 9188ae92-5313-4f57-af2e-2a516e923fe1

# 启用任务
openclaw cron enable 9188ae92-5313-4f57-af2e-2a516e923fe1
```

---

## ⚠️ 注意事项

- **Gateway 必须运行**: cron 任务依赖 Gateway daemon
- **检查 Gateway 状态**: `openclaw gateway status`
- **日志位置**: `/tmp/openclaw/openclaw-2026-04-14.log`
