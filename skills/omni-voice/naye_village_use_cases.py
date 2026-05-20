"""
那耶村OmniVoiceStudio应用场景
"""

from omni_voice import OmniVoice, create_tutor_voice, speak_tutor_response
from typing import List, Dict
import json

class NayeVillageVoiceSystem:
    """那耶村语音系统"""
    
    def __init__(self):
        self.voice = OmniVoice()
        self.spots = self._load_tourist_spots()
        
    def _load_tourist_spots(self) -> Dict:
        """加载景点数据"""
        return {
            "spot-001": {
                "name": "那耶梯田观景台",
                "description": "那耶村最佳摄影点，可俯瞰千亩梯田",
                "stories": [
                    "那耶梯田始于明代，已有500年历史...",
                    "每年春季，村民们会举行开耕节..."
                ]
            },
            "spot-002": {
                "name": "百年古榕树",
                "description": "村里最古老的榕树，树龄超过300年",
                "stories": [
                    "这棵榕树见证了那耶村的兴衰...",
                    "每年农历三月三，村民会来这里祈福..."
                ]
            },
            "spot-003": {
                "name": "古法造纸坊",
                "description": "传承百年的手工造纸技艺",
                "stories": [
                    "那耶村的造纸术源自中原...",
                    "一张手工纸需要经过72道工序..."
                ]
            }
        }
    
    def get_spot_audio_guide(self, spot_id: str, user_language: str = "zh-CN") -> Dict:
        """
        获取景点语音导览
        
        Args:
            spot_id: 景点ID
            user_language: 用户语言（支持646种）
        
        Returns:
            音频URL和元数据
        """
        spot = self.spots.get(spot_id)
        if not spot:
            return {"error": "景点不存在"}
        
        # 构建导览内容
        content = f"欢迎来到{spot['name']}。{spot['description']}"
        if spot['stories']:
            content += f"让我为您讲述这里的故事：{spot['stories'][0]}"
        
        # 自动翻译（如果非中文）
        if user_language != "zh-CN":
            content = self._translate(content, user_language)
        
        # 生成语音
        result = self.voice.tts(
            text=content,
            language=user_language,
            voice_id=f"guide-{user_language}",
            emotion="warm"
        )
        
        # 记录消费（5 CH一次）
        self._record_consumption("tourist_guide", 5, spot_id)
        
        return {
            "spot_name": spot['name'],
            "audio_url": result.audio_url,
            "duration": result.duration_seconds,
            "language": user_language,
            "cost": 5
        }
    
    def create_farmer_livestream_voice(self, farmer_id: str, sample_audio: str) -> str:
        """
        为农户创建直播声音克隆
        
        Args:
            farmer_id: 农户ID
            sample_audio: 农户声音样本路径
        
        Returns:
            voice_id
        """
        clone = self.voice.clone(
            audio_path=sample_audio,
            voice_name=f"farmer-{farmer_id}",
            description=f"农户{farmer_id}的直播声音",
            language="zh-CN"
        )
        
        print(f"✅ 已为农户{farmer_id}克隆声音: {clone.voice_id}")
        return clone.voice_id
    
    def generate_product_pitch(self, 
                              product_name: str,
                              farmer_voice_id: str,
                              highlights: List[str]) -> str:
        """
        生成农产品推销语音
        
        Args:
            product_name: 产品名称
            farmer_voice_id: 农户声音ID
            highlights: 卖点列表
        
        Returns:
            音频URL
        """
        # 构建推销话术
        script = f"大家好，我是那耶村的农户。今天给大家带来的{product_name}，"
        script += "是我们用传统方法种植的。" + "。".join(highlights)
        script += "支持我们，就是支持乡村振兴！"
        
        result = self.voice.tts(
            text=script,
            voice_id=farmer_voice_id,
            emotion="enthusiastic",
            speed=0.95  # 稍慢一点，更有亲和力
        )
        
        return result.audio_url
    
    def create_elder_companion(self, 
                              elder_id: str,
                              child_audio_sample: str) -> Dict:
        """
        为老人创建子女声音陪伴系统
        
        Args:
            elder_id: 老人ID
            child_audio_sample: 子女声音样本
        
        Returns:
            配置信息
        """
        # 克隆子女声音
        clone = self.voice.clone(
            audio_path=child_audio_sample,
            voice_name=f"child-of-{elder_id}",
            description=f"{elder_id}的子女声音"
        )
        
        # 创建定时提醒配置
        schedule_config = {
            "morning": {
                "time": "08:00",
                "messages": [
                    "妈，早上好！记得吃早餐。",
                    "今天天气不错，可以出去走走。",
                    "别忘了吃降压药。"
                ]
            },
            "noon": {
                "time": "12:00",
                "messages": [
                    "爸，该吃午饭了。",
                    "别吃太多油腻的。"
                ]
            },
            "evening": {
                "time": "20:00",
                "messages": [
                    "妈，晚上好，早点休息。",
                    "明天早上我再提醒您吃药。"
                ]
            }
        }
        
        # 保存配置
        config_path = f"/config/elder-companion/{elder_id}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({
                "elder_id": elder_id,
                "voice_id": clone.voice_id,
                "schedule": schedule_config,
                "cost": clone.coin_hour_cost
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已为老人{elder_id}创建子女声音陪伴系统")
        print(f"   花费: {clone.coin_hour_cost} CH")
        
        return {
            "voice_id": clone.voice_id,
            "config_path": config_path,
            "cost": clone.coin_hour_cost
        }
    
    def _translate(self, text: str, target_language: str) -> str:
        """翻译文本（简化版，实际集成翻译API）"""
        # 这里可以集成AIX的翻译Skill
        # 简化演示：假设有翻译服务
        return f"[{target_language}] {text}"
    
    def _record_consumption(self, service_type: str, cost: int, reference: str):
        """记录消费到UTXO账本"""
        # 实际集成AIX账本
        print(f"💰 记录消费: {service_type} - {cost} CH - {reference}")


# 使用示例
def demo():
    """那耶村语音系统演示"""
    print("🌾 那耶村OmniVoiceStudio应用场景演示")
    print("=" * 60)
    
    system = NayeVillageVoiceSystem()
    
    # 场景1: 景点语音导览
    print("\n📍 场景1: 游客扫码获取语音导览")
    guide = system.get_spot_audio_guide("spot-001", "zh-CN")
    print(f"✅ 已生成: {guide['spot_name']}")
    print(f"   音频: {guide['audio_url']}")
    print(f"   花费: {guide['cost']} CH")
    
    # 场景2: 多语言支持
    print("\n🌍 场景2: 国际游客（英文）")
    guide_en = system.get_spot_audio_guide("spot-001", "en-US")
    print(f"✅ 英文导览已生成: {guide_en['audio_url']}")
    
    # 场景3: 农户直播
    print("\n📺 场景3: 农产品直播配音")
    highlights = [
        "纯天然种植，不打农药",
        "口感软糯，香甜可口",
        "现摘现发，新鲜直达"
    ]
    # 假设已有克隆的声音
    pitch_audio = system.generate_product_pitch(
        product_name="那耶梯田红米",
        farmer_voice_id="farmer-001",
        highlights=highlights
    )
    print(f"✅ 推销语音已生成: {pitch_audio}")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    demo()
