# AIX Box 技术实现文档

> 文档版本: 1.0 | 创建日期: 2026-04-12 | 目标读者: 开发工程师、架构师

## 系统架构设计

四层架构：用户层 → 核心服务层 → 模型层 → 基础设施层

核心服务层：多模态输入模块、三段式脱敏引擎、智能路由系统、本地推理引擎、云端对接模块、Coin Hour支付系统

## 核心模块实现

### 模块1：多模态输入处理模块

MultimodalInputProcessor（基类）
├─ TextInputProcessor：文本预处理、分词、特征提取
├─ AudioInputProcessor：Whisper语音识别（RK3588可运行）
└─ VideoInputProcessor：LLaVA-7B视频理解（量化版）

关键技术：Whisper-tiny.en（39M参数，200-500ms延迟）、LLaVA-7B量化版（500-1000ms延迟）

### 模块2：三段式脱敏引擎

敏感信息识别规则：
- 个人信息：姓名、手机号(1[3-9]\d{9})、身份证号、邮箱
- 企业信息：公司名称、财务数据、银行账号
- 敏感内容：机密、保密、内部

脱敏流程：
1. 本地脱敏：多模态解析→语义理解→敏感信息识别→替换
2. 云端处理：脱敏数据加密传输→云端模型推理
3. 本地回填：精准回填原始信息→语义一致性校验

核心类：
- SensitiveInfoDetector：正则匹配 + NER
- Desensitizer：从后往前替换（避免位置偏移）
- PrivacyReconstructor：精准回填 + 一致性校验

### 模块3：端云一体智能路由

任务复杂度：SIMPLE（简单对话）、MEDIUM（文档总结）、COMPLEX（复杂推理）
隐私敏感度：LOW（公开）、MEDIUM（个人信息）、HIGH（企业机密）
用户偏好：COST_FIRST、QUALITY_FIRST、PRIVACY_FIRST

路由决策矩阵：
- 简单 + 低隐私 → 本地推理（免费）
- 简单 + 中/高隐私 → 三段式脱敏
- 中等 + 低隐私 + 质量优先 → 云端直接
- 中等 + 中/高隐私 + 质量优先 → 三段式脱敏
- 复杂 + 低隐私 + 质量优先 → 云端直接
- 复杂 + 中/高隐私 → 三段式脱敏

失败降级策略：云端直接 → 三段式 → 本地

### 模块4：Coin Hour支付系统

定价规则：
- 本地推理：0 CH（免费）
- 文本脱敏：10 CH/1K tokens
- 语音脱敏：50 CH/分钟
- 视频脱敏：100 CH/分钟
- GLM-4：100 CH/1K tokens
- Kimi：150 CH/1K tokens
- MiniMax：120 CH/1K tokens

支付流程：
1. 准备支付（锁定金额）
2. 执行服务
3. 完成支付（扣除金额）
4. 失败则取消支付（解锁金额）

核心类：PricingEngine、WalletManager、PaymentProcessor、CoinHourPaymentSystem

## 数据库设计

用户表(users)、交易记录表(transactions)、敏感信息映射表(sensitive_mappings)、路由决策日志表(routing_logs)

索引：user_id、status、created_at

## 部署方案

Docker Compose 服务：
- aix-core（核心服务）
- local-model（本地模型）
- desensitization（脱敏引擎）
- payment（支付系统）
- database（PostgreSQL）
- skywire（去中心化网络）

硬件配置：RK3588 + 8GB RAM + 512GB NVMe SSD + USB 3.0 + MIPI CSI + WiFi 6

## 测试方案

单元测试：敏感信息识别、脱敏处理、隐私重构
集成测试：完整三段式流程、智能路由、支付流程

性能指标：
- 本地推理延迟：<200ms
- 多模态处理延迟：<1s
- 脱敏处理延迟：<100ms
- 云端请求延迟：<3s
- 路由决策延迟：<50ms

## 技术选型

Python 3.10+、PyTorch 2.0+、Transformers 4.35+、Whisper base、LLaVA 7B、Qwen2.5 7B、bitsandbytes 0.41+、PostgreSQL 14+、Docker 24.0+

云端模型API：GLM-5(zhipu.ai)、Kimi(moonshot.cn)、MiniMax(minimax.chat)

## 下一步开发计划（12周）

Week 1-2: 多模态输入模块
Week 3-4: 三段式脱敏引擎
Week 5-6: 云端对接
Week 7-8: 支付系统
Week 9-10: 智能路由
Week 11-12: 集成测试

---

文档版本: 1.0 | 最后更新: 2026-04-12 | 文档状态: 技术评审中
