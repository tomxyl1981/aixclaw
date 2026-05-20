-- xmemory Schema-Grounded Memory Architecture
-- arXiv 2604.27906: "reads become constrained queries over verified records"

-- 核心原则：
-- 1. Schema定义"必须记住什么"
-- 2. Schema定义"绝不能推断什么"
-- 3. 写路径验证，读路径约束查询

-- ========== 实体表（必须记住的对象） ==========

-- 人物
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('person', 'project', 'company', 'event', 'concept')),
    name TEXT NOT NULL,
    display_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT,  -- 扩展字段，但需明确标注"可推断"
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0 AND confidence <= 1),
    source TEXT NOT NULL,  -- 来源：必须标注，绝不能推断
    verified INTEGER DEFAULT 0  -- 是否经过验证门控
);

-- 关系（必须记住的关系）
CREATE TABLE IF NOT EXISTS relations (
    id TEXT PRIMARY KEY,
    from_entity TEXT NOT NULL,
    to_entity TEXT NOT NULL,
    relation_type TEXT NOT NULL CHECK(relation_type IN (
        'owns', 'works_for', 'created', 'member_of', 'partner', 
        'competitor', 'depends_on', 'related_to', 'uses', 'invested_in'
    )),
    strength REAL DEFAULT 1.0 CHECK(strength >= 0 AND strength <= 1),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,  -- 来源：必须标注
    verified INTEGER DEFAULT 0,
    FOREIGN KEY (from_entity) REFERENCES entities(id),
    FOREIGN KEY (to_entity) REFERENCES entities(id)
);

-- 事实（必须记住的精确事实）
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    field TEXT NOT NULL,  -- 字段名
    value TEXT NOT NULL,  -- 字段值
    value_type TEXT NOT NULL CHECK(value_type IN ('string', 'number', 'boolean', 'date', 'url', 'id')),
    confidence REAL DEFAULT 1.0 CHECK(confidence >= 0 AND confidence <= 1),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source TEXT NOT NULL,  -- 来源：必须标注
    verified INTEGER DEFAULT 0,
    cannot_infer INTEGER DEFAULT 0,  -- 标记"绝不能推断"
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);

-- ========== 写路径验证记录 ==========

CREATE TABLE IF NOT EXISTS write_log (
    id TEXT PRIMARY KEY,
    operation TEXT NOT NULL CHECK(operation IN ('insert', 'update', 'delete')),
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    validation_stage TEXT NOT NULL CHECK(validation_stage IN (
        'object_detection', 'field_detection', 'field_value_extraction'
    )),
    passed INTEGER NOT NULL,  -- 是否通过验证
    retry_count INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT,  -- 执行写入的agent
    session_id TEXT  -- 会话ID
);

-- ========== 读路径查询缓存 ==========

CREATE TABLE IF NOT EXISTS read_cache (
    id TEXT PRIMARY KEY,
    query_type TEXT NOT NULL,
    query_params TEXT NOT NULL,  -- JSON格式
    result TEXT NOT NULL,  -- JSON格式
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT  -- 过期时间（状态化计算需要）
);

-- ========== 索引 ==========

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_relations_from ON relations(from_entity);
CREATE INDEX IF NOT EXISTS idx_relations_to ON relations(to_entity);
CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity_id);
CREATE INDEX IF NOT EXISTS idx_facts_field ON facts(field);
CREATE INDEX IF NOT EXISTS idx_write_log_timestamp ON write_log(timestamp);
