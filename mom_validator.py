#!/usr/bin/env python3
"""
MoM (Mixture of Models) 验证模块

PPIO 对标实现：对高风险决策启用多模型交叉验证。
当前架构：单一 DeepSeek 模型，通过不同 Prompt 策略模拟"多视角验证"。
未来可扩展：真多模型 API 调用。

集成点：
  1. 靶点置信度声明（target-discovery）
  2. OPC 药学剂量/相互作用结论（opc-pharma）
  3. session_risk ≥ 0.6 的高风险会话
"""

import json, sqlite3, os
from datetime import datetime, timezone

MOM_LOG = os.environ.get("AIXBOX_MOM_DB", "/tmp/aixbox_mom_log.db")

# ========== Prompt 策略模板 ==========

PROMPT_STRATEGIES = {
    "target_confidence": {
        # 主视角：验证证据强度
        "verifier": {
            "system": "你是一个靶点验证专家，擅长严格评估科学证据。",
            "user": """你是一个靶点验证专家。请严格评估以下靶点结论的证据强度。

任务：验证以下靶点-疾病关联的置信度声明。

靶点结论：
{conclusion}

原始证据：
{evidence_context}

请评估：
1. 该置信度声明是否有足够证据支持？
2. 证据的弱点和局限性是什么？
3. 你给出的置信度分数（0-1）是多少？

请输出 JSON 格式：
{{
    "supports": true/false,
    "confidence_score": float,
    "weaknesses": ["弱项1", "弱项2"],
    "missing_evidence": ["缺失证据类型"],
    "recommendation": "一句话建议"
}}""",
        },

        # 反方视角：主动寻找漏洞
        "adversarial": {
            "system": "你是一个魔鬼代言人，专业从反面找茬。",
            "user": """你是靶点验证的'魔鬼代言人'。你的职责是找出结论中所有可能的漏洞。

靶点结论：
{conclusion}

请从以下角度攻击该结论：
1. 统计可靠性：样本量足够吗？多重检验校正做了吗？
2. 因果性：是关联还是因果？是否有反向因果或混淆因素？
3. 可重复性：其他独立队列是否验证过？
4. 生物学合理性：通路机制说得通吗？

输出 JSON：
{{
    "critical_issues": ["致命问题"],
    "moderate_concerns": ["中等问题"],
    "minor_issues": ["小问题"],
    "overall_assessment": "该结论是否可靠？",
    "score_adjustment": -0.1
}}""",
        },

        # 务实视角：关注可操作性和价值
        "pragmatic": {
            "system": "你是一个靶点商业评估专家，关注商业价值和可操作性。",
            "user": """你是靶点商业评估专家。关注该靶点的实际价值和可操作性。

靶点结论：
{conclusion}

请评估：
1. 该靶点的可药性如何？
2. 商业价值（市场规模、竞争格局）？
3. 如果置信度不足，下一步做什么实验能最快提升置信度？

输出 JSON：
{{
    "druggability": "high/medium/low",
    "commercial_value": "一句话评估",
    "next_step_experiment": "最推荐的下一个验证实验",
    "est_cost_next_step": "实验估算成本"
}}""",
        },
    },

    "opc_pharma": {
        # 药理学验证
        "verifier": {
            "system": "你是一名临床药学专家，擅长安全审核。",
            "user": """你是一名临床药学专家。请审核以下药学结论的安全性。

药学结论：
{conclusion}

患者信息：
{patient_context}

请评估：
1. 剂量是否合理（考虑年龄、体重、肾功能等）？
2. 有无严重药物相互作用？
3. 禁忌症是否被考虑？
4. 是否需要监测指标？

输出 JSON：
{{
    "dosage_appropriate": true/false,
    "interaction_risk": "high/medium/low",
    "contraindications_checked": true/false,
    "monitoring_needed": ["监测项"],
    "safety_rating": "safe/conditional/unsafe",
    "warnings": ["警告内容"]
}}""",
        },

        # 替代方案分析
        "alternatives": {
            "system": "你是药物治疗学专家，擅长制定替代方案。",
            "user": """你是药物治疗学专家。请分析以下药学结论的替代方案。

药学结论：
{conclusion}

请评估：
1. 是否有更优的一线治疗选择？
2. 特殊人群（孕/儿/老）是否有不同推荐？
3. 非药物替代方案？

输出 JSON：
{{
    "first_line_alternative": "首选替代方案",
    "special_population_notes": "特殊人群注意事项",
    "non_drug_options": ["非药物方案"],
    "guideline_consistency": "与指南一致/部分一致/不一致"
}}""",
        },
    },
}


