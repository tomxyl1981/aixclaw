# AIX Box + Harness Design: 个性化 AI 审美系统

> 将 Anthropic 的 Harness Design 整合进 AIX Box，实现本地化的 AI 输出质量监控与个性化审美注入

---

## 一、Anthropic Harness Design 核心概念

### 1.1 什么是 Harness Design？

**原文核心观点**:
- 长期运行的 AI 应用需要**持续评估机制**
- 不是一次性对话，而是**持续服务**
- 需要注入**人类审美 (Taste)** 到系统中

**传统 AI 的问题**:
```
用户输入 → AI 输出 → 结束
              ↓
        没有反馈闭环
        没有质量监控
        没有个性化优化
```

**Harness Design 解决方案**:
```
用户输入 → AI 输出 → 评估器 (Evaluator) → 反馈 → 优化
              ↓              ↓
        质量评分      审美匹配度
        用户反馈      长期记忆更新
```

### 1.2 核心组件

| 组件 | 功能 | 示例 |
|-----|------|------|
| **Evaluators** | 评估 AI 输出质量 | 准确性、流畅度、相关性 |
| **Taste Injection** | 注入人类审美 | 语气、风格、偏好 |
| **Feedback Loop** | 持续优化 | 基于历史数据调整 |
| **Long-running Context** | 长期记忆 | 跨会话保持一致性 |

---

## 二、与 AIX Box 的整合方案

### 2.1 为什么 AIX Box 是 Harness Design 的最佳载体？

**Anthropic 方案的局限**:
- 评估运行在云端 → 用户数据上传到服务商
- 审美注入是中心化配置 → 无法个性化
- 长期记忆存储在云端 → 用户失去控制

**AIX Box 的优势**:
```
本地运行 Harness
    ↓
数据不上云 (主权)
    ↓
个性化审美配置 (每个 Box 不同)
    ↓
结合语义记忆 (长期优化)
    ↓
钱包身份绑定 (审美可追溯)
```

### 2.2 AIX Box Harness 架构

```
┌─────────────────────────────────────────────────────────────┐
│              AIX Box Harness 系统                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 4: 审美配置层 (Taste Profile)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • 语气偏好 (正式/随意/幽默)                          │   │
│  │  • 风格模板 (商务/学术/创意)                          │   │
│  │  • 价值观约束 (安全/中立/冒险)                        │   │
│  │  • 个人禁忌词 (用户定义)                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↓ 绑定到 DID                        │
│  Layer 3: 评估器层 (Evaluators)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • 准确性评估 (事实检查)                              │   │
│  │  • 流畅度评估 (语言质量)                              │   │
│  │  • 相关性评估 (与上下文匹配)                          │   │
│  │  • 审美匹配度 (与用户偏好匹配)                        │   │
│  │  • 安全评估 (有害内容检测)                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↓ 实时运行                          │
│  Layer 2: 反馈循环 (Feedback Loop)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • 用户显式反馈 (👍/👎)                               │   │
│  │  • 隐式反馈 (编辑行为、停留时间)                      │   │
│  │  • 自动评分 (基于 Evaluators)                         │   │
│  │  • 记忆更新 (写入 Knowledge Graph)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↓ 持续优化                          │
│  Layer 1: 本地优化器 (Local Optimizer)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • 提示词优化 (基于反馈调整 prompt)                   │   │
│  │  • 模型微调 (本地 LoRA 适配)                          │   │
│  │  • RAG 增强 (检索相关记忆)                            │   │
│  │  • 输出后处理 (基于 Taste Profile)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、核心功能设计

### 3.1 Taste Profile (审美配置)

**用户自定义审美**:

```json
{
  "tasteProfile": {
    "version": "1.0",
    "ownerDID": "did:aix:0x742d...",
    
    "tone": {
      "formality": 0.7,
      "humor": 0.3,
      "empathy": 0.8,
      "assertiveness": 0.6
    },
    
    "style": {
      "domain": "business",
      "templates": ["executive_summary", "detailed_report"],
      "preferredStructures": ["bullet_points", "numbered_list"]
    },
    
    "constraints": {
      "forbiddenWords": ["绝对", "永远", "不可能"],
      "requiredCitations": true,
      "maxResponseLength": 500,
      "language": "zh-CN"
    },
    
    "values": {
      "accuracy": 0.9,
      "creativity": 0.6,
      "safety": 0.95,
      "conciseness": 0.7
    }
  }
}
```

**Taste Profile 来源**:
1. **显式配置**: 用户在设置界面调整
2. **学习所得**: 基于用户历史反馈自动学习
3. **Skill 导入**: 使用专业 Skill 时继承其审美配置

### 3.2 Evaluators (评估器)

**本地运行的评估器**:

```python
class HarnessEvaluator:
    """AIX Box 本地评估器"""
    
    def evaluate(self, input_text, output_text, context):
        scores = {
            "accuracy": self.check_accuracy(output_text),
            "fluency": self.check_fluency(output_text),
            "relevance": self.check_relevance(input_text, output_text),
            "taste_match": self.check_taste_match(output_text, self.taste_profile),
            "safety": self.check_safety(output_text)
        }
        
        # 综合评分
        overall = weighted_average(scores, self.taste_profile.values)
        
        return {
            "scores": scores,
            "overall": overall,
            "passed": overall > 0.7,
            "suggestions": self.generate_suggestions(scores)
        }
