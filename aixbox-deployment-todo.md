# AIX Box 完整部署 Todo List

**创建时间**: 2026-04-22 06:38 UTC  
**分配者**: Jane (ou_0f69829f208490a428d5cdede9e508bc)

## 硬件部分 (刘威)

### Phase 1: 硬件选型与采购 (Week 1)
- [ ] **ATECC608B 安全芯片选型**
  - 评估 SDA/SCL 引脚兼容性
  - 确认 I2C 地址配置
  - 采购开发板套件
  
- [ ] **主板接口确认**
  - I2C 总线预留 (GPIO 2/3 或 4/5)
  - 物理按键 GPIO 预留
  - LED 指示灯 GPIO 预留
  - 可选: OLED/I2C 显示屏接口

- [ ] **J1900 原型机改造**
  - 焊接 ATECC608B 芯片
  - 连接物理按键 (GPIO 或 USB 扩展)
  - 连接 LED 指示灯
  - 验证 I2C 通信正常

### Phase 2: 硬件安全测试 (Week 2)
- [ ] **ATECC608B 功能验证**
  - 芯片配置区写入测试
  - Slot 0 私钥生成测试
  - Slot 1 助记词加密存储测试
  - ECDSA 签名测试
  
- [ ] **物理交互验证**
  - 按键响应时间 < 100ms
  - LED 状态切换正常
  - 屏幕显示交易信息 (如配备)

### Phase 3: 量产准备 (Week 3-4)
- [ ] **RK3588 主板设计**
  - ATECC608B 集成到主板
  - 物理按键 PCB 布局
  - 外壳开孔设计
  - 散热方案确认

---

## 软件部分 (用户377861)

### Phase 1: AIX 硬件钱包 (Week 1-2)
- [ ] **ATECC608B 驱动开发**
  ```bash
  # 依赖安装
  pip install cryptoauthlib
  pip install cryptography
  ```
  
- [ ] **钱包核心模块**
  - [ ] `wallet_hal.py` - 硬件抽象层
  - [ ] `wallet_key.py` - 密钥管理 (生成/派生/签名)
  - [ ] `wallet_backup.py` - 助记词备份/恢复
  - [ ] `wallet_tx.py` - 交易签名流程

- [ ] **UTXO 账本集成**
  - 连接 AIX 链节点
  - 余额查询
  - 交易构造与广播
  - Coin Hour 计算逻辑

- [ ] **交互界面**
  - 命令行钱包 CLI
  - 交易确认流程 (显示 → 按键 → 签名)
  - 助记词显示/输入界面

### Phase 2: Skywire 节点 (Week 2-3)
- [ ] **Skywire 安装部署**
  ```bash
  # 安装脚本
  git clone https://github.com/skycoin/skywire.git
  cd skywire
  make install
  ```
  
- [ ] **节点配置**
  - 生成 Skywire 密钥对
  - 配置节点类型 (计算/存储/传输)
  - 配置连接策略
  
- [ ] **与钱包集成**
  - Skywire 支付使用 AIX/Coin Hour
  - 节点收益自动存入硬件钱包

### Phase 3: Emercoin 全节点 (Week 3)
- [ ] **Emercoin 部署**
  ```bash
  # 安装
  wget https://emercoin.com/en/downloads
  # 配置 emercoin.conf
  ```
  
- [ ] **NVS (Name Value Storage)**
  - EmerDNS 配置
  - 去中心化域名解析
  - 与 AIX Box 身份绑定

- [ ] **全节点同步**
  - 区块链数据存储 (SSD 预留 100GB+)
  - 同步状态监控
  - RPC API 接口配置

### Phase 4: 分布式存储 BPFS (Week 3-4)
- [ ] **BPFS 节点部署**
  ```bash
  # 基于 IPFS 修改
  ipfs init --profile=lowpower
  ipfs config --json Experimental.Libp2pStreamMounting true
  ```
  
- [ ] **存储合约**
  - 存储提供者注册
  - 存储价格设定 (Coin Hour)
  - 数据冗余策略
  
- [ ] **与 Skywire 集成**
  - 数据传输走 Skywire 网络
  - 加密存储 (使用 ATECC608B 派生密钥)

### Phase 5: Pico Claw AI (Week 4)
- [ ] **Pico Claw 本地化部署**
  ```bash
  # 类似 claude-code-local
  git clone https://github.com/nicedreamzapp/claude-code-local
  # 适配到 AIX Box
  ```
  
- [ ] **Hindsight 记忆集成**
  - Docker 部署 Hindsight
  - 配置本地向量存储
  - 与 ATECC608B 加密层对接

- [ ] **与钱包联动**
  - AI 服务使用 Coin Hour 计费
  - 每个 API 调用扣费
  - 收益自动存入硬件钱包

