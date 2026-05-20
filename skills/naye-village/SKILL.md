# 那耶村专属技能库

> AIX那耶村MVP场景的本地AI能力
> 基于Skill Graphs 2.0框架设计
> 最后更新：2026-05-09

---

## 技能概述

那耶村（云南文山富宁梯田艺术村）是AIX第一个MVP场景。本技能库为那耶村提供本地AI能力，支持数字主权理念。

---

## 原子技能（Atomic Skills）

### 1. 方言识别与转换

```yaml
name: naye-dialect-recognize
description: 那耶村方言识别与标准文本转换
input:
  - speech/audio
  - text/local-dialect
output:
  - text/standard-chinese
coin_hour: 1
tech_stack:
  - Deepgram（语音识别）
  - MiniMind（本地模型，本地语料训练）
```

### 2. 梯田知识查询

```yaml
name: naye-terrace-knowledge
description: 梯田文化知识检索
input:
  - query_keyword
output:
  - knowledge_card
coin_hour: 0.5
tech_stack:
  - Awareness-Local（记忆存储）
  - Graphify（知识图谱）
memory_source:
  - 梯田历史文档
  - 农耕文化资料
  - 本地口述历史
```

### 3. 民宿推荐

```yaml
name: naye-homestay-recommend
description: 那耶村民宿智能推荐
input:
  - guest_preferences
  - budget_range
  - stay_duration
output:
  - homestay_list
  - recommendation_reason
coin_hour: 2
tech_stack:
  - Composio（预订平台API）
  - Awareness-Local（民宿数据库）
data_source:
  - 民宿房源数据
  - 评价历史
  - 房间图片
```

### 4. 美食推荐

```yaml
name: naye-cuisine-recommend
description: 梯田美食智能推荐
input:
  - taste_preference
  - budget_range
  - dietary_restrictions
output:
  - dish_list
  - restaurant_info
coin_hour: 2
tech_stack:
  - Awareness-Local（美食数据库）
  - Tavily（本地餐厅搜索）
specialties:
  - 梯田鸭
  - 稻田鱼
  - 五色糯米饭
  - 野生菌
```

### 5. 路线规划

```yaml
name: naye-route-planning
description: 梯田游览路线智能规划
input:
  - available_time
  - physical_ability
  - interests
output:
  - tour_route
  - estimated_time
  - difficulty_level
coin_hour: 5
tech_stack:
  - Arnis（地理数据）
  - Graphify（景点关系图谱）
  - Awareness-Local（历史路线记忆）
landmarks:
  - 观景台
  - 体验区
  - 民宿区
  - 美食区
  - 文化展示区
```

### 6. 文化讲解生成

```yaml
name: naye-culture-story
description: 梯田文化故事生成
input:
  - topic_keyword
  - audience_age
  - language_style
output:
  - story_text
  - voice_audio（可选）
coin_hour: 5
tech_stack:
  - ms-swift（本地模型）
  - ElevenLabs（语音合成）
  - Awareness-Local（文化知识库）
content_types:
  - 梯田历史
  - 农耕技术
  - 民族文化
  - 传说故事
```

### 7. 短剧生成

```yaml
name: naye-short-video
description: 那耶村宣传短剧生成
input:
  - story_keyword
  - duration_target
output:
  - video_file
coin_hour: 20-50
tech_stack:
  - deep-comedy-pro（短剧生成）
  - Browser Harness（自动发布）
  - Awareness-Local（素材库）
themes:
  - 梯田四季
  - 民宿故事
  - 美食探店
  - 农耕体验
```

### 8. 虚拟导览

```yaml
name: naye-virtual-tour
description: Minecraft虚拟梯田导览
input:
  - guest_id
output:
  - minecraft_access
  - tour_guide_npc
coin_hour: 10
tech_stack:
  - Arnis（地理生成）
  - Minecraft服务器
  - AIX Box（本地托管）
features:
  - 虚拟梯田探索
  - NPC导览讲解
  - 预订转化入口
```

---

## 分子技能（Molecular Skills）

### 1. 游客需求分析

```yaml
name: naye-guest-analysis
description: 游客需求综合分析
atomic_skills:
  - naye-dialect-recognize
  - naye-terrace-knowledge
  - intent_recognition
coin_hour: 5
workflow:
  1. 方言识别转换
  2. 需求意图提取
  3. 历史偏好匹配
  4. 个性化建议生成
```

### 2. 导览路线生成

```yaml
name: naye-tour-route
description: 完整导览路线生成
atomic_skills:
  - naye-route-planning
  - naye-terrace-knowledge
  - naye-culture-story
coin_hour: 15
workflow:
  1. 路线规划
  2. 景点知识匹配
  3. 讲解内容生成
  4. 时间估算
```

### 3. 服务推荐组合

