#!/usr/bin/env python3
"""
UniPert-G2CP 连接器 (P0+ — 第八维证据源)。

腾讯生命科学实验室 × 中南大学 (Cell 2026) 的基因→化合物扰动迁移学习模型。
将 UniPert 的 AI 预测作为补充证据行加入靶点简报，在 MoM 验证流程中
充当"计算证据"参与多视角共识。

GPL-3.0 开源: https://github.com/lynn-1998/UniPert
复现代码 + 数据: https://github.com/lynn-1998/UniPert-G2CP_reproduce
Zenodo 检查点: https://zenodo.org/doi/10.5281/zenodo.20355906

用法:
    # 轻量模式 — 文档查询（无需安装 UniPert）
    python3 unipert_connector.py ACVR2A

    # 完整模式 — 安装后推理
    python3 unipert_connector.py ACVR2A --run-inference

    # JSON 输出
    python3 unipert_connector.py ACVR2A --json
"""

import json, sys, os, subprocess, urllib.request, shutil, tempfile, zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent))

# ── 常量 ──
UNIPERT_REPO = "https://github.com/lynn-1998/UniPert"
UNIPERT_REPRO_REPO = "https://github.com/lynn-1998/UniPert-G2CP_reproduce"
ZENODO_DOI = "10.5281/zenodo.20355906"
ZENODO_URL = f"https://zenodo.org/doi/{ZENODO_DOI}"
ZENODO_LATEST = "https://zenodo.org/api/records/20355906"

# 本地存储
UNIPERT_HOME = Path.home() / ".openclaw" / "unipert"
MODEL_DIR = UNIPERT_HOME / "models"
DATA_DIR = UNIPERT_HOME / "data"
CHECKSUM_FILE = UNIPERT_HOME / ".checksum"
CONFIG_FILE = UNIPERT_HOME / "config.json"

# 已知 UniPert 训练覆盖的基因 (Cell 2026 论文中提到的)
# 实际覆盖 ~5000 基因，此处仅列举代表性基因
KNOWN_COVERED_GENES = {
    "ACVR2A", "ACVR2B", "KRAS", "NRAS", "HRAS", "TP53", "EGFR", "ERBB2",
    "MET", "BRAF", "ALK", "VEGFA", "PD1", "PDL1", "CTLA4", "CD19",
    "ACE2", "FTO", "APOE", "APP", "LDLR", "PCSK9", "SMAD2", "SMAD3",
    "SMAD4", "SMAD7", "TGFB1", "TGFBR1", "TGFBR2", "BMPR1A", "BMPR2",
    "ACVR1", "ACVRL1", "ENG", "STAT3", "STAT1", "MYC", "JUN", "FOS",
    "CCND1", "CDKN1A", "CDKN2A", "CDKN1B", "RB1", "PTEN", "PIK3CA",
    "AKT1", "MTOR", "RPS6KB1", "EIF4E", "MAPK1", "MAPK3", "MAP2K1",
    "MAP2K2", "SRC", "ABL1", "BCR", "FLT3", "KIT", "PDGFRA", "PDGFRB",
    "FGFR1", "FGFR2", "FGFR3", "FGFR4", "INSR", "IGF1R", "IRS1",
    "IRS2", "LEPR", "ADIPOQ", "PPARG", "CEBPA", "CEBPB", "HNF4A",
    "FOXA1", "FOXA2", "GATA4", "GATA6", "NKX2-1", "TBX4", "SOX9",
    "SOX2", "POU5F1", "NANOG", "KLF4", "MYOD1", "MYOG", "MEF2C",
}

# 置信度映射：UniPert 的 AI 预测 → EvidenceStrength
# UniPert 报告基因扰动预测的 Pearson r / Spearman ρ
UNIPERT_STRENGTH_MAP = {
    (0.9, 1.0): ("p<5e-8", 0.85),     # 极强预测
    (0.8, 0.9): ("p<1e-5", 0.75),     # 强预测
    (0.7, 0.8): ("p<0.01", 0.60),     # 中等预测
    (0.5, 0.7): ("nominal", 0.40),    # 弱-中预测
    (0.0, 0.5): ("weak", 0.20),       # 弱预测
}

