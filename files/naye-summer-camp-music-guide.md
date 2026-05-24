# 那耶村夏令营配乐方案

> 为视频宣传生成 | 2026-05-22

---

## 三段配乐设计

### 第一段：开场氛围（0-15秒）

**风格**：Ambient, Cinematic, Nature soundscape

**AI生成提示词**：
```
Create a 15-second ambient cinematic intro music.
Style: Ethereal, mysterious, hopeful
Instruments: Wind chimes, soft piano, ambient synth, natural wind sounds
Mood: Peaceful dawn, clouds rolling over terraced rice fields
BPM: 60-70
Key: Major, uplifting
Description: Early morning in Yunnan highlands, sea of clouds over ancient rice terraces, gentle awakening
```

**Suno提示词**：
```
[Instrumental]
Ambient cinematic intro, wind soundscape, soft piano, mysterious atmosphere, Chinese highlands dawn, sea of clouds
```

---

### 第二段：壮族民歌改编（15-40秒）

**风格**：Zhuang ethnic folk, World music fusion, Epic

**AI生成提示词**：
```
Create a 25-second world fusion music segment.
Style: Zhuang ethnic folk meets modern cinematic
Instruments: Bronze drum (铜鼓), Lusheng (芦笙), strings, epic percussion
Mood: Pride, heritage, grandeur
BPM: 90-100
Key: Minor to major progression
Description: Thousand-year-old rice terraces, Zhuang people's legacy, "Elephant plowing, bird harrowing" legend comes alive
Keywords: Yunnan, Zhuang, terraced fields, ancient civilization, cultural pride
```

**Suno提示词**：
```
[Instrumental]
Zhuang ethnic folk music, bronze drums, lusheng, epic world fusion, Chinese minority heritage, thousand-year terraces, cultural pride, building crescendo
```

---

### 第三段：现代AI感（40-60秒）

**风格**：Electronic, Future bass, World fusion

**AI生成提示词**：
```
Create a 20-second electronic world fusion finale.
Style: Future bass meets ethnic elements
Instruments: Synthesizers, electronic drums, bronze drum samples, vocal chops
Mood: Modern, innovative, hopeful, energetic
BPM: 110-120
Key: Major, uplifting
Description: AI era meets ancient village, youth innovation, bright future for Naye Village
Keywords: AI, innovation, youth, summer camp, future, fusion
```

**Suno提示词**：
```
[Instrumental]
Future bass, electronic world fusion, Zhuang ethnic samples, modern energetic, AI innovation theme, uplifting finale, youth summer camp
```

---

## 完整版60秒配乐提示词

### Suno完整版

```
Style: Cinematic world fusion, Zhuang ethnic folk meets electronic

[0-15s] 
Ambient intro with wind soundscape, soft piano, mysterious dawn atmosphere over Yunnan highlands

[15-40s]
Zhuang folk melody on bronze drums and lusheng, building to epic crescendo, thousand-year terraced fields pride

[40-60s]
Electronic beat drops with ethnic fusion, future bass elements, uplifting finale representing AI innovation and youth

Mood: Hopeful, epic, cultural pride, futuristic
BPM progression: 60 → 100 → 120
```

### Udio完整版

```
Prompt: Cinematic world fusion music for promotional video of ancient Zhuang village rice terraces
Style: Zhuang ethnic folk, world fusion, future bass
Duration: 60 seconds
Structure: Ambient intro → Ethnic epic middle → Electronic fusion finale
Instruments: Bronze drums, lusheng, piano, synthesizers, electronic beats
Mood: Mysterious → Epic → Hopeful
Description: Promotional video music for Naye Village AI Summer Camp in Yunnan, featuring thousand-year-old rice terraces and Zhuang ethnic heritage
```

---

## 歌词版本（可选）

### Suno歌词版提示词

```
Style: World fusion pop, Zhuang ethnic influence

[Verse 1 - Soft, atmospheric]
象耕鸟耘 千年梯田
云海之上 那耶村边

[Chorus - Building, epic]
万亩梯田 层层叠叠
壮族先民 开垦天地
千年文明 在这片土壤

[Bridge - Modern, electronic]
AI时代 新的篇章
夏令营里 少年成长
那耶未来 由我们唱

[Outro - Uplifting]
象耕鸟耘 永恒传唱
那耶村 我们的家乡
```

---

## 生成工具推荐

| 工具 | 网址 | 特点 | 推荐用途 |
|------|------|------|----------|
| Suno | suno.ai | 高质量、支持歌词 | 带人声版本 |
| Udio | udio.com | 音乐性强 | 纯音乐版本 |
| MusicGen | 本地部署 | 免费、可AIX Box运行 | 本地生成 |

---

## AIX Box本地生成方案

使用MusicGen在AIX Box本地运行：

```
# 安装
pip install audiocraft

# 生成命令
python -m audiocraft.scripts.musicgen \
  --prompt "Zhuang ethnic folk meets electronic, cinematic world fusion, bronze drums, lusheng, future bass, Yunnan rice terraces, AI innovation" \
  --duration 60 \
  --output naye_theme.wav
```

---

## 使用说明

1. 复制上述提示词到Suno或Udio
2. 生成多个版本（建议3-5个）
3. 选择最贴合画面的版本
4. 根据视频剪辑调整音乐长度
5. 音视频合成

---

*为那耶村AI夏令营策划 | 2026-05-22*
