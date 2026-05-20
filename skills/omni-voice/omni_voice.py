"""
OmniVoiceStudio Skill for AIX Box
本地语音合成与克隆封装
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TTSResult:
    """TTS生成结果"""
    audio_url: str
    duration_seconds: float
    coin_hour_cost: int
    characters: int

@dataclass
class VoiceClone:
    """声音克隆结果"""
    voice_id: str
    status: str
    coin_hour_cost: int
    preview_url: str

class OmniVoice:
    """
    AIX Box本地语音服务客户端
    
    使用示例：
        >>> voice = OmniVoice()
        >>> result = voice.tts("欢迎来到AIX", language="zh-CN")
        >>> print(f"生成了{result.duration_seconds}秒音频，花费{result.coin_hour_cost} CH")
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化OmniVoice客户端
        
        Args:
            config_path: 配置文件路径，默认使用默认配置
        """
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['service']['host']}:{self.config['service']['port']}"
        self.session = requests.Session()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            "service": {
                "host": "localhost",
                "port": 8080,
                "coin_hour_enabled": True,
                "coin_hour_price_per_minute": 1
            },
            "models": {
                "tts_model": "omni-voice-base-v1",
                "language_support": 646
            },
            "storage": {
                "voice_clones_path": "./clones",
                "max_clones_per_user": 10
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def tts(self, 
            text: str,
            voice_id: str = "default-zh",
            language: str = "zh-CN",
            speed: float = 1.0,
            emotion: str = "neutral",
            output_format: str = "mp3",
            user_id: Optional[str] = None) -> TTSResult:
        """
        文字转语音
        
        Args:
            text: 要合成的文本
            voice_id: 声音ID
            language: 语言代码（支持646种）
            speed: 语速（0.5-2.0）
            emotion: 情感（neutral/happy/sad/excited）
            output_format: 输出格式（mp3/wav/ogg）
            user_id: 用户ID（用于Coin Hour计费）
        
        Returns:
            TTSResult对象
        """
        payload = {
            "text": text,
            "voice_id": voice_id,
            "language": language,
            "speed": speed,
            "emotion": emotion,
            "output_format": output_format,
            "user_id": user_id or "anonymous"
        }
        
        response = self.session.post(
            f"{self.base_url}/api/tts",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return TTSResult(
            audio_url=data["audio_url"],
            duration_seconds=data["duration_seconds"],
            coin_hour_cost=data["coin_hour_cost"],
            characters=data["characters"]
        )
    
    def clone(self,
              audio_path: str,
              voice_name: str,
              description: str = "",
              language: str = "zh-CN",
              user_id: Optional[str] = None) -> VoiceClone:
        """
        克隆声音
        
        Args:
            audio_path: 样本音频文件路径（3-30秒）
            voice_name: 克隆声音的名称
            description: 描述
            language: 语言
            user_id: 用户ID
        
        Returns:
            VoiceClone对象
        """
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            data = {
                'name': voice_name,
                'description': description,
                'language': language,
                'user_id': user_id or "anonymous"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/voice/clone",
                files=files,
                data=data,
                timeout=120
            )
        
        response.raise_for_status()
        data = response.json()
        
        return VoiceClone(
            voice_id=data["voice_id"],
            status=data["status"],
            coin_hour_cost=data["coin_hour_cost"],
            preview_url=data["preview_url"]
        )
    
    def list_voices(self, 
                    language: Optional[str] = None,
                    include_clones: bool = True) -> list:
        """
        列出可用声音
        
        Args:
            language: 筛选语言
            include_clones: 是否包含克隆声音
        
        Returns:
            声音列表
        """
        params = {
            "include_clones": include_clones
        }
        if language:
            params["language"] = language
        
        response = self.session.get(
            f"{self.base_url}/api/voices",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()["voices"]
    
    def video_dub(self,
                  video_path: str,
                  audio_text: str,
                  voice_id: str,
                  target_language: str = "zh-CN",
                  lip_sync: bool = True) -> Dict[str, Any]:
        """
        视频配音
        
        Args:
            video_path: 视频文件路径
            audio_text: 配音文本
            voice_id: 声音ID
            target_language: 目标语言
            lip_sync: 是否启用唇形同步
        
        Returns:
            配音结果
        """
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {
                'audio_text': audio_text,
                'voice_id': voice_id,
                'target_language': target_language,
                'lip_sync': lip_sync
            }
            
            response = self.session.post(
                f"{self.base_url}/api/video/dub",
                files=files,
                data=data,
                timeout=300
            )
        
        response.raise_for_status()
        return response.json()
    
    def get_coin_hour_balance(self, user_id: str) -> int:
        """查询用户Coin Hour余额"""
        response = self.session.get(
            f"{self.base_url}/api/balance/{user_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()["balance"]


# DeepTutor集成辅助函数

def create_tutor_voice(omni_voice: OmniVoice, 
                       tutor_name: str,
                       sample_audio: Optional[str] = None) -> str:
    """
    为TutorBot创建声音
    
    Args:
        omni_voice: OmniVoice实例
        tutor_name: 导师名称
        sample_audio: 样本音频路径（可选，默认使用系统声音）
    
    Returns:
        voice_id
    """
    if sample_audio:
        clone = omni_voice.clone(
            audio_path=sample_audio,
            voice_name=f"tutor-{tutor_name}",
            description=f"{tutor_name}的专属声音"
        )
        return clone.voice_id
    else:
        # 使用默认系统声音
        return f"default-tutor-{tutor_name.lower().replace(' ', '-')}"


def speak_tutor_response(omni_voice: OmniVoice,
                        tutor_id: str,
                        text: str,
                        emotion: str = "neutral") -> TTSResult:
    """
    TutorBot说话
    
    Args:
        omni_voice: OmniVoice实例
        tutor_id: 导师ID
        text: 要说的文本
        emotion: 情感
    
    Returns:
        TTS结果
    """
    voice_mapping = {
        "sovereignty": "aix-tutor-sovereignty",
        "tech": "aix-tutor-tech",
        "product": "aix-tutor-product",
        "business": "aix-tutor-business"
    }
    
    voice_id = voice_mapping.get(tutor_id, "default-zh")
    
    return omni_voice.tts(
        text=text,
        voice_id=voice_id,
        emotion=emotion,
        language="zh-CN"
    )


if __name__ == "__main__":
    # 测试代码
    print("🎙️ OmniVoiceStudio AIX Skill Test")
    print("-" * 50)
    
    voice = OmniVoice()
    
    # 测试TTS
    print("\n1. 测试文字转语音...")
    result = voice.tts("欢迎来到AIX生态系统，这是本地语音合成测试。")
    print(f"✅ 生成成功: {result.duration_seconds}秒, 花费{result.coin_hour_cost} CH")
    print(f"📁 音频文件: {result.audio_url}")
    
    # 测试列出声音
    print("\n2. 列出可用声音...")
    voices = voice.list_voices(language="zh-CN")
    print(f"✅ 找到{len(voices)}个中文声音")
    for v in voices[:3]:
        print(f"   - {v['name']} ({v['type']})")
    
    print("\n✅ 所有测试通过！")