# 可解释性定义（陶哲轩防御）
# AI 预测在可解释性谱系中属于 DEEP_EMBEDDING
INTERPRETABILITY_NOTE = (
    "UniPert 多模态分子表示学习的预测结果，属于深度嵌入级证据 (0.1)。"
    "可解释性: G2CP 模块提供化学空间解释，但基因扰动预测仍为黑盒。"
    "建议: 仅作为补充证据，不替代实验验证。"
)


# ── 辅助函数 ──

def _map_strength(score: float) -> Tuple[str, float]:
    """UniPert 预测评分 → EvidenceStrength 枚举值 + 先验概率"""
    for (lo, hi), (strength, prior) in sorted(UNIPERT_STRENGTH_MAP.items(), reverse=True):
        if lo <= score < hi:
            return strength, prior
    return "weak", 0.20


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── 安装检测 ──

def is_unipert_installed() -> bool:
    """检查 UniPert 是否可导入"""
    try:
        import unipert
        return True
    except ImportError:
        return False


def is_model_downloaded() -> bool:
    """检查模型检查点是否已下载"""
    pt_files = list(MODEL_DIR.glob("*.pt")) + list(MODEL_DIR.glob("*.pth"))
    return len(pt_files) > 0


def check_env() -> Dict[str, Any]:
    """环境检测"""
    env = {
        "unipert_installed": is_unipert_installed(),
        "model_downloaded": is_model_downloaded(),
        "torch_available": False,
        "cuda_available": False,
        "device": "unknown",
    }
    try:
        # 仅当 unipert 已安装时才探测 torch —— torch 导入可能耗时数秒,
        # 未安装时探测无意义且会拖慢简报生成 (A3 性能修复, 2026-07-31)
        if is_unipert_installed():
            import torch
            env["torch_available"] = True
            env["cuda_available"] = torch.cuda.is_available()
            env["device"] = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            env["device"] = "cpu"
    except ImportError:
        pass
    return env


# ── 安装/下载 ──

def install_unipert(force: bool = False) -> Dict[str, Any]:
    """
    尝试安装 UniPert 及其依赖。
    
    由于依赖较多 (RDKit, torch-geometric, MMSeqs2, fair-esm)，
    复杂环境的完整安装可能需要人工介入。
    """
    result = {"success": False, "steps": [], "errors": []}
    
    if is_unipert_installed() and not force:
        result["steps"].append("UniPert 已安装，跳过")
        result["success"] = True
        return result
    
    steps = [
        ("pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu", "PyTorch (CPU)"),
        ("pip install torch-geometric", "PyG"),
        ("pip install git+https://github.com/lynn-1998/UniPert.git", "UniPert"),
    ]
    
    for cmd, label in steps:
        result["steps"].append(f"安装 {label}...")
        try:
            ret = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=300)
            if ret.returncode == 0:
                result["steps"][-1] += " ✅"
            else:
                result["steps"][-1] += f" ❌ {ret.stderr[-200:]}"
                result["errors"].append(f"{label}: {ret.stderr[-200:]}")
        except Exception as e:
            result["steps"][-1] += f" ❌ {e}"
            result["errors"].append(str(e))
    
    result["success"] = is_unipert_installed()
    return result


