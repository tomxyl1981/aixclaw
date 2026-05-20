# 漫剧平台Skill套件

**项目名称**：Manhua Platform Skill Suite  
**版本**：v1.0.0  
**适配平台**：Hermes Agent / OpenClaw / skills-manage  
**许可**：MIT  

---

## 一、套件架构

```
漫剧平台Skill套件
├── 核心技能（Core Skills）
│   ├── manhua-writer（剧本生成）
│   ├── manhua-storyboard（分镜设计）
│   ├── manhua-painter（画面生成）
│   ├── manhua-voice（配音合成）
│   └── manhua-composer（视频合成）
│
├── 整合技能（Integration Skills）
│   ├── manhua-oneclick（一键生成）
│   └── manhua-batch（批量生产）
│
└── 宣发技能（Marketing Skills）
    ├── manhua-trailer（预告片制作）
    └── manhua-promo（宣发内容生成）
```

---

## 二、核心技能详解

### Skill 1: manhua-writer（剧本生成）

**功能**：从创意到完整漫剧剧本

**输入**：
- 主题/题材（如：都市爱情、玄幻修仙）
- 角色设定（主角、配角、反派）
- 剧情走向（起始、冲突、高潮、结局）
- 风格要求（搞笑、悬疑、热血）

**输出**：
- 角色人设卡（外貌、性格、口头禅）
- 章节大纲（10-50集规划）
- 分集剧本（对话、旁白、场景描述）

**Prompt模板**：

```markdown
# Role
你是专业漫剧编剧，擅长{题材}类型创作。

# Task
根据用户需求生成漫剧剧本

# Input
- 主题：{topic}
- 角色设定：{characters}
- 风格：{style}
- 集数：{episodes}

# Output Format
## 角色设定
- 主角：{姓名}|{年龄}|{性格}|{外貌描述}|{口头禅}
- 配角：...

## 章节大纲
- 第1集：{标题} - {剧情概要}
- ...

## 分集剧本（第{N}集）
### 场景{M}：{场景描述}
- 角色：{出场角色}
- 对话：
  - {角色A}：{台词}
  - {角色B}：{台词}
- 动作：{角色动作描述}
- 旁白：{旁白内容}
```

**依赖**：
- LLM（Hermes/Claude）
- 漫剧剧本知识库

---

### Skill 2: manhua-storyboard（分镜设计）

**功能**：将剧本转化为分镜脚本

**输入**：
- 分集剧本（来自manhua-writer）
- 画面风格（日漫、韩漫、国漫）
- 格式要求（竖屏/横屏）

**输出**：
- 分镜脚本（每格画面的精确描述）
- 镜头运动（推拉摇移）
- 画面构图（近景/中景/远景）

**Prompt模板**：

```markdown
# Role
你是专业漫剧分镜师，擅长将剧本转化为视觉画面。

# Task
根据剧本生成分镜脚本

# Input
- 剧本片段：{script_segment}
- 风格：{art_style}
- 格式：{format}

# Output Format
## 分镜{N}
- 场景：{场景名称}
- 镜头：{特写/中景/远景}
- 构图：{画面布局描述}
- 角色：{出场角色及位置}
- 表情：{角色表情}
- 动作：{角色动作}
- 台词：{本格台词}
- 氛围：{光线/色调/情绪}
- 时长：{建议秒数}
```

**依赖**：
- manhua-writer输出
- 分镜知识库

---

### Skill 3: manhua-painter（画面生成）

**功能**：根据分镜生成画面

**输入**：
- 分镜脚本（来自manhua-storyboard）
- 角色参考图（保证一致性）
- 风格LoRA（漫剧风格模型）

**输出**：
- 画面提示词（用于Midjourney/SD）
- 批量生成脚本
- 质量检查清单

**Prompt模板**：

```markdown
# Role
你是AI绘画提示词专家，擅长将分镜转化为精准的绘画Prompt。

# Task
根据分镜生成画面提示词

# Input
- 分镜描述：{storyboard}
- 角色参考：{character_refs}
- 风格：{style_lora}

# Output Format
## 画面{N}提示词
**正向提示词**：
{主体描述}, {角色外貌}, {动作姿态}, {表情}, {场景环境}, {光线}, {构图}, {风格标签}

**负向提示词**：
{排除元素}

**参数建议**：
- 尺寸：{宽x高}
- 步数：{steps}
- CFG：{cfg_scale}
- 种子：{seed}（保持角色一致性）
```

