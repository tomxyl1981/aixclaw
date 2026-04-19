# AIX Box "百万美元架构师" Skill 系统

> 基于 Dan Koe 的超级个体生存法则
> 生成日期：2026-04-19

---

## Dan Koe 的核心框架

### 三支柱系统

| 支柱 | 定义 | 核心价值 |
|------|------|----------|
| **品牌** | 信任容器 | 独特经历+硬核技能+两个痴迷兴趣 = 人设护城河 |
| **内容** | 生态杠杆 | 深度通讯→AI裂变→推文/短视频/YouTube = 信任飞轮 |
| **供给** | 变现终端 | 流量→精准转化→订单 = 收入 |

### 关键公式

```
年入百万 = 每天18份 × 150美元产品
         = 2.5%转化率 × 720精准访客/天
         = 持续输出 × 高转化供给
```

### 三步法

```
输入 → 顶级素材（喂给AI拆解爆款逻辑）
提纯 → 自己的洞察（重构内容）
架构 → 一源多用（AI裂变多平台）
```

### 关键认知

> "不是找AI代劳，而是让AI当文案教练，把同质化内容海变成你的护城河。"

---

## 如何转化为 AIX Box Skill 系统

### Skill 架构

```
AIX Box "百万美元架构师" Skill Pack
├── 品牌定位 Skill
├── 内容裂变 Skill
├── 变现优化 Skill
└── 知识库 Skill
```

---

## Skill 1：品牌定位 Skill

### 功能

帮助用户找到自己的"独特性护城河"

### 输入

- 用户经历（AI访谈提取）
- 技能清单（硬核技能）
- 两个痴迷兴趣（用户自己定义）

### 输出

- 品牌定位文档（类似DESIGN.md，但是针对个人品牌）
- 人设关键词列表
- 差异化主张（一句话说清楚你和别人有什么不同）

### 技术实现

```python
class BrandPositioningSkill:
    def analyze_uniqueness(self, experience, skills, interests):
        prompt = f"""
        分析这个人的独特性：
        
        经历：{experience}
        技能：{skills}
        两个痴迷兴趣：{interests}
        
        输出：
        1. 品牌关键词（3-5个）
        2. 人设差异化主张（一句话）
        3. 潜在受众痛点（5个）
        4. 可切入的内容方向（3个）
        """
        return pico_claw.generate(prompt)
    
    def create_brand_document(self):
        # 生成类似DESIGN.md的个人品牌文档
        pass
```

### Coin Hour 消耗

- 品牌定位分析：10 Coin Hour
- 品牌文档生成：20 Coin Hour

---

## Skill 2：内容裂变 Skill

### 功能

"一源多用"的生态杠杆系统

### 输入

- 深度通讯/长文/视频脚本（源内容）
- 目标平台（Twitter、抖音、小红书、YouTube）
- 目标受众

### 输出

- 推文版本（280字精华）
- 短视频脚本（30秒-60秒）
- 长视频脚本（YouTube）
- 简报版本（Newsletter）

### 技术实现

```python
class ContentLeverageSkill:
    def input_to_insight(self, source_content):
        # 第一步：输入 → 提纯
        prompt = f"""
        分析这篇内容的洞察点：
        {source_content}
        
        提取：
        1. 核心洞察（1个）
        2. 支撑论点（3个）
        3. 可执行建议（3个）
        4. 金句（5个）
        """
        return pico_claw.generate(prompt)
    
    def insight_to_multipublish(self, insight, platforms):
        # 第二步：提纯 → 架构（多平台裂变）
        outputs = {}
        for platform in platforms:
            outputs[platform] = self.adapt_for_platform(insight, platform)
        return outputs
    
    def adapt_for_platform(self, insight, platform):
        if platform == "twitter":
            return self.to_tweet(insight)
        elif platform == "douyin":
            return self.to_short_video(insight)
        elif platform == "youtube":
            return self.to_long_video(insight)
        elif platform == "newsletter":
            return self.to_newsletter(insight)
```

