---
skill: search-strategy
version: 1.0.0
description: 那耶村知识库搜索策略
triggers:
  - pattern: "/naye:search"
    priority: high
  - pattern: "/search"
    priority: medium
---

# 搜索策略

## 意图识别

接收用户查询后，执行以下分析：

1. **提取关键词**
   - 中文字符序列
   - 英文单词
   - 专有名词（那耶村、梁越、ViMax等）

2. **识别过滤条件**
   - `from:memory` - 只搜索MEMORY.md
   - `from:knowledge` - 只搜索知识库
   - `after:YYYY-MM-DD` - 时间之后
   - `before:YYYY-MM-DD` - 时间之前

3. **确定搜索意图**
   - `project_status` - 项目进度查询
   - `decision` - 决策方案查询
   - `person` - 人物相关
   - `ch` - Coin Hour相关
   - `general` - 一般查询

## 搜索优化

### 源选择策略

```yaml
意图 → 优先数据源:
  project_status:
    - memory (最近30天)
    - workspace
  
  decision:
    - memory
    - knowledge (category: decisions)
  
  person:
    - knowledge (tags: people)
    - memory
  
  ch:
    - memory
    - workspace
  
  general:
    - knowledge
    - memory
    - workspace (按顺序)
```

### 分数计算

```python
最终分数 = 基础分数 × 源权重 × 时效性系数

基础分数:
  - 标题匹配: +0.4
  - 关键词出现: +0.1/次 (最高0.4)
  - 标签匹配: +0.2

源权重:
  - memory: 1.0 (最权威)
  - knowledge: 0.9
  - workspace: 0.7

时效性系数:
  - 7天内: 1.2
  - 30天内: 1.0
  - 90天内: 0.9
  - 更早: 0.8
```

## 回答合成

### 结果聚合

```
查询: "梁越的作品"

memory结果:
  - 2026-05-28.md: 梁越完成《隐没的战象》
  - 2026-05-20.md: 梁越作品列表

knowledge结果:
  - liang-yue-works.md: 梁越作品详细目录

合成回答:
  "根据记忆和知识库，梁越的作品包括：
   - 《隐没的战象》（2024年出版，那耶村驻村创作）
   - 《西去的使节》（2018年）
   - ...
   
   来源：MEMORY.md(2条) + knowledge/liang-yue-works.md"
```

### 置信度评估

```yaml
高置信 (>0.7):
  - 精确匹配关键词
  - 时间范围符合
  - 多个源交叉验证

中置信 (0.4-0.7):
  - 部分匹配
  - 单一来源

低置信 (<0.4):
  - 模糊匹配
  - 需用户确认
```

## 常见场景处理

### 场景1: 找不到相关信息

```
用户: "那耶村的交通方式"
发现: 无相关结果
行动:
  1. 扩大搜索范围（去掉时间过滤）
  2. 关联搜索（云南、文山、富宁）
  3. 建议: "未找到具体信息，建议补充到知识库"
```

### 场景2: 多个冲突信息

```
用户: "CH汇率"
发现:
  - memory/2026-05-01.md: 1 CH = 1 RMB
  - memory/2026-05-15.md: 1 CH = 1.1 RMB
行动:
  1. 标注时间戳
  2. 提示: "最新信息（5月15日）: 1 CH = 1.1 RMB"
  3. 建议: "汇率可能有变动，请以最新记录为准"
```

### 场景3: 需要跨文档推理

```
用户: "那耶村去年收入"
发现:
  - memory中没有总收入数字
  - 有各项目收入: 短剧1000 CH + 旅游500 CH + ...
行动:
  1. 自动汇总计算
  2. 提示: "根据记录汇总，去年收入约为..."
  3. 建议: "建议创建年度财务报表统一记录"
```
