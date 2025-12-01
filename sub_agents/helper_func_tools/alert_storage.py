import sqlite3
from typing import List, Dict, Any

DB_NAME = "alerts.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            target REAL NOT NULL,
            direction TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()


def add_alert(token: str, target: float, direction: str, email: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO alerts (token, target, direction, email, status)
        VALUES (?, ?, ?, ?, 'active')
    """, (token.upper(), target, direction, email))
    conn.commit()
    conn.close()


def get_active_alerts() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, token, target, direction, email FROM alerts WHERE status='active'")
    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "token": r[1],
            "target": r[2],
            "direction": r[3],
            "email": r[4],
        } for r in rows
    ]


def cancel_alert(token: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE alerts SET status='cancelled' WHERE token=? AND status='active'", (token.upper(),))
    conn.commit()
    conn.close()


def mark_triggered(alert_id: int):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE alerts SET status='triggered' WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()


# Auto-init DB on import
init_db()
