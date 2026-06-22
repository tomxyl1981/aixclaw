# Terraform + Ansible + Semaphore：AI治理基础设施架构

> 来源：企业AI落地实践总结  
> 记录时间：2026-06-22  
> 核心主题：为AI辅助运维构建可审计、可控制的基础设施

---

## 一、架构设计核心目标

### 双重目的
1. **基础设施代码化**：从「人肉运维」升级成「可版本化的代码」
2. **AI治理前置**：提前规划好AI能做什么、不能做什么的执行边界

### 物理底座原则
- **有限资源下的规划**：十几台异构机器的合理分工
- **网段统一优先**：所有自动化前提是网络拓扑清晰
- **资产与代码分离**：物理资产清单与IaC代码分文件维护

---

## 二、IaC双引擎分工

### Terraform：定义"有什么"
- **职责**：VM拓扑的代码化
- **管理对象**：infra集群、build集群、dev/test/uat环境、IaC控制机
- **关键实践**：
  - `locals.tf` 作为 VM 和 IP 的唯一事实源
  - `terraform.tfvars` 存敏感变量，不入库
  - 执行前必须 `terraform plan` 确认
  - `outputs.tf` 生成 Inventory

### Ansible：定义"变成什么样"
- **职责**：从基线到 k3s 的配置管理
- **部署顺序**：
  1. k3s NFS 宿主机
  2. infra 集群（Harbor/Nexus）
  3. build 集群
  4. dev/test/uat 环境
  5. NFS 动态 StorageClass
- **关键实践**：
  - 典型 playbook 串联：openEuler基线 → Docker → k3s master → k3s worker
  - `group_vars` 按环境隔离
  - Inventory 自动生成，禁手改

### Inventory自动生成流水线
```
terraform/locals.tf + vm_*.tf
        ↓
terraform/outputs.tf → all_clusters_inventory
        ↓
sync-inventory 脚本
        ↓
ansible/inventory/hosts.yml（全量生成，勿手改）
```

**改地址流程**：改 locals → plan → apply → sync-inventory → 写回

---

## 三、平台分层架构（L0-L3）

```
L0 虚拟化    物理机 + openEuler VM
     ↓
L1 编排      Terraform 创建 VM + Ansible 装系统/k3s
     ↓
L2 平台      Semaphore（IaC 控制）+ infra 集群 + build 集群
     ↓
L3 环境      dev / test / uat 业务集群
```

### 各层职责
| 层级 | 组件 | 核心职责 |
|------|------|---------|
| **L0** | pxvirt + openEuler | 虚拟化底座，支持异构（x86/ARM/龙芯） |
| **L1** | Terraform + Ansible | VM 定义与系统配置 |
| **L2** | Semaphore + infra + build | 控制面 + 制品中枢 + CI构建 |
| **L3** | dev/test/uat | 业务运行环境 |

### 关键设计决策
- **infra 集群**：Harbor/Nexus，所有环境的制品中枢
- **build 集群**：专跑 CI/CD，与制品存储解耦
- **多集群网络隔离**：独立 Pod CIDR 和 Service CIDR，按环境分配

---

## 四、Semaphore：L3变更的唯一入口

### 为什么需要Semaphore
- **不可逆操作集中管理**：terraform apply / ansible-playbook 影响面大
- **统一审批流程**：避免本机执行无留痕
- **AI执行风险隔离**：防止AI助手"顺手帮你跑一下 apply"

### 代码与状态分离
```
git push（开发机）
    ↓
Semaphore 任务开始 → 自动 git pull 最新代码
    ↓
代码在任务临时目录（.tf / playbook 始终最新）
state / tfvars 在持久化挂载卷（跨任务保留）
SSH 密钥在 Key Store 或容器挂载路径
```

### 审批机制（补Community版不足）
| 模板类型 | 审批方式 |
|---------|---------|
| Terraform | 运行时勾选 Plan 仅预览；不勾选则 plan 后在任务详情页人工确认再 apply |
| Ansible deploy | 无内置二次确认；靠流程：先跑只读检查模板 → 人工 review 日志 → 再点 Run 执行 L3 |
| 组织留痕 | 任务历史 + 变更说明记录任务 ID、执行人、影响范围 |

### 模板体系（80%场景5-7个模板）
- `terraform-apply`：唯一通用 TF 模板
- `ansible-install-docker-stack`：一键 Docker + Compose
- `ansible-baseline`：Guest OS 安全基线加固
- `ansible-ping`：连通性自检
- `ansible-k3s-nfs-hosts`：NFS 宿主机配置
- `ansible-deploy-env-*`：按环境部署
- `bash-sync-inventory`：apply 后同步 Inventory

---

## 五、AI治理：执行边界设计

### AI能做什么
- 写 Terraform 代码定义新的 VM 和集群
- 写 Ansible playbook 自动化系统配置
- 生成 Semaphore 模板定义
- 分析 plan 输出给出变更影响评估
- 写 sync-inventory 脚本和 CI 流水线

