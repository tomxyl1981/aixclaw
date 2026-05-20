# UniVidX：统一多模态视频生成框架

> 来源：https://github.com/houyuanchen111/UniVidX | SIGGRAPH 2026 | 分析日期：2026-05-15

## 基本信息
- Stars: 200 | 语言: Python
- 论文：https://arxiv.org/abs/2605.00658
- 项目页：https://houyuanchen111.github.io/UniVidX.github.io/

## 核心创新
- SCM（随机条件掩码）：打破固定映射，全向条件生成
- DGL（解耦门控LoRA）：保持VDM强先验
- CMSA（跨模态自注意力）：促进模态间对齐

## 支持任务
- UniVid-Intrinsic：RGB/Albedo/Irradiance/Normal四模态分解
- UniVid-Alpha：RGB/Alpha/前景/背景四模态分离
- 15种任务组合（Text→X、X→X、Text&X→X）

## 关键优势
- <1,000训练视频达到SOTA
- 野外泛化能力强
- 统一框架替代多个专用模型

## AIX应用
- 那耶村宣传片生成：50-100 CH
- 视频修复/编辑：30-150 CH
- 云海素材二次创作：20-80 CH
- 成本降幅：99%+

## 部署
- GPU: 24GB+ VRAM（14B模型）
- Mac Studio M3 Ultra可运行
- 推理时间：2-5分钟/视频

## 建议
- 关注项目等待社区反馈
- Mac Studio上测试推理
- 集成到AIX内容生产工具链
