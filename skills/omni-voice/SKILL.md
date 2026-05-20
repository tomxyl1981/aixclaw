# OmniVoiceStudio Skill for AIX

## Description
AIX Box本地语音合成与克隆能力封装。开源ElevenLabs替代，支持646种语言，3秒音频零样本克隆，完全本地运行保护数据主权。

## Author
AIX Foundation

## Version
1.0.0

## Requirements
- AIX Box with GPU support (or Mac mini M4 for CPU inference)
- 8GB+ RAM
- 5GB storage for models
- Docker or Python 3.10+

## Installation

### Option 1: Docker部署（推荐）
```bash
# 拉取OmniVoiceStudio镜像
docker pull aix-ecosystem/omni-voice:latest

# 启动服务
docker run -d \
  --name omni-voice \
  -p 8080:8080 \
  -v ./models:/app/models \
  -v ./clones:/app/clones \
  aix-ecosystem/omni-voice:latest
```

### Option 2: AIX Box原生集成
```bash
# 安装依赖
pip install omni-voice-studio

# 下载模型（约4GB）
omni-voice download-models

# 启动服务
omni-voice serve --port 8080
```

## Configuration

### config.json
```json
{
  "service": {
    "host": "localhost",
    "port": 8080,
    "coin_hour_enabled": true,
    "coin_hour_price_per_minute": 1
  },
  "models": {
    "tts_model": "omni-voice-base-v1",
    "clone_model": "omni-voice-clone-v1",
    "language_support": 646
  },
  "storage": {
    "voice_clones_path": "./clones",
    "max_clones_per_user": 10,
    "retention_days": 365
  },
  "aix_integration": {
    "utxo_ledger_url": "http://localhost:8545",
    "auto_billing": true,
    "default_voice": "aix-tutor-default"
  }
}
```

## Tools

### 1. tts.generate
文字转语音

**Input:**
```json
{
  "text": "欢迎来到AIX生态系统",
  "voice_id": "default-zh",
  "language": "zh-CN",
  "speed": 1.0,
  "emotion": "neutral",
  "output_format": "mp3"
}
```

**Output:**
```json
{
  "audio_url": "/audio/output-xxx.mp3",
  "duration_seconds": 3.5,
  "coin_hour_cost": 4,
  "characters": 12
}
```

### 2. voice.clone
克隆声音

**Input:**
```json
{
  "audio_sample": "/uploads/sample-xxx.wav",
  "voice_name": "my-voice-01",
  "description": "我的个人声音克隆",
  "language": "zh-CN"
}
```

**Requirements:**
- 音频长度：3-30秒
- 格式：WAV/MP3/M4A
- 采样率：22050Hz+
- 信噪比：>20dB

**Output:**
```json
{
  "voice_id": "clone-xxx-xxx",
  "status": "ready",
  "coin_hour_cost": 50,
  "preview_url": "/audio/preview-xxx.mp3"
}
```

### 3. voice.list
列出可用声音

**Input:**
```json
{
  "filter": "all",
  "include_clones": true,
  "language": "zh-CN"
}
```

**Output:**
```json
{
  "voices": [
    {"id": "default-zh", "name": "默认中文", "type": "system"},
    {"id": "clone-xxx", "name": "我的声音", "type": "clone"}
  ]
}
```

### 4. video.dub
视频配音（唇形同步）

**Input:**
```json
{
  "video_url": "/uploads/video-xxx.mp4",
  "audio_text": "这是新的配音内容",
  "target_language": "en-US",
  "voice_id": "clone-xxx",
  "lip_sync": true
}
```

**Output:**
```json
{
  "video_url": "/video/dubbed-xxx.mp4",
  "duration": 120,
  "coin_hour_cost": 120
}
```

## Coin Hour定价

| 服务 | 定价 | 说明 |
|------|------|------|
| TTS生成 | 1 CH/分钟 | 按输出音频时长计费 |
| 声音克隆 | 50 CH/次 | 一次性费用，永久使用 |
| 视频配音 | 1 CH/分钟 | 含唇形同步 |
| API调用 | 0.1 CH/次 | 查询类操作 |

## AIX TutorBot集成

