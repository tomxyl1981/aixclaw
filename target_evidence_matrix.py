"""
靶点证据矩阵 (Target Evidence Matrix)
==========================================

HMS Evidence Ledger 方法论的靶点发现适配版。

功能：
  - 定义靶点证据的六维结构化数据结构
  - 多源检索结果 → 结构化证据账本的转换器
  - 缺失检测 + 矛盾标记 + 因果推断骨架

设计原则：
  - 纯内存操作，不依赖任何后端基础设施
  - 输入是 agent-reach / scRNA-seq 等工具的输出
  - 输出是结构化的 JSON 账本，可喂给 LLM 或生成报告
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ── 数据驱动权重集成 (张红 2026-07-30) ──
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))
from row_weight import compute_data_weight
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════
# 枚举定义
# ═══════════════════════════════════════════════

class EvidenceStrength(str, Enum):
    """证据强度分级"""
    P_VALUE_LT_5E8 = "p<5e-8"        # 全基因组显著性
    P_VALUE_LT_1E5 = "p<1e-5"        # 暗示性关联
    P_VALUE_LT_0_01 = "p<0.01"       # 一般显著性
    AUC_GT_0_8 = "AUC>0.8"           # 预测模型高区分度
    AUC_GT_0_6 = "AUC>0.6"           # 中等区分度
    LOG2FC_GT_1 = "log2FC>1"         # 差异表达显著
    LOG2FC_GT_0_5 = "log2FC>0.5"     # 差异表达中等
    NOMINAL = "nominal"              # 名义显著
    WEAK = "weak"                    # 弱信号
    NOT_SIGNIFICANT = "not_significant"  # 不显著
    UNKNOWN = "unknown"              # 未知


class EvidenceDirection(str, Enum):
    """证据方向"""
    UPREGULATED = "upregulated"       # 上调/激活/促进
    DOWNREGULATED = "downregulated"   # 下调/抑制/保护
    GAIN_OF_FUNCTION = "gain_of_function"   # 功能获得
    LOSS_OF_FUNCTION = "loss_of_function"   # 功能缺失
    ASSOCIATED = "associated"         # 关联（方向不明）
    BIDIRECTIONAL = "bidirectional"   # 双向效应
    NOT_CHANGED = "not_changed"       # 无变化
    UNKNOWN = "unknown"


class EvidenceDimension(str, Enum):
    """证据维度（按数据类型分类）"""
    GWAS = "gwas"                     # 全基因组关联研究
    EQTL = "eqtl"                     # 表达数量性状位点
    PWAS = "pwas"                     # 蛋白质组关联
    SCRNA_SEQ = "scRNA_seq"           # 单细胞转录组
    BULK_RNA_SEQ = "bulk_RNA_seq"     # 批量化转录组
    PROTEOMICS = "proteomics"         # 蛋白质组学
    ANIMAL_MODEL = "animal_model"     # 动物模型（敲除/过表达）
    CLINICAL_SAMPLE = "clinical_sample"  # 临床样本（IHC/ELISA等）
    CAUSAL_EVIDENCE = "causal_evidence"  # 孟德尔随机化因果证据
    DRUGGABILITY = "druggability"     # 可药性评估
    EDITABLEITY = "editableity"    # CRISPR可编辑性（Phase 4）
    SAFETY = "safety"                 # 安全性（已知毒性）
    PATHWAY = "pathway"               # 通路富集
    LITERATURE = "literature"         # 文献证据（其他）
    AI_PREDICTION = "AI_prediction"   # AI 预测
    CLINICAL_GENETICS = "clinical_genetics"  # 临床遗传学（ClinVar 致病变异）
    ESSENTIALITY = "essentiality"    # 基因必需性（DepMap + MGI）
    # ── gnomAD 拆解 (原 POPULATION_TOLERANCE) ──
    POPULATION_TOLERANCE_PLI = "population_tolerance_pli"          # pLI 概率
    POPULATION_TOLERANCE_LOEUF = "population_tolerance_loeuf"      # LOEUF 上限
    POPULATION_TOLERANCE_MISSENSE_Z = "population_tolerance_mis_z" # 错义 Z 值
    POPULATION_TOLERANCE_SYNONYMOUS_Z = "population_tolerance_syn_z" # 同义 Z 值
    POPULATION_TOLERANCE_OE_LOF = "population_tolerance_oe_lof"    # O/E LOF 比值
    # ── STRING 拆解 (原 PPI_NETWORK) ──
    PPI_DEGREE = "ppi_degree"              # 互作中心度
    PPI_FDA_OVERLAP = "ppi_fda_overlap"    # FDA 靶点重叠
    PPI_DISEASE_MODULE = "ppi_disease_module"  # 疾病模块
    PPI_GO_ENRICHMENT = "ppi_go_enrichment"    # GO 富集
    # ── ClinVar 拆解 (原 CLINICAL_GENETICS) ──
    CLINICAL_GENETICS_PATHOGENIC = "clinical_genetics_pathogenic"  # P/LP 致病变异
    CLINICAL_GENETICS_VUS = "clinical_genetics_vus"                # VUS 意义不明
    CLINICAL_GENETICS_DOMAIN = "clinical_genetics_domain"          # 功能域富集
    # ── DepMap 拆解 (原 ESSENTIALITY) ──
    ESSENTIALITY_CHRONOS = "essentiality_chronos"      # Chronos 评分
    ESSENTIALITY_COESSENTIAL = "essentiality_coessential"  # 共必需性
    ESSENTIALITY_TISSUE = "essentiality_tissue"        # 组织特异性
    # ── GTEx 拆解 ──
    TISSUE_EXPRESSION = "tissue_expression"            # 组织表达水平
    EXPRESSION_SELECTIVITY = "expression_selectivity"  # 表达选择性指数
    GTEX_EQTL = "gtex_eqtl"                            # GTEx eQTL 组织特异性
    # ── Conservation 拆解 ──
    CONSERVATION_EXON = "conservation_exon"            # 外显子保守性
    CONSERVATION_INTRON = "conservation_intron"        # 内含子保守性
    CONSERVATION_REGULATORY = "conservation_regulatory" # 调控区保守性
    # ── Immune Microenv 拆解 ──
    IMMUNE_INFILTRATION = "immune_infiltration"        # 免疫细胞浸润
    IMMUNE_CHECKPOINT = "immune_checkpoint"            # 免疫检查点共表达
    IMMUNE_MODULATOR = "immune_modulator"              # 免疫调控信号
    # ── CellxGene 拆解 ──
    CELLXGENE_TISSUE = "cellxgene_tissue"              # 泛组织单细胞表达
    CELLXGENE_CELLTYPE = "cellxgene_celltype"          # 细胞类型特异性
    CELLXGENE_DEVELOPMENT = "cellxgene_development"
    # ── Phase II 表观遗传 (ENCODE) ──
    ENCODE_HISTONE = "encode_histone"
    ENCODE_TF_BINDING = "encode_tf_binding"
    ENCODE_CHROMATIN_ACCESS = "encode_chromatin_access"
    ENCODE_METHYLATION = "encode_methylation"
    # ── Phase II GTEx 全54组织 ──
    GTEX_TISSUE_SPECIFIC = "gtex_tissue_specific"
    GTEX_EQTL_CIS = "gtex_eqtl_cis"
    GTEX_SPLICING_QTL = "gtex_splicing_qtl"
    # ── Phase II CCLE 癌症细胞系 ──
    CCLE_DRUG_SENSITIVITY = "ccle_drug_sensitivity"
    CCLE_GENETIC_DEP = "ccle_genetic_dep"
    CCLE_EXPRESSION_PROFILE = "ccle_expression_profile"
    CCLE_MUTATION_SIGNATURE = "ccle_mutation_signature"
    # ── Phase III Batch 0: 交叉计算 ──
    CROSS_CELLTYPE_RELEVANCE = "cross_celltype_relevance"
    CROSS_IMMUNE_RISK = "cross_immune_risk"
    CROSS_NETWORK_DRUG = "cross_network_drug"
    CROSS_PATHOGENIC_PRIORITY = "cross_pathogenic_priority"
    # ── Phase III Batch 1: HPA 蛋白表达 ──
    HPA_TISSUE_PROTEIN = "hpa_tissue_protein"
    HPA_SUBCELLULAR = "hpa_subcellular"
    HPA_PATHOLOGY = "hpa_pathology"
    # ── Phase III Batch 2: DisGeNET ──
    DISGENET_GDA = "disgenet_gda"
    DISGENET_VARIANT = "disgenet_variant"
    DISGENET_LITERATURE = "disgenet_literature"
    # ── Phase III Batch 3: COSMIC ──
    COSMIC_CENSUS = "cosmic_census"
    COSMIC_MUTATION = "cosmic_mutation"
    COSMIC_DRUGGABLE = "cosmic_druggable"
    # ── Phase III Batch 3: DrugBank 通道 ──
    DRUGBANK_APPROVED = "drugbank_approved"
    DRUGBANK_ADMET = "drugbank_admet"
    # ── Phase III Batch 4: miRNA / 3D 基因组 ──
    MIRNA_TARGET = "mirna_target"
    MIRNA_DISEASE = "mirna_disease"
    GENOME3D_LOOP = "genome3d_loop"
    GENOME3D_COMPARTMENT = "genome3d_compartment"
    GENOME3D_PROM_ENH = "genome3d_prom_enh"
    # ── Phase III Batch 5: DGIdb ──
    DGIDB_INTERACTION = "dgidb_interaction"
    DGIDB_CATEGORY = "dgidb_category"
    DGIDB_EVIDENCE = "dgidb_evidence"
    DGIDB_FDA_APPROVED = "dgidb_fda_approved"
    # ── Phase III 续: UniProt 功能 ──
    UNIPROT_FUNCTION = "uniprot_function"
    UNIPROT_PROCESS = "uniprot_process"
    UNIPROT_COMPONENT = "uniprot_component"
    UNIPROT_DOMAIN = "uniprot_domain"
    UNIPROT_SUBCELL = "uniprot_subcell"
    UNIPROT_ISOFORM = "uniprot_isoform"
    # ── Phase III 续: Reactome 通路 ──
    REACTOME_PATHWAY = "reactome_pathway"
    REACTOME_HIERARCHY = "reactome_hierarchy"
    REACTOME_DISEASE = "reactome_disease"
    REACTOME_CONSERVATION = "reactome_conservation"
    # ── Phase III-C: OT 扩展 ──
    OT_TARGET_TIER = "ot_target_tier"
    OT_PHARMA_CLASS = "ot_pharma_class"
    OT_TISSUE_PROFILE = "ot_tissue_profile"
    OT_DISEASE_SPAN = "ot_disease_span"
    # ── Phase III-C: ClinVar/ClinGen ──
    CLINVAR_PATHOGENICITY = "clinvar_pathogenicity"
    CLINVAR_REVIEW = "clinvar_review"
    CLINGEN_HAPLO = "clingen_haplo"
    CLINGEN_TRIPLO = "clingen_triplo"
    CLINGEN_CLINEFF = "clingen_clineff"
    # ── Phase III-C: GTEx 扩展 ──
    GTEX_SEX_BIAS = "gtex_sex_bias"
    GTEX_AGE_CORR = "gtex_age_corr"
    GTEX_TISSUE_SPEC = "gtex_tissue_spec"
    # ── Phase III-C: STRING 扩展 ──
    STRING_COEXPR = "string_coexpr"
    STRING_COEVOLVE = "string_coevolve"
    STRING_TEXTMINING = "string_textmining"
    STRING_EXPERIMENT = "string_experiment"
    # ── Phase III-C: MGI ──
    MGI_LETHALITY = "mgi_lethality"
    MGI_PHENO_SIM = "mgi_pheno_sim"
    MGI_DEVELOPMENT = "mgi_development"
    MGI_REPRODUCTION = "mgi_reproduction"
    MGI_MP_TERM = "mgi_mp_term"
    # ── Phase III-C: SIDER ──
    SIDER_SIDE_EFFECT = "sider_side_effect"
    SIDER_ORGAN_SYSTEM = "sider_organ_system"
    SIDER_FREQUENCY = "sider_frequency"
    SIDER_SEVERITY = "sider_severity"
    # ── Phase III-C: HPO ──
    HPO_TERM_COUNT = "hpo_term_count"
    HPO_ONSET = "hpo_onset"
    HPO_INHERITANCE = "hpo_inheritance"
    # ── Phase III-C: PharmGKB ──
    PHARMGKB_ANNOT = "pharmgkb_annot"
    PHARMGKB_DOSING = "pharmgkb_dosing"
    # ── Phase III-C: JASPAR ──
    JASPAR_TF_COUNT = "jaspar_tf_count"
    JASPAR_TF_FAMILY = "jaspar_tf_family"
    JASPAR_TF_CONSV = "jaspar_tf_consv"
    # ── Phase III-C: GDSC ──
    GDSC_SENSITIVITY = "gdsc_sensitivity"
    GDSC_MUT_STATE = "gdsc_mut_state"
    GDSC_TISSUE_PROF = "gdsc_tissue_prof"
    # ── Phase III-C: GWAS 扩展 ──
    GWAS_SNP_DENSITY = "gwas_snp_density"
    GWAS_OR_SPECTRUM = "gwas_or_spectrum"
    GWAS_POP_COVER = "gwas_pop_cover"
    GWAS_EARLY_STUDY = "gwas_early_study"
    # ── Phase III-C: PDB ──
    PDB_STRUCT_CNT = "pdb_struct_cnt"
    PDB_RESOLUTION = "pdb_resolution"
    PDB_LIGAND_CNT = "pdb_ligand_cnt"
    # ── Phase III-C: HMDB ──
    HMDB_METAB_CNT = "hmdb_metab_cnt"
    HMDB_PATHWAY = "hmdb_pathway"
    HMDB_TISSUE_CONC = "hmdb_tissue_conc"
    # ── Phase III-C: DrugCentral ──
    DRUGCENTRAL_INTERACT = "drugcentral_interact"
    DRUGCENTRAL_FDA = "drugcentral_fda"
    DRUGCENTRAL_SIDE = "drugcentral_side"
    # ── Phase III-C: ClinicalTrials 扩展 ──
    CT_RECRUIT = "ct_recruit"
    CT_GEOGRAPHY = "ct_geography"
    CT_PHASE_DIST = "ct_phase_dist"
    CT_AGE_SPECTRUM = "ct_age_spectrum"
    # ── Phase III-C: ProteomicsDB ──
    PROTEOMICSDB_ABUND = "proteomicsdb_abund"
    PROTEOMICSDB_TISSUE = "proteomicsdb_tissue"
    # ── Phase III-C: NeXtProt ──
    NEXTPROT_EVIDENCE = "nextprot_evidence"
    NEXTPROT_CLASS = "nextprot_class"
    # ── Phase III-C: TISSUES ──
    TISSUES_EXPR_SPEC = "tissues_expr_spec"
    TISSUES_INTEGRATED = "tissues_integrated"
    # ── Phase III-C: 动物模型 ──
    ZFIN_PHENO = "zfin_pheno"
    ZFIN_DEVELOPMENT = "zfin_development"
    FLYBASE_LETHAL = "flybase_lethal"
    FLYBASE_REGULATORY = "flybase_regulatory"
    WORMBASE_RNAI = "wormbase_rnai"
    WORMBASE_NEIGHBOR = "wormbase_neighbor"
    RGD_DISEASE = "rgd_disease"
    RGD_QTL = "rgd_qtl"
    # ── Phase III-C: DepMap 扩展 ──
    DEPMAP_GENE_ESS = "depmap_gene_tag"
    DEPMAP_CODEP = "depmap_codep"
    DEPMAP_DRUG_ASSAY = "depmap_drug_assay"
    # ── Phase III-C: ENCODE 扩展 ──
    ENCODE_HISTONE_ALT = "encode_histone_alt"
    ENCODE_DNASE = "encode_dnase"
    ENCODE_ATAC = "encode_atac"
    ENCODE_CTCF = "encode_ctcf"
    ENCODE_RNA_BP = "encode_rna_bp"
    # ── Phase III-C: 交叉 Omics ──
    CROSS_TRANSCRIPT_PROT = "cross_transcript_prot"
    CROSS_METHYL_EXPR = "cross_methyl_expr"
    CROSS_CNV_EXPR = "cross_cnv_expr"
    # ── Phase III-C: Bgee ──
    BGEE_ANATOMY = "bgee_anatomy"
    BGEE_DEVO = "bgee_devo"
    # ── Phase III-C: PheWAS ──
    PHEWAS_CROSS_DISEASE = "phewas_cross_disease"
    PHEWAS_PHENO_SPECTRUM = "phewas_pheno_spectrum"
    # ── Phase III-D: 新增临床数据源 (2026-07-29) ──
    CHICTR_TRIAL = "chictr_trial"              # 中国临床试验注册中心
    CDE_APPROVAL = "cde_approval"              # NMPA/CDE 药品审批
    CKB_COHORT = "ckb_cohort"                  # 中国慢性病前瞻性研究
    BIOBANK_JAPAN = "biobank_japan"            # BioBank Japan 人群队列
    ORPHANET = "orphanet"                      # Orphanet 罕见病-基因关联
    # ── Phase III-C: SMPDB ──
    SMPDB_METAB_PATHWAY = "smpdb_metab_pathway"
    SMPDB_DISEASE_PW = "smpdb_disease_pw"
    # ── Phase III-C: EPD ──
    EPD_PROMOTER = "epd_promoter"
    EPD_TSS = "epd_tss"
    # ── Phase III-C: 细胞状态 ──
    CELL_ACTIVATION = "cell_activation"
    CELL_DIFFERENTIATION = "cell_differentiation"
    # ── Phase III-C: 时间拆分 ──
    TIME_CIRCADIAN = "time_circadian"
    TIME_DEVELOPMENTAL = "time_developmental"
    # ── Phase III-C: TOPMed ──
    TOPMED_POP_FREQ = "topmed_pop_freq"
    TOPMED_RARE_VAR = "topmed_rare_var"
    # ── Phase III-C: ArrayExpress ──
    ARRAYEXPRESS_DIFF = "arrayexpress_diff"
    ARRAYEXPRESS_BATCH = "arrayexpress_batch"
    # ── Phase III-C: HumanMine ──
    HUMANMINE_PROTEOMICS = "humanmine_proteomics"
    HUMANMINE_INTERACTOME = "humanmine_interactome"
    HUMANMINE_PHENO = "humanmine_pheno"
    # ── Phase III-C: CPDB ──
    CPDB_CONSENSUS = "cpdb_consensus"
    CPDB_NETWORK = "cpdb_network"
    # ── Phase III-C: GPS-Prot ──
    GPS_MEMBRANE = "gps_membrane"
    GPS_SECRETED = "gps_secreted"
    # ── Phase III-C: NURSA ──
    NURSA_NUCLEAR = "nursa_nuclear"
    NURSA_COREG = "nursa_coreg"
    # ── Phase III-C: CORUM ──
    CORUM_COMPLEX = "corum_complex"
    CORUM_FUNCTION = "corum_function"
    # ── Phase III-C: Gene2Function ──
    GENE2FUNC_GO = "gene2func_go"
    GENE2FUNC_OVERREP = "gene2func_overrep"
    # ── Phase III-C: 疾病本体 ──
    ONTOLOGY_MONDO = "ontology_mondo"
    ONTOLOGY_DOID = "ontology_doid"    # 发育表达谱
    # ── Pancancer 拆解 ──
    PANCANCER_MUTATION = "pancancer_mutation"  # 突变频率
    PANCANCER_CNA = "pancancer_cna"            # 拷贝数变异
    # 保留旧枚举兼容性（部分枚举已拆解到上层，仅保留全量引用）
    OTHER = "other"


class SafetySeverity(str, Enum):
    """安全事件严重程度 (Mei案例评估驱动)"""
    SEVERE_AE = "severe_ae"           # 严重不良事件 (SAE)，如 TMA/死亡
    MODERATE_AE = "moderate_ae"       # 中度不良事件，如肝损伤
    MILD_AE = "mild_ae"               # 轻度不良反应
    ANIMAL_SAE = "animal_sae"         # 动物模型严重毒性信号 (4/4 肝损伤级别)
    BIOMARKER_RISK = "biomarker_risk"  # 生物标志物提示风险
    NO_SIGNAL = "no_signal"           # 未检测到安全信号
    UNKNOWN = "unknown"               # 未知


class InterpretabilityLevel(str, Enum):
    """证据可解释性分级 (陶哲轩「天书证明」防御性设计)."""
    CAUSAL_CHAIN = "causal_chain"
    CLEAR_ASSOCIATION = "clear_association"
    FUZZY_ASSOCIATION = "fuzzy_association"
    MULTI_OMIC_FUSION = "multi_omic_fusion"
    DEEP_EMBEDDING = "deep_embedding"
    BLACKBOX = "blackbox"
    UNKNOWN = "unknown"

_DIM_EXPLAINABILITY: dict[str, InterpretabilityLevel] = {
    "animal_model": InterpretabilityLevel.CAUSAL_CHAIN,
    "eqtl": InterpretabilityLevel.CLEAR_ASSOCIATION,
    "pwas": InterpretabilityLevel.CLEAR_ASSOCIATION,
    "bulk_RNA_seq": InterpretabilityLevel.CLEAR_ASSOCIATION,
    "safety": InterpretabilityLevel.CAUSAL_CHAIN,
    "clinical_sample": InterpretabilityLevel.CLEAR_ASSOCIATION,
    "gwas": InterpretabilityLevel.FUZZY_ASSOCIATION,
    "scRNA_seq": InterpretabilityLevel.FUZZY_ASSOCIATION,
    "proteomics": InterpretabilityLevel.FUZZY_ASSOCIATION,
    "druggability": InterpretabilityLevel.MULTI_OMIC_FUSION,
    "pathway": InterpretabilityLevel.MULTI_OMIC_FUSION,
    "literature": InterpretabilityLevel.FUZZY_ASSOCIATION,
    "AI_prediction": InterpretabilityLevel.DEEP_EMBEDDING,
    "other": InterpretabilityLevel.FUZZY_ASSOCIATION,
}

def interpretability_for_dim(dim_value: str) -> InterpretabilityLevel:
    return _DIM_EXPLAINABILITY.get(dim_value, InterpretabilityLevel.FUZZY_ASSOCIATION)



class ConsistencyStatus(str, Enum):
    """跨证据一致性"""
    HIGH = "high"                     # 高度一致
    MODERATE = "moderate"             # 中等一致
    LOW = "low"                       # 低一致性
    CONTRADICTORY = "contradictory"   # 矛盾
    UNKNOWN = "unknown"               # 未知（仅单来源）


# ═══════════════════════════════════════════════
# 核心数据结构
# ═══════════════════════════════════════════════

@dataclass
class EvidenceRow:
    """
    证据账本中的单行记录。
    
    对标 HMS 的 evidence_ledger_row，扩展为 6 维靶点标注。
    """
    
    # 基本信息
    target_gene: str                  # 靶点基因名（如 ACVR2A）
    disease: str                      # 关联疾病
    
    # ── 维1：证据类型 ──
    dimension: EvidenceDimension      # 数据类型
    
    # ── 维2：强度 ──
    strength: EvidenceStrength        # 统计强度
    direction: EvidenceDirection      # 表达/功能方向
    sub_dimension: str = ""           # 子类型（如 "GWAS Catalog", "FinnGen"）
    raw_stat: str = ""                # 原始统计值（如 "p=2.3e-8", "AUC=0.89"）
    sample_size: int | None = None    # 样本量
    effect_size: float | None = None  # 效应量
    confidence_interval: str = ""     # 置信区间
    
    # ── 维4：来源 ──
    source_id: str = ""               # PMID / 数据库 ID
    source_url: str = ""              # 可追溯链接
    source_date: str = ""             # 发表/更新日期
    source_name: str = ""             # 数据库/期刊名称

    # ── 可解释性（陶哲轩防御）──
    explainability: InterpretabilityLevel | None = None
    consistency: ConsistencyStatus = ConsistencyStatus.UNKNOWN
    
    # ── 维7：安全反指征 ──
    safety_severity: SafetySeverity | None = None  # 安全事件严重程度
    safety_signal: str = ""             # 具体安全信号描述（如 "4/4 肝损伤", "TMA")
    safety_population: str = ""         # 受影响人群（如 "儿童", "成人"）

    # ── 维8：定性 ──
    raw_snippet: str = ""             # 原始引用片段
    key_finding: str = ""             # 一句话核心结论
    notes: str = ""                   # 备注/特殊说明
    
    # ── 熵态分析（邓煜t=0独立→熵增框架）──
    natural_confidence: float = 0.5   # 维度独立计算的原始置信度
    pressure_path: str = "natural"    # natural|mom|human|mixed
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """序列化"""
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class CausalEdge:
    """
    因果边：基因→通路→表型 因果链中的一段。
    """
    source: str                       # 起点（如 "ACVR2A"）
    target: str                       # 终点（如 "SMAD2"）
    relation: str                     # 关系类型（如 "activates", "inhibits"）
    evidence_level: float             # 证据等级 0-1
    source_id: str = ""               # 证据PMID
    confidence: float = 0.5           # 正确率置信度


@dataclass
class MissingEvidence:
    """
    缺失证据标记。
    """
    dimension: EvidenceDimension      # 缺失哪类证据
    reason: str                       # 为什么需要
    priority: str = "medium"          # high/medium/low


@dataclass
class TargetContradiction:
    """
    矛盾标记。
    """
    dimension_a: EvidenceDimension
    dimension_b: EvidenceDimension
    description: str                  # 矛盾描述
    resolution: str = ""              # 可能的解释（如组织特异性/splicing变异）


@dataclass
class ReasoningStep:
    """
    推理链中的单步记录。

    构建靶点证据评估的可追溯推理过程。
    对标 HMS 的 reasoning_step，匹配 EnhancedTargetEngine._compute_bayesian_confidence() 的输出。
    """
    def __init__(
        self,
        step_id: int,
        step_type: str,
        input_data: str = "",
        reasoning: str = "",
        output: str = "",
        confidence: float = 0.5,
        alternatives_considered: str = "",
        resolution_reason: str = "",
        source_references: list[str] | None = None,
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.input_data = input_data
        self.reasoning = reasoning
        self.output = output
        self.confidence = confidence
        self.alternatives_considered = alternatives_considered
        self.resolution_reason = resolution_reason
        self.source_references = source_references or []

    def to_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "input_data": self.input_data,
            "reasoning": self.reasoning,
            "output": self.output,
            "confidence": self.confidence,
            "alternatives_considered": self.alternatives_considered,
            "resolution_reason": self.resolution_reason,
            "source_references": self.source_references,
        }

    def __repr__(self):
        return f"<ReasoningStep #{self.step_id} [{self.step_type}] conf={self.confidence:.3f}>"


class SafetyContraindication:
    """
    安全反指征标记 (第七维)。

    Mei 案例启示: 动物模型的 SAE 信号必须在方案设计阶段就被标记和量化。
    安全反指征不降低
    
    这是实现"决策过程可追溯"的关键数据结构——不是记录"结果是什么"，
    而是记录"为什么得出这个结果"。
    """
    step_id: int                                          # 步进序号
    step_type: str                                        # extract/classify/validate/score/debate
    input_data: str                                       # 输入：原始数据摘要
    reasoning: str                                        # LLM 判断逻辑
    output: str                                           # 输出结论
    confidence: float                                     # 本步置信度 0-1
    alternatives_considered: str = ""                     # 考虑了哪些替代方案
    resolution_reason: str = ""                          # 为什么选了这条路
    source_references: list[str] = field(default_factory=list)  # 引用来源
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class TargetEvidenceMatrix:
    """
    一个靶点的完整证据矩阵。
    
    等同于 HMS 的 evidence_ledger，但结构化为靶点发现专用。
    """
    
    # 靶点标识
    target_gene: str                  # 基因名
    disease: str = ""                 # 关联疾病
    
    # 六维证据行
    rows: list[EvidenceRow] = field(default_factory=list)
    
    # 因果路径
    causal_paths: list[list[CausalEdge]] = field(default_factory=list)
    
    # 诊断信息
    missing_evidence: list[MissingEvidence] = field(default_factory=list)
    contradictions: list[TargetContradiction] = field(default_factory=list)
    
    # 推理链：记录每一步决策的"为什么"
    reasoning_chain: list[ReasoningStep] = field(default_factory=list)
    
    # 安全约束
    safety_ceiling: float | None = None  # 安全因素导致的置信度上限 (如 0.20)
    safety_contraindications: list[SafetyContraindication] = field(default_factory=list)

    # 综合评价（账本构建后由 LLM 或规则填充）
    overall_confidence: float = 0.0   # 0-1
    overall_explainability: float = 0.0  # 整体可解释性 0-1 (陶哲轩防御)
    recommendation: str = ""          # 推荐/不推荐/需要更多证据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    _audit_hook = None  # optional audit callback

    # ═══════════════════════════════════════════════
    # 数据驱动权重集成 (张红 2026-07-30 授权)
    # ═══════════════════════════════════════════════
    _EXPECTED_DIMENSIONS = {
        EvidenceDimension.GWAS,
        EvidenceDimension.SCRNA_SEQ,
        EvidenceDimension.ANIMAL_MODEL,
        EvidenceDimension.SAFETY,
        EvidenceDimension.DRUGGABILITY,
        EvidenceDimension.PATHWAY,
    }

    def compute_weighted_confidence(self) -> dict:
        """
        基于数据驱动权重的综合置信度评分。

        替代原有的 flat scoring。

        在调用前，确认每条 EvidenceRow 有 data_weight 字段；
        如没有则自动从 row_weight.compute_data_weight 获取。

        权重逻辑 (张红 2026-07-30 批准):
          1. 每条证据行权重 = row_weight.compute_data_weight(row)
          2. overall = sum(w * row.weight) / sum(w)
          3. 横向一致性：同维度同方向多条 +0.15 boost
          4. 矛盾扣分：同维度不同方向 -0.3 * min_weight_ratio
          5. 缺失扣分：预计应有维度缺失，-0.1 每个

        Returns:
            dict with keys: weighted_score, weights_raw, weights_normalized,
                            num_rows, dimension_coverage, contradictions
        """
        from collections import Counter, defaultdict

        if not self.rows:
            return {
                "weighted_score": 0.0,
                "weights_raw": [],
                "weights_normalized": [],
                "num_rows": 0,
                "dimension_coverage": {},
                "contradictions": [],
            }

        # ── Step 1: 确保每条行有 data_weight ──
        raw_weights = []
        for r in self.rows:
            w = compute_data_weight(r)
            r.data_weight = w  # 动态设置，dataclass 允许
            raw_weights.append(w)

        # ── Step 2: 综合置信度 = 加权平均 ──
        # w = data_weight（质量权重），同时也作为信号值
        # overall = sum(w^2) / sum(w)
        total_weight = sum(raw_weights)
        weighted_sum = sum(w * w for w in raw_weights)
        weighted_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        # ── Step 3: 归一化权重 ──
        max_w = max(raw_weights) if raw_weights else 1.0
        normalized = [w / max_w for w in raw_weights] if max_w > 0 else []

        # ── Step 4: 维度覆盖率 ──
        present_dims = {r.dimension for r in self.rows}
        dim_coverage = {}
        for dim in sorted(self._EXPECTED_DIMENSIONS, key=lambda d: d.value):
            dim_coverage[dim.value] = dim in present_dims
        coverage_pct = sum(1 for v in dim_coverage.values() if v) / len(dim_coverage) if dim_coverage else 0.0

        # ── Step 5: 横向一致性 boost ──
        # 同维度同方向多条证据 → +0.15
        dim_dir_counts = defaultdict(int)
        for r in self.rows:
            dim_dir_counts[(r.dimension, r.direction)] += 1

        consistency_boost = 0.0
        dim_dir_detail = {}
        for (dim, dirc), cnt in dim_dir_counts.items():
            if cnt >= 2:
                consistency_boost += 0.05  # 2026-07-30: 收窄系数 (原0.15→0.05)
                dim_dir_detail[f"{dim.value}/{dirc.value}"] = cnt

        # ── Step 6: 矛盾扣分 ──
        # 同维度不同方向 → -0.3 * min_weight_ratio
        contradiction_penalty = 0.0
        contradiction_details = []
        for c in self.contradictions:
            # 计算该维度内最小/最大权重比
            dim_rows = [
                r for r in self.rows
                if r.dimension == c.dimension_a
            ]
            if dim_rows:
                dim_weights = [getattr(r, "data_weight", compute_data_weight(r)) for r in dim_rows]
                min_w = min(dim_weights)
                max_w = max(dim_weights)
                ratio = min_w / max_w if max_w > 0 else 0.0
                penalty = 0.3 * ratio
                contradiction_penalty += penalty
                contradiction_details.append({
                    "dimension_a": c.dimension_a.value,
                    "dimension_b": c.dimension_b.value,
                    "description": c.description,
                    "min_weight_ratio": round(ratio, 4),
                    "penalty": round(penalty, 4),
                })

        # ── Step 7: 缺失扣分 ──
        # 已有 detect_missing() 填充 self.missing_evidence
        # 对预计应有的维度缺失扣分
        missing_penalty = 0.0
        missing_details = []
        for me in self.missing_evidence:
            if me.priority == "high":
                missing_penalty += 0.1
                missing_details.append({
                    "dimension": me.dimension.value,
                    "reason": me.reason,
                    "priority": me.priority,
                    "penalty": 0.1,
                })

        # ── Step 8: 综合得分（含调整） ──
        final_score = weighted_score + consistency_boost - contradiction_penalty - missing_penalty
        final_score = max(0.0, min(final_score, 1.0))  # 钳制到 [0, 1]

        return {
            "weighted_score": round(final_score, 4),
            "weighted_score_raw": round(weighted_score, 4),
            "weights_raw": [round(w, 4) for w in raw_weights],
            "weights_normalized": [round(n, 4) for n in normalized],
            "num_rows": len(self.rows),
            "dimension_coverage": {
                "dimensions": dim_coverage,
                "coverage_pct": round(coverage_pct, 4),
                "present": sorted(d.value for d in present_dims),
            },
            "adjustments": {
                "consistency_boost": round(consistency_boost, 4),
                "contradiction_penalty": round(contradiction_penalty, 4),
                "missing_penalty": round(missing_penalty, 4),
            },
            "contradictions": contradiction_details,
            "missing": missing_details,
        }

    def compute_interpretability(self) -> float:
        """计算整体可解释性评分。"""
        if not self.rows:
            return 0.0
        scores = [(r.explainability.to_score() if r.explainability else 0.5) for r in self.rows]
        return sum(scores) / len(scores)

    def compute_interpretability(self) -> float:
        """计算整体可解释性评分。"""
        if not self.rows:
            return 0.0
        scores = [(r.explainability.to_score() if r.explainability else 0.5) for r in self.rows]
        return sum(scores) / len(scores)

    def compute_interpretability(self) -> float:
        """计算整体可解释性评分。"""
        if not self.rows:
            return 0.0
        scores = [(r.explainability.to_score() if r.explainability else 0.5) for r in self.rows]
        return sum(scores) / len(scores)

    def set_audit_hook(self, hook):
        self._audit_hook = hook

    def add_row(self, row: EvidenceRow):
        """添加一行证据"""
        self.rows.append(row)
        # 自动更新一致性状态
        self._update_consistency(row)
        if self._audit_hook:
            self._audit_hook(row, self.target_gene)
    
    def add_reasoning_step(self, step: ReasoningStep):
        """添加一步推理过程"""
        self.reasoning_chain.append(step)
    
    def _update_consistency(self, new_row: EvidenceRow):
        """添加新行时自动检测一致性"""
        if len(self.rows) < 2:
            return
        # 检查是否有同维度的矛盾行
        for existing in self.rows:
            if existing is new_row:
                continue
            same_dim = existing.dimension == new_row.dimension
            same_target = existing.target_gene == new_row.target_gene
            if same_dim and same_target:
                if existing.direction != new_row.direction and \
                   existing.direction != EvidenceDirection.UNKNOWN and \
                   new_row.direction != EvidenceDirection.UNKNOWN:
                    self.contradictions.append(TargetContradiction(
                        dimension_a=existing.dimension,
                        dimension_b=new_row.dimension,
                        description=(
                            f"{existing.target_gene}: {existing.dimension.value} "
                            f"{existing.direction.value} vs {new_row.direction.value}"
                        )
                    ))
    
    def detect_missing(self):
        """
        检测缺失证据维度。
        根据疾病类型和已有证据，智能判断还需要什么。
        """
        present_dims = {r.dimension for r in self.rows}
        
        # 基础必检维度
        required = [
            (EvidenceDimension.GWAS, "遗传关联是靶点发现的基本证据", "high"),
            (EvidenceDimension.SCRNA_SEQ, "单细胞表达提供细胞类型分辨率", "high"),
            (EvidenceDimension.ANIMAL_MODEL, "功能验证的体内证据", "medium"),
        ]
        
        for dim, reason, priority in required:
            if dim not in present_dims:
                self.missing_evidence.append(MissingEvidence(
                    dimension=dim, reason=reason, priority=priority
            ))

        # 安全证据缺失检测: 有动物模型但没有安全维度 → 预警
        has_animal = EvidenceDimension.ANIMAL_MODEL in present_dims
        has_safety = EvidenceDimension.SAFETY in present_dims
        if has_animal and not has_safety:
            self.missing_evidence.append(MissingEvidence(
                dimension=EvidenceDimension.SAFETY,
                reason="动物模型存在毒性信号但未做系统安全评估",
                priority="high"
            ))
    
    def to_chain_snapshot(self) -> dict[str, Any]:
        """
        生成 L4 链上存证快照（Nostr kind:30004 事件 JSON 基础）。
        
        该快照可广播到 AIXWire Nostr relay，实现不可篡改的靶点评估存证。
        """
        return {
            "type": "target_evidence_snapshot",
            "target_gene": self.target_gene,
            "disease": self.disease,
            "timestamp": datetime.now().isoformat(),
            "overall_confidence": self.overall_confidence,
            "recommendation": self.recommendation,
            # 证据摘要（不存全文，避免链上拥堵）
            "evidence_count": len(self.rows),
            "dimensions_present": list({r.dimension.value for r in self.rows}),
            "contradiction_count": len(self.contradictions),
            "missing_count": len(self.missing_evidence),
            "reasoning_chain_hash": self._hash_chain(),
            # 证据统计
            "by_dimension": self._count_by_dimension(),
            "by_direction": self._count_by_direction(),
        }
    
    def _hash_chain(self) -> str:
        """推理链 SHA256 摘要，验证完整性"""
        import hashlib
        chain_str = json.dumps([r.to_dict() for r in self.reasoning_chain], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(chain_str.encode()).hexdigest()
    
    def _count_by_dimension(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.rows:
            key = r.dimension.value
            counts[key] = counts.get(key, 0) + 1
        return counts
    
    def _count_by_direction(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.rows:
            key = r.direction.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_llm_context(self) -> str:
        """
        将证据矩阵格式化为 LLM 可读的结构化上下文。
        
        这是核心方法——LLM 看到的是结构化账本而不是原始文本。
        """
        parts = [f"# 靶点证据矩阵: {self.target_gene} ({self.disease})"]
        parts.append(f"综合置信度: {self.overall_confidence:.2f}")
        parts.append(f"推荐: {self.recommendation}\n")
        
        # 证据表格
        parts.append("## 证据明细")
        parts.append(f"{'维度':<18} {'强度':<18} {'方向':<18} {'来源':<20} {'可解释性':<10} {'一致性':<12} {'核心结论'}")
        parts.append("-" * 140)
        for r in self.rows:
            parts.append(
                f"{r.dimension.value:<18} "
                f"{r.strength.value:<18} "
                f"{r.direction.value:<18} "
                f"{r.source_id[:18]:<20} "
                f"{r.explainability.to_score() if r.explainability else 0.5:<10.2f} "
                f"{r.consistency.value:<12} "
                f"{r.key_finding[:30]}"
            )
        
        # 推理链
        if self.reasoning_chain:
            parts.append("\n## 推理链")
            for r in self.reasoning_chain:
                parts.append(
                    f"#{r.step_id} [{r.step_type}] "
                    f"输入: {r.input_data[:40]}... "
                    f"→ 输出: {r.output[:40]}... "
                    f"(置信度: {r.confidence:.2f})"
                )
                if r.alternatives_considered:
                    parts.append(f"   替代方案: {r.alternatives_considered[:60]}...")
                if r.resolution_reason:
                    parts.append(f"   决策理由: {r.resolution_reason[:60]}...")
        
        # 缺失检测
        if self.missing_evidence:
            parts.append("\n## 缺失证据")
            for m in self.missing_evidence:
                parts.append(f"- {m.dimension.value} [{m.priority}]: {m.reason}")
        
        # 矛盾
        if self.contradictions:
            parts.append("\n## 检测到的矛盾")
            for c in self.contradictions:
                parts.append(f"- {c.dimension_a.value} vs {c.dimension_b.value}: {c.description}")
        
        # 因果路径
        if self.causal_paths:
            parts.append("\n## 因果路径")
            for i, path in enumerate(self.causal_paths):
                steps = " → ".join(e.relation for e in path)
                nodes = " → ".join(f"{e.source}→{e.target}" for e in path)
                parts.append(f"路径{i+1}: {nodes} ({steps})")
        
        return "\n".join(parts)
    
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ═══════════════════════════════════════════════
# 证据矩阵构建器
# ═══════════════════════════════════════════════

class EvidenceMatrixBuilder:
    """
    多源检索结果 → 靶点证据矩阵 的转换器。
    
    输入: 来自 agent-reach / scRNA-seq / PubChem 等工具的结构化输出
    输出: TargetEvidenceMatrix
    """
    
    def __init__(self, target_gene: str, disease: str = ""):
        self.matrix = TargetEvidenceMatrix(
            target_gene=target_gene,
            disease=disease
        )
    
    # ── 适配器：不同类型数据源的 row 转换 ──
    
    def from_gwas(
        self,
        p_value: str,
        direction: str,
        source_id: str,
        sample_size: int | None = None,
        effect_size: float | None = None,
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从 GWAS 结果构建证据行"""
        # 自动强度分级
        if "e-" in p_value.lower():
            try:
                p = float(p_value.lower().replace("e", "e"))
                if p < 5e-8:
                    strength = EvidenceStrength.P_VALUE_LT_5E8
                elif p < 1e-5:
                    strength = EvidenceStrength.P_VALUE_LT_1E5
                elif p < 0.01:
                    strength = EvidenceStrength.P_VALUE_LT_0_01
                else:
                    strength = EvidenceStrength.NOMINAL
            except ValueError:
                strength = EvidenceStrength.UNKNOWN
        else:
            strength = EvidenceStrength.UNKNOWN
        
        dir_map = {
            "up": EvidenceDirection.UPREGULATED,
            "down": EvidenceDirection.DOWNREGULATED,
            "gain": EvidenceDirection.GAIN_OF_FUNCTION,
            "loss": EvidenceDirection.LOSS_OF_FUNCTION,
            "associated": EvidenceDirection.ASSOCIATED,
        }
        direction_enum = dir_map.get(direction.lower(), EvidenceDirection.ASSOCIATED)
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.GWAS,
            strength=strength,
            raw_stat=f"p={p_value}",
            direction=direction_enum,
            source_id=source_id,
            sample_size=sample_size,
            effect_size=effect_size,
            key_finding=raw_finding or f"GWAS 关联 {self.matrix.target_gene}-{self.matrix.disease}",
        )
    
    def from_scRNA_seq(
        self,
        log2fc: str,
        p_value: str,
        cell_type: str,
        direction: str,
        source_id: str,
        auc: float | None = None,
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从 scRNA-seq 差异表达结果构建证据行"""
        try:
            fc = float(log2fc)
            if abs(fc) > 1:
                strength = EvidenceStrength.LOG2FC_GT_1
            elif abs(fc) > 0.5:
                strength = EvidenceStrength.LOG2FC_GT_0_5
            else:
                strength = EvidenceStrength.NOMINAL
        except ValueError:
            strength = EvidenceStrength.UNKNOWN
        
        if auc is not None and auc > 0:
            strength = EvidenceStrength.AUC_GT_0_8 if auc > 0.8 else EvidenceStrength.AUC_GT_0_6
        
        dir_map = {
            "up": EvidenceDirection.UPREGULATED,
            "down": EvidenceDirection.DOWNREGULATED,
        }
        direction_enum = dir_map.get(direction.lower(), EvidenceDirection.UNKNOWN)
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.SCRNA_SEQ,
            sub_dimension=cell_type,
            strength=strength,
            raw_stat=f"log2FC={log2fc}, p={p_value}",
            direction=direction_enum,
            source_id=source_id,
            key_finding=raw_finding or f"在 {cell_type} 中差异表达",
        )
    
    def from_animal_model(
        self,
        model_type: str,              # "knockout", "overexpression", "CRISPR"
        phenotype: str,               # 表型
        effect_direction: str,        # "protective", "harmful", "no_effect"
        source_id: str,
        species: str = "mouse",
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从动物模型结果构建证据行"""
        dir_map = {
            "protective": EvidenceDirection.DOWNREGULATED,
            "harmful": EvidenceDirection.UPREGULATED,
            "gain": EvidenceDirection.GAIN_OF_FUNCTION,
            "loss": EvidenceDirection.LOSS_OF_FUNCTION,
            "no_effect": EvidenceDirection.NOT_CHANGED,
        }
        direction_enum = dir_map.get(effect_direction.lower(), EvidenceDirection.UNKNOWN)
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.ANIMAL_MODEL,
            sub_dimension=f"{species} {model_type}",
            strength=EvidenceStrength.NOMINAL,
            raw_stat=f"模型: {species} {model_type}, 表型: {phenotype}",
            direction=direction_enum,
            source_id=source_id,
            key_finding=raw_finding or f"{model_type} 导致 {phenotype}",
        )
    
    def from_druggability(
        self,
        chembl_target_class: str,
        has_small_molecule: bool,
        has_antibody: bool,
        tractability_score: float,     # 0-1
        source_id: str = "",
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从可药性评估构建证据行"""
        tractability_map = {
            t: EvidenceStrength.P_VALUE_LT_5E8
            for t in ["high", "1.0", "0.9", "0.8"]
        }
        strength = EvidenceStrength.UNKNOWN
        if str(tractability_score) in tractability_map:
            strength = tractability_map[str(tractability_score)]
        elif tractability_score > 0.6:
            strength = EvidenceStrength.P_VALUE_LT_1E5
        elif tractability_score > 0.3:
            strength = EvidenceStrength.NOMINAL
        else:
            strength = EvidenceStrength.WEAK
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.DRUGGABILITY,
            sub_dimension=chembl_target_class,
            strength=strength,
            raw_stat=f"tractability={tractability_score:.2f}",
            direction=EvidenceDirection.UNKNOWN,
            source_id=source_id,
            key_finding=raw_finding or f"可药性评分 {tractability_score:.2f}" + 
                (" (有机会)" if tractability_score > 0.5 else " (挑战大)"),
        )
    
    def from_safety(
        self,
        severity: str,                # "severe_ae", "animal_sae", "moderate_ae", "mild_ae", "no_signal"
        signal_description: str,      # 安全信号描述（如 "4/4 肝损伤", "TMA")
        affected_population: str,     # 受影响人群
        source_id: str,
        animal_model: bool = False,   # 是否来自动物模型
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从安全评估数据构建证据行"""
        sev_map = {
            "severe_ae": SafetySeverity.SEVERE_AE,
            "moderate_ae": SafetySeverity.MODERATE_AE,
            "mild_ae": SafetySeverity.MILD_AE,
            "animal_sae": SafetySeverity.ANIMAL_SAE,
            "biomarker_risk": SafetySeverity.BIOMARKER_RISK,
            "no_signal": SafetySeverity.NO_SIGNAL,
        }
        severity_enum = sev_map.get(severity.lower(), SafetySeverity.UNKNOWN)

        # 从严重程度推断证据强度
        st_map = {
            SafetySeverity.SEVERE_AE: EvidenceStrength.P_VALUE_LT_5E8,
            SafetySeverity.ANIMAL_SAE: EvidenceStrength.P_VALUE_LT_5E8,
            SafetySeverity.MODERATE_AE: EvidenceStrength.P_VALUE_LT_1E5,
            SafetySeverity.MILD_AE: EvidenceStrength.NOMINAL,
            SafetySeverity.BIOMARKER_RISK: EvidenceStrength.NOMINAL,
            SafetySeverity.NO_SIGNAL: EvidenceStrength.NOT_SIGNIFICANT,
        }
        strength = st_map.get(severity_enum, EvidenceStrength.UNKNOWN)

        # 安全维度始终是 DOWNREGULATED（负向/有害方向）
        direction = EvidenceDirection.DOWNREGULATED if severity_enum not in (
            SafetySeverity.NO_SIGNAL, SafetySeverity.UNKNOWN
        ) else EvidenceDirection.NOT_CHANGED

        dim = EvidenceDimension.ANIMAL_MODEL if animal_model else EvidenceDimension.SAFETY

        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=dim,
            sub_dimension=f"safety:{severity}",
            strength=strength,
            direction=direction,
            source_id=source_id,
            key_finding=raw_finding or f"安全信号: {signal_description} ({affected_population})",
            safety_severity=severity_enum,
            safety_signal=signal_description,
            safety_population=affected_population,
        )

    def from_pathway(
        self,
        pathway_name: str,
        pathway_role: str,            # "activator", "inhibitor", "member"
        enrichment_p: str,
        source_id: str,
        raw_finding: str = "",
    ) -> EvidenceRow:
        """从通路富集结果构建证据行"""
        dir_map = {
            "activator": EvidenceDirection.UPREGULATED,
            "inhibitor": EvidenceDirection.DOWNREGULATED,
            "member": EvidenceDirection.ASSOCIATED,
        }
        direction_enum = dir_map.get(pathway_role.lower(), EvidenceDirection.ASSOCIATED)
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.PATHWAY,
            sub_dimension=pathway_name,
            strength=EvidenceStrength.NOMINAL,
            raw_stat=f"富集 p={enrichment_p}",
            direction=direction_enum,
            source_id=source_id,
            key_finding=raw_finding or f"{self.matrix.target_gene} 是 {pathway_name} 的 {pathway_role}",
        )
    
    def from_literature_abstract(
        self,
        pmid: str,
        key_finding: str,
        strength: str = "nominal",
    ) -> EvidenceRow:
        """从文献摘要构建证据行"""
        st_map = {
            "strong": EvidenceStrength.P_VALUE_LT_5E8,
            "moderate": EvidenceStrength.P_VALUE_LT_1E5,
            "nominal": EvidenceStrength.NOMINAL,
        }
        
        return EvidenceRow(
            target_gene=self.matrix.target_gene,
            disease=self.matrix.disease,
            dimension=EvidenceDimension.LITERATURE,
            strength=st_map.get(strength, EvidenceStrength.NOMINAL),
            direction=EvidenceDirection.ASSOCIATED,
            source_id=pmid,
            key_finding=key_finding,
        )
    
    # ── 构建方法 ──
    
    def add(self, row: EvidenceRow) -> "EvidenceMatrixBuilder":
        """添加一行证据（支持链式调用）"""
        self.matrix.add_row(row)
        return self
    
    def add_causal_path(self, path: list[CausalEdge]):
        """添加一条因果路径"""
        self.matrix.causal_paths.append(path)
        return self
    
    def build(self) -> TargetEvidenceMatrix:
        """
        完成矩阵构建，自动运行缺失检测和综合评价。
        """
        m = self.matrix
        m.detect_missing()
        
        # 简单分数计算
        if m.rows:
            # 统计各维度的覆盖度
            dimensions_present = len({r.dimension for r in m.rows})
            total_dimensions = len(EvidenceDimension)
            coverage = dimensions_present / min(total_dimensions, 8)  # 取8个主要维度
            
            # 统计强度
            strong_rows = sum(1 for r in m.rows if r.strength in [
                EvidenceStrength.P_VALUE_LT_5E8,
                EvidenceStrength.AUC_GT_0_8,
                EvidenceStrength.LOG2FC_GT_1,
            ])
            strength_ratio = strong_rows / max(len(m.rows), 1)
            
            # ── 安全约束 (Mei案例驱动) ──
            animal_sae = any(
                r.dimension == EvidenceDimension.ANIMAL_MODEL
                and r.safety_severity in (SafetySeverity.ANIMAL_SAE, SafetySeverity.SEVERE_AE)
                for r in m.rows
            )
            safety_sae = any(
                r.dimension == EvidenceDimension.SAFETY
                and r.safety_severity in (SafetySeverity.SEVERE_AE, SafetySeverity.ANIMAL_SAE)
                for r in m.rows
            )

            if animal_sae or safety_sae:
                # 动物模型全部SAE或已知严重AE → 置信度强制上限 0.20
                m.safety_ceiling = 0.20
            elif any(r.safety_severity == SafetySeverity.MODERATE_AE for r in m.rows):
                m.safety_ceiling = 0.50
            has_safety_dim = any(r.dimension == EvidenceDimension.SAFETY for r in m.rows)
            if has_safety_dim:
                m.safety_ceiling = 0.80

            # 一致性惩罚
            contradiction_penalty = len(m.contradictions) * 0.1
            
            # 缺失惩罚
            missing_penalty = len(m.missing_evidence) * 0.05

            # 安全上限惩罚
            safety_penalty = 0.0
            if m.safety_ceiling is not None:
                safety_penalty = max(0.0, score - m.safety_ceiling)
            
            score = (coverage * 0.3 + strength_ratio * 0.4) - contradiction_penalty - missing_penalty - safety_penalty
            m.overall_confidence = max(0.0, min(1.0, round(score, 2)))
            
            if m.overall_confidence >= 0.7:
                m.recommendation = "推荐优先验证"
            elif m.overall_confidence >= 0.4:
                m.recommendation = "需要更多证据"
            else:
                m.recommendation = "证据不足，需补充实验"
        
        return m
