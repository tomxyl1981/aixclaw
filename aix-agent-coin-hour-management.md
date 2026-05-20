# Agent自动管理Coin Hour流程设计

**场景**：用户指令"每月自动充值100 Coin Hour"，Agent安全执行

---

## 一、整体架构

```
┌─────────────────────────────────────────────┐
│         用户指令层                           │
│  "每月自动充值100 CH"                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Pico Claw Agent（决策层）              │
│  - 解析指令：金额、周期、来源               │
│  - 风险评估：余额检查、限额校验             │
│  - 执行计划：生成UTXO交易指令               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Harness硬件层（治理层）                │
│  - 权限校验：单笔上限、日累计上限           │
│  - 合规检查：黑名单、白名单                 │
│  - 物理锁死：禁止导出私钥                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         UTXO账本（执行层）                   │
│  - 原子交易：成功/失败                      │
│  - 余额更新：Coin Hour +100                 │
│  - 记录存证：交易哈希、时间戳               │
└─────────────────────────────────────────────┘
```

---

## 二、详细流程设计

### 流程图

```
用户指令："每月自动充值100 CH"
         ↓
    ┌────────────┐
    │ 指令解析   │ → 提取：金额=100、周期=月、来源=AIX兑换
    └────────────┘
         ↓
    ┌────────────┐
    │ 风险评估   │ → 检查：用户AIX余额≥?、历史交易正常?
    └────────────┘
         ↓ 是
    ┌────────────┐
    │ 限额校验   │ → Harness检查：单笔≤500 CH、月累计≤2000 CH
    └────────────┘
         ↓ 通过
    ┌────────────┐
    │ 生成交易   │ → 创建UTXO交易指令
    └────────────┘
         ↓
    ┌────────────┐
    │ Harness审批│ → 硬件层签名确认
    └────────────┘
         ↓
    ┌────────────┐
    │ 执行交易   │ → UTXO账本原子更新
    └────────────┘
         ↓
    ┌────────────┐
    │ 结果反馈   │ → "已充值100 CH，余额：xxx"
    └────────────┘
         ↓
    ┌────────────┐
    │ 定时注册   │ → 注册下月自动执行任务
    └────────────┘
```

---

## 三、安全机制设计

### 3.1 多层权限控制

| 层级 | 控制项 | 规则 |
|------|--------|------|
| **用户层** | 操作确认 | 首次需用户确认，后续自动执行 |
| **Agent层** | 风险评估 | 异常交易（大额/频繁）需人工确认 |
| **Harness层** | 硬件锁死 | 单笔上限500 CH、日累计1000 CH、月累计2000 CH |
| **UTXO层** | 原子校验 | 交易要么成功要么失败，无中间态 |

### 3.2 异常处理

| 异常场景 | 处理方式 |
|----------|----------|
| **余额不足** | Agent通知用户"余额不足，请充值AIX" |
| **超过限额** | Harness拒绝执行，Agent提示"超过单笔上限" |
| **网络异常** | 自动重试3次，失败则通知用户 |
| **可疑交易** | Agent冻结自动任务，需人工确认 |

### 3.3 审计追踪

```json
{
  "transaction_id": "tx_20260427_001",
  "user": "ou_0432f14b...",
  "action": "auto_recharge",
  "amount": 100,
  "currency": "Coin Hour",
  "source": "AIX兑换",
  "timestamp": "2026-04-27T14:40:00Z",
  "status": "success",
  "agent_id": "pico-claw-001",
  "harness_signature": "0xabc123...",
  "utxo_hash": "0xdef456..."
}
```

---

## 四、用户交互流程

### 首次设置

```
用户："每月自动充值100 Coin Hour"

Agent：
"已为您设置自动充值计划：
✅ 充值金额：100 CH/月
✅ 执行时间：每月1号
✅ 扣款来源：AIX兑换
✅ 当前AIX余额：500（足够5个月）

请确认开启自动充值？"

用户："确认"

Agent：
"✅ 自动充值已开启
- 下次执行：2026-05-01
- 您可随时说'取消自动充值'来关闭"
```

### 定期执行

```
[2026-05-01 00:00]

Agent自动执行：
1. 检查AIX余额充足
2. Harness审批通过
3. UTXO交易执行
4. 发送通知：

"📊 自动充值完成
- 充值金额：100 CH
- 当前余额：xxx CH
- 下次执行：2026-06-01"
```

### 异常通知

```
Agent：
"⚠️ 自动充值失败
- 原因：AIX余额不足
- 当前余额：50 AIX
- 需要金额：100 AIX

请充值AIX或调整自动充值金额"
```

---

## 五、技术实现

### 5.1 Agent指令解析

```python
class CoinHourAgent:
    def parse_recharge_command(self, user_input):
        """
        解析用户充值指令
        """
        # 提取关键信息
        amount = extract_amount(user_input)  # 100
        period = extract_period(user_input)  # "每月"
        source = extract_source(user_input)  # 默认AIX兑换
        
        # 验证参数
        if amount > HARNESS_LIMITS['single_tx']:
            return {"error": "超过单笔上限"}
        
        return {
            "action": "auto_recharge",
            "amount": amount,
            "period": period,
            "source": source
        }
```

### 5.2 Harness权限校验