```yaml
name: naye-service-recommend
description: 住宿餐饮特产综合推荐
atomic_skills:
  - naye-homestay-recommend
  - naye-cuisine-recommend
  - naye-terrace-knowledge
coin_hour: 10
workflow:
  1. 民宿推荐
  2. 美食推荐
  3. 特产推荐
  4. 预订链接生成
```

---

## 复合技能（Composite Skills）

### 1. 梯田导览全流程

```yaml
name: naye-full-tour-service
description: 那耶村梯田导览完整服务
molecular_skills:
  - naye-guest-analysis
  - naye-tour-route
  - naye-service-recommend
coin_hour: 50-100
workflow:
  1. 游客需求分析
  2. 导览路线生成
  3. 文化讲解（实时）
  4. 服务推荐
  5. 预订处理
  6. 反馈收集
output:
  - 个性化导览体验
  - 服务预订确认
  - Coin Hour消费记录
```

### 2. 短剧制作发布

```yaml
name: naye-video-production
description: 那耶村宣传短剧制作与发布
molecular_skills:
  - naye-short-video
  - content_optimization
  - multi_platform_publish
coin_hour: 100-200
workflow:
  1. 选题策划
  2. 短剧生成
  3. 内容优化
  4. 多平台发布（Browser Harness）
  5. 效果追踪
output:
  - 抖音/快手短剧
  - Coin Hour创作者收益
```

### 3. 虚拟+实体联动

```yaml
name: naye-virtual-real-tour
description: 虚拟梯田导览→实体转化
molecular_skills:
  - naye-virtual-tour
  - naye-full-tour-service
coin_hour: 150-300
workflow:
  1. Minecraft虚拟导览
  2. 兴趣点标记
  3. 实体预订转化
  4. 到村服务衔接
output:
  - 虚拟体验→实体消费转化
  - Coin Hour双重计费
```

---

## Coin Hour定价汇总

| 技能层级 | 技能名称 | Coin Hour |
|---------|---------|----------|
| **原子技能** | | |
| 方言识别 | naye-dialect-recognize | 1 CH |
| 梯田知识 | naye-terrace-knowledge | 0.5 CH |
| 民宿推荐 | naye-homestay-recommend | 2 CH |
| 美食推荐 | naye-cuisine-recommend | 2 CH |
| 路线规划 | naye-route-planning | 5 CH |
| 文化讲解 | naye-culture-story | 5 CH |
| 短剧生成 | naye-short-video | 20-50 CH |
| 虚拟导览 | naye-virtual-tour | 10 CH |
| **分子技能** | | |
| 游客分析 | naye-guest-analysis | 5 CH |
| 导览路线 | naye-tour-route | 15 CH |
| 服务推荐 | naye-service-recommend | 10 CH |
| **复合技能** | | |
| 梯田导览全流程 | naye-full-tour-service | 50-100 CH |
| 短剧制作发布 | naye-video-production | 100-200 CH |
| 虚拟+实体联动 | naye-virtual-real-tour | 150-300 CH |

---

## 技术栈整合

```
那耶村技能库技术栈：

[AIX Box] ← 硬件层治理（本地托管）
    ↓
[Awareness-Local] ← 记忆层（那耶村知识库）
    ↓
[Skills Manager] ← 技能管理（统一同步）
    ↓
那耶村专属技能
├── 原子技能（8个）
├── 分子技能（3个）
└── 复合技能（3个）
    ↓
[OpenClaw Agent] ← 运行时
    ↓
[Composio/Tavily/Browser Harness] ← 工具层
    ↓
Coin Hour计费 + UTXO审计
```

---

## 实施路线

### Phase 1：数据准备（1周）

- [ ] 收集梯田文化文档
- [ ] 整理民宿美食数据
- [ ] 建立景点地理数据
- [ ] 录制本地方言语料

### Phase 2：原子技能开发（2周）

- [ ] 训练方言识别MiniMind模型
- [ ] 构建梯田知识Graphify图谱
- [ ] 建立民宿美食数据库
- [ ] Arnis生成那耶村Minecraft世界

### Phase 3：技能组合测试（1周）

- [ ] 测试分子技能组合
- [ ] 测试复合技能全流程
- [ ] Coin Hour计费对接

### Phase 4：实地部署（2周）

- [ ] AIX Box部署到那耶村
- [ ] 村民培训
- [ ] 真实游客测试
- [ ] 反馈优化

---

## 数据主权保障

所有那耶村技能遵循数字主权原则：

| 原则 | 实现 |
|------|------|
| 数据本地存储 | Awareness-Local + AIX Box |
| 无云端依赖 | 离线可用 |
| Coin Hour内循环 | 不换法币 |
| UTXO审计 | 每笔可追溯 |
| 村民可编辑 | Markdown透明 |

---

*持续更新中*
