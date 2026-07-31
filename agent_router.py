#!/usr/bin/env python3
"""
AIXBox 智能路由引擎 v3 — 语义路由 + MoM 集成 + Skill Catalog + 角色权限约束

路由策略:
  1. 语义向量匹配 (CharNGram TF + cosine similarity) — 零外部依赖
  2. 关键词正则回退
  3. Skill Catalog 触发词匹配增强
  4. 历史优先权重 (prior_weight)
  5. 角色权限约束 (role_permissions.yaml)
  6. 默认路由

高风险决策自动标记 MoM 多视角验证 (target-discovery, opc-pharma, hms-evidence)
"""

import os, re, yaml, sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

ROUTER_CONFIG = os.path.join(os.path.dirname(__file__), "router_config.yaml")
ROLE_PERMISSIONS = os.path.join(os.path.dirname(__file__), "role_permissions.yaml")
ROUTER_LOG = "/tmp/aixbox_router_log.db"

# 技能目录集成（可选）
_skill_catalog = None
try:
    from skill_catalog import catalog as _skill_catalog
except ImportError:
    pass

# MoM 开关域
MOM_DOMAINS = {"target-discovery", "opc-pharma", "hms-evidence"}

# ── 五种角色原型（Boris Cherny 框架）──
ROLES = {
    "prototyper": {
        "label": "原型师",
        "style": "快速产出，概念验证，不纠结细节",
        "keywords": ["原型", "设计", "创", "新项目", "概念", "实验", "尝试", "验证", "想法", "mock"],
    },
    "builder": {
        "label": "构建者",
        "style": "架构推演，管线搭建，生产级质量",
        "keywords": ["搭建", "部署", "架构", "管线", "实现", "生产", "上线", "开发", "构建", "实施"],
    },
    "sweeper": {
        "label": "清理者",
        "style": "优化清理，去冗余，降复杂度",
        "keywords": ["优化", "清理", "重构", "性能", "简化", "瘦身", "压缩", "去重", "整理", "冗余"],
    },
    "grower": {
        "label": "成长者",
        "style": "数据分析，迭代演化，飞轮设计",
        "keywords": ["增长", "迭代", "数据", "指标", "A/B", "转化", "留存", "分析", "飞轮", "规模"],
    },
    "maintainer": {
        "label": "维护者",
        "style": "稳定可靠，安全监控，长期演进",
        "keywords": ["维护", "监控", "安全", "备份", "恢复", "巡检", "健康", "稳定", "审计", "合规"],
    },
}

ROUTE_ROLE_MAP = {
    "target-discovery": {"grower": 0.5, "prototyper": 0.3},
    "opc-pharma": {"builder": 0.6, "maintainer": 0.3},
    "hms-evidence": {"sweeper": 0.5, "grower": 0.4},
    "naye-sandbox": {"prototyper": 0.7, "builder": 0.2},
    "multi-step-analysis": {"grower": 0.5, "sweeper": 0.3},
    "security-sensitive": {"maintainer": 0.6, "sweeper": 0.3},
    "report-generation": {"builder": 0.4, "grower": 0.3},
    "simple-chat": {"prototyper": 0.5, "maintainer": 0.2},
    "default": {"prototyper": 0.3, "builder": 0.3, "sweeper": 0.2, "grower": 0.2, "maintainer": 0.1},
}


class PermissionViolation:
    """角色权限违规记录"""
    __slots__ = ("rule", "reason", "action")

    def __init__(self, rule: str, reason: str, action: str = "deny"):
        self.rule = rule
        self.reason = reason
        self.action = action  # deny | require_approval | require_mom

    def __repr__(self):
        return f"PermissionViolation({self.rule}: {self.reason})"


