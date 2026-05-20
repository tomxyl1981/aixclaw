# 漫剧平台Skill套件

**一键漫剧生成** - 从主题到视频，全流程自动化

---

## 快速开始

### 1. 导入技能套件

```bash
# 方式1：skills-manage导入
skills-manage import manhua-platform-skills

# 方式2：手动复制到Hermes
cp -r manhua-platform-skills/* ~/.hermes/skills/
```

### 2. 一键生成漫剧

```
用户：/oneclick 主题：都市爱情咖啡厅初遇，风格：搞笑，集数：1

Agent：✅ 漫剧生成完成！
- 剧名：《咖啡厅的初恋》
- 第1集：3分24秒
- Coin Hour消耗：20 CH
- 观看链接：[点击播放]
```

---

## 技能列表

### 核心技能

| 技能 | 触发词 | 功能 | Coin Hour |
|------|--------|------|-----------|
| **manhua-writer** | `/manhua-writer` | 剧本生成 | 5 CH/集 |
| **manhua-storyboard** | `/manhua-storyboard` | 分镜设计 | 2 CH/集 |
| **manhua-painter** | `/manhua-painter` | 画面生成 | 10 CH/集 |
| **manhua-voice** | `/manhua-voice` | 配音合成 | 3 CH/集 |
| **manhua-composer** | `/manhua-composer` | 视频合成 | 1 CH/集 |

### 整合技能

| 技能 | 触发词 | 功能 | Coin Hour |
|------|--------|------|-----------|
| **manhua-oneclick** | `/oneclick` | 一键生成 | 20 CH/集 |
| **manhua-batch** | `/manhua-batch` | 批量生产 | 15-18 CH/集 |

### 宣发技能

| 技能 | 触发词 | 功能 | Coin Hour |
|------|--------|------|-----------|
| **manhua-trailer** | `/manhua-trailer` | 预告片制作 | 5 CH/次 |
| **manhua-promo** | `/manhua-promo` | 宣发内容 | 2 CH/平台 |

---

## 架构图

```
┌─────────────────────────────────────────────┐
│           用户输入主题                       │
│  "/oneclick 都市爱情咖啡厅初遇"             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Hermes Agent执行                    │
│  - 调用manhua-oneclick技能                  │
│  - 协调5个子技能顺序执行                    │
│  - Coin Hour自动结算                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Mac mini M4推理中枢                  │
│  - LLM生成剧本                              │
│  - SD生成画面                               │
│  - TTS生成配音                              │
│  - FFmpeg合成视频                           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         AIX Box存储节点                      │
│  - 存储漫剧素材                             │
│  - UTXO账本记录交易                         │
│  - Web播放器提供服务                        │
└─────────────────────────────────────────────┘
```

---

## Coin Hour消费闭环

```
┌─────────────────────────────────────────────┐
│         用户持有AIX                         │
│  ↓ 每小时自动产出Coin Hour                 │
│  1 AIX = 24 Coin Hour/天                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         创作漫剧                             │
│  - 一集漫剧消耗20 Coin Hour                 │
│  - 或者购买Coin Hour充值                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         漫剧上架销售                         │
│  - 那耶村本地消费                           │
│  - 或对外销售获得收益                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         收益回流                             │
│  - 收益购买更多AIX                          │
│  - 持续产出更多Coin Hour                     │
│  - 创作更多漫剧                             │
└─────────────────────────────────────────────┘
```

---

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent框架 | Hermes Agent |
| 技能管理 | skills-manage |
| LLM | Llama-3-70B / Qwen-72B |
| 绘画 | Stable Diffusion XL + LoRA |
| TTS | ElevenLabs / VITS |
| 视频合成 | anime.js + FFmpeg |
| 播放器 | React + anime.js |
| 结算 | Coin Hour + UTXO |

---

## 那耶村MVP

| 场景 | 实现 |
|------|------|
| 村民创作 | Hermes本地部署 + Coin Hour结算 |
| 本地播放 | Web播放器 + AIX Box存储 |
| 消费闭环 | Coin Hour在村里流通 |
| 经济循环 | 创作收入回流购买AIX |

---

## 文件结构

```
manhua-platform-skills/
├── README.md
├── SKILL-SUITE.md
├── manhua-writer/
│   ├── SKILL.md
│   └── prompts/
├── manhua-storyboard/
│   ├── SKILL.md
│   └── prompts/
├── manhua-painter/
│   ├── SKILL.md
│   └── prompts/
├── manhua-voice/
│   ├── SKILL.md
│   └── prompts/
├── manhua-composer/
│   ├── SKILL.md
│   └── configs/
├── manhua-oneclick/
│   ├── SKILL.md
│   └── workflow.yaml
├── manhua-batch/
│   ├── SKILL.md
│   └── queue-manager.py
├── manhua-trailer/
│   ├── SKILL.md
│   └── pixelle-integration.py
└── manhua-promo/
    ├── SKILL.md
    └── templates/
```

---

## 开源协议

MIT License

---

## 更新

- 2026-04-27 v1.0.0 初始发布

---

*让每个人都能创作漫剧*