```python
class HarnessLayer:
    LIMITS = {
        'single_tx': 500,      # 单笔上限
        'daily_total': 1000,   # 日累计上限
        'monthly_total': 2000  # 月累计上限
    }
    
    def validate_transaction(self, tx):
        """
        硬件层交易校验
        """
        # 检查单笔上限
        if tx.amount > self.LIMITS['single_tx']:
            return {"approved": False, "reason": "exceed_single_limit"}
        
        # 检查日累计
        daily_total = self.get_daily_total(tx.user_id)
        if daily_total + tx.amount > self.LIMITS['daily_total']:
            return {"approved": False, "reason": "exceed_daily_limit"}
        
        # 检查月累计
        monthly_total = self.get_monthly_total(tx.user_id)
        if monthly_total + tx.amount > self.LIMITS['monthly_total']:
            return {"approved": False, "reason": "exceed_monthly_limit"}
        
        # 物理签名
        signature = self.hardware_sign(tx)
        
        return {"approved": True, "signature": signature}
```

### 5.3 UTXO交易执行

```python
class UTXOLedger:
    def execute_transaction(self, tx, signature):
        """
        执行UTXO原子交易
        """
        # 验证签名
        if not self.verify_signature(tx, signature):
            return {"status": "failed", "reason": "invalid_signature"}
        
        # 原子更新
        try:
            # 锁定输入
            self.lock_utxo(tx.input_utxo)
            
            # 创建输出
            new_utxo = self.create_utxo(
                owner=tx.user_id,
                amount=tx.amount,
                type="Coin Hour"
            )
            
            # 提交交易
            self.commit_transaction(tx)
            
            return {"status": "success", "new_utxo": new_utxo}
            
        except Exception as e:
            # 回滚
            self.rollback_transaction(tx)
            return {"status": "failed", "reason": str(e)}
```

### 5.4 定时任务调度

```python
class AutoRechargeScheduler:
    def register_task(self, user_id, amount, period):
        """
        注册自动充值任务
        """
        cron_expr = self.period_to_cron(period)  # "0 0 1 * *"
        
        task = {
            "task_id": f"auto_recharge_{user_id}",
            "user_id": user_id,
            "amount": amount,
            "cron": cron_expr,
            "created_at": datetime.now()
        }
        
        self.task_queue.add(task)
        return task
    
    def execute_task(self, task):
        """
        执行自动充值任务
        """
        agent = CoinHourAgent()
        
        # 检查余额
        if not agent.check_balance(task.user_id, task.amount):
            agent.notify_user(task.user_id, "余额不足")
            return
        
        # 执行充值
        result = agent.recharge(
            user_id=task.user_id,
            amount=task.amount
        )
        
        # 通知用户
        agent.notify_user(task.user_id, result)
```

---

## 六、扩展场景

### 6.1 自动支付租金

```
用户："每月1号自动支付房租500 Coin Hour给房东张三"

Agent：
1. 解析指令
2. 校验收款人（张三的Coin Hour地址）
3. Harness审批
4. UTXO执行
5. 定时注册
```

### 6.2 自动分发工资

```
用户："每月15号自动发放工资给团队成员：
- 李四：200 CH
- 王五：150 CH
- 赵六：100 CH"

Agent：
1. 批量创建UTXO交易
2. Harness审批（总额450 CH）
3. 原子执行（全部成功或全部失败）
4. 通知所有收款人
```

### 6.3 自动投资

```
用户："每季度自动买入价值1000 Coin Hour的AIX"

Agent：
1. 监控Coin Hour价格
2. 价格合适时执行兑换
3. Harness审批
4. UTXO执行
5. 记录投资成本
```

---

## 七、安全最佳实践

### 7.1 用户教育

| 场景 | 提示 |
|------|------|
| 首次设置 | "自动充值将从您的AIX余额扣除，请确保余额充足" |
| 大额交易 | "单笔超过200 CH需要二次确认" |
| 异常检测 | "检测到频繁交易，已暂时冻结自动任务" |

### 7.2 风控规则

| 规则 | 阈值 | 动作 |
|------|------|------|
| 单笔上限 | 500 CH | Harness拒绝 |
| 日累计上限 | 1000 CH | Harness拒绝 |
| 月累计上限 | 2000 CH | Harness拒绝 |
| 异常频率 | 1小时>5次 | Agent冻结+人工确认 |
| 新收款人 | 首次转账 | 需人工确认 |

### 7.3 应急处理

```
用户："取消所有自动任务"

Agent：
"已取消以下自动任务：
✅ 每月自动充值100 CH
✅ 每月自动支付房租500 CH

所有定时任务已停止。"
```

---

## 八、那耶村MVP场景

| 场景 | 实现 |
|------|------|
| **村民自动充值** | 每月自动充值Coin Hour |
| **漫剧消费** | 观看漫剧自动扣费 |
| **村内转账** | 自动支付服务费 |
| **收益自动分发** | DAO收益自动分发到村民账户 |

---

## 九、总结

### 核心设计原则

1. **AI决策，硬件否决** → Agent有执行权，Harness有锁死权
2. **原子交易** → 成功或失败，无中间态
3. **多层审计** → 用户→Agent→Harness→UTXO全链路记录
4. **用户可控** → 随时取消、随时调整

### 一句话

> **用户说一句话，Agent自动执行，Harness硬性锁死，UTXO原子记录。**
> 
> **安全、可控、可审计。**

---

*Agent自动管理Coin Hour——让AI成为可靠的经济助手*