class MoMValidator:
    """多模型验证引擎"""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(MOM_LOG)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mom_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                domain TEXT,
                conclusion TEXT,
                strategies_used TEXT,
                results TEXT,
                consensus TEXT,
                final_decision TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _call_model(self, system_prompt, user_prompt):
        """返回 Prompt 结构供 AIXClaw 工作流使用"""
        return {
            "system": system_prompt.strip(),
            "user": user_prompt.strip(),
            "format": "json",
        }

    def generate_verification_prompts(self, domain, conclusion, context=""):
        """
        生成多视角验证的 Prompt 列表。
        
        PROMPT_STRATEGIES[domain][strategy] = {
            "system": "...",    # system prompt
            "user": "...",      # user prompt (may contain {conclusion}, {evidence_context}, {patient_context})
        }

        返回: 策略名称 → {system, user, format} 的字典
        """
        if domain not in PROMPT_STRATEGIES:
            return {"error": f"Unknown domain: {domain}"}

        strategies = PROMPT_STRATEGIES[domain]
        result = {}
        for name, template in strategies.items():
            system_prompt = template["system"]
            user_prompt = template["user"].format(
                conclusion=conclusion,
                evidence_context=context,
                patient_context=context,
            )
            result[name] = self._call_model(system_prompt, user_prompt)
        return result

    def compute_consensus(self, domain, results):
        """
        根据多视角验证结果计算共识度。
        
        输入: results = {策略名: {评分/结论 dict}}
        输出: {consensus: str, score_range: (min,max), disagreements: []}
        """
        if domain == "target_confidence":
            scores = []
            for name, r in results.items():
                if isinstance(r, dict):
                    score = r.get("confidence_score", 0.5)
                    if isinstance(score, (int, float)):
                        scores.append(score)
                    adj = r.get("score_adjustment", 0)
                    if isinstance(adj, (int, float)):
                        scores.append(0.5 + adj)

            if not scores:
                return {"consensus": "unknown", "score_range": (0, 0), "disagreements": []}

            avg = sum(scores) / len(scores)
            spread = max(scores) - min(scores)

            if spread <= 0.15:
                consensus = "high"
            elif spread <= 0.3:
                consensus = "medium"
            else:
                consensus = "low"

            # ── 熵态指标（邓煜框架 / P1 2026-07-31）──
            # 自然态熵: 分数分散度 → 1 - (1 - spread) = spread
            natural_entropy = round(spread, 3)
            # 压熵后共识: avg 越接近 1 越低熵
            pressure_ratio = round(avg / (1.0 + spread) - 0.5, 3) if spread > 0 else 0.0

            return {
                "consensus": consensus,
                "avg_score": round(avg, 3),
                "score_range": (min(scores), max(scores)),
                "spread": round(spread, 3),
                "disagreements": [f"分数差异 {spread}"] if spread > 0.3 else [],
                # ── 熵态（P1）──
                "natural_entropy": natural_entropy,
                "pressure_ratio": pressure_ratio,
                "divergence_detail": [
                    {"perspective": k, "score": v.get("confidence_score", 0.5)}
                    for k, v in results.items()
                    if isinstance(v, dict)
                ] if spread > 0.3 else [],
            }

        if domain == "opc_pharma":
            verdicts = []
            for name, r in results.items():
                if isinstance(r, dict):
                    verdicts.append(r.get("safety_rating", "unknown"))

            if not verdicts:
                return {"consensus": "unknown", "verdicts": [], "disagreements": []}

            if "unsafe" in verdicts:
                consensus = "low"
            elif "conditional" in verdicts:
                consensus = "medium"
            elif all(v == "safe" for v in verdicts):
                consensus = "high"
            else:
                consensus = "medium"

            return {
                "consensus": consensus,
                "verdicts": verdicts,
                "disagreements": [],
            }

        return {"consensus": "unknown", "disagreements": []}

    def log_verification(self, domain, conclusion, strategies, results, consensus, decision):
        conn = sqlite3.connect(MOM_LOG)
        conn.execute("""
            INSERT INTO mom_log(timestamp, domain, conclusion, strategies_used,
                results, consensus, final_decision)
            VALUES (?,?,?,?,?,?,?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            domain, conclusion[:200],
            json.dumps(strategies, ensure_ascii=False),
            json.dumps(results, ensure_ascii=False),
            json.dumps(consensus, ensure_ascii=False),
            decision,
        ))
        conn.commit()
        conn.close()

    def verify(self, domain, conclusion, context=""):
        """
        全流程：生成验证 Prompt → 返回待执行计划。
        调用方执行各 Prompt 后调用 complete_verification()。
        """
        prompts = self.generate_verification_prompts(domain, conclusion, context)
        return {
            "prompts": prompts,
            "status": "pending_verification",
            "domain": domain,
            "conclusion": conclusion[:200],
        }

    def complete_verification(self, domain, conclusion, results, auto_card=True):
        """填入各视角执行结果 → 计算共识 → 记录日志 → 自动沉淀判断力卡片"""
        consensus = self.compute_consensus(domain, results)
        decision = consensus.get("consensus", "unknown")

        strategies_used = list(results.keys())
        self.log_verification(domain, conclusion, strategies_used, results, consensus, decision)

        # 判断力显性化：自动创建 JudgmentCard
        if auto_card:
            try:
                from judgment_card import from_mom_consensus
                from_mom_consensus(domain, conclusion, consensus)
            except ImportError:
                pass
            except Exception as e:
                print(f"[MoM] JudgmentCard 创建跳过: {e}")

        return {
            "consensus": consensus,
            "decision": decision,
            "recommendation": self._make_recommendation(domain, consensus, results),
            # ── 熵态（P1 2026-07-31）──
            "entropy": {
                "natural_entropy": consensus.get("natural_entropy", 0),
                "pressure_ratio": consensus.get("pressure_ratio", 0),
                "divergence": consensus.get("divergence_detail", []),
                "framework": "Deng Yu (t=0 independent → entropy increase)",
            },
        }

    def _make_recommendation(self, domain, consensus, results):
        if domain == "target_confidence":
            c = consensus.get("consensus", "unknown")
            avg = consensus.get("avg_score", 0.5)
            if c == "high":
                return f"高共识 (avg={avg:.2f})，可以采信。"
            elif c == "medium":
                return f"中等共识 (avg={avg:.2f})，建议补充证据再判断。"
            else:
                return f"低共识 (spread={consensus.get('spread')})，强烈建议暂缓决策。"

        elif domain == "opc_pharma":
            c = consensus.get("consensus", "unknown")
            if c == "high":
                return "安全验证通过。"
            elif c == "medium":
                return "有条件安全，需加上注意事项。"
            else:
                return "安全风险，建议拒绝执行。"

        return "无推荐"

    def stats(self, days=7):
        conn = sqlite3.connect(MOM_LOG)
        total = conn.execute("SELECT COUNT(*) FROM mom_log").fetchone()[0]
        by_domain = conn.execute("SELECT domain, COUNT(*) FROM mom_log GROUP BY domain").fetchall()
        by_consensus = conn.execute("SELECT consensus, COUNT(*) FROM mom_log GROUP BY consensus").fetchall()
        conn.close()
        return {"total": total, "by_domain": by_domain, "by_consensus": by_consensus}


# Singleton
mom = MoMValidator()


# ========== CLI 测试 ==========



# ══════════════════════════════════════════════════════════════════
# Pre-hoc MoM — 方案设计阶段风险预警 (Mei案例驱动)
# ══════════════════════════════════════════════════════════════════
# DataFlow-Harness 模式延伸: 不仅做结论后验证, 更做方案设计前预警
# 三个视角:
#   1. 临床安全 — 治疗方案的已知毒理风险
#   2. 剂量工程 — 剂量/载体/递送方式的合理性
#   3. 伦理公平 — 知情同意公平性 (特别是sponsor-patient利益绑定)
# ══════════════════════════════════════════════════════════════════

PRE_HOC_VIEWPOINTS = {
    "clinical_safety": {
        "name": "临床安全视角",
        "focus": "评估目标人群的脆弱性和已知毒理风险",
        "questions": [
            "目标人群是否有年龄/器官成熟度相关的特殊风险?",
            "治疗方案的已知毒理是否与目标人群匹配?",
            "动物模型的安全数据是否完全转化到临床?",
        ],
    },
    "dose_engineering": {
        "name": "剂量工程视角",
        "focus": "评估剂量选择的工程合理性",
        "questions": [
            "剂量选择是否有充分的剂量效应数据支撑?",
            "递送载体的免疫原性/剂量限制性毒性是否评估?",
            "剂量安全窗口 (therapeutic index) 是否足够宽?",
        ],
    },
    "ethics_equity": {
        "name": "伦理公平视角",
        "focus": "评估知情同意过程公平性",
        "questions": [
            "患者/家属与资助方之间是否存在经济绑定关系?",
            "是否存在'最后一搏'心理压力影响知情同意?",
            "终止标准是否在方案中明确定义并告知?",
        ],
    },
}

def pre_hoc_mom(
    protocol_description: str,
    target_population: str = "",
    animal_safety_summary: str = "",
    sponsor_patient_relationship: str = "",
) -> dict:
    """
    方案设计阶段的多视角风险预警。

    返回:
        {
            "risk_level": "low" | "moderate" | "high" | "critical",
            "viewpoints": {
                "clinical_safety": {"score": 0-1, "flags": [...], "recommendation": str},
                "dose_engineering": {"score": 0-1, "flags": [...], "recommendation": str},
                "ethics_equity": {"score": 0-1, "flags": [...], "recommendation": str},
            },
            "recommendation": str,
            "timestamp": str,
        }
    """
    results = {}
    flags = []
    
    for vp_id, vp_info in PRE_HOC_VIEWPOINTS.items():
        # 每个视角产出一个初步评分
        # 后续可以接入 LLM 做更精细的推理
        score = 0.5  # 默认中等风险
        vp_flags = []
        vp_rec = ""
        
        if vp_id == "clinical_safety":
            # 检测儿童/老人等脆弱人群
            vulnerable_keywords = ["儿童", "幼儿", "新生儿", "老人", "孕妇", "pediatric", "child", "infant", "elderly"]
            for kw in vulnerable_keywords:
                if kw in target_population.lower() or kw in protocol_description.lower():
                    vp_flags.append(f"目标人群为脆弱群体: {kw}")
                    score += 0.15
            
            # 检测动物模型 SAE
            sae_keywords = ["肝损伤", "死亡", "TMA", "severe", "lethal", "toxic", "损伤", "全部", "4/4", "all animals"]
            for kw in sae_keywords:
                if kw in animal_safety_summary.lower():
                    vp_flags.append(f"动物模型 SAE 信号: {kw}")
                    score += 0.25
            
            # 检测双载体/高剂量
            if "双载体" in protocol_description or "dual" in protocol_description.lower():
                vp_flags.append("双载体方案增加递送复杂度和免疫原性风险")
                score += 0.15
            if "超高剂量" in protocol_description or "high dose" in protocol_description.lower():
                vp_flags.append("高剂量方案增加免疫原性风险")
                score += 0.15
        
        elif vp_id == "dose_engineering":
            if "双载体" in protocol_description or "dual" in protocol_description.lower():
                vp_flags.append("双载体 AAV 效率损失需超高剂量补偿, 安全窗口收窄")
                score += 0.20
            if "AAV" in protocol_description or "腺病毒" in protocol_description:
                vp_flags.append("AAV 递送已知免疫原性风险随剂量增加")
                score += 0.10
            if "碱基编辑器" in protocol_description or "base edit" in protocol_description.lower():
                vp_flags.append("碱基编辑器的脱靶效应尚未充分表征")
                score += 0.10
        
        elif vp_id == "ethics_equity":
            if "资助" in sponsor_patient_relationship or "fund" in sponsor_patient_relationship.lower() or "invest" in sponsor_patient_relationship.lower():
                vp_flags.append("患者/家属与资助方存在经济绑定, 知情同意可能失效")
                score += 0.30
            if "家人" in sponsor_patient_relationship or "family" in sponsor_patient_relationship.lower() or "家属" in sponsor_patient_relationship:
                vp_flags.append("家属主动出资资助研究 — 强经济绑定的典型场景")
                score += 0.25
        
        # 综合每个视角的评分
        score = min(1.0, score)
        if score >= 0.7:
            vp_rec = "高风险, 建议重新评估或暂停"
        elif score >= 0.4:
            vp_rec = "中等风险, 需补充信息后再推进"
        else:
            vp_rec = "低风险, 可以继续但保持监测"
        
        results[vp_id] = {
            "score": round(score, 2),
            "flags": vp_flags,
            "recommendation": vp_rec,
        }
        flags.extend(vp_flags)
    
    # 综合风险等级
    max_score = max(r["score"] for r in results.values())
    if max_score >= 0.8:
        risk_level = "critical"
    elif max_score >= 0.6:
        risk_level = "high"
    elif max_score >= 0.4:
        risk_level = "moderate"
    else:
        risk_level = "low"
    
    if max_score >= 0.6:
        overall_rec = "方案存在重大风险, 建议在启动前补充毒理数据、重新设计剂量方案或重新审查知情同意流程"
    elif max_score >= 0.4:
        overall_rec = "方案存在中度风险, 建议针对性补充缺失信息"
    else:
        overall_rec = "方案风险可控"
    
    from datetime import datetime, timezone
    return {
        "risk_level": risk_level,
        "viewpoints": results,
        "recommendation": overall_rec,
        "flags": flags,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# 为旧的 mom 对象添加 pre-hoc 方法
_mom_v2_added = False
try:
    from mom_validator import mom as _old_mom
    # 动态注入(如果对象支持)
    if hasattr(_old_mom, '__dict__'):
        _old_mom.pre_hoc = pre_hoc_mom
        _old_mom.PRE_HOC_VIEWPOINTS = PRE_HOC_VIEWPOINTS
        _mom_v2_added = True
except (ImportError, AttributeError):
    pass


if __name__ == "__main__":
    # 靶点测试
    target_r = mom.verify(
        domain="target_confidence",
        conclusion="ACVR2A 与 2 型糖尿病有因果关联，置信度 0.866",
        context="GWAS: rs12922394 (p=3e-8, OR=1.15), GTEx: 成纤维细胞表达, 48条证据行"
    )
    print(f"Target verification: {len(target_r['prompts'])} strategies")
    for name in target_r['prompts']:
        print(f"  - {name}: system={target_r['prompts'][name]['system'][:40]}...")

    # 药学测试
    pharma_r = mom.verify(
        domain="opc_pharma",
        conclusion="头孢克肟 30-60mg bid 适用于 20kg 儿童呼吸道感染",
        context="患者: 6岁, 20kg, 无药物过敏史, 肾功能正常"
    )
    print(f"\nOPC verification: {len(pharma_r['prompts'])} strategies")
    for name in pharma_r['prompts']:
        print(f"  - {name}: system={pharma_r['prompts'][name]['system'][:40]}...")

    # 模拟完整流程
    print("\n--- Simulated completion ---")
    simulated = {
        "verifier": {"supports": True, "confidence_score": 0.82, "weaknesses": ["样本量中等"]},
        "adversarial": {"score_adjustment": -0.08, "critical_issues": [], "moderate_concerns": ["多重检验未确认"]},
        "pragmatic": {"druggability": "high", "commercial_value": "中型市场"},
    }
    final = mom.complete_verification("target_confidence",
        "ACVR2A 与 2 型糖尿病有因果关联，置信度 0.866", simulated)
    print(f"Consensus: {final['consensus']} (avg={final['consensus']['avg_score']:.3f})" if isinstance(final['consensus'], dict) else f"Consensus: {final['consensus']}")
    print(f"Recommendation: {final['recommendation'][:40]}")

    stats = mom.stats()
    print(f"\nMoM log: {stats}")
