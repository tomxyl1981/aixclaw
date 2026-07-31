#!/usr/bin/env python3
"""
AIXBox 操作符注册表 (Operator Registry)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

模式来源: DataFlow-Harness (北大开源, Apache-2.0)
  → 所有可执行操作定义在注册表中，Agent 仅能通过注册表选择操作
  → 消除 Agent"猜操作名/猜参数"导致的脚本幻觉
  → 配合 MCP 接口暴露，实现结构化约束

三个域:
  1. target-discovery / hms-evidence — 靶点发现证据管线
  2. opc-pharma — 药学咨询
  3. naye-sandbox — 那耶村/蜂群/沙盒

每个 Operator 定义:
  - id:   唯一标识符
  - name: 显示名称
  - domain: 所属域
  - description: 做什么
  - inputs: 所需输入 (名称, 类型, 描述, required?)
  - outputs: 输出 (名称, 类型, 描述)
  - procedure: 执行步骤提示 (给 Agent 的指引，不被直接调用)
"""

import json
from typing import Any, Optional


# ── 操作符定义 ──────────────────────────────────────────────────────

OPERATORS = {
    # ── 靶点发现域 ────────────────────────────────────────────────
    "search_pubmed": {
        "id": "search_pubmed",
        "name": "PubMed 文献检索",
        "domain": "target-discovery",
        "description": "通过 PMID 或 Gene Symbol 检索 PubMed 文献，提取靶点相关证据",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因符号 (如 ACVR2A)", "required": True},
            {"name": "disease", "type": "str", "description": "关联疾病", "required": False},
            {"name": "max_results", "type": "int", "description": "最大结果数", "default": 10, "required": False},
        ],
        "outputs": [
            {"name": "evidence_rows", "type": "list[dict]", "description": "提取的证据行列表 (PMID, 证据类型, 结论, 置信度)"},
        ],
        "procedure": "调用 evidence_pubmed_connector.py 的 search_and_extract() 方法",
    },
    "query_gwas": {
        "id": "query_gwas",
        "name": "GWAS Catalog 查询",
        "domain": "target-discovery",
        "description": "查询 GWAS Catalog (EMBL-EBI) 获取靶点的关联位点和统计量",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因符号", "required": True},
            {"name": "p_threshold", "type": "float", "description": "显著性阈值", "default": 5e-8, "required": False},
        ],
        "outputs": [
            {"name": "associations", "type": "list[dict]", "description": "显著关联列表 (RSID, p-value, OR/beta, 研究)"},
        ],
        "procedure": "调用 gwas_catalog_connector.py 的 query_by_gene() 方法",
    },
    "query_gtex_expression": {
        "id": "query_gtex_expression",
        "name": "GTEx 组织表达查询",
        "domain": "target-discovery",
        "description": "查询 GTEx Portal 获取靶点在多组织/多细胞类型的表达数据",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因 ENSEMBL ID 或符号", "required": True},
            {"name": "data_type", "type": "str", "description": "bulk_rna | snrnaseq", "default": "snrnaseq", "required": False},
        ],
        "outputs": [
            {"name": "expression_profiles", "type": "list[dict]", "description": "表达谱 (组织, 细胞类型, mwz/median)"},
        ],
        "procedure": "调用 gtex_connector.py 的 query_expression() 方法",
    },
    "scan_evidence_matrix": {
        "id": "scan_evidence_matrix",
        "name": "证据矩阵全扫描",
        "domain": "target-discovery",
        "description": "对靶点进行六维证据矩阵扫描 (PubMed + OpenTargets + GTEx + GWAS)，生成完整证据报告",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因符号", "required": True},
            {"name": "disease_context", "type": "str", "description": "疾病上下文，用于搜索过滤", "required": False},
        ],
        "outputs": [
            {"name": "matrix_summary", "type": "dict", "description": "六维证据矩阵汇总"},
            {"name": "confidence_score", "type": "float", "description": "Bayesian 置信度"},
            {"name": "contradictions", "type": "list[dict]", "description": "检测到的矛盾证据"},
        ],
        "procedure": "调用 target_evidence_matrix.py + evidence_server.py 的 /scan/{target} 端点",
    },
    "bayesian_update": {
        "id": "bayesian_update",
        "name": "Bayesian 置信度更新",
        "domain": "target-discovery",
        "description": "使用 Bayesian 后验更新合并新旧证据，计算综合置信度",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因符号", "required": True},
            {"name": "new_evidence", "type": "list[dict]", "description": "新证据行列表", "required": True},
        ],
        "outputs": [
            {"name": "posterior", "type": "float", "description": "后验置信度 (0-1)"},
            {"name": "contradiction_flags", "type": "list[str]", "description": "矛盾标记"},
        ],
        "procedure": "调用 hms_core/evolve.py 的 BayesianUpdateLayer.update() 方法",
    },
    "run_bilevel_optimize": {
        "id": "run_bilevel_optimize",
        "name": "双层自优化 (Bilevel Autoresearch)",
        "domain": "target-discovery",
        "description": "启用弱点挖掘→机制注入闭环，自动优化证据检索策略",
        "inputs": [
            {"name": "pipeline_stage", "type": "str", "description": "管线阶段名", "required": True},
            {"name": "auto_mode", "type": "bool", "description": "是否全自动运行", "default": False, "required": False},
        ],
        "outputs": [
            {"name": "injected_mechanisms", "type": "list[str]", "description": "已注入的机制"},
            {"name": "improvement_metrics", "type": "dict", "description": "改进指标对比"},
        ],
        "procedure": "调用 bilevel-autoresearch 技能的 executor.py 主循环",
    },

    # ── 药学咨询域 ────────────────────────────────────────────────
    "drug_dose_query": {
        "id": "drug_dose_query",
        "name": "药品剂量查询",
        "domain": "opc-pharma",
        "description": "查询药品标准剂量、儿童/老年人剂量调整方案",
        "inputs": [
            {"name": "drug_name", "type": "str", "description": "药品通用名", "required": True},
            {"name": "patient_info", "type": "str", "description": "患者信息 (年龄/体重/肾功能)", "required": False},
        ],
        "outputs": [
            {"name": "standard_dose", "type": "str", "description": "标准剂量"},
            {"name": "adjustment", "type": "str", "description": "剂量调整建议", "required": False},
        ],
        "procedure": "检索 OPC 药品知识库 + 说明书中剂量信息",
    },
    "drug_interaction_check": {
        "id": "drug_interaction_check",
        "name": "药物相互作用检查",
        "domain": "opc-pharma",
        "description": "检查两种或多种药物的潜在相互作用",
        "inputs": [
            {"name": "drugs", "type": "list[str]", "description": "药品列表", "required": True},
            {"name": "severity_filter", "type": "str", "description": "严重程度过滤: all | major | moderate | minor", "default": "all", "required": False},
        ],
        "outputs": [
            {"name": "interactions", "type": "list[dict]", "description": "相互作用列表 (药对, 严重程度, 机制, 建议)"},
        ],
        "procedure": "检索药品知识库的相互作用表",
    },
    "prescription_audit": {
        "id": "prescription_audit",
        "name": "处方审核",
        "domain": "opc-pharma",
        "description": "审核处方的合理性，包括适应症、剂量、禁忌症",
        "inputs": [
            {"name": "prescription", "type": "str", "description": "处方文本", "required": True},
            {"name": "patient_profile", "type": "str", "description": "患者档案", "required": False},
        ],
        "outputs": [
            {"name": "audit_result", "type": "str", "description": "审核结论: 合理 | 需关注 | 不合理"},
            {"name": "issues", "type": "list[str]", "description": "发现的问题列表"},
        ],
        "procedure": "调用 OPC 药学审核管线",
    },
    "opc_mom_verify": {
        "id": "opc_mom_verify",
        "name": "药学多视角验证 (MoM)",
        "domain": "opc-pharma",
        "description": "对药学结论进行多视角交叉验证 (药理/替代方案/安全性)",
        "inputs": [
            {"name": "conclusion", "type": "str", "description": "待验证的结论", "required": True},
            {"name": "patient_context", "type": "str", "description": "患者上下文", "required": False},
            {"name": "evidence_context", "type": "str", "description": "证据上下文", "required": False},
        ],
        "outputs": [
            {"name": "consensus", "type": "float", "description": "共识分 (0-1)"},
            {"name": "per_verdicts", "type": "dict", "description": "各视角判断"},
        ],
        "procedure": "调用 mom_validator.py 的 complete_verification() 方法",
    },

    # ── 那耶沙盒域 ────────────────────────────────────────────────
    "naye_simulate_swarm": {
        "id": "naye_simulate_swarm",
        "name": "蜂群仿真",
        "domain": "naye-sandbox",
        "description": "在沙盒中仿真蜂群协调行为（3D打印机/无人机群）",
        "inputs": [
            {"name": "node_count", "type": "int", "description": "节点数量", "required": True},
            {"name": "task_description", "type": "str", "description": "任务描述", "required": True},
            {"name": "duration_seconds", "type": "int", "description": "仿真时长", "default": 300, "required": False},
        ],
        "outputs": [
            {"name": "simulation_log", "type": "str", "description": "仿真运行日志"},
            {"name": "metrics", "type": "dict", "description": "关键指标 (收敛时间/消息量/故障处理)"},
        ],
        "procedure": "调用那耶沙盒仿真引擎 (尚在开发中)",
    },
    "naye_dsl_compile": {
        "id": "naye_dsl_compile",
        "name": "建筑 DSL 编译",
        "domain": "naye-sandbox",
        "description": "将建筑描述 (DSL) 编译为蜂群可执行的分块打印指令",
        "inputs": [
            {"name": "dsl_input", "type": "str", "description": "建筑 DSL 描述", "required": True},
            {"name": "printer_count", "type": "int", "description": "打印机数量", "default": 3, "required": False},
        ],
        "outputs": [
            {"name": "blocks", "type": "list[dict]", "description": "分块列表 (每块: 坐标, 体积, 材料, 时序依赖)"},
            {"name": "estimated_time", "type": "float", "description": "预估打印时间 (分钟)"},
        ],
        "procedure": "调用蜂群建筑 DSL 编译器 (Phase 1 设计中)",
    },

    # ── 通用工具域 ────────────────────────────────────────────────
    "generate_report": {
        "id": "generate_report",
        "name": "报告生成",
        "domain": "general",
        "description": "将结构化数据生成为 Markdown/PDF 报告",
        "inputs": [
            {"name": "template", "type": "str", "description": "报告模板: buy_side_memo | whitepaper | summary", "required": True},
            {"name": "data", "type": "dict", "description": "数据内容", "required": True},
        ],
        "outputs": [
            {"name": "report_path", "type": "str", "description": "输出文件路径"},
        ],
        "procedure": "调用报告生成管线 (MD → Pandoc PDF)",
    },
    "mom_verification": {
        "id": "mom_verification",
        "name": "MoM 多视角验证",
        "domain": "general",
        "description": "对高风险结论执行多视角 (验证者/对抗/实用) 共识验证",
        "inputs": [
            {"name": "domain", "type": "str", "description": "验证域: target_confidence | opc_pharma", "required": True},
            {"name": "conclusion", "type": "str", "description": "待验证的结论", "required": True},
            {"name": "context", "type": "str", "description": "验证上下文", "required": False},
        ],
        "outputs": [
            {"name": "consensus", "type": "float", "description": "共识分"},
            {"name": "verdicts", "type": "dict", "description": "各视角判断详情"},
        ],
        "procedure": "调用 mom_validator.py 的 complete_verification() 方法",
    },
    "semantic_reroute": {
        "id": "semantic_reroute",
        "name": "语义重路由",
        "domain": "general",
        "description": "分析用户消息意图并重新路由到最合适的 Agent/管线",
        "inputs": [
            {"name": "message", "type": "str", "description": "用户消息", "required": True},
            {"name": "context", "type": "dict", "description": "上下文", "required": False},
        ],
    },
    # ── 安全反指征域 (SAFETY, 第七维) ──────────────────────────
    "safety_scan_contraindication": {
        "id": "safety_scan_contraindication",
        "name": "安全反指征扫描",
        "domain": "safety",
        "description": "对靶点扫描已知安全反指征: 动物模型SAE/临床AE/已知毒性。发现SEVERE信号时自动设置置信度上限0.20",
        "inputs": [
            {"name": "target", "type": "str", "description": "靶点基因符号", "required": True},
            {"name": "disease_context", "type": "str", "description": "疾病上下文", "required": False},
        ],
        "outputs": [
            {"name": "contraindications", "type": "list[dict]", "description": "安全反指征列表 (严重程度, 信号描述, 受影响人群)"},
            {"name": "safety_ceiling", "type": "float", "description": "安全因素导致的置信度上限"},
        ],
        "procedure": "调用 target_evidence_matrix.py 的 EvidenceMatrixBuilder.from_safety() 方法",
    },
    "pre_hoc_mom_safety": {
        "id": "pre_hoc_mom_safety",
        "name": "Pre-hoc MoM 方案风险预警",
        "domain": "safety",
        "description": "在治疗方案设计阶段执行多视角风险预警: 检测动物模型AE/剂量合理性/目标人群脆弱性/知情同意公平性",
        "inputs": [
            {"name": "protocol", "type": "str", "description": "治疗方案描述", "required": True},
            {"name": "target", "type": "str", "description": "靶点/基因", "required": False},
            {"name": "population", "type": "str", "description": "目标人群 (如儿童, 成人)", "required": False},
            {"name": "animal_safety_data", "type": "str", "description": "动物毒理数据", "required": False},
        ],
        "outputs": [
            {"name": "risk_assessment", "type": "str", "description": "风险评估: low | moderate | high | critical"},
            {"name": "risk_flags", "type": "list[str]", "description": "风险标记列表"},
            {"name": "recommendation", "type": "str", "description": "行动建议"},
        ],
        "procedure": "调用 mom_validator.py 的 pre_hoc_mom() 方法; 三个视角: 临床安全/工程剂量/伦理公平",
    },

    # ── AI 结构预测域 (大厂模型接入) ──────────────
    "run_protenix": {
        "id": "run_protenix",
        "name": "Protenix 蛋白质结构预测",
        "domain": "target-discovery",
        "description": "调用字节跳动开源Protenix预测蛋白质三维结构",
        "inputs": [
            {"name": "sequence", "type": "str", "description": "氨基酸单字母序列", "required": True},
            {"name": "mode", "type": "str", "description": "monomer|multimer", "default": "monomer", "required": False},
        ],
        "outputs": [
            {"name": "pdb", "type": "str"},
            {"name": "plddt", "type": "float", "description": "pLDDT 0-100"},
            {"name": "ptm", "type": "float", "description": "pTM 0-1"},
        ],
        "procedure": "调用 protenix_adapter.py 的 run_protenix()",
    },
    "run_helixfold3": {
        "id": "run_helixfold3",
        "name": "HelixFold3 结构预测",
        "domain": "target-discovery",
        "description": "调用百度开源HelixFold3蛋白质/RNA/DNA结构预测",
        "inputs": [
            {"name": "sequences", "type": "list", "description": "序列列表(protein/rna/dna)", "required": True},
        ],
        "outputs": [
            {"name": "pdb", "type": "str"},
            {"name": "confidence_score", "type": "float", "description": "置信度 0-1"},
            {"name": "iptm", "type": "float", "description": "接口预测TM"},
        ],
        "procedure": "调用 helixfold_adapter.py 的 run_helixfold3()",
    },
}

