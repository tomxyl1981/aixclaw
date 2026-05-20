#!/usr/bin/env python3
"""
那耶村预测市场 - 基础版
Coin Hour结算 + UTXO账本
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class NayePredictionMarket:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "~/.openclaw/workspace/prediction-market/market.db"
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS markets (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                category TEXT,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                outcome TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT,
                total_yes REAL DEFAULT 0,
                total_no REAL DEFAULT 0,
                fee_percent REAL DEFAULT 5.0
            );
            
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                market_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                outcome TEXT NOT NULL,
                amount REAL NOT NULL,
                shares REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (market_id) REFERENCES markets(id)
            );
            
            CREATE TABLE IF NOT EXISTS utxo_log (
                id TEXT PRIMARY KEY,
                tx_type TEXT NOT NULL,
                user_id TEXT,
                market_id TEXT,
                amount REAL,
                outcome TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_positions_market ON positions(market_id);
            CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id);
        """)
        conn.commit()
        conn.close()
    
    def create_market(self, question: str, end_time: str, 
                     category: str = "general") -> str:
        """创建预测市场"""
        market_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO markets (id, question, category, end_time)
            VALUES (?, ?, ?, ?)
        """, (market_id, question, category, end_time))
        conn.commit()
        conn.close()
        
        self._log_utxo("create_market", None, market_id, 10, None)
        return market_id
    
    def bet(self, market_id: str, user_id: str, 
            outcome: str, amount: float) -> Tuple[str, float]:
        """押注"""
        if outcome not in ["yes", "no"]:
            return None, "Invalid outcome"
        
        conn = sqlite3.connect(self.db_path)
        
        # 检查市场状态
        cur = conn.execute(
            "SELECT status FROM markets WHERE id=?", (market_id,)
        )
        row = cur.fetchone()
        if not row or row[0] != "open":
            conn.close()
            return None, "Market not open"
        
        # 简化：1 Coin Hour = 1 share
        shares = amount
        
        # 创建持仓
        position_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO positions (id, market_id, user_id, outcome, amount, shares)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (position_id, market_id, user_id, outcome, amount, shares))
        
        # 更新市场总额
        if outcome == "yes":
            conn.execute(
                "UPDATE markets SET total_yes = total_yes + ? WHERE id=?",
                (amount, market_id)
            )
        else:
            conn.execute(
                "UPDATE markets SET total_no = total_no + ? WHERE id=?",
                (amount, market_id)
            )
        
        conn.commit()
        conn.close()
        
        self._log_utxo("bet", user_id, market_id, amount, outcome)
        return position_id, shares
    
    def resolve(self, market_id: str, outcome: str) -> Dict:
        """结算市场"""
        if outcome not in ["yes", "no"]:
            return {"error": "Invalid outcome"}
        
        conn = sqlite3.connect(self.db_path)
        
        # 更新市场状态
        conn.execute("""
            UPDATE markets 
            SET status = 'resolved', outcome = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (outcome, market_id))
        
        # 获取胜方池和负方池
        cur = conn.execute(
            "SELECT total_yes, total_no, fee_percent FROM markets WHERE id=?",
            (market_id,)
        )
        row = cur.fetchone()
        total_yes, total_no, fee_pct = row
        
        winner_pool = total_yes if outcome == "yes" else total_no
        loser_pool = total_no if outcome == "yes" else total_yes
        total_pool = winner_pool + loser_pool
        
        # 计算手续费
        fee = total_pool * (fee_pct / 100)
        distributable = total_pool - fee
        
        # 获取赢家持仓
        cur = conn.execute("""
            SELECT user_id, shares FROM positions 
            WHERE market_id = ? AND outcome = ?
        """, (market_id, outcome))
        
        winners = cur.fetchall()
        total_winner_shares = sum(w[1] for w in winners)
        
        # 分配奖励
        rewards = {}
        for user_id, shares in winners:
            reward = (shares / total_winner_shares) * distributable
            rewards[user_id] = reward
        
        conn.commit()
        conn.close()
        
        self._log_utxo("resolve", None, market_id, fee, outcome)
        
        return {
            "outcome": outcome,
            "total_pool": total_pool,
            "fee": fee,
            "distributable": distributable,
            "winners": len(winners),
            "rewards": rewards
        }
    
    def claim_reward(self, position_id: str) -> Tuple[bool, float]:
        """领取奖励"""
        conn = sqlite3.connect(self.db_path)
        
        # 获取持仓信息
        cur = conn.execute("""
            SELECT p.user_id, p.market_id, p.outcome, p.shares, m.outcome as market_outcome
            FROM positions p
            JOIN markets m ON p.market_id = m.id
            WHERE p.id = ?
        """, (position_id,))
        
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, 0
        
        user_id, market_id, outcome, shares, market_outcome = row
        
        if outcome != market_outcome:
            conn.close()
            return False, 0
        
        # 计算奖励（简化版）
        cur = conn.execute(
            "SELECT total_yes, total_no, fee_percent FROM markets WHERE id=?",
            (market_id,)
        )
        market_row = cur.fetchone()
        total_yes, total_no, fee_pct = market_row
        
        winner_pool = total_yes if outcome == "yes" else total_no
        loser_pool = total_no if outcome == "yes" else total_yes
        total_pool = winner_pool + loser_pool
        fee = total_pool * (fee_pct / 100)
        distributable = total_pool - fee
        
        # 删除持仓（已领取）
        conn.execute("DELETE FROM positions WHERE id=?", (position_id,))
        conn.commit()
        conn.close()
        
        # TODO: 实际奖励需要根据所有赢家shares比例计算
        reward = shares  # 简化
        
        self._log_utxo("claim", user_id, market_id, reward, outcome)
        return True, reward
    
    def get_markets(self, status: str = None) -> List[Dict]:
        """获取市场列表"""
        conn = sqlite3.connect(self.db_path)
        
        if status:
            cur = conn.execute(
                "SELECT * FROM markets WHERE status = ?", (status,)
            )
        else:
            cur = conn.execute("SELECT * FROM markets")
        
        rows = cur.fetchall()
        conn.close()
        
        return [{
            "id": r[0],
            "question": r[1],
            "category": r[2],
            "end_time": r[3],
            "status": r[4],
            "outcome": r[5],
            "total_yes": r[8],
            "total_no": r[9]
        } for r in rows]
    
    def _log_utxo(self, tx_type: str, user_id: str, 
                  market_id: str, amount: float, outcome: str):
        """记录UTXO日志"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO utxo_log (id, tx_type, user_id, market_id, amount, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), tx_type, user_id, market_id, amount, outcome))
        conn.commit()
        conn.close()

# 使用示例
if __name__ == "__main__":
    market = NayePredictionMarket()
    
    # 创建市场
    q = "那耶村2026年游客超过1万人？"
    market_id = market.create_market(q, "2026-12-31")
    print(f"市场创建: {market_id}")
    
    # 押注
    market.bet(market_id, "user_alice", "yes", 100)
    market.bet(market_id, "user_bob", "no", 50)
    market.bet(market_id, "user_charlie", "yes", 200)
    
    # 查看市场
    markets = market.get_markets("open")
    print(f"当前市场: {markets}")
    
    # 结算
    result = market.resolve(market_id, "yes")
    print(f"结算结果: {result}")
