#!/usr/bin/env python3
"""xmemory: Schema-Grounded Memory - arXiv 2604.27906"""

import sqlite3, json, os, uuid
from datetime import datetime
from typing import Optional, Dict, List, Tuple

ENTITY_TYPES = ["person", "project", "company", "event", "concept"]
RELATION_TYPES = ["owns", "works_for", "created", "member_of", "partner", 
                  "competitor", "depends_on", "related_to", "uses", "invested_in"]
CANNOT_INFER = ["private_key", "api_key", "password", "secret", 
                "wallet_address", "phone_number", "id_card", "bank_account"]

class XMemory:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.expanduser("~/.openclaw/workspace/memory/system/memory.db")
    
    def add_entity(self, etype, name, source, display_name=None, confidence=1.0):
        """添加实体"""
        if etype not in ENTITY_TYPES:
            return None, f"Invalid type: {etype}"
        
        eid = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""INSERT INTO entities 
                (id, type, name, display_name, confidence, source, verified)
                VALUES (?, ?, ?, ?, ?, ?, 0)""", 
                (eid, etype, name, display_name, confidence, source))
            conn.commit()
            self._log_write("insert", "entities", eid, "object_detection", True)
            return eid, "OK"
        except Exception as e:
            self._log_write("insert", "entities", eid, "object_detection", False)
            return None, str(e)
        finally:
            conn.close()
    
    def add_fact(self, entity_id, field, value, value_type, source, confidence=1.0, cannot_infer=False):
        """添加事实"""
        if field in CANNOT_INFER:
            return None, f"Cannot store: {field}"
        
        fid = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""INSERT INTO facts 
                (id, entity_id, field, value, value_type, confidence, source, cannot_infer, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (fid, entity_id, field, value, value_type, confidence, source, int(cannot_infer)))
            conn.commit()
            return fid, "OK"
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    def add_relation(self, from_e, to_e, rtype, source, strength=1.0):
        """添加关系"""
        if rtype not in RELATION_TYPES:
            return None, f"Invalid relation: {rtype}"
        
        rid = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""INSERT INTO relations 
                (id, from_entity, to_entity, relation_type, strength, source, verified)
                VALUES (?, ?, ?, ?, ?, ?, 0)""", 
                (rid, from_e, to_e, rtype, strength, source))
            conn.commit()
            return rid, "OK"
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    def get_entity(self, eid):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("SELECT * FROM entities WHERE id=?", (eid,))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "type": row[1], "name": row[2], 
                        "display_name": row[3], "source": row[8], "verified": row[9]}
            return None
        finally:
            conn.close()
    
    def get_facts(self, entity_id):
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("SELECT * FROM facts WHERE entity_id=?", (entity_id,))
            return [{"field": r[2], "value": r[3], "type": r[4], "source": r[8], 
                     "cannot_infer": bool(r[10])} for r in cur.fetchall()]
        finally:
            conn.close()
    
    def search(self, name=None, etype=None):
        conn = sqlite3.connect(self.db_path)
        try:
            sql = "SELECT id, type, name, source FROM entities WHERE 1=1"
            params = []
            if name:
                sql += " AND name LIKE ?"
                params.append(f"%{name}%")
            if etype:
                sql += " AND type=?"
                params.append(etype)
            cur = conn.execute(sql, params)
            return [{"id": r[0], "type": r[1], "name": r[2], "source": r[3]} for r in cur.fetchall()]
        finally:
            conn.close()
    
    def _log_write(self, op, table, rid, stage, passed):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""INSERT INTO write_log 
                (id, operation, table_name, record_id, validation_stage, passed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), op, table, rid, stage, int(passed), 
                 datetime.utcnow().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def sync_to_md(self, out_dir=None):
        out_dir = out_dir or os.path.expanduser("~/.openclaw/workspace/memory")
        os.makedirs(out_dir, exist_ok=True)
        
        for e in self.search():
            fname = f"{e['type']}_{e['name'].replace(' ', '_')}.md"
            facts = self.get_facts(e['id'])
            
            with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
                f.write(f"# {e['name']}\n\n")
                f.write(f"- Type: {e['type']}\n- Source: {e['source']}\n\n")
                if facts:
                    f.write("## Facts\n\n")
                    for fact in facts:
                        mark = " ⚠️" if fact['cannot_infer'] else ""
                        f.write(f"- {fact['field']}: {fact['value']}{mark}\n")
        
        print(f"Synced {len(self.search())} entities")

if __name__ == "__main__":
    import sys
    m = XMemory()
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "add_entity":
        eid, msg = m.add_entity(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"ID: {eid}, Msg: {msg}")
    elif cmd == "add_fact":
        fid, msg = m.add_fact(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print(f"ID: {fid}, Msg: {msg}")
    elif cmd == "search":
        print(json.dumps(m.search(sys.argv[2] if len(sys.argv)>2 else None), indent=2))
    elif cmd == "sync":
        m.sync_to_md()
    else:
        print("Commands: add_entity, add_fact, search, sync")