### AI不能做什么（硬红线）
| 禁止行为 | 架构保障机制 |
|---------|------------|
| **直接 apply** | terraform apply 和 ansible-playbook 默认走 Semaphore，不在本机执行 |
| **接触密钥** | 仓库里无真实密码，AI 只能看到变量名和注入说明 |
| **绕过审批** | Terraform 必须在任务详情页人工确认；Ansible 必须先只读检查 |
| **修改 Inventory** | Inventory 由脚本自动生成，禁手改 |

### Docker诊断 vs 执行边界
- **诊断容器**（只读）：plan、ping、syntax-check → 本机 Docker 安全
- **执行容器**（改变状态）：apply → 必须走 Semaphore

### 给未来 AI Agent 留接口
| 层级 | 接口能力 | 权限边界 |
|------|---------|---------|
| **L1** | 只读接口 | AI Agent 可随时跑 plan/ping/syntax-check 做持续监控 |
| **L2** | 任务触发 | AI Agent 可在 Semaphore 中创建任务请求，执行仍需人工确认 |
| **L3** | 审计接口 | AI Agent 可读取所有执行结果和日志，用于分析和建议 |

**核心原则**：AI Agent 权限是「读 + 建议 + 触发请求」，不是「直接执行」

---

## 六、对AIX项目的架构启示

### 启示一："LLM打工，代码做主"的工程实践

这篇文章完美诠释了AIX项目的核心理念：

| 理念维度 | 文章实践 | AIX对应 |
|---------|---------|---------|
| **LLM打工** | AI写Terraform/Ansible代码 | Pico Claw Agent执行语义理解 |
| **代码做主** | 执行必须走Semaphore审批 | 硬件钱包写入拦截逻辑 |
| **执行边界** | AI不能直接apply | 禁止违规操作的物理锁死 |

### 启示二：AIX Box运维基础设施设计

可借鉴的分层架构：

```
L0 硬件层    AIX Box 物理设备（硬件钱包+边缘计算+存储）
     ↓
L1 编排层    本地IaC定义（UTXO账本+Coin Hour规则）
     ↓
L2 控制层    Pico Claw Agent（本地推理+执行控制）
     ↓
L3 应用层    社区服务（交易、NFT、算力共享）
```

### 启示三：Pico Claw Agent的执行边界

参考Semaphore的审批机制：

| 操作类型 | Agent权限 | 人工确认 |
|---------|----------|---------|
| **只读查询** | 可自主执行 | 不需要 |
| **Coin Hour转账** | 可建议金额 | 硬件钱包确认 |
| **UTXO账本修改** | 可写代码 | 多签治理 |
| **智能合约部署** | 可生成合约 | 社区投票 |

### 启示四：去中心化治理的审计机制

Semaphore的任务历史 = 审计日志，对应AIX的：

- **UTXO账本**：天然带时间戳和签名链
- **Coin Hour流向**：完整的经济活动轨迹
- **Agent操作日志**：所有执行结果可追溯

---

## 七、技术选型参考

### 虚拟化平台：pxvirt
- **核心优势**：信创场景下的异构支持（x86/ARM/龙芯）
- **技术基础**：Proxmox VE fork，完整API体系
- **Terraform集成**：有现成provider对接

### Guest OS：openEuler 24.03 LTS
- **兼容性检查**：x86-64-v2指令集（老CPU可能缺popcnt）
- **国产生态**：信创路线首选
- **稳定性**：LTS版本适合基础设施

### IaC工具链
- **Terraform**：VM定义与生命周期管理
- **Ansible**：系统配置与应用部署
- **Semaphore**：执行控制与审计平台

---

## 八、首次部署顺序

```
① terraform-apply（勾 Plan，确认 VM 规划）
② terraform-apply（不勾 Plan，任务内确认后创建 VM）
③ bash-sync-inventory（write → check → 可选 git push）
④ ansible-syntax-check
⑤ ansible-k3s-nfs-hosts（各环境 NFS 宿主机）
⑥ ansible-deploy-infra（infra 集群 + Harbor/Nexus）
⑦ ansible-deploy-env × 4（build → dev → test → uat）
⑧ CI/CD 注册构建集群和发布目标
⑨ 验收：ping、kubectl get nodes、Harbor/Nexus 健康检查
```

---

## 九、核心经验总结

| 维度 | 核心经验 |
|------|---------|
| **物理层** | 有限资源下的混部策略，NFS 宿主机直装，网段与地址代码化 |
| **IaC 层** | Terraform 定义 VM，Ansible 配置系统，Inventory 自动生成 |
| **平台层** | infra 管制品、build 管 CI、三套环境管业务，职责分离 |
| **执行层** | Semaphore 作为 L3 唯一入口，Terraform 任务内 plan 确认，Ansible 只读检查先行 |
| **AI 治理** | AI 能写代码不能 apply，密钥不进仓库，执行必须人工确认 |

**一句话总结**：
> 用 IaC 把基础设施变成可版本化的代码，用 Semaphore 把执行面集中到一个有审计的平台，然后给 AI 划好执行边界。

---

**更新记录**：
- 2026-06-22：初始记录，提炼架构设计与AI治理边界
