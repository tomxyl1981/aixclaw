# AIX Box 部署文件清单

**生成时间**: 2026-04-22 07:13 UTC

---

## 📁 目录结构

```
/opt/aixbox/
├── config/                    # 配置文件
│   ├── aixbox.conf
│   ├── wallet.conf
│   └── skywire.json
│
├── wallet/                    # 钱包核心 (硬件+密钥)
│   ├── hal.py                 # ATECC608B接口
│   ├── key.py                 # BIP39/BIP32密钥派生
│   ├── tx.py                  # UTXO交易签名
│   └── ui.py                  # CLI交互
│
├── chain/                     # 区块链交互
│   ├── aix_client.py          # AIX链RPC
│   ├── coinhour.py            # CH计算逻辑
│   └── emercoin_client.py     # Emercoin RPC
│
├── network/                   # 网络服务
│   ├── skywire_service.py     # Skywire节点
│   └── ipfs_service.py        # IPFS存储
│
├── ai/                        # AI服务
│   ├── pico_claw.py           # 本地AI
│   ├── hindsight_client.py    # 记忆接口
│   └── billing.py             # 计费模块
│
├── scripts/                   # 工具脚本
│   ├── init_wallet.py         # 初始化钱包
│   ├── check_hardware.py      # 硬件检测
│   └── monitor.py             # 服务监控
│
└── main.py                    # 主服务入口
```

---

## 🔧 核心文件 (刘威 - 硬件)

### wallet/hal.py
```python
# ATECC608B硬件抽象层
class ATECC608B:
    def generate_keypair(self, slot: int) -> bytes:
        """芯片内生成密钥对,私钥永不出芯片"""
        pass
    
    def sign_message(self, slot: int, message: bytes) -> bytes:
        """硬件签名"""
        pass
    
    def encrypt_data(self, slot: int, data: bytes) -> bytes:
        """硬件加密助记词"""
        pass
```

---

## 💻 核心文件 (汤比特 - 软件)

### wallet/key.py
```python
# BIP39助记词 + BIP32密钥派生
def generate_mnemonic() -> list[str]:
    """生成12词助记词"""
    pass

def derive_private_key(mnemonic: list[str], path: str) -> bytes:
    """从助记词派生私钥"""
    pass
```

### wallet/tx.py
```python
# UTXO交易构造与签名
class Transaction:
    def create(self, inputs: list, outputs: list) -> dict:
        """构造交易"""
        pass
    
    def sign(self, tx: dict, private_key: bytes) -> str:
        """签名并返回hex"""
        pass
```

### chain/aix_client.py
```python
# AIX链RPC客户端
class AIXClient:
    def get_balance(self, address: str) -> float:
        """查询AIX余额"""
        pass
    
    def send_raw_tx(self, signed_tx: str) -> str:
        """广播交易,返回txid"""
        pass
    
    def get_coinhour_balance(self, address: str) -> float:
        """查询CH余额"""
        pass
```

---

## 📋 Systemd服务

### /etc/systemd/system/aixbox.service
```ini
[Unit]
Description=AIX Box Core Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aixbox
ExecStart=/opt/aixbox/venv/bin/python /opt/aixbox/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📦 依赖安装命令

```bash
# 系统依赖
sudo apt install i2c-tools libusb-1.0-0-dev docker.io

# Python依赖
pip install cryptoauthlib cryptography requests pydantic

# 外部服务
# - Skywire: git clone https://github.com/skycoin/skywire
# - Emercoin: wget emercoin-0.7.10
# - IPFS: wget dist.ipfs.tech/kubo
# - Hindsight: docker pull ghcr.io/vectorize-io/hindsight
```

---

## 🚀 开发顺序

| 周次 | 刘威(硬件) | 汤比特(软件) |
|------|-----------|-------------|
| W1 | ATECC608B焊接+I2C测试 | 环境搭建+项目框架 |
| W2 | 按键/LED GPIO配置 | wallet/key.py + wallet/tx.py |
| W3 | 硬件安全测试 | chain/aix_client.py + UTXO集成 |
| W4 | RK3588主板设计 | Skywire+Emercoin+IPFS部署 |
| W5 | 量产准备 | Hindsight+PicoClaw集成 |

**完整文件清单已保存到**: `~/.openclaw/workspace/aixbox-deploy/FILE_LIST.md`