# ── 域分类索引 ──

def list_operators_by_domain(domain: str) -> list[dict]:
    """按域列出操作符"""
    return [op for op in OPERATORS.values() if op["domain"] == domain]

def list_operator_categories() -> list[str]:
    """列出所有域"""
    return sorted(set(op["domain"] for op in OPERATORS.values()))

def get_operator_detail(operator_id: str) -> Optional[dict]:
    """获取单个操作符详情"""
    return OPERATORS.get(operator_id)

def list_all_operators() -> list[dict]:
    """列出所有操作符"""
    return list(OPERATORS.values())


# ── 验证 ──────────────────────────────────────────────────────────

def validate_operator_chain(operator_ids: list[str]) -> dict:
    """
    验证操作符链 (DAG) 的结构合法性。

    类似 DataFlow 的 Validation Engine:
      - 检查每个操作符是否存在
      - 检查相邻操作符的输入输出类型兼容性
      - 识别缺失的中间操作符

    Args:
        operator_ids: 操作符 ID 列表，表示执行顺序

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
        }
    """
    errors = []
    warnings = []

    for i, op_id in enumerate(operator_ids):
        op = get_operator_detail(op_id)
        if not op:
            errors.append(f"[{i}] 操作符 '{op_id}' 不存在")
            continue

    if not errors:
        # 检查相邻操作符的域一致性
        for i in range(len(operator_ids) - 1):
            a = get_operator_detail(operator_ids[i])
            b = get_operator_detail(operator_ids[i + 1])
            if a and b and a.get("domain") != b.get("domain") and a.get("domain") != "general" and b.get("domain") != "general":
                warnings.append(
                    f"操作符 '{operator_ids[i]}' (域={a['domain']}) → "
                    f"'{operator_ids[i+1]}' (域={b['domain']}) 跨域组合"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ── MCP 兼容性接口 ───────────────────────────────────────────────

def mcp_tool_spec() -> list[dict]:
    """
    生成兼容 MCP Server 的工具定义列表。

    用于 HyperTarget MCP Server 或其他 MCP 端点，
    让 Agent 通过 MCP 工具访问 Operator Registry。

    每个 operator 映射为一个 MCP tool。

    返回格式符合 MCP Tool schema:
    {
        "name": str,
        "description": str,
        "inputSchema": {...}
    }
    """
    tools = []
    for op_id, op in OPERATORS.items():
        props = {}
        required = []
        for inp in op.get("inputs", []):
            prop = {
                "type": inp.get("type", "string"),
                "description": inp.get("description", ""),
            }
            if "default" in inp:
                prop["default"] = inp["default"]
            props[inp["name"]] = prop
            if inp.get("required", False):
                required.append(inp["name"])

        tools.append({
            "name": f"operator_{op_id}",
            "description": op["description"],
            "inputSchema": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        })
    return tools


# ── CLI ──────────────────────────────────────────────────────────

def print_registry():
    print("=" * 65)
    print("  AIXBox 操作符注册表 (Operator Registry)")
    print("=" * 65)
    print()

    for category in list_operator_categories():
        ops = list_operators_by_domain(category)
        print(f"  [{category}] ({len(ops)} 操作符)")
        for op in ops:
            inp_names = ", ".join(i["name"] for i in op.get("inputs", []))
            print(f"    {op['id']:<25} 输入: {inp_names}")
        print()

    print(f"  总计: {len(OPERATORS)} 操作符, {len(list_operator_categories())} 域")


if __name__ == "__main__":
    print_registry()

    # 测试验证
    chain = ["search_pubmed", "query_gwas", "bayesian_update", "generate_report"]
    result = validate_operator_chain(chain)
    print(f"\n  链验证: {result}")

    # 测试 MCP spec
    tools = mcp_tool_spec()
    print(f"\n  MCP 工具数: {len(tools)}")
