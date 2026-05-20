# Paperclip：Agent编排层（公司治理）

> 来源：https://github.com/paperclipai/paperclip | 分析日期：2026-05-14

## 基本信息
- Stars: 65,234 | Forks: 11,823
- 语言: TypeScript | 创建: 2026-03-02（仅2个月）
- 官网: https://paperclip.ing

## 核心定位
> "如果OpenClaw是员工，Paperclip就是公司"

- Agent编排层：把多个AI Agent组织成公司架构
- 统一管理目标、预算、治理、审计
- 支持OpenClaw/Claude Code/Codex/Cursor等任何Agent

## 核心功能
| 功能 | 说明 |
|------|------|
| 组织架构 | CEO/CTO/工程师角色、汇报线、权限 |
| 目标对齐 | 任务追溯到公司使命 |
| 心跳调度 | 定时唤醒Agent执行任务 |
| 预算控制 | 每Agent月度预算，超限停止 |
| 治理审批 | 董事会批准招聘/策略/终止 |
| 多公司隔离 | 一个部署，多个公司 |
| 审计追踪 | 每个对话/决策/工具调用记录 |

## 与AIX关系
- 互补：Paperclip=软件编排层，AIX Box=硬件基座+经济层
- 可部署在Mac mini M4上
- 技术栈第六层：Agent编排层（与PraisonAI同级）

## 一人公司场景
CEO Agent(Claude Code) → CTO Agent(Codex) → 工程师Agent(OpenClaw) → 营销Agent(AiToEarn)
Paperclip负责：目标对齐、预算分配、任务调度、审计追踪