```

**评估器类型**:

| 评估器 | 功能 | 实现方式 |
|-------|------|---------|
| **Accuracy Evaluator** | 事实准确性 | 本地知识库验证 + 置信度评分 |
| **Fluency Evaluator** | 语言流畅度 | 本地语言模型评分 |
| **Relevance Evaluator** | 相关性 | 语义相似度计算 |
| **Taste Evaluator** | 审美匹配 | 与 Taste Profile 对比 |
| **Safety Evaluator** | 安全合规 | 本地敏感词库 + 模型检测 |

### 3.3 反馈循环 (Feedback Loop)

**多维度反馈收集**:

```
显式反馈:
├── 用户 👍/👎
├── 星级评分 (1-5)
└── 文字反馈

隐式反馈:
├── 用户是否编辑了输出
├── 用户复制/保存行为
├── 响应时间 (阅读时长)
└── 后续对话引用

自动反馈:
├── Evaluators 评分
├── 一致性检查
└── 知识图谱更新
```

**反馈存储到 Knowledge Graph**:

```
实体: 对话回合 #123
  ├── 输入: "请帮我写一封商务邮件"
  ├── 输出: [邮件内容]
  ├── 评估分数: {accuracy: 0.9, taste: 0.8}
  ├── 用户反馈: 👍
  ├── 时间戳: 2024-01-20T10:30:00Z
  └── 优化建议: ["更正式一些", "添加签名"]
```

### 3.4 本地优化器 (Local Optimizer)

**基于反馈的持续优化**:

```
低分输出 detected
    ↓
分析原因 (哪个 Evaluator 失败)
    ↓
查询相关记忆 (类似场景如何处理)
    ↓
调整策略:
  ├── 修改系统提示词
  ├── 调整 Temperature
  ├── 增强 RAG 上下文
  └── 应用后处理规则
    ↓
重新生成
    ↓
再次评估
    ↓
满意 → 更新 Taste Profile
不满意 → 记录失败案例
```

**LoRA 微调 (可选)**:

```python
# 基于用户反馈进行本地模型微调
class LocalTuner:
    def fine_tune(self, feedback_data):
        # 收集高质量输出作为正样本
        positive_samples = feedback_data[feedback.score > 0.8]
        
        # 收集低质量输出作为负样本
        negative_samples = feedback_data[feedback.score < 0.5]
        
        # 本地 LoRA 微调
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"]
        )
        
        # 训练 (不影响基础模型)
        model = get_peft_model(base_model, lora_config)
        model.train(positive_samples, negative_samples)
```

---

## 四、与语义记忆的结合

### 4.1 Taste Profile 作为 Ontology

```
Taste Profile 可以定义为 Ontology:

Class: UserPreference
  ├── Property: tone (正式度)
  ├── Property: style (风格)
  ├── Property: constraints (约束)
  └── Property: values (价值观权重)

实例化:
  用户张三的 Taste Profile → Knowledge Graph 中的实体
    └── 可以与 Skill、记忆、反馈关联
```

### 4.2 Evaluators 利用知识图谱

```
准确性评估示例:

AI 输出: "苹果公司 2024 年营收 1000 亿美元"
    ↓
查询 Knowledge Graph:
  实体[苹果公司] --[营收]--> ?
    ↓
发现冲突:
  记忆中存储: 2024 年营收 = 3800 亿美元
    ↓
降低准确性评分
提示用户: "检测到数据不一致，请确认"
```

### 4.3 长期审美学习

```
基于 Knowledge Graph 中的反馈数据:

查询:
  用户过去 100 次 👍 的输出有什么共同特征？
    ↓