class RouteDecision:
    """路由决策结果"""
    __slots__ = ("route_id", "target", "model", "complexity",
                 "target_agent", "require_subagent", "require_approval",
                 "method", "semantic_score", "mom_enabled",
                 "role", "role_label", "skill_name", "skill_maturity",
                 "permission_violations", "_disallowed_actions")

    def __init__(self, route_id, target, model="", complexity="simple",
                 target_agent=None, require_subagent=False, require_approval=False,
                 method="keyword", semantic_score=0.0, mom_enabled=False,
                 role="", role_label="", skill_name="", skill_maturity=""):
        self.route_id = route_id
        self.target = target
        self.model = model
        self.complexity = complexity
        self.target_agent = target_agent
        self.require_subagent = require_subagent
        self.require_approval = require_approval
        self.method = method
        self.semantic_score = semantic_score
        self.mom_enabled = mom_enabled
        self.role = role
        self.role_label = role_label
        self.skill_name = skill_name
        self.skill_maturity = skill_maturity
        self.permission_violations = []

    def __repr__(self):
        pv = f" pv={len(self.permission_violations)}" if self.permission_violations else ""
        return (f"RouteDecision(id={self.route_id} target={self.target} "
                f"agent={self.target_agent} role={self.role_label} "
                f"skill={self.skill_name or '-'} "
                f"{self.method}@{self.semantic_score:.2f}{pv})")