**依赖**：
- Stable Diffusion / Midjourney API
- 漫剧风格LoRA模型

---

### Skill 4: manhua-voice（配音合成）

**功能**：为角色配音

**输入**：
- 角色台词（来自剧本）
- 角色声线设定（男/女、年龄、性格）
- 情绪标注（开心、悲伤、愤怒）

**输出**：
- TTS提示词
- 批量配音脚本
- 音频文件列表

**Prompt模板**：

```markdown
# Role
你是配音导演，负责将台词转化为TTS指令。

# Task
根据角色台词生成配音指令

# Input
- 角色：{character_name}
- 声线：{voice_type}（如：温柔女声-25岁）
- 台词：{dialogue}
- 情绪：{emotion}

# Output Format
## 配音指令
- 文本：{dialogue}
- 说话人：{speaker_id}
- 情感：{emotion_tag}
- 语速：{speed}
- 音调：{pitch}
- 停顿：{pause_positions}
```

**依赖**：
- ElevenLabs API
- 本地TTS引擎（VITS/SoVITS）

---

### Skill 5: manhua-composer（视频合成）

**功能**：将画面+音频合成为视频

**输入**：
- 画面序列（来自manhua-painter）
- 音频序列（来自manhua-voice）
- 转场效果（淡入淡出、推拉）
- BGM配置

**输出**：
- 合成脚本（anime.js配置）
- 视频文件
- 播放器配置

**Prompt模板**：

```markdown
# Role
你是视频合成专家，负责将画面和音频组装成流畅的漫剧视频。

# Task
生成视频合成配置

# Input
- 画面：{image_sequence}
- 音频：{audio_sequence}
- 转场：{transition_effects}
- BGM：{background_music}

# Output Format
## 合成配置
```json
{
  "frames": [
    {
      "image": "{image_path}",
      "audio": "{audio_path}",
      "duration": {seconds},
      "transition": "{transition_type}",
      "effects": ["{effect1}", "{effect2}"]
    }
  ],
  "bgm": "{bgm_path}",
  "bgm_volume": 0.3,
  "output": "{output_path}"
}
```
```

**依赖**：
- anime.js（Web动画引擎）
- FFmpeg（视频处理）
- Web播放器

---

## 三、整合技能

### Skill 6: manhua-oneclick（一键生成）

**功能**：从主题到完整视频，一键完成

**工作流**：
```
主题输入
  ↓
manhua-writer（生成剧本）
  ↓
manhua-storyboard（生成分镜）
  ↓
manhua-painter（生成画面）
  ↓
manhua-voice（生成配音）
  ↓
manhua-composer（合成视频）
  ↓
完整漫剧视频输出
```

**配置文件**：

```yaml
skill: manhua-oneclick
name: 一键漫剧生成
version: 1.0.0

workflow:
  - step: manhua-writer
    input:
      topic: "${user_input.topic}"
      style: "${user_input.style}"
      episodes: "${user_input.episodes}"
    output:
      - script

  - step: manhua-storyboard
    input:
      script: "${steps.manhua-writer.output.script}"
    output:
      - storyboard

  - step: manhua-painter
    input:
      storyboard: "${steps.manhua-storyboard.output.storyboard}"
      style_lora: "${config.style_lora}"
    output:
      - images

  - step: manhua-voice
    input:
      script: "${steps.manhua-writer.output.script}"
    output:
      - audios

  - step: manhua-composer
    input:
      images: "${steps.manhua-painter.output.images}"
      audios: "${steps.manhua-voice.output.audios}"
    output:
      - video

trigger: /oneclick
```

---

### Skill 7: manhua-batch（批量生产）

**功能**：批量生成多集漫剧

**输入**：
- 完整剧本（所有集数）
- 并行配置（同时生成多少集）
- 队列管理

**输出**：
- 批量生成任务队列
- 进度监控
- 自动排队

---

## 四、宣发技能

### Skill 8: manhua-trailer（预告片制作）