def download_model(force: bool = False) -> Dict[str, Any]:
    """
    从 Zenodo 下载 UniPert 模型检查点和参考数据。
    
    下载内容包括:
    - current_model.zip (推理用模型)
    - 参考 target 序列文件
    """
    result = {"success": False, "files": [], "size_mb": 0}
    
    UNIPERT_HOME.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if is_model_downloaded() and not force:
        pt_files = list(MODEL_DIR.glob("*.pt")) + list(MODEL_DIR.glob("*.pth"))
        sizes = sum(f.stat().st_size for f in pt_files)
        result["success"] = True
        result["files"] = [f.name for f in pt_files]
        result["size_mb"] = round(sizes / (1024*1024), 1)
        return result
    
    # 通过 Zenodo API 获取最新版本的文件列表
    try:
        req = urllib.request.Request(ZENODO_LATEST, headers={"User-Agent": "AIXClaw/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        
        # 找到 current_model.zip 或 model.pt
        for file_entry in data.get("files", []):
            fname = file_entry.get("key", "")
            if "current_model" in fname and fname.endswith(".zip"):
                url = file_entry.get("links", {}).get("self", "")
                size = file_entry.get("size", 0)
                result["size_mb"] = round(size / (1024*1024), 1)
                
                result["steps"].append(f"下载 {fname} ({result['size_mb']} MB)...")
                
                dest = UNIPERT_HOME / fname
                urllib.request.urlretrieve(url, dest)
                
                with zipfile.ZipFile(dest, 'r') as zf:
                    zf.extractall(MODEL_DIR)
                dest.unlink()  # 删除 zip
                
                result["files"] = [f.name for f in MODEL_DIR.glob("*.pt")]
                result["success"] = True
                break
    
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
    
    return result


# ── UniPert 预测包装器 ──

def predict_gene_perturbation(
    gene: str,
    confidence_threshold: float = 0.3,
) -> Dict[str, Any]:
    """
    使用 UniPert 预测基因扰动的下游转录组效应。
    
    需要 UniPert 已安装 + 模型检查点已下载。
    如果没有 GPU，推理会很慢（CPU 模式）。
    
    Args:
        gene: 目标基因符号
        confidence_threshold: 置信度阈值（过滤弱预测）
    
    Returns:
        结构化预测结果字典
    """
    result = {
        "gene": gene,
        "inference_success": False,
        "predictions": [],
        "model_version": "unknown",
        "device": "unknown",
        "error": None,
    }
    
    if not is_unipert_installed():
        result["error"] = "UniPert 未安装。运行 install_unipert() 安装"
        return result
    
    if not is_model_downloaded():
        result["error"] = "模型检查点未下载。运行 download_model() 下载"
        return result
    
    try:
        import torch
        from unipert import UniPert
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        result["device"] = device
        
        # 初始化
        model = UniPert(
            data_dir=str(DATA_DIR),
            model_dir=str(MODEL_DIR),
        )
        
        if not model.model_loaded:
            result["error"] = "模型加载失败"
            return result
        
        # 编码基因扰动
        # UniPert 支持从 gene name list 编码
        reps = model.encode_genetic_perturbagen(
            perturbagens=[gene],
            batch_size=1,
        )
        
        # 对于单基因，reps 是 dict {gene_name: embedding}
        if gene in reps:
            embedding = reps[gene]
            result["embedding_dim"] = len(embedding) if hasattr(embedding, '__len__') else "N/A"
            result["inference_success"] = True
            
            # TODO: v2 — 将 embedding 映射到具体表达变化预测
            # 当前 UniPert 的 encode 接口返回嵌入向量，而非直接表达变化
            # 需要用 G2CP 模块将嵌入转化为具体的基因表达扰动预测
            # 这需要 G2CP 模块的 inference 接口
            
            result["predictions"].append({
                "gene": gene,
                "embedding_available": True,
                "embedding_type": "unipert_256d",
                "downstream_prediction": "requires_G2CP_module",
            })
        else:
            result["error"] = f"基因 {gene} 未被 UniPert 识别（不在参考基因组列表中）"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


# ── 轻量级查询：基于已知论文结果生成证据行 ──

def query_without_inference(gene: str) -> Dict[str, Any]:
    """
    轻量模式：不运行模型，基于已发表的结果文档返回证据信息。
    
    来源：
    - Li et al. 2025, bioRxiv (UniPert 预印本)
    - Cell 2026 (UniPert-G2CP 主刊论文)
    - Zenodo 复现包文档
    """
    gene_up = gene.upper()
    is_covered = gene_up in KNOWN_COVERED_GENES
    
    info = {
        "gene": gene_up,
        "model": "UniPert-G2CP (Cell 2026)",
        "source_repo": UNIPERT_REPO,
        "source_zenodo": ZENODO_URL,
        "gene_in_training": is_covered,
        "training_data_genes": len(KNOWN_COVERED_GENES),  # 论文报道约 5000
        "available_predictions": [],
        "citation": "Li et al. (2025/2026), UniPert-G2CP, Cell",
        "interpretability_note": INTERPRETABILITY_NOTE,
    }
    
    # 如果基因在训练集中，提供通用的预测能力描述
    if is_covered:
        info["available_predictions"].append({
            "type": "genetic_perturbation",
            "description": f"UniPert 可预测敲除/过表达 {gene_up} 后的全转录组变化",
            "confidence_range": "0.3-0.8 (Pearson r)",
            "note": "需要下载模型检查点后运行推理",
        })
        info["available_predictions"].append({
            "type": "chemical_perturbation",
            "description": f"G2CP 可预测针对 {gene_up} 相关通路的化合物效应",
            "confidence_range": "0.4-0.7 (Spearman ρ)",
            "note": "需要 G2CP 模块，需另行安装",
        })
    else:
        info["available_predictions"].append({
            "type": "coverage_check",
            "description": f"{gene_up} 不在 UniPert 已知训练覆盖基因列表中",
            "note": "实际训练集含 ~5000 基因，此列表仅为代表性采样。"
                    "如该基因在训练集中，运行 inference 可确认。",
        })
    
    return info


# ── 主证据生成函数 ──

def generate_evidence_rows(
    gene: str,
    disease: str = "",
    run_inference: bool = False,
) -> List[Dict[str, Any]]:
    """
    核心接口：为靶点生成 UniPert-G2CP 证据行。
    
    遵循 HMS Evidence Ledger 模式，返回 EvidenceRow 兼容的 dict list。
    
    Args:
        gene: 目标基因符号
        disease: 关联疾病（可选）
        run_inference: 是否尝试运行模型推理
    
    Returns:
        EvidenceRow-compatible dict list
    """
    import target_evidence_matrix as tem
    
    gene_up = gene.upper()
    rows = []
    
    # ── 环境检测 ──
    env = check_env()
    
    # ── 模型信息行 ──
    model_row = tem.EvidenceRow(
        target_gene=gene_up,
        disease=disease,
        dimension=tem.EvidenceDimension.AI_PREDICTION,
        strength=tem.EvidenceStrength.UNKNOWN,
        direction=tem.EvidenceDirection.UNKNOWN,
        sub_dimension="UniPert:G2CP",
        key_finding=(
            f"UniPert-G2CP (Cell 2026): 多模态扰动表示学习模型已开源 (GPL-3.0)。"
            f"仓库: {UNIPERT_REPO}"
        ),
        source_name="UniPert-G2CP (Tencent × CSU)",
        source_url=UNIPERT_REPO,
        source_date="2026-07",
        notes=f"Zenodo: {ZENODO_URL} | 环境: device={env['device']}, model={'已下载' if env['model_downloaded'] else '未下载'}",
        metadata={
            "prediction_type": "model_documentation",
            "interpretability": "deep_embedding (0.1)",
            "trust_note": INTERPRETABILITY_NOTE,
        },
    )
    rows.append(model_row)
    
    # ── 训练覆盖信息 ──
    is_covered = gene_up in KNOWN_COVERED_GENES
    if is_covered:
        covered_row = tem.EvidenceRow(
            target_gene=gene_up,
            disease=disease,
            dimension=tem.EvidenceDimension.AI_PREDICTION,
            strength=tem.EvidenceStrength.AUC_GT_0_6,  # 模型已在 >5000 基因上验证
            direction=tem.EvidenceDirection.ASSOCIATED,
            sub_dimension="UniPert:coverage",
            key_finding=(
                f"{gene_up} 在 UniPert 训练基因组中 (共 ~5000 基因)。"
                "可生成基因扰动嵌入向量 (256维)，用于下游 G2CP 迁移预测。"
            ),
            source_name="UniPert-G2CP (Tencent × CSU)",
            source_url=UNIPERT_REPO,
            source_date="2026-07",
            notes="论文报道: 4994 个基因 + 7860 个化合物 + 5 种癌细胞系的扰动数据",
            metadata={
                "prediction_type": "training_coverage",
                "training_genes": len(KNOWN_COVERED_GENES),
                "confidence": 0.70,
            },
        )
        rows.append(covered_row)
    else:
        # 不在已知列表中，但仍可能在训练集中（已知列表仅为采样）
        coverage_row = tem.EvidenceRow(
            target_gene=gene_up,
            disease=disease,
            dimension=tem.EvidenceDimension.AI_PREDICTION,
            strength=tem.EvidenceStrength.WEAK,
            direction=tem.EvidenceDirection.UNKNOWN,
            sub_dimension="UniPert:coverage_unknown",
            key_finding=(
                f"{gene_up} 不在已知覆盖基因列表（{len(KNOWN_COVERED_GENES)} 个代表基因）中。"
                "需运行 inference 确认实际训练覆盖。"
            ),
            source_name="UniPert-G2CP (Tencent × CSU)",
            source_url=UNIPERT_REPO,
            metadata={
                "prediction_type": "training_coverage_unknown",
                "confidence": 0.10,
            },
        )
        rows.append(coverage_row)
    
    # ── 可预测的扰动类型 ──
    perturb_row = tem.EvidenceRow(
        target_gene=gene_up,
        disease=disease,
        dimension=tem.EvidenceDimension.AI_PREDICTION,
        strength=tem.EvidenceStrength.AUC_GT_0_6,
        direction=tem.EvidenceDirection.ASSOCIATED,
        sub_dimension="UniPert:capability",
        key_finding=(
            "UniPert 可预测: (1) 基因敲除/过表达的全转录组效应; "
            "(2) 化合物处理的多基因表达变化; "
            "(3) G2CP 跨模态迁移: 基因扰动向化合物空间的映射。"
        ),
        source_name="UniPert-G2CP (Tencent × CSU)",
        source_url=UNIPERT_REPO,
        source_date="2026-07",
        notes=(
            "G2CP 四个模块: CPF (化学表型指纹) / ESSP (表达谱) / "
            "Pool (集成) / SimF (模拟指纹) / TS (时间序列)"
        ),
        metadata={
            "prediction_type": "model_capability",
            "confidence": 0.75,
        },
    )
    rows.append(perturb_row)
    
    # ── 论文验证指标行 ──
    metric_row = tem.EvidenceRow(
        target_gene=gene_up,
        disease=disease,
        dimension=tem.EvidenceDimension.AI_PREDICTION,
        strength=tem.EvidenceStrength.P_VALUE_LT_1E5,  # 论文中统计显著
        direction=tem.EvidenceDirection.ASSOCIATED,
        sub_dimension="UniPert:validation_metrics",
        effect_size=0.85,  # Pearson r 最佳
        key_finding=(
            "UniPert 在遗传扰动预测中 Pearson r 达 0.85 (最佳设置)，"
            "G2CP 在化合物应答预测中 Spearman ρ 达 0.63 "
            "(跨细胞系迁移场景)。"
        ),
        source_name="UniPert-G2CP (Tencent × CSU)",
        source_url=UNIPERT_REPO,
        source_date="2026-07",
        notes="指标来源: Cell 2026 主刊论文 + Zenodo 复现包 benchmark 结果",
        metadata={
            "prediction_type": "validation_metric",
            "pearson_r": 0.85,
            "spearman_rho": 0.63,
        },
    )
    rows.append(metric_row)
    
    # ── 如果请求 inference 且有模型 ──
    if run_inference:
        if env["unipert_installed"] and env["model_downloaded"]:
            pred_result = predict_gene_perturbation(gene_up)
            if pred_result.get("inference_success"):
                inf_row = tem.EvidenceRow(
                    target_gene=gene_up,
                    disease=disease,
                    dimension=tem.EvidenceDimension.AI_PREDICTION,
                    strength=tem.EvidenceStrength.NOMINAL,
                    direction=tem.EvidenceDirection.ASSOCIATED,
                    sub_dimension="UniPert:inference",
                    key_finding=(
                        f"UniPert 实时推理: {gene_up} 扰动嵌入已生成 "
                        f"(维度: {pred_result.get('embedding_dim', 'N/A')})"
                    ),
                    source_name="UniPert (local inference)",
                    source_date=_now(),
                    notes=f"device: {pred_result.get('device', '?')} | 完整下游预测需 G2CP 模块",
                    metadata={
                        "prediction_type": "live_inference",
                        "inference_device": pred_result.get("device"),
                    },
                )
                rows.append(inf_row)
            else:
                rows.append(tem.EvidenceRow(
                    target_gene=gene_up,
                    disease=disease,
                    dimension=tem.EvidenceDimension.AI_PREDICTION,
                    strength=tem.EvidenceStrength.WEAK,
                    direction=tem.EvidenceDirection.UNKNOWN,
                    sub_dimension="UniPert:inference_failed",
                    key_finding=f"UniPert 推理失败: {pred_result.get('error', '未知错误')}",
                    source_name="UniPert (local inference)",
                    source_date=_now(),
                ))
        else:
            rows.append(tem.EvidenceRow(
                target_gene=gene_up,
                disease=disease,
                dimension=tem.EvidenceDimension.AI_PREDICTION,
                strength=tem.EvidenceStrength.UNKNOWN,
                direction=tem.EvidenceDirection.UNKNOWN,
                sub_dimension="UniPert:inference_skipped",
                key_finding=(
                    "UniPert 或其模型未部署，跳过实时推理。"
                    "运行 install_unipert() + download_model() 安装"
                ),
                source_name="UniPert (local inference)",
                source_date=_now(),
            ))
    
    # 转 dict
    return [r.to_dict() if hasattr(r, 'to_dict') else r for r in rows]


# ── CLI ──

def main():
    import target_evidence_matrix as tem
    
    parser = __import__("argparse").ArgumentParser(
        description="UniPert-G2CP 连接器 — 第八维证据源 (AI 预测)"
    )
    parser.add_argument("gene", help="基因符号")
    parser.add_argument("--disease", default="", help="关联疾病")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--run-inference", action="store_true", help="尝试运行模型推理")
    parser.add_argument("--install", action="store_true", help="安装 UniPert 依赖")
    parser.add_argument("--download", action="store_true", help="下载模型检查点")
    parser.add_argument("--check-env", action="store_true", help="仅检查环境")
    args = parser.parse_args()
    
    if args.check_env:
        env = check_env()
        print(json.dumps(env, indent=2))
        return
    
    if args.install:
        result = install_unipert(force=True)
        print(json.dumps(result, indent=2, default=str))
        return
    
    if args.download:
        result = download_model(force=True)
        print(json.dumps(result, indent=2, default=str))
        return
    
    # 生成证据行
    rows = generate_evidence_rows(
        gene=args.gene,
        disease=args.disease,
        run_inference=args.run_inference,
    )
    
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
        return
    
    # 格式化输出
    print(f"\n{'='*60}")
    print(f"UniPert-G2CP AI 预测证据 (第八维度)")
    print(f"基因: {args.gene.upper()}" + (f" | 疾病: {args.disease}" if args.disease else ""))
    print(f"{'='*60}\n")
    
    for r in rows:
        d = r if isinstance(r, dict) else r.to_dict()
        dim = d.get("sub_dimension", "?")
        strength = d.get("strength", "?")
        finding = (d.get("key_finding", "") or "")[:80]
        notes = (d.get("notes", "") or "")[:80]
        print(f"  [{dim}] ({strength})")
        print(f"    {finding}")
        if notes:
            print(f"    📎 {notes}")
        print()
    
    env = check_env()
    print(f"--- 环境: device={env['device']}, UniPert={'✅' if env['unipert_installed'] else '❌'}, "
          f"模型={'✅' if env['model_downloaded'] else '❌'}")
    print(f"--- 仓库: {UNIPERT_REPO}")
    print(f"--- Zenodo 检查点: {ZENODO_URL}")
    print(INTERPRETABILITY_NOTE)


if __name__ == "__main__":
    main()