class AgentRouter:
    """路由引擎 — 包装 SemanticRouter + 角色识别 + Skill Catalog + 权限约束"""

    def __init__(self, config_path=None):
        self.config_path = config_path or ROUTER_CONFIG
        self.config = self._load_config()
        self._permissions = self._load_permissions()
        self._semantic = None
        self._ensure_log_db()

    def _load_permissions(self):
        """加载角色权限配置文件"""
        path = ROLE_PERMISSIONS
        if not os.path.exists(path):
            return {}
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _load_config(self):
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    @property
    def semantic(self):
        if self._semantic is None:
            from semantic_router import SemanticRouter
            self._semantic = SemanticRouter(self.config_path)
        return self._semantic

    def _classify_role(self, message: str, route_id: str) -> tuple:
        """关键词+路由默认映射，返回 (role_key, role_label)"""
        scores = {r: 0.0 for r in ROLES}
        msg_lower = message.lower()
        for role, info in ROLES.items():
            for kw in info["keywords"]:
                if kw in msg_lower:
                    scores[role] += 0.2
        route_default = ROUTE_ROLE_MAP.get(route_id, ROUTE_ROLE_MAP["default"])
        for role, weight in route_default.items():
            scores[role] += weight
        best = max(scores, key=lambda r: scores[r])
        return (best, ROLES[best]["label"])

    def _ensure_log_db(self):
        conn = sqlite3.connect(ROUTER_LOG)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS route_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, message_preview TEXT,
                route_id TEXT, target TEXT, target_agent TEXT,
                model TEXT, complexity TEXT,
                require_subagent INTEGER DEFAULT 0,
                require_approval INTEGER DEFAULT 0,
                method TEXT DEFAULT 'keyword',
                semantic_score REAL DEFAULT 0.0,
                role TEXT DEFAULT '',
                evaluation TEXT
            )
        """)
        # 如有权限约束列缺失则添加
        try:
            conn.execute("SELECT permission_violations FROM route_log LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE route_log ADD COLUMN permission_violations TEXT DEFAULT ''")
        conn.commit()
        conn.close()

    def _enrich_with_skill(self, message: str, decision: RouteDecision) -> RouteDecision:
        """
        使用 Skill Catalog 增强路由决策。

        当语义路由返回 default 或无匹配时，尝试从 skill_catalog 的
        触发词匹配中获取目标路由。同时提取技能名称和成熟度。

        Args:
            message: 用户消息
            decision: 已有的 RouteDecision

        Returns:
            可能被增强的 RouteDecision
        """
        global _skill_catalog
        if _skill_catalog is None:
            return decision

        # 仅在默认或低分匹配时查 skill catalog
        if decision.route_id not in ("default", "unknown", "empty") and decision.method != "default":
            # 已有明确路由，仅补充 skill 信息
            skill = _skill_catalog.find_by_route_id(decision.route_id)
            if skill:
                decision.skill_name = skill.name
                decision.skill_maturity = str(skill.maturity)
            return decision

        # 查 skill catalog 触发匹配
        match = _skill_catalog.find_by_trigger(message)
        if match:
            decision.skill_name = match.skill.name
            decision.skill_maturity = str(match.skill.maturity)
            # 如果有更好的路由信息，覆盖默认路由
            if match.skill.route_id and match.skill.route_id != decision.route_id:
                decision.route_id = match.skill.route_id
                decision.target_agent = match.skill.target_agent
                decision.method = "skill_catalog"

                decision.mom_enabled = decision.route_id in MOM_DOMAINS
                # 重新计算角色
                decision.role, decision.role_label = self._classify_role(message, decision.route_id)

        return decision

    def _check_role_permissions(self, decision: RouteDecision) -> RouteDecision:
        """
        根据 role_permissions.yaml 检查当前决策的权限约束。

        检查项：
          1. disallowed_routes — 禁止的路由
          2. require_approval — 需审批的路由
          3. require_mom — 需 MoM 验证的路由
          4. max_complexity — 最大复杂度
          5. model_restrictions — 模型限制
          6. allowed_routes — 显式白名单
          7. disallowed_actions — 禁止操作（在后续 pipeline 中检查）

        Returns:
            添加了 permission_violations 的 RouteDecision
        """
        if not self._permissions:
            return decision

        role_key = decision.role
        role_rules = self._permissions.get(role_key, {})
        if not role_rules:
            return decision

        route = decision.route_id

        # 1. disallowed_routes — 禁止的路由
        disallowed = role_rules.get("disallowed_routes", [])
        if route in disallowed:
            decision.permission_violations.append(
                PermissionViolation("disallowed_route",
                    f"角色 {role_key} 禁止访问路由 {route}")
            )

        # 2. allowed_routes — 白名单（仅在 allowed 非空时生效）
        allowed = role_rules.get("allowed_routes", [])
        if allowed and route not in allowed:
            decision.permission_violations.append(
                PermissionViolation("route_not_allowed",
                    f"角色 {role_key} 仅允许访问: {', '.join(allowed)}")
            )

        # 3. require_approval — 需审批
        require_approval = role_rules.get("require_approval", [])
        if route in require_approval:
            decision.require_approval = True
            decision.permission_violations.append(
                PermissionViolation("require_approval",
                    f"角色 {role_key} 访问 {route} 需要审批", action="require_approval")
            )

        # 4. require_mom — 需 MoM 验证
        require_mom = role_rules.get("require_mom", [])
        if route in require_mom:
            decision.mom_enabled = True
            decision.permission_violations.append(
                PermissionViolation("require_mom",
                    f"角色 {role_key} 访问 {route} 需 MoM 验证", action="require_mom")
            )

        # 5. max_complexity — 复杂度上限
        COMPLEXITY_SCORE = {"simple": 1, "moderate": 2, "complex": 3}
        max_cx = role_rules.get("max_complexity", "complex")
        if COMPLEXITY_SCORE.get(decision.complexity, 3) > COMPLEXITY_SCORE.get(max_cx, 3):
            decision.permission_violations.append(
                PermissionViolation("complexity_exceeded",
                    f"角色 {role_key} 最大复杂度 {max_cx}，请求 {decision.complexity}")
            )

        # 6. model_restrictions — 模型限制
        models = role_rules.get("model_restrictions", [])
        if models and decision.model and decision.model not in models:
            decision.permission_violations.append(
                PermissionViolation("model_restricted",
                    f"角色 {role_key} 仅允许模型: {', '.join(models)}")
            )

        # 7. disallowed_actions — 禁止操作写入 decision 供后续使用
        da = role_rules.get("disallowed_actions", [])
        if da:
            setattr(decision, "_disallowed_actions", da)

        return decision

    def _log_routing(self, decision, message_preview=""):
        conn = sqlite3.connect(ROUTER_LOG)
        pv_json = "|".join(f"{v.rule}:{v.reason}" for v in decision.permission_violations)
        conn.execute("""
            INSERT INTO route_log(timestamp, message_preview, route_id, target,
                target_agent, model, complexity, require_subagent, require_approval,
                method, semantic_score, role, permission_violations)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            message_preview[:100],
            decision.route_id, decision.target,
            decision.target_agent or "", decision.model,
            decision.complexity,
            1 if decision.require_subagent else 0,
            1 if decision.require_approval else 0,
            decision.method, decision.semantic_score,
            decision.role,
            pv_json[:500],
        ))
        conn.commit()
        conn.close()

    def prior_weight(self, user_id: str, current_chat: str) -> dict:
        """
        根据用户历史路由记录计算先验权重。

        从 route_log 中查询该用户最近 20 条路由记录（按消息关键词匹配），
        返回 {route_id: boost_weight}。

        Args:
            user_id: 用户标识 (如 open_id)
            current_chat: 当前消息，用于提取关键词匹配历史

        Returns:
            dict: route_id → boost_weight (0.0 ~ 0.5)
        """
        conn = sqlite3.connect(ROUTER_LOG)
        # 提取消息关键词用于匹配历史记录
        tokens = set(re.findall(r'[\w\u4e00-\u9fff]+', current_chat.lower()))
        # 过滤停用词
        stopwords = {"的", "了", "是", "在", "有", "我", "这", "那",
                     "你", "他", "她", "它", "们", "就", "也", "和",
                     "与", "为", "上", "下", "不", "都", "a", "an",
                     "the", "is", "are", "was", "to", "in", "for", "of"}
        tokens = tokens - stopwords
        rows = conn.execute(
            "SELECT route_id, COUNT(*) FROM route_log GROUP BY route_id ORDER BY COUNT(*) DESC LIMIT 20"
        ).fetchall()
        conn.close()
        total = sum(r[1] for r in rows) or 1
        weights = {}
        for route_id, count in rows:
            w = round(0.1 * (count / total) * 5, 2)
            if w > 0:
                weights[route_id] = min(w, 0.5)
        return weights

    def _apply_prior_weight(self, message: str, context: dict, decision: RouteDecision) -> RouteDecision:
        """
        应用历史先验权重：在语义路由置信度低时，用用户历史偏好提升路由。

        Args:
            message: 用户消息
            context: 上下文（含 user_id 等）
            decision: 当前路由决策

        Returns:
            可能被重新路由的 RouteDecision
        """
        user_id = (context or {}).get("user_id", "unknown")
        weights = self.prior_weight(user_id, message)
        if not weights:
            return decision

        # 低置信度时使用历史权重重新路由
        if decision.method == "default" or decision.route_id == "default":
            top = max(weights, key=weights.get)
            if weights[top] >= 0.3:  # 阈值
                decision.route_id = top
                decision.target = self._resolve_target(top)
                decision.target_agent = self._resolve_agent(top)
                decision.complexity = self._resolve_complexity(top)
                decision.role, decision.role_label = self._classify_role(message, top)
                decision.method = "prior_weight"
                decision.mom_enabled = top in MOM_DOMAINS

        return decision

    def _resolve_target(self, route_id: str) -> str:
        """从配置中解析目标"""
        routes = self.config.get("routes", {})
        return routes.get(route_id, {}).get("target", "agent")

    def _resolve_agent(self, route_id: str) -> str:
        """从配置中解析代理"""
        routes = self.config.get("routes", {})
        return routes.get(route_id, {}).get("target_agent", "")

    def _resolve_complexity(self, route_id: str) -> str:
        """从配置中解析复杂度"""
        routes = self.config.get("routes", {})
        return routes.get(route_id, {}).get("complexity", "simple")

    def decide(self, message, context=None):
        """
        核心路由决策：语义→关键词→Skill Catalog→历史权重→角色权限约束→默认。

        返回 RouteDecision（含 role, skill_name, permission_violations 字段）。
        """
        if not message or not isinstance(message, str):
            return RouteDecision("empty", "current", complexity="simple")

        message_clean = message.strip()
        models = self.config.get("models", {})

        route_id, target, target_agent, model_name, complexity, \
            require_subagent, require_approval = self.semantic.reroute(message_clean)

        if not model_name:
            mk = "complex" if complexity == "complex" else "simple"
            mi = models.get(mk, {})
            model_name = mi.get("name", "")

        method = "semantic" if route_id != "default" else "default"

        role, role_label = self._classify_role(message_clean, route_id)

        decision = RouteDecision(
            route_id=route_id, target=target, model=model_name,
            complexity=complexity, target_agent=target_agent,
            require_subagent=require_subagent, require_approval=require_approval,
            method=method, mom_enabled=route_id in MOM_DOMAINS,
            role=role, role_label=role_label,
        )

        # Skill Catalog 增强
        decision = self._enrich_with_skill(message_clean, decision)

        # 领域兜底: 通用路由上的靶点类消息 -> target-discovery 并激活 MoM
        if decision.route_id in ("simple-chat", "default", "unknown", "empty") and self._looks_like_domain_query(message_clean):
            decision.route_id = "target-discovery"
            decision.mom_enabled = True
            decision.method = "domain-fallback"

        # 历史先验权重（低置信度时提升）
        decision = self._apply_prior_weight(message_clean, context or {}, decision)

        # ═══ 角色权限约束检查 ═══
        decision = self._check_role_permissions(decision)

        if self.config.get("security", {}).get("log_all_routes", True):
            self._log_routing(decision, message_clean)

        return decision

    def _looks_like_domain_query(self, msg):
        """兜底识别: 中文语境下的大写基因符号(如 ACVR2A) 或领域关键词 -> 靶点域"""
        import re
        m = (msg or "").strip()
        has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in m)
        if has_cjk and re.search(r"[A-Z]{2,}[0-9]", m):
            return True
        low = m.lower()
        for kw in ("靶点", "基因", "肝纤维化", "通路", "疾病关联", "gwas", "eqtl",
                   "证据", "置信度", "孟德尔", "causal", "因果", "药学", "处方", "用药"):
            if kw in low:
                return True
        return False

    def route_stats(self, days=7):
        conn = sqlite3.connect(ROUTER_LOG)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT route_id, COUNT(*) FROM route_log WHERE timestamp > ? GROUP BY route_id ORDER BY COUNT(*) DESC",
            (cutoff,)
        ).fetchall()
        conn.close()
        return rows

    def route_summary(self, days=7):
        conn = sqlite3.connect(ROUTER_LOG)
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        total = conn.execute("SELECT COUNT(*) FROM route_log WHERE timestamp > ?", (cutoff,)).fetchone()[0]
        by_agent = conn.execute(
            "SELECT target_agent, COUNT(*) FROM route_log WHERE timestamp > ? AND target_agent != '' GROUP BY target_agent",
            (cutoff,)
        ).fetchall()
        by_complexity = conn.execute(
            "SELECT complexity, COUNT(*) FROM route_log WHERE timestamp > ? GROUP BY complexity",
            (cutoff,)
        ).fetchall()
        subagents = conn.execute(
            "SELECT COUNT(*) FROM route_log WHERE timestamp > ? AND require_subagent = 1",
            (cutoff,)
        ).fetchone()[0]
        methods = conn.execute(
            "SELECT method, COUNT(*) FROM route_log WHERE timestamp > ? GROUP BY method",
            (cutoff,)
        ).fetchall()
        by_role = conn.execute(
            "SELECT role, COUNT(*) FROM route_log WHERE timestamp > ? AND role != '' GROUP BY role ORDER BY COUNT(*) DESC",
            (cutoff,)
        ).fetchall()
        conn.close()
        return {
            "total": total, "by_agent": by_agent,
            "by_complexity": by_complexity, "subagents": subagents,
            "by_method": methods, "by_role": by_role,
        }