**功能**：用Pixelle-Video生成预告片

**输入**：
- 漫剧亮点片段
- 漫剧标题
- 宣传文案

**输出**：
- 预告片视频（30-60秒）

**Prompt模板**：

```markdown
# Role
你是预告片制作专家，擅长用Pixelle-Video生成吸引人的宣传视频。

# Task
生成漫剧预告片

# Input
- 标题：{manhua_title}
- 亮点：{highlights}
- 文案：{promo_copy}

# Output
- 输入选题：{optimized_topic}
- 素材关键词：{material_keywords}
- BGM风格：{bgm_style}
```

---

### Skill 9: manhua-promo（宣发内容生成）

**功能**：生成各平台宣发内容

**输出**：
- 小红书文案+图片
- 抖音短视频脚本
- 微博文案
- 公众号文章

---

## 五、技术架构

### 5.1 本地部署架构

```
┌─────────────────────────────────────────────┐
│         AIX Box边缘节点                      │
│  - 存储漫剧素材                             │
│  - UTXO账本记录                             │
│  - Coin Hour结算                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       Mac mini M4推理中枢                    │
│  - 运行Hermes Agent                         │
│  - 本地模型推理（LLM + SD）                 │
│  - Skill执行引擎                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         漫剧平台服务层                       │
│  - Web播放器（anime.js渲染）                │
│  - 用户管理系统                              │
│  - Coin Hour支付接口                        │
└─────────────────────────────────────────────┘
```

### 5.2 技术栈

| 组件 | 技术选择 |
|------|----------|
| Agent框架 | Hermes Agent |
| 技能管理 | skills-manage |
| LLM | 本地模型（Llama/Qwen）+ 云端API |
| 绘画 | Stable Diffusion XL + LoRA |
| TTS | ElevenLabs / 本地VITS |
| 视频合成 | anime.js + FFmpeg |
| 播放器 | Web（React）+ 原生App |
| 结算 | Coin Hour + UTXO账本 |

---

## 六、使用示例

### 示例1：生成单集漫剧

```
用户：生成一集都市爱情漫剧，主题是"初遇咖啡厅"，搞笑风格

Agent执行：
1. manhua-writer → 生成剧本（角色：小雨（女）、阿杰（男））
2. manhua-storyboard → 生成分镜（12格画面）
3. manhua-painter → 生成画面提示词
4. manhua-voice → 生成配音指令
5. manhua-composer → 合成视频
6. 输出：完整视频 + Coin Hour消费记录
```

### 示例2：批量生成50集

```
用户：生成50集玄幻漫剧《修仙少年》

Agent执行：
1. manhua-writer → 生成50集完整剧本
2. manhua-batch → 创建批量任务队列
3. 并行执行：manhua-storyboard → manhua-painter → manhua-voice → manhua-composer
4. 输出：50集视频 + 进度监控面板
```

---

## 七、Coin Hour消费模型

| 技能 | Coin Hour消耗 |
|------|---------------|
| manhua-writer | 5 CH/集 |
| manhua-storyboard | 2 CH/集 |
| manhua-painter | 10 CH/集 |
| manhua-voice | 3 CH/集 |
| manhua-composer | 1 CH/集 |
| manhua-oneclick | 20 CH/集（打包价） |
| manhua-trailer | 5 CH/次 |

**消费闭环**：
- 用户持有AIX → 产出Coin Hour
- 消费Coin Hour生成漫剧
- 漫剧上架销售 → 收益回流
- 收益购买更多AIX → 持续产出

---

## 八、那耶村MVP场景

| 场景 | 实现 |
|------|------|
| 村民创作漫剧 | 本地Hermes + Coin Hour消费 |
| 村里播放漫剧 | Web播放器 + 本地存储 |
| Coin Hour消费 | 漫剧制作消耗Coin Hour |
| Coin Hour收入 | 漫剧销售收入回流 |

---

## 九、开源地址

- GitHub: https://github.com/aix-project/manhua-platform-skills（示例）
- skills-manage导入：`skills-manage import manhua-platform`

---

## 十、更新日志

- 2026-04-27 v1.0.0 初始版本，包含9个核心技能

---

*漫剧平台Skill套件——让每个人都能创作漫剧*
