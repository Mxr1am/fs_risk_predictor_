import time
import sqlite3
from typing import Optional

from app.database import get_db_connection
from app.utils.security import generate_salt, get_hash, generate_session_token

def create_account(user: dict) -> int:
    salt = generate_salt()
    password_hash = get_hash(user["password"], salt)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users
            (team_name, team_leader_name, car_type, email, password, salt, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user["team_name"], user["team_leader_name"], user["car_type"], user["email"], password_hash, salt.hex(), int(time.time()*1000)))
        conn.commit()
        return int(cur.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise ValueError("team name or email already in use") from exc
    finally:
        conn.close()

def authenticate_user(team_name: str, password: str) -> Optional[int]:
    conn = get_db_connection()
    row = conn.execute("SELECT user_id, password, salt FROM users WHERE team_name = ?", (team_name,)).fetchone()
    conn.close()
    if row is None:
        return None
    salt = bytes.fromhex(row["salt"] or "")
    return int(row["user_id"]) if row["password"] == get_hash(password, salt) else None

def get_token(user_id: int) -> Optional[str]:
    conn = get_db_connection()
    row = conn.execute("SELECT session_token FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row["session_token"] if row and row["session_token"] else None

def set_token(user_id: int) -> str:
    token = generate_session_token()
    conn = get_db_connection()
    conn.execute("UPDATE users SET session_token = ? WHERE user_id = ?", (token, user_id))
    conn.commit()
    conn.close()
    return token

def get_user_from_token(token: str | None) -> Optional[dict]:
    if not token:
        return None
    conn = get_db_connection()
    row = conn.execute("""
        SELECT user_id, team_name, team_leader_name, car_type, email
        FROM users WHERE session_token = ?
    """, (token,)).fetchone()
    conn.close()
    return dict(row) if row else None

def remove_token(token: str) -> None:
    conn = get_db_connection()
    conn.execute("UPDATE users SET session_token = NULL WHERE session_token = ?", (token,))
    conn.commit()
    conn.close()

def update_profile(user_id: int, updates: dict) -> dict:
    allowed_fields = ["team_leader_name", "email"]
    clean_updates = {
        key: value for key, value in updates.items()
        if key in allowed_fields and value is not None
    }

    if not clean_updates:
        raise ValueError("no profile fields supplied")

    set_clause = ", ".join([f"{key} = ?" for key in clean_updates.keys()])
    values = list(clean_updates.values())
    values.append(user_id)

    conn = get_db_connection()
    try:
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?",
            values
        )
        conn.commit()

        row = conn.execute("""
            SELECT user_id, team_name, team_leader_name, car_type, email
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        if row is None:
            raise ValueError("user not found")

        return dict(row)

    except sqlite3.IntegrityError as exc:
        raise ValueError("email already in use") from exc

    finally:
        conn.close()