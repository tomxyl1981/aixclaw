# xmemory实现：arXiv 2604.27906

## 论文核心概念 → 实现对应

### 1. Schema约束

**论文**：
- Schema定义"必须记住什么"
- Schema定义"绝不能推断什么"

**实现**：
```python
ENTITY_TYPES = ["person", "project", "company", "event", "concept"]
CANNOT_INFER = ["private_key", "api_key", "password", "secret", 
                "wallet_address", "phone_number", "id_card", "bank_account"]
```

### 2. 三阶段写路径验证

**论文**：
- 对象检测（Object Detection）
- 字段检测（Field Detection）
- 字段值提取（Field-Value Extraction）

**实现**：
- `add_entity()` → 对象检测（验证entity_type）
- `add_fact()` → 字段检测（检查CANNOT_INFER）
- `add_fact()` → 字段值验证（检查value_type）

### 3. 写路径日志

**论文**：
- 验证门控（Validation Gates）
- 本地重试（Local Retries）
- 状态化Prompt控制

**实现**：
```sql
CREATE TABLE write_log (
    id TEXT PRIMARY KEY,
    operation TEXT,      -- insert/update/delete
    validation_stage TEXT, -- object_detection/field_detection/field_value_extraction
    passed INTEGER,      -- 是否通过
    retry_count INTEGER  -- 重试次数
)
```

### 4. 读路径约束查询

**论文**：
> "reads become constrained queries over verified records"

**实现**：
- `get_entity()` → 按ID查询（不是全文检索）
- `get_facts()` → 按entity_id查询（不是语义搜索）
- `search()` → LIKE约束查询（不是向量搜索）

### 5. SQLite + Markdown双轨

**SQLite**：
- 结构化存储（Schema约束）
- 写路径验证日志
- 约束查询

**Markdown**：
- 人类可读
- 版本控制（git）
- 同步备份

## 核心判断对比

| 论文判断 | 实现体现 |
|---------|---------|
| "架构比检索规模更重要" | SQLite约束查询，不是向量检索 |
| "写路径优于读路径" | 三阶段验证在写入时完成 |
| "绝不能推断的字段" | CANNOT_INFER硬编码拦截 |

## 下一步扩展

根据论文，还需要实现：

1. **验证门控（Validation Gates）**
   - 当前：基础验证
   - 需要：judge-in-the-loop配置

2. **本地重试（Local Retries）**
   - 当前：无重试
   - 需要：max_retries=3配置

3. **状态化Prompt控制**
   - 当前：无
   - 需要：prompt状态机

## 评测目标

论文结果：
- 对象级准确率：90.42%
- 输出级准确率：62.67%
- 端到端F1：97.10%

当前实现：
- 基础架构完成 ✅
- 验证门控基础版 ✅
- 写日志记录 ✅
- Markdown同步 ✅

待完成：
- 重试机制 ❌
- 完整验证门控 ❌
- 性能评测 ❌
