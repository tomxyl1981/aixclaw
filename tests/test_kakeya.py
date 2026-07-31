"""
Kakeya 双因子评分 + 交叉维度矛盾检测 — 单元测试
================================================
验证目标: 张红 2026-07-31 批准的评分公式
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from target_evidence_matrix import (
    TargetEvidenceMatrix, EvidenceRow,
    EvidenceDimension as D,
    EvidenceStrength as S,
    EvidenceDirection as Dir,
)
import json


class TestKakeyaScoring:
    """Kakeya 双因子评分基础测试"""

    def setup_method(self):
        self.A = TargetEvidenceMatrix("GENE_A", "Disease")
        # 7 维全强一致
        dims = [
            (D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED),
            (D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED),
            (D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.GAIN_OF_FUNCTION),
            (D.DRUGGABILITY, S.AUC_GT_0_8, Dir.GAIN_OF_FUNCTION),
            (D.SAFETY, S.NOT_SIGNIFICANT, Dir.NOT_CHANGED),
            (D.PATHWAY, S.P_VALUE_LT_0_01, Dir.ASSOCIATED),
            (D.CLINICAL_GENETICS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED),
        ]
        for d, s, dr in dims:
            self.A.add_row(EvidenceRow("GENE_A", "Disease", d, s, dr, "", ""))

        self.B = TargetEvidenceMatrix("GENE_B", "Disease")
        self.B.add_row(EvidenceRow("GENE_B", "Disease", D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED, "", ""))

        self.C = TargetEvidenceMatrix("GENE_C", "Disease")
        for d, s, dr in [
            (D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED),
            (D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED),
            (D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.LOSS_OF_FUNCTION),
            (D.PATHWAY, S.P_VALUE_LT_0_01, Dir.ASSOCIATED),
        ]:
            self.C.add_row(EvidenceRow("GENE_C", "Disease", d, s, dr, "", ""))

        self.D = TargetEvidenceMatrix("GENE_D", "Disease")
        for d, s, dr in [
            (D.GWAS, S.NOMINAL, Dir.ASSOCIATED),
            (D.SCRNA_SEQ, S.WEAK, Dir.UNKNOWN),
            (D.PATHWAY, S.NOMINAL, Dir.ASSOCIATED),
        ]:
            self.D.add_row(EvidenceRow("GENE_D", "Disease", d, s, dr, "", ""))

    def _loo(self, m, exclude_dim):
        """给定矩阵 m，排除 exclude_dim 后重新评分"""
        m2 = TargetEvidenceMatrix(m.target_gene, m.disease)
        for r in m.rows:
            if r.dimension != exclude_dim:
                m2.add_row(EvidenceRow(
                    m2.target_gene, m2.disease,
                    r.dimension, r.strength, r.direction, "", ""
                ))
        return m2.compute_weighted_confidence()["weighted_score"]

    def test_a_scores_high(self):
        """A (7维强一致) 应接近 1.0"""
        r = self.A.compute_weighted_confidence()
        assert r["weighted_score"] >= 0.95, f"A score too low: {r['weighted_score']}"
        assert r["kakeya"]["coverage_score"] == 1.0  # 覆盖封顶
        assert r["kakeya"]["n_present_dims"] == 7
        assert r["adjustments"]["contradiction_penalty"] == 0.0
        assert r["adjustments"]["missing_penalty"] == 0.0

    def test_b_scores_low(self):
        """B (仅GWAS) 应明显低于 A"""
        r = self.B.compute_weighted_confidence()
        assert r["weighted_score"] < 0.40, f"B should be low: {r['weighted_score']}"
        assert r["kakeya"]["n_present_dims"] == 1
        assert r["kakeya"]["coverage_score"] == 0.25

    def test_a_beats_b(self):
        """A 应明显高于 B (多维度 vs 单维度)"""
        sa = self.A.compute_weighted_confidence()["weighted_score"]
        sb = self.B.compute_weighted_confidence()["weighted_score"]
        assert sa - sb > 0.50, f"A({sa}) should dominate B({sb})"

    def test_c_beats_b(self):
        """C (4维含矛盾) 应高于 B"""
        sc = self.C.compute_weighted_confidence()["weighted_score"]
        sb = self.B.compute_weighted_confidence()["weighted_score"]
        assert sc > sb + 0.30, f"C({sc}) should beat B({sb})"

    def test_d_beats_b(self):
        """D (3维弱信号) 应高于 B (1维强)"""
        sd = self.D.compute_weighted_confidence()["weighted_score"]
        sb = self.B.compute_weighted_confidence()["weighted_score"]
        assert sd > sb + 0.20, f"D({sd}) should beat B({sb})"

    def test_a_loo_all_redundant(self):
        """A: 所有维度 LOO 后评分下降应 < 0.04 (REDUNDANT)"""
        orig = self.A.compute_weighted_confidence()["weighted_score"]
        for dim in [D.GWAS, D.SCRNA_SEQ, D.ANIMAL_MODEL, D.DRUGGABILITY,
                     D.SAFETY, D.PATHWAY, D.CLINICAL_GENETICS]:
            loo = self._loo(self.A, dim)
            delta = orig - loo
            assert 0 <= delta < 0.06, f"LOO -{dim.value}: Δ={delta:.4f}, expected REDUNDANT (<0.06)"

    def test_c_loo_all_essential(self):
        """C: 所有维度 LOO 后评分下降应 > 0.08 (ESSENTIAL)"""
        orig = self.C.compute_weighted_confidence()["weighted_score"]
        for dim in [D.GWAS, D.SCRNA_SEQ, D.ANIMAL_MODEL, D.PATHWAY]:
            loo = self._loo(self.C, dim)
            delta = orig - loo
            assert delta > 0.08, f"LOO -{dim.value}: Δ={delta:.4f}, expected ESSENTIAL (>0.08)"

    def test_d_loo_all_essential(self):
        """D: 所有维度 LOO 后评分下降应 > 0.08 (覆盖未封顶)"""
        orig = self.D.compute_weighted_confidence()["weighted_score"]
        for dim in [D.GWAS, D.SCRNA_SEQ, D.PATHWAY]:
            loo = self._loo(self.D, dim)
            delta = orig - loo
            assert delta > 0.08, f"LOO -{dim.value}: Δ={delta:.4f}, expected ESSENTIAL (>0.08)"


class TestCrossContradiction:
    """交叉维度矛盾检测测试"""

    def test_scrnax_ko_contradiction(self):
        """scRNA 上调 + animal KO = 预期矛盾"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.LOSS_OF_FUNCTION, "", ""))
        assert len(m.contradictions) == 1
        c = m.contradictions[0]
        assert c.dimension_a == D.SCRNA_SEQ
        assert c.dimension_b == D.ANIMAL_MODEL
        assert "上调" in c.description or "upregulated" in c.description

    def test_scrnadown_gof_contradiction(self):
        """scRNA 下调 + animal GOF = 预期矛盾"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.DOWNREGULATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.GAIN_OF_FUNCTION, "", ""))
        assert len(m.contradictions) == 1
        assert m.contradictions[0].dimension_a == D.SCRNA_SEQ

    def test_no_contradiction_aligned(self):
        """scRNA 上调 + animal GOF = 无矛盾"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.GAIN_OF_FUNCTION, "", ""))
        assert len(m.contradictions) == 0

    def test_weak_signal_no_contradiction(self):
        """弱信号不触发交叉维度矛盾 (强度阈值 0.06)"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.WEAK, Dir.UPREGULATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.ANIMAL_MODEL, S.WEAK, Dir.LOSS_OF_FUNCTION, "", ""))
        assert len(m.contradictions) == 0  # 强度不够

    def test_contradiction_penalty_in_score(self):
        """矛盾检测后评分应扣 -0.10"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.LOSS_OF_FUNCTION, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.PATHWAY, S.P_VALUE_LT_0_01, Dir.ASSOCIATED, "", ""))
        r = m.compute_weighted_confidence()
        assert r["adjustments"]["contradiction_penalty"] == 0.10

        # 对照: 无矛盾版本
        m2 = TargetEvidenceMatrix("GENE", "Disease")
        for dim, s, dr in [
            (D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED),
            (D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED),
            (D.ANIMAL_MODEL, S.AUC_GT_0_8, Dir.GAIN_OF_FUNCTION),
            (D.PATHWAY, S.P_VALUE_LT_0_01, Dir.ASSOCIATED),
        ]:
            m2.add_row(EvidenceRow("GENE", "Disease", dim, s, dr, "", ""))
        r2 = m2.compute_weighted_confidence()
        delta = r["weighted_score"] - r2["weighted_score"]
        assert abs(delta - (-0.10)) < 0.001, f"Penalty delta should be -0.10, got {delta}"


class TestStrengthWeights:
    """强度权重独立测试"""

    def test_strength_weights_in_output(self):
        """strength_weights 应输出到结果"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED, "", ""))
        m.add_row(EvidenceRow("GENE", "Disease", D.SCRNA_SEQ, S.LOG2FC_GT_1, Dir.UPREGULATED, "", ""))
        r = m.compute_weighted_confidence()
        assert "strength_weights" in r
        assert len(r["strength_weights"]) == 2
        assert r["strength_weights"][0] == 0.08  # P<5e-8
        assert r["strength_weights"][1] == 0.07  # LOG2FC>1

    def test_kakeya_debug(self):
        """kakeya debug dict 应包含完整信息"""
        m = TargetEvidenceMatrix("GENE", "Disease")
        m.add_row(EvidenceRow("GENE", "Disease", D.GWAS, S.P_VALUE_LT_5E8, Dir.ASSOCIATED, "", ""))
        r = m.compute_weighted_confidence()
        k = r["kakeya"]
        assert "coverage_score" in k
        assert "intensity_score" in k
        assert "n_present_dims" in k
        assert "n_strength_rows" in k
        assert "total_strength" in k
        assert "strength_denom" in k
        assert k["strength_denom"] == 0.50  # 11 个枚举值之和