### AI 当教练（而非代劳）

关键实现：**不是AI直接生成内容，而是AI给用户反馈**

```python
class ContentCoachMode:
    def review_content(self, user_draft, platform):
        prompt = f"""
        你是文案教练，点评用户的内容：
        
        用户草稿：{user_draft}
        平台：{platform}
        
        点评维度：
        1. 开头是否抓人？
        2. 中间是否有情绪波动？
        3. 结尾是否有行动呼唤？
        4. 是否符合用户的品牌调性？
        
        给出3条具体改进建议，而不是直接改写。
        """
        return pico_claw.generate(prompt)
```

### Coin Hour 消耗

- 内容裂变（1源→4平台）：50 Coin Hour
- AI教练点评（单次）：5 Coin Hour

---

## Skill 3：变现优化 Skill

### 功能

帮助用户设计"高转化供给"

### 输入

- 用户技能/知识资产
- 目标收入（如年入百万）
- 可投入时间

### 输出

- 产品设计建议（什么产品、定价多少）
- 转化路径设计（从流量到订单）
- 每日目标算账（需要多少访客、多少转化）

### 技术实现

```python
class MonetizationSkill:
    def design_product(self, skill_asset, target_income):
        prompt = f"""
        用户技能资产：{skill_asset}
        目标年收入：{target_income}
        
        设计产品矩阵：
        1. 低客单产品（$50-$200）：每天销售目标
        2. 中客单产品（$500-$2000）：每周销售目标
        3. 高客单产品（$2000+）：每月销售目标
        
        输出：
        1. 产品类型建议
        2. 定价策略
        3. 销售目标分解（年→月→周→日）
        4. 转化率估算
        """
        return pico_claw.generate(prompt)
    
    def calculate_daily_targets(self, yearly_goal, product_price, conversion_rate):
        daily_revenue = yearly_goal / 365
        daily_sales = daily_revenue / product_price
        daily_visitors = daily_sales / conversion_rate
        
        return {
            "daily_revenue_target": daily_revenue,
            "daily_sales_target": daily_sales,
            "daily_visitor_target": daily_visitors,
            "monthly_visitor_target": daily_visitors * 30
        }
```

### 案例：年入百万的算账

```python
skill = MonetizationSkill()
result = skill.calculate_daily_targets(
    yearly_goal=1000000,
    product_price=150,  # $150美元产品
    conversion_rate=0.025  # 2.5%转化率
)

# 输出：
{
    "daily_revenue_target": 2740,  # 日收入目标
    "daily_sales_target": 18,  # 每天卖18份
    "daily_visitor_target": 720,  # 每天需要720精准访客
    "monthly_visitor_target": 21600  # 月需要2.16万访客
}
```

### Coin Hour 消耗

- 产品设计分析：30 Coin Hour
- 目标算账：10 Coin Hour
- 转化路径优化：20 Coin Hour

---

## Skill 4：知识库 Skill

### 功能

持续学习，积累洞察——这是"输入"的源头

### 输入

- 用户每天阅读的内容（文章、视频、书籍）
- 学习笔记
- 行业动态

### 输出

- 洞察卡片库（可随时调用的素材）
- 每周洞察简报
- 热点追踪报告

### 技术实现

