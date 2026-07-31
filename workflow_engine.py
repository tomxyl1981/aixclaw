#!/usr/bin/env python3
"""
AIXBox 统一工作流引擎 (MoM + 语义路由 + 验证闭环)

将三个模块串联:
  1. 语义路由 → 自动识别意图
  2. 高风险路由 → 自动预生成 MoM 多视角验证 Prompt
  3. 结果 → 可执行工作计划

工作流示例:
  wf = AIXBoxWorkflow()
  plan = wf.process("ACVR2A 的 GWAS 证据可信吗？", context)
  # plan = {
  #   "decision": RouteDecision(...),       # 路由决策
  #   "mom_plan": {                         # 如果高风险域
  #     "domain": "target_confidence",
  #     "prompts": {"verifier": ..., "adversarial": ..., "pragmatic": ...}
  #   },
  #   "response_hint": "用 deepseek-v4-flash 深入分析"
  # }
"""

import os, sys, json
from datetime import datetime, timezone
from typing import Optional

# 导路由和 MoM
sys.path.insert(0, os.path.dirname(__file__))
from agent_router import router, RouteDecision, MOM_DOMAINS
from mom_validator import mom, PROMPT_STRATEGIES
from trajectory_evaluator import TrajectoryEvaluator, build_minimal_trajectory

# DataFlow-Harness 模式: 操作符注册表 + 预执行验证
# 来源: 北大 OpenDCAI/DataFlow-Harness (Apache-2.0)
# 核心模式: Agent 不猜测操作名/参数, 仅从注册表选择
_OPERATOR_REGISTRY = None
try:
    from operator_registry import (
        get_operator_detail, list_operators_by_domain,
        list_operator_categories, validate_operator_chain,
        list_all_operators,
    )
    _OPERATOR_REGISTRY = True
except ImportError:
    pass

# Middleware Pipeline 支持（可选导入，不影响现有功能）
_HAS_PIPELINE = False
try:
    from pipeline import (
        PipelineContext, MiddlewareChain, Middleware,
        RouterMiddleware, SkillMiddleware, LoggingMiddleware,
        create_default_chain,
    )
    _HAS_PIPELINE = True
except ImportError:
    pass

try:
    from goal_loop import GoalCheckMiddleware, create_goal_state
    _HAS_GOAL_LOOP = True
except ImportError:
    GoalCheckMiddleware = None  # type: ignore
    _HAS_GOAL_LOOP = False

try:
    from delegation_ledger import DelegationMiddleware, DelegationLedger
    _HAS_DELEGATION = True
except ImportError:
    DelegationMiddleware = None  # type: ignore
    _HAS_DELEGATION = False


ROUTER_LOG = "/tmp/aixbox_router_log.db"


