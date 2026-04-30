import json
import time
from app.database import get_db_connection

def save_test(user_id: int, component: str, input_data: dict, risk_score: float, risk_level: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO test_history (user_id, component, input_data, risk_score, risk_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, component, json.dumps(input_data), float(risk_score), risk_level, int(time.time()*1000)))
    conn.commit()
    test_id = int(cur.lastrowid)
    conn.close()
    return test_id

def get_history(user_id: int):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT test_id, component, input_data, risk_score, risk_level, created_at
        FROM test_history WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [{"test_id": r["test_id"], "component": r["component"], "input_data": json.loads(r["input_data"]), "risk_score": r["risk_score"], "risk_level": r["risk_level"], "created_at": r["created_at"]} for r in rows]


def delete_test(user_id: int, test_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM test_history
        WHERE test_id = ? AND user_id = ?
    """, (test_id, user_id))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def delete_all_history(user_id: int) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM test_history
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    deleted_count = cur.rowcount
    conn.close()
    return deleted_count