```python
class KnowledgeBaseSkill:
    def __init__(self):
        self.knowledge_store = IPFS()  # 本地存储
    
    def consume_content(self, content_url, source_type):
        # 抓取内容（用Firecrawl）
        if source_type == "web":
            content = firecrawl.scrape(content_url)
        elif source_type == "video":
            content = self.extract_transcript(content_url)
        elif source_type == "book":
            content = self.extract_highlights(content_url)
        
        return self.extract_insights(content)
    
    def extract_insights(self, content):
        prompt = f"""
        从以下内容提取洞察：
        {content}
        
        输出格式：
        1. 核心观点（1个）
        2. 惊人事实（1个）
        3. 可执行建议（3个）
        4. 金句（3个）
        5. 可关联的我的经历/观点（2个）
        """
        insights = pico_claw.generate(prompt)
        
        # 存入本地IPFS
        self.knowledge_store.save(insights)
        
        return insights
    
    def weekly_digester(self):
        # 每周生成洞察简报
        weekly_insights = self.knowledge_store.get_this_week()
        
        prompt = f"""
        基于本周学习的洞察，生成周报：
        {weekly_insights}
        
        输出：
        1. 本周最重要的3个洞察
        2. 可以展开写的3个内容方向
        3. 行动建议
        """
        return pico_claw.generate(prompt)
```

### Coin Hour 消耗

- 内容洞察提取：5 Coin Hour/篇
- 周报生成：10 Coin Hour/周

---

## 完整工作流

### 用户日常流程（超级个体的一天）

```
早晨（30分钟）：
1. 阅读3篇行业文章 → 知识库Skill提取洞察
2. 消耗 15 Coin Hour

午间（1小时）：
3. 查看本周洞察简报 → 选择一个方向展开
4. 写深度内容草稿 → 内容裂变Skill教练模式点评
5. 根据反馈修改 → AI裂变多平台版本
6. 消耗 60 Coin Hour

晚间（30分钟）：
7. 查看当日数据（访客、转化、收入）
8. 变现优化Skill给出建议
9. 消耗 10 Coin Hour

总消耗：85 Coin Hour/天 ≈ 85元/天（持有AIX产出可覆盖）
```

---

## Skill Store 上架方案

### 定价策略

| Skill | 单次价格 | 月卡价格 | 说明 |
|-------|---------|---------|------|
| 品牌定位 | 30 CH | 200 CH | 一次性，可多次迭代 |
| 内容裂变 | 50 CH | 300 CH | 高频使用，月卡划算 |
| 变现优化 | 60 CH | 400 CH | 中频使用 |
| 知识库 | 100 CH | 600 CH | 持续使用，本地存储 |

### 套餐组合

- **入门包**：品牌定位 + 内容裂变 = 400 Coin Hour/月
- **进阶包**：品牌 + 内容 + 变现 = 700 Coin Hour/月
- **全套**：四合一 = 1200 Coin Hour/月

---

## 与其他项目的协同

| 项目 | 协同方式 |
|------|----------|
| **DESIGN.md** | 品牌定位输出品牌DESIGN.md文档 |
| **Firecrawl** | 知识库Skill抓取行业内容 |
| **预测市场** | 变现优化Skill分析市场机会 |
| **AI电商** | 用户产品上架到预测电商平台 |
| **那耶村** | 艺术家用这些Skill打造个人品牌 |

---

## 金句

> "Dan Koe 说让AI当教练，AIX Box 的 Skill 就是你的私人教练。"

> "年入百万的算账公式，变现优化 Skill 帮你算清楚。"

> "知识库 Skill 让你每天学习的内容变成可随时调用的洞察卡片。"

> "内容裂变 Skill不是帮你写，是帮你一源多用——写一次，裂变四次。"

---

## 总结

**Dan Koe 的三支柱系统** → **AIX Box 四大 Skill**：

| Dan Koe | AIX Box Skill |
|---------|--------------|
| 品牌（信任容器） | 品牌定位 Skill |
| 内容（生态杠杆） | 内容裂变 Skill |
| 供给（变现终端） | 变现优化 Skill |
| 输入（学习积累） | 知识库 Skill |

**核心理念一致**：
- Dan Koe："不是AI代劳，是AI当教练"
- AIX Box："LLM打工，代码做主"——Skill是确定性规则，AI执行

**经济闭环**：
- 用户囤AIX → 产出Coin Hour → 购买Skill → 使用Skill → 提升收入 → 更多Coin Hour

---

*生成时间：2026-04-19（UTC）*