class AIXBoxWorkflow:
    """
    统一工作流入口。

    输入用户消息 + 上下文，返回完整的执行计划。
    调用方（AIXClaw 主循环）按计划执行即可。

    Agent 轨迹互读 (2026-07-20):
      inject_agent_context() 自动从路由日志拉取目标 Agent 最近记录,
      实现"AI 解读他人聊天轨迹实现秒级信息同步"。
    """

    def __init__(self):
        self.router = router
        self.mom = mom
        self.workflow_log = []  # 本会话的工作流记录
        self._middleware_chain: Optional['MiddlewareChain'] = None

    def inject_agent_context(self, target_agent, limit=5):
        """
        读取目标 Agent 最近的轨迹记录作为上下文。

        从路由日志 SQLite 中捞取 target_agent (或 route_id) 的最近记录，
        让即将被调用的 Agent 知道同事们在忙什么。

        Args:
            target_agent: str — Agent 名称 (如 "target-discovery", "hms-core")
            limit: int — 最多返回条数

        Returns:
            list[dict] — 最近的路由记录, 按时间倒序
        """
        if not os.path.exists(ROUTER_LOG):
            return []

        try:
            import sqlite3
            conn = sqlite3.connect(ROUTER_LOG)
            rows = conn.execute(
                "SELECT timestamp, message_preview, route_id, target_agent, "
                "model, complexity, method "
                "FROM route_log "
                "WHERE target_agent = ? OR route_id = ? "
                "ORDER BY id DESC LIMIT ?",
                (target_agent, target_agent, limit)
            ).fetchall()
            conn.close()
        except Exception:
            return []

        return [
            {
                "time": r[0],
                "message": r[1],
                "route": r[2],
                "agent": r[3],
                "model": r[4],
                "complexity": r[5],
                "method": r[6],
            }
            for r in rows
        ]

    def agent_context_summary(self, target_agent, limit=5):
        """生成给目标 Agent 的浓缩上下文摘要文本"""
        records = self.inject_agent_context(target_agent, limit)
        if not records:
            return ""

        lines = [f"📋 Agent [{target_agent}] 最近工作轨迹:"]
        for r in records:
            ts = (r["time"] or "")[:16]
            msg = (r["message"] or "")[:60]
            lines.append(f"  [{ts}] {r['method']:<8} → {r['route']:<20} \"{msg}\"")

        return "\n".join(lines)

    def process(self, message, context=None):
        """
        全流程处理 (v2 — 集成 Operator Registry 验证)。
        
        Args:
            message: str — 用户消息
            context: dict — 可选上下文 {
                "project": str,       # 当前项目范围
                "conclusion": str,    # 如果已生成结论（需验证）
                "evidence": str,      # 证据上下文
                "patient": str,       # 患者上下文
                "history": [...],     # 历史路由
                "operators": [...],   # 可选: 建议的操作符链 (operator_ids)
            }

        Returns:
            dict — 执行计划 {
                "decision": RouteDecision 的 dict,
                "mom_plan": dict | None,
                "agent_context": str | None,  # Agent 轨迹上下文摘要
                "response_hint": str,
                "timestamp": str,
                "operator_suggestions": [...] | None,  # [新增] 推荐操作符
                "operator_validation": dict | None,    # [新增] 操作符链验证
            }
        """
        context = context or {}
        decision = self.router.decide(message, context)

        plan = {
            "decision": {
                "route_id": decision.route_id,
                "target": decision.target,
                "target_agent": decision.target_agent,
                "model": decision.model,
                "complexity": decision.complexity,
                "require_subagent": decision.require_subagent,
                "require_approval": decision.require_approval,
                "method": decision.method,
                "mom_enabled": decision.mom_enabled,
            },
            "route_log_id": getattr(decision, "route_log_id", None),
            "mom_plan": None,
            "agent_context": None,  # Agent 轨迹互读
            "operator_suggestions": None,
            "operator_validation": None,
            "response_hint": self._build_hint(decision),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Agent 轨迹互读: 当路由到某个 Agent 时, 自动注入其最近工作轨迹
        if decision.target_agent:
            summary = self.agent_context_summary(decision.target_agent, limit=5)
            if summary:
                plan["agent_context"] = summary

        # ── DataFlow 模式: 操作符建议 + 预执行验证 ──
        if _OPERATOR_REGISTRY:
            # 1) 根据路由域推荐可用操作符
            route_id = decision.route_id
            domain_map = {
                "target-discovery": "target-discovery",
                "hms-evidence": "target-discovery",
                "opc-pharma": "opc-pharma",
                "naye-sandbox": "naye-sandbox",
            }
            domain = domain_map.get(route_id)
            if domain:
                ops = list_operators_by_domain(domain)
                if ops:
                    plan["operator_suggestions"] = [
                        {"id": o["id"], "name": o["name"], "description": o["description"]}
                        for o in ops
                    ]
                # 还注入通用操作符
                general_ops = list_operators_by_domain("general")
                if general_ops:
                    plan.setdefault("operator_suggestions", []).extend(
                        {"id": o["id"], "name": o["name"], "description": o["description"]}
                        for o in general_ops
                    )

            # 2) 如果上下文中传入了建议操作符链, 做预执行验证
            operator_chain = context.get("operators")
            if operator_chain:
                plan["operator_validation"] = validate_operator_chain(operator_chain)

        # 高风险路由 → 自动输出 MoM 验证 Prompt 计划
        if decision.mom_enabled:
            plan["mom_plan"] = self._build_mom_plan(decision, context)
            # P1: 若上下文中已带回多视角验证结果, 立即计算熵态并回填
            mom_results = context.get("mom_results")
            if mom_results and plan["mom_plan"]:
                self._attach_mom_entropy(plan["mom_plan"], mom_results)

        # 记录本会话工作流
        self.workflow_log.append({
            "time": plan["timestamp"],
            "message": message[:80],
            "route_id": decision.route_id,
            "mom": decision.mom_enabled,
            "mom_plan": plan.get("mom_plan"),  # P1: 熵态回填后可在 summary 读取
            "route_log_id": getattr(decision, "route_log_id", None),
        })

        return plan

    def _build_mom_plan(self, decision, context):
        """为高风险域构建 MoM 验证计划"""
        route_id = decision.route_id

        # 映射路由 → MoM domain
        domain_map = {
            "target-discovery": "target_confidence",
            "hms-evidence": "target_confidence",
            "naye-sandbox": None,  # 那耶沙盒暂不启用 MoM
            "opc-pharma": "opc_pharma",
        }
        domain = domain_map.get(route_id)
        if not domain:
            return None
        if domain not in PROMPT_STRATEGIES:
            return None

        # 从上下文中提取结论和证据
        conclusion = context.get("conclusion", "")
        evidence = context.get("evidence", "")
        patient = context.get("patient", "")

        if not conclusion:
            return self._mom_pending_plan(domain)

        # 生成验证 Prompt 集
        prompts = self.mom.generate_verification_prompts(
            domain, conclusion,
            context=evidence or patient
        )

        return {
            "domain": domain,
            "conclusion": conclusion[:200],
            "strategies": list(prompts.keys()),
            "prompts": prompts,
            "status": "ready_for_execution",
            "advice": self._mom_advisory(domain),
            # P1: 熵态契约 — 结论生成并完成多视角验证后回填
            "entropy": {
                "status": "pending",
                "natural_entropy": None,
                "pressure_ratio": None,
                "consensus": None,
                "note": "调用 _attach_mom_entropy() 或传 context['mom_results'] 回填",
            },
        }

    def _mom_pending_plan(self, domain):
        """结论尚未生成时的 MoM 占位计划"""
        return {
            "domain": domain,
            "conclusion": "(待生成)",
            "strategies": list(PROMPT_STRATEGIES.get(domain, {}).keys()),
            "prompts": {},
            "status": "pending_conclusion",
            "advice": "先由 Agent 生成结论，再走 MoM 多视角验证",
            "entropy": {
                "status": "pending",
                "natural_entropy": None,
                "pressure_ratio": None,
                "consensus": None,
                "note": "结论生成后由 compute_consensus() 计算",
            },
        }

    def _attach_mom_entropy(self, mom_plan: dict, results: dict) -> dict:
        """P1: 多视角验证结果 → 熵态回填。

        调用 mom.compute_consensus() 提取自然态熵 / 压熵比 / 共识度,
        写入 mom_plan["entropy"]。结果缺失时保留 pending 并给出原因。

        Args:
            mom_plan: _build_mom_plan() 返回的计划 (就地修改)
            results: {策略名: {评分/结论 dict}}, 即 compute_consensus() 的输入

        Returns:
            dict — 更新后的 entropy 字段
        """
        ent = mom_plan.setdefault("entropy", {
            "status": "pending",
            "natural_entropy": None,
            "pressure_ratio": None,
            "consensus": None,
            "note": "",
        })
        domain = mom_plan.get("domain")
        if not domain or not isinstance(results, dict) or not results:
            ent.update({"status": "error", "note": "缺少 domain 或 mom_results"})
            return ent
        # P1: mom_results 可能是 {domain: [{view, confidence, reason}, ...]} 的视图列表,
        # 而 compute_consensus() 期望 {策略名: {confidence_score: ...}}, 需先归一化。
        payload = results
        if domain in results and isinstance(results[domain], list):
            payload = {}
            for item in results[domain]:
                if not isinstance(item, dict) or not item.get("view"):
                    continue
                payload[item["view"]] = {
                    "confidence_score": item.get("confidence", item.get("confidence_score")),
                }
            if not payload:
                ent.update({"status": "error", "note": "mom_results 视图列表无法解析"})
                return ent
        try:
            consensus = self.mom.compute_consensus(domain, payload)
        except Exception as e:
            ent.update({"status": "error", "note": f"compute_consensus 异常: {e}"})
            return ent

        # 熵字段可能因 domain 分支不同而缺失 (如 opc_pharma 无分数熵)
        ne = consensus.get("natural_entropy")
        pr = consensus.get("pressure_ratio")
        if ne is None or pr is None:
            ent.update({
                "status": "n/a",
                "natural_entropy": ne,
                "pressure_ratio": pr,
                "consensus": consensus.get("consensus"),
                "note": f"{domain} 分支不产出分数熵, 仅共识度可用",
            })
            return ent

        ent.update({
            "status": "computed",
            "natural_entropy": ne,
            "pressure_ratio": pr,
            "consensus": consensus.get("consensus"),
            "note": "",
        })
        return ent

    def _mom_advisory(self, domain):
        advisories = {
            "target_confidence": (
                "将靶点结论 + 证据上下文分别喂给 3 个视角 (verifier/adversarial/pragmatic)，"
                "用 compute_consensus() 合成最终置信度。"
            ),
            "opc_pharma": (
                "将药学结论 + 患者信息分别喂给药理学验证和替代方案分析，"
                "用 compute_consensus() 判断安全等级。"
            ),
        }
        return advisories.get(domain, "")

    def _build_hint(self, decision):
        """给 AIXClaw 主循环的执行提示"""
        route = decision.route_id
        agent = decision.target_agent
        complexity = decision.complexity

        if route == "empty":
            return "消息为空，返回默认对话模式。"
        if route == "security-sensitive":
            return f"安全敏感操作 (require_approval={decision.require_approval}), 需用户确认后再执行。"

        if agent:
            base = f"路由到 Agent [{agent}]，使用模型 {decision.model}。"
        else:
            base = f"就地处理 ({route})，使用模型 {decision.model}。"

        if decision.mom_enabled:
            base += " 高风险域已标记 MoM 验证，生成结论后调用 mom.complete_verification()。"

        if complexity == "complex":
            base += " 多步分析，建议启用 subagent 或深度推理。"
        elif complexity == "simple":
            base += " 简单任务，直接回复即可。"

        # 添加操作符提示 (DataFlow 模式)
        if _OPERATOR_REGISTRY:
            ops = list_operators_by_domain(
                {"target-discovery": "target-discovery",
                 "hms-evidence": "target-discovery",
                 "opc-pharma": "opc-pharma",
                 "naye-sandbox": "naye-sandbox"}.get(route, "")
            )
            if ops:
                op_names = ", ".join(o["name"] for o in ops[:5])
                base += f" 可用操作符 ({len(ops)}个): {op_names}..."

        return base

    def post_evaluate(self, route_log_id: int, trajectory: dict, rules: list = None) -> dict:
        """
        Agent 执行后评价其轨迹 (P0)。

        由 AIXClaw 主循环在 Agent 完成回复后调用。
        评价结果写回 route_log 的 evaluation 字段。

        Args:
            route_log_id: 路由日志 ID (从 process() 返回的 plan 中获取)
            trajectory: 轨迹数据 (构建自工具调用日志 + 回复 + 环境状态)
            rules: 可选业务规则列表 (覆盖默认规则)

        Returns:
            dict — 三层验证结果
        """
        evaluator = TrajectoryEvaluator(rules)
        result = evaluator.evaluate(trajectory, use_llm=False)

        # 写回 route_log
        try:
            import sqlite3
            # 从 agent_router 获取 ROUTER_LOG 路径
            try:
                from agent_router import ROUTER_LOG
                db_path = ROUTER_LOG
            except ImportError:
                db_path = "/tmp/aixbox_router_log.db"
            evaluator.set_db(db_path)
            evaluator.store_evaluation(route_log_id, result)
        except Exception as e:
            result["_store_error"] = str(e)

        return result

    def workflow_summary(self):
        """当前会话工作流汇总 (P1: 含熵态统计)"""
        if not self.workflow_log:
            return "暂无工作流记录"
        n = len(self.workflow_log)
        mom_count = sum(1 for w in self.workflow_log if w["mom"])
        routes = set(w["route_id"] for w in self.workflow_log)
        # P1: 熵态统计 — 统计最近一次 mom_plan 的熵状态
        ent_stats = ""
        latest_ent = self._latest_entropy()
        if latest_ent:
            s = latest_ent.get("status")
            if s == "computed":
                ent_stats = (f" | 熵态: 自然熵={latest_ent.get('natural_entropy')}, "
                             f"压熵比={latest_ent.get('pressure_ratio')}, "
                             f"共识={latest_ent.get('consensus')}")
            else:
                ent_stats = f" | 熵态: {s}"
        return (f"会话共 {n} 次路由，{mom_count} 次 MoM 激活，涉及路由: {', '.join(routes)}"
                f"{ent_stats}")

    def _latest_entropy(self):
        """P1: 取最近一次含熵态的 mom_plan"""
        for w in reversed(self.workflow_log):
            mp = w.get("mom_plan")
            if isinstance(mp, dict) and "entropy" in mp:
                return mp["entropy"]
        return None

    # ============================================================
    # Middleware Pipeline 支持 (v2 — 向后兼容)
    # ============================================================
    #
    # 新增 process_with_pipeline() 方法，包装原有 process() 逻辑
    # 为 Middleware 链。原有 process() 接口不变，保持向后兼容。
    #
    # 用法:
    #   wf = AIXBoxWorkflow()
    #   chain = create_default_chain()
    #   plan = wf.process_with_pipeline("ACVR2A 证据", {}, chain)
    #
    # 或通过 set_middleware_chain() 设置持久链:
    #   wf.set_middleware_chain(chain)
    #   plan = wf.process_with_pipeline("ACVR2A 证据")
    # ============================================================

    def set_middleware_chain(self, chain: 'MiddlewareChain'):
        """
        设置持久 Middleware 链。

        设置后，process_with_pipeline() 将自动使用此链。
        要重置为手动模式，传入 None。

        Args:
            chain: MiddlewareChain 实例，或 None
        """
        self._middleware_chain = chain

    def get_middleware_chain(self) -> Optional['MiddlewareChain']:
        """获取当前设置的 Middleware 链。"""
        return self._middleware_chain

    def process_with_pipeline(self, message: str, context: Optional[dict] = None,
                               chain: Optional['MiddlewareChain'] = None) -> dict:
        """
        带 Middleware Pipeline 的全流程处理。

        调用方式优先级:
          1. 如果传入了 chain 参数，使用它
          2. 否则使用 set_middleware_chain() 设置的持久链
          3. 如果都没有，降级为普通 process() 调用

        流程:
          1. 创建 PipelineContext
          2. chain.before(ctx) — 依次执行各 Middleware 的 before()
          3. 调用原有 process() 核心逻辑
          4. chain.after(ctx, result) — 依次执行各 Middleware 的 after()
          5. 返回最终 result（可能被 after 修改过）

        Args:
            message: 用户消息
            context: 可选上下文 dict
            chain: 可选 MiddlewareChain（优先级最高）

        Returns:
            dict — 执行计划（与 process() 返回格式一致）
        """
        if not _HAS_PIPELINE:
            return self.process(message, context)

        # 如果没有 chain，降级为普通 process
        active_chain = chain or self._middleware_chain
        if active_chain is None:
            return self.process(message, context)

        context = context or {}

        # 1) 创建 PipelineContext
        ctx = PipelineContext(
            user_msg=message,
            context=context,
        )

        # 2) 执行 before() 链
        ctx.stage = "middleware_before"
        active_chain.run_before(ctx)

        # 如果在 before 链中发生了错误，尽早返回
        if ctx.is_error:
            result = self.process(message, context)
            result["pipeline_errors"] = ctx.errors
            result["pipeline_ctx"] = ctx.to_dict()
            return result

        # 3) 执行核心路由逻辑
        ctx.stage = "executing"
        result = self.process(message, context)

        # 将 Middleware 的信息注入 result
        if ctx.route_info:
            result["pipeline_route"] = dict(ctx.route_info)
        if ctx.skill_info:
            result["pipeline_skill"] = dict(ctx.skill_info)
        if ctx.metadata:
            result["pipeline_meta"] = dict(ctx.metadata)

        # 4) 执行 after() 链
        ctx.stage = "middleware_after"
        result = active_chain.run_after(ctx, result)

        # 5) 标记完成
        ctx.stage = "done"
        result["pipeline_elapsed"] = round(ctx.elapsed(), 4)
        result["pipeline_middleware_count"] = active_chain.count

        # 如果有错误，附加到 result
        if ctx.errors:
            result["pipeline_errors"] = ctx.errors

        # 6) 自动评价路由决策 (P0 层 — 不依赖 tool_calls)
        # 每次路由后立即评价结果有效性和规则合规性
        self._auto_evaluate_routing(result)

        return result

    def _auto_evaluate_routing(self, plan: dict):
        """对路由决策进行自动评价 (非阻塞, 静默写 route_log)"""
        decision = plan.get("decision", {}) or {}
        route_log_id = getattr(decision, "route_log_id", None) if hasattr(decision, "route_log_id") else None
        if route_log_id is None:
            route_log_id = plan.get("route_log_id")
        if route_log_id is None:
            return  # 无 route_log_id 无法写回

        try:
            evaluator = TrajectoryEvaluator()
            # 最小化轨迹: 只有路由决策, 无 tool_calls/replies
            traj = build_minimal_trajectory(
                route_id=getattr(decision, "route_id", "unknown") if hasattr(decision, "route_id") else "unknown",
                message=ctx.user_msg if "ctx" in dir() else plan.get("message", ""),
                tool_calls=[],
                replies=[],
                env_checks={"plan_valid": plan.get("mom_plan") is not None or bool(decision)},
                permissions=[getattr(decision, "target_agent", "")] if hasattr(decision, "target_agent") else [],
                rules={"route_id": getattr(decision, "route_id", None)},
            )
            result = evaluator.evaluate(traj, use_llm=False)
            # 写回 route_log
            evaluator.set_db("/tmp/aixbox_router_log.db")
            evaluator.store_evaluation(route_log_id, result)
        except Exception:
            pass


# Singleton
workflow = AIXBoxWorkflow()


# ========== CLI 测试 ==========

if __name__ == "__main__":
    wf = AIXBoxWorkflow()

    test_cases = [
        # (消息, 上下文)
        ("ACVR2A 的 GWAS 证据可信吗？",
         {"conclusion": "ACVR2A 与 2 型糖尿病因果关联置信度 0.866",
          "evidence": "GWAS: rs12922394 p=3e-8 OR=1.15, GTEx: 成纤维细胞表达, 48条证据行"}),

        ("头孢克肟 50mg bid 适合 20kg 儿童吗？",
         {"conclusion": "头孢克肟 30-60mg bid 适用于 20kg 儿童呼吸道感染",
          "patient": "6岁, 20kg, 无过敏史, 肾功能正常"}),

        ("帮我生成 HyperTarget 白皮书 PDF",
         {}),

        ("今天几号",
         {}),
    ]

    print(f"{'='*60}")
    print(f"  AIXBox 统一工作流引擎 v1")
    print(f"{'='*60}\n")

    for msg, ctx in test_cases:
        plan = wf.process(msg, ctx)
        d = plan["decision"]
        mom = plan["mom_plan"]

        print(f"── [{d['complexity']}] {msg}")
        print(f"   路由: {d['route_id']:25} 方法: {d['method']:<10}")
        print(f"   Agent: {str(d['target_agent']):20} 模型: {d['model']}")
        if d['mom_enabled']:
            print(f"   ⚠ MoM 验证: {'✓ 就绪' if mom and mom['status']=='ready_for_execution' else '○ 待结论'}")
            if mom:
                print(f"     视角: {', '.join(mom['strategies'])}")
                print(f"     建议: {mom['advice'][:50]}...")
        if plan['agent_context']:
            ctx_lines = plan['agent_context'].split('\n')
            print(f"   📋 轨迹互读: {ctx_lines[0]}")
            for line in ctx_lines[1:3]:
                print(f"      {line}")
            if len(ctx_lines) > 3:
                print(f"      ... 共 {len(ctx_lines)-1} 条记录")
        print(f"   提示: {plan['response_hint'][:80]}")
        print()

    print(f"=== 会话汇总 ===")
    print(f"  {wf.workflow_summary()}")