分析:
  - 80% 使用了 bullet points
  - 90% 语气正式度 > 0.7
  - 经常引用具体数据
    ↓
自动更新 Taste Profile:
  增加 "bullet_points" 到 preferredStructures
  提高 "formality" 权重
```

---

## 五、与钱包身份的结合

### 5.1 Taste Profile 绑定 DID

```
Taste Profile
  └── ownerDID: did:aix:0x742d...
  └── signature: 0x9a8f... (防篡改)

价值:
- 用户可以导出/迁移自己的审美配置
- 跨 Box 同步 Taste Profile
- 出售/分享专业 Taste Profile (作为 Skill)
```

### 5.2 审美声誉系统

```
创作者的审美质量可以被评估:

创作者: did:aix:0xabcd...
  ├── 发布的 Skill 数量: 10
  ├── 平均用户评分: 4.5/5
  ├── Taste Profile 被采用次数: 500
  └── 审美声誉分数: 92/100

购买者可以选择:
- "使用创作者的 Taste Profile"
- "基于创作者的审美训练自己的 Box"
```

---

## 六、应用场景

### 6.1 企业场景

**场景**: 律师事务所使用 AIX Box

```
Taste Profile (商务法律风格):
- 语气: 高度正式 (0.9)
- 结构: 条款编号、引用法条
- 约束: 必须标注法律依据
- 禁忌词: ["大概", "可能", "我觉得"]

Evaluators:
- 准确性: 验证法律条文有效性
- 安全: 检测敏感信息泄露
- 合规: 检查格式是否符合律所标准

反馈循环:
- 合伙人审核每份 AI 生成的文件
- 低质量输出自动学习改进
- 优秀模板存入 Knowledge Graph
```

### 6.2 个人场景

**场景**: 作家使用 AIX Box 写作

```
Taste Profile (创意文学风格):
- 语气: 随意、幽默 (0.8)
- 风格: 叙事性强、比喻丰富
- 约束: 避免陈词滥调
- 偏好: 短句、对话驱动

Evaluators:
- 创意度: 检测新颖表达
- 流畅度: 检查叙事节奏
- 一致性: 验证人物设定前后一致

反馈循环:
- 读者反馈整合
- 基于历史作品学习风格
- 生成个性化写作建议
```

---

## 七、技术实现

### 7.1 组件选型

| 组件 | 技术 | 理由 |
|-----|------|------|
| Evaluators | 本地轻量模型 + 规则引擎 | 隐私、低延迟 |
| Taste Profile | JSON + Ontology | 结构化、可共享 |
| 反馈存储 | Knowledge Graph | 关联记忆 |
| 优化器 | Prompt 工程 + LoRA | 轻量、有效 |
| 监控面板 | Web UI (本地) | 用户可视化 |

### 7.2 性能考虑

```
评估开销控制:
- 异步评估 (不阻塞响应)
- 缓存评估结果
- 分层评估 (快速筛选 → 深度评估)

资源占用:
- Evaluators: < 500MB RAM
- 响应延迟增加: < 200ms
- 存储: 评估历史可配置保留策略
```

---

## 八、与 Anthropic 方案的对比

| 维度 | Anthropic Harness | AIX Box Harness |
|-----|------------------|-----------------|
| 运行位置 | 云端 | 本地 Box |
| 数据隐私 | 上传服务商 | 完全本地 |
| 个性化 | 中心化配置 | 每个 Box 独立 |
| 用户控制 | 有限 | 完全控制 |
| 长期记忆 | 云端存储 | 本地 KG + 可选备份 |
| 审美共享 | 不支持 | Skill 市场支持 |
| 离线使用 | 不支持 | 完全支持 |

---

## 九、总结

**AIX Box Harness = 本地化的 AI 审美系统**

核心价值:
1. **数据主权**: 评估和反馈完全本地运行
2. **深度个性化**: 每个 Box 有独立的 Taste Profile
3. **持续优化**: 基于语义记忆的长期学习
4. **价值变现**: 优质 Taste Profile 可作为 Skill 出售

**与 AIX Box 生态的整合**:
```
Taste Profile (审美配置)
    ↓ 作为 Skill 在 Skill Store 交易
Harness Evaluators (质量监控)
    ↓ 基于 Knowledge Graph 的反馈数据
Wallet DID (身份绑定)
    ↓ 确保审美配置的可追溯和可迁移
Semantic Memory (语义记忆)
    ↓ 支持长期审美学习和优化
```

这是 AIX Box 从"工具"升级为"个性化 AI 伙伴"的关键一步。