### DeepTutor配置
```yaml
tutor_bots:
  - name: "数字主权导师"
    voice_id: "aix-tutor-sovereignty"
    language: "zh-CN"
    emotion_profile: "warm_authoritative"
  
  - name: "技术导师"
    voice_id: "aix-tutor-tech"
    language: "zh-CN"
    emotion_profile: "enthusiastic"
```

### 自动语音生成
当TutorBot回复时，自动调用OmniVoiceStudio生成语音：
```python
def on_tutor_response(text, tutor_id):
    voice = get_tutor_voice(tutor_id)
    audio = omni_voice.tts.generate(
        text=text,
        voice_id=voice.id,
        auto_bill=True  # 自动扣除Coin Hour
    )
    return {"text": text, "audio": audio.url}
```

## 那耶村应用场景

### 1. 多语言导游系统
```python
# 游客扫码触发
def tourist_guide(spot_id, user_language):
    content = get_spot_content(spot_id)
    
    # 自动翻译+语音生成
    translated = translate(content, user_language)
    audio = omni_voice.tts.generate(
        text=translated,
        language=user_language,
        voice_id=f"guide-{user_language}"
    )
    
    # 记录到UTXO账本
    record_consumption(spot_id, "audio_guide", 5)  # 5 CH
    
    return audio
```

### 2. 农产品直播配音
```python
def product_livestream(product_id, script):
    # 克隆农户声音
    farmer_voice = omni_voice.voice.clone(
        audio_sample=f"farmers/{product_id}/voice.wav",
        voice_name=f"farmer-{product_id}"
    )
    
    # 生成直播语音
    for segment in script:
        audio = omni_voice.tts.generate(
            text=segment,
            voice_id=farmer_voice.id,
            emotion="enthusiastic"
        )
        stream_audio(audio)
```

### 3. 老人陪伴（子女声音克隆）
```python
def elder_companion(elder_id, child_audio_sample):
    # 克隆子女声音
    child_voice = omni_voice.voice.clone(
        audio_sample=child_audio_sample,
        voice_name=f"child-of-{elder_id}"
    )
    
    # 定时播报天气/提醒
    def daily_reminder():
        weather = get_weather()
        text = f"妈妈，今天{weather}，记得带伞。"
        audio = omni_voice.tts.generate(
            text=text,
            voice_id=child_voice.id
        )
        play_in_room(elder_id, audio)
```

## 数据主权保障

### 本地运行原则
```
用户音频 → AIX Box本地处理 → 本地存储
   ↓
不上传云端
   ↓
Coin Hour结算通过本地UTXO账本
```

### 隐私设置
```json
{
  "privacy": {
    "allow_voice_sharing": false,
    "auto_delete_after_days": 365,
    "encrypt_clones": true,
    "audit_log": true
  }
}
```

## 性能基准（Mac mini M4）

| 任务 | 性能 | 延迟 |
|------|------|------|
| TTS生成 | 10x实时 | <100ms首字节 |
| 声音克隆 | 3秒样本→30秒处理 | 30秒 |
| 视频配音（唇形同步） | 0.5x实时 | 2x视频时长 |

## API参考

### RESTful API

```bash
# TTS
curl -X POST http://localhost:8080/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，AIX",
    "voice_id": "default-zh",
    "user_id": "user-xxx"
  }'

# 克隆
curl -X POST http://localhost:8080/api/voice/clone \
  -F "audio=@sample.wav" \
  -F "name=my-voice" \
  -F "user_id=user-xxx"
```

### Python SDK
```python
from aix_skills import OmniVoice

voice = OmniVoice()

# TTS
audio = voice.tts("你好，AIX", voice_id="default-zh")
audio.save("output.mp3")

# 克隆
clone = voice.clone("sample.wav", name="我的声音")

# 使用克隆声音
audio = voice.tts("这是克隆的声音", voice_id=clone.id)
```

## Roadmap

- [x] v1.0.0 基础TTS与克隆
- [ ] v1.1.0 实时语音对话
- [ ] v1.2.0 情感控制增强
- [ ] v1.3.0 多说话人分离
- [ ] v2.0.0 与AIX Box硬件深度集成

## License
MIT License - 与OmniVoiceStudio保持一致

## 相关链接
- OmniVoiceStudio: https://github.com/depalash/OmniVoiceStudio
- AIX Docs: https://docs.aix.foundation
- Coin Hour Spec: https://docs.aix.foundation/coin-hour
