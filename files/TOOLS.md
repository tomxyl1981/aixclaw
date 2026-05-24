
---

## HuggingFace 镜像配置（中国环境）

**全局规则：所有 HuggingFace 访问统一使用镜像站**

```bash
# 环境变量（必须设置）
export HF_ENDPOINT=https://hf-mirror.com

# 镜像站地址
https://hf-mirror.com
```

**适用场景：**
- 模型下载（HuggingFace Hub）
- 数据集下载
- Semble 嵌入模型
- 其他所有 HF 资源

**已配置项目：**
- Semble：✓ 已配置
- Tree-sitter 解析器：✓ 已手动下载

**注意：** 所有涉及 HuggingFace 的操作，必须先设置 `HF_ENDPOINT` 环境变量！

---

*更新时间：2026-05-20*