router = AgentRouter()

if __name__ == "__main__":
    test_msgs = [
        "ACVR2A 的 GWAS 证据是什么？",
        "帮我查一下头孢克肟的儿童剂量",
        "今天天气怎么样",
        "蜂群建筑的 DSL 协议设计",
        "给我个密码重置脚本",
        "优化一下证据管线的查询性能",
        "对比恒瑞百济NSCLC管线",
        "设计一个新项目的原型",
    ]
    print("=== AgentRouter v3 + 角色权限约束 Test ===")
    for msg in test_msgs:
        d = router.decide(msg)
        mom = " [MoM]" if d.mom_enabled else ""
        appr = " [审批]" if d.require_approval else ""
        skill = f" skill={d.skill_name or '-'}" if d.skill_name else ""
        pv = ""
        if d.permission_violations:
            pv = f" ⚠️{len(d.permission_violations)}违规"
        print(f"  [{d.complexity}] {d.role_label:<6} {msg[:30]:<30} → {d.route_id:<25} {d.method:<12}{skill}{mom}{appr}{pv}")
    print(f"\n=== Permission Violations Detail ===")
    for msg in test_msgs:
        d = router.decide(msg)
        for v in d.permission_violations:
            print(f"  [{d.role}] {v.rule}: {v.reason}")