---

## 集成测试 (Week 5)

### 硬件+软件联调
- [ ] **完整流程测试**
  1. Box 首次启动 → 生成钱包 → 显示助记词
  2. 连接 Skywire 网络 → 获得节点身份
  3. 同步 Emercoin 节点 → 解析 EmerDNS
  4. 启动 BPFS 存储 → 接受存储任务
  5. 启动 Pico Claw → AI 服务计费

- [ ] **Coin Hour 闭环测试**
  - 持有 AIX → 产出 Coin Hour
  - 使用 AI 服务 → 消耗 Coin Hour
  - 提供存储 → 赚取 Coin Hour

- [ ] **那耶村场景模拟**
  - 离线环境运行 (断网 72 小时)
  - 本地交易验证
  - 数据主权验证 (数据不离开 Box)

---

## 里程碑

| 周次 | 里程碑 | 验收标准 |
|------|--------|----------|
| Week 1 | 硬件改造完成 | ATECC608B 焊接成功，I2C 通信正常 |
| Week 2 | 钱包功能可用 | 可生成地址、签名交易、备份助记词 |
| Week 3 | 网络节点就绪 | Skywire + Emercoin 运行正常 |
| Week 4 | 完整系统就绪 | 五合一系统全部运行 |
| Week 5 | 集成测试通过 | 那耶村场景模拟成功 |

---

## 关键依赖

- **硬件**: ATECC608B 芯片、I2C 转接板、物理按键、LED
- **软件**: cryptoauthlib、skywire、emercoin、ipfs-go、docker
- **网络**: Skywire 网络接入、Emercoin 节点连接
- **链**: AIX 链 RPC 接口、Coin Hour 计算服务

---

**记录时间**: 2026-04-22 06:38 UTC

## 🆕 新增: Turix Skill 集成 (Week 4-5)

**提出者**: Jane (ou_0f69829f208490a428d5cdede9e508bc)
**时间**: 2026-04-22 07:14 UTC

### Turix CUA Skill 概述
- **GitHub**: Turix CUA (2.3K stars)
- **功能**: 视觉识别+模拟操作,自动化微信等封闭App
- **价值**: AIX Box本地化微信运营+获客自动化

### 开发任务 (用户377861)

#### Phase 1: Turix集成 (Week 4)
- [ ] **部署Turix到AIX Box**
  - 安装Turix依赖 (OpenCV, PyAutoGUI等)
  - 配置视觉模型本地运行
  - 测试微信自动化操作

- [ ] **封装为Capsule Skill**
  ```
  skills/turix-wechat/
  ├── manifest.json          # Skill元数据
  ├── turix_adapter.py       # Turix接口封装
  ├── actions/               # 微信操作定义
  │   ├── accept_friend.py   # 自动通过好友
  │   ├── auto_reply.py      # 自动回复
  │   └── send_message.py    # 发送消息
  └── billing.yaml           # Coin Hour计费规则
  ```

#### Phase 2: 自动化获客场景 (Week 5)
- [ ] **那耶村农产品销售自动化**
  - 微信好友自动通过+欢迎语
  - 农产品信息自动回复
  - 订单收集+Coin Hour收款

- [ ] **微信指数数据采集**
  - 定时抓取微信指数
  - 本地分析存储
  - 生成市场报告

### 计费模型

| 功能 | 计费 | 说明 |
|------|------|------|
| 通过好友请求 | 0.1 CH/次 | 每通过1个好友扣费 |
| 发送消息 | 0.05 CH/条 | 自动回复消息 |
| 数据采集 | 0.2 CH/次 | 微信指数抓取 |
| 完整获客流程 | 1 CH/潜在客户 | 从添加→咨询→下单 |

### 与AIX Box整合

```
用户使用Turix Skill运营微信
    ↓
AIX Box本地运行 (数据不出门)
    ↓
每次操作扣Coin Hour
    ↓
收益分配给:
  - 70% Turix Skill作者
  - 20% AIX DAO储备池
  - 10% 节点运营者
```

### 隐私优势

| 对比 | 传统方案 | AIX Box+Turix |
|------|---------|---------------|
| 数据流 | 微信→云端AI→指令返回 | 微信→本地Box→本地执行 |
| 隐私风险 | 高 (数据经过第三方) | 低 (数据物理隔离) |
| 计费透明 | 不透明 | UTXO账本记录每笔 |

### 验收标准
- [ ] Turix在J1900/RK3588上运行流畅
- [ ] 微信自动化操作成功率>90%
- [ ] Coin Hour计费准确记录
- [ ] 那耶村农产品销售自动化跑通

---

**记录时间**: 2026-04-22 07:14 UTC
