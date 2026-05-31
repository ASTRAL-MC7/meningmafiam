import sqlite3
import os

DB_PATH = "mafia_users.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, user_id: int):
        self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )
        self.conn.commit()

    def user_count(self) -> int:
        cur = self.conn.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

    def all_users(self) -> list:
        cur = self.conn.execute("SELECT user_id FROM users")
        return [row[0] for row in cur.fetchall()]

db = Database()
