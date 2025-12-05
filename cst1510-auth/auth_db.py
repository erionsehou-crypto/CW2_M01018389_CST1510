import sqlite3
import bcrypt

DB_PATH = "database.db"   

def get_conn():
    return sqlite3.connect(DB_PATH)

def user_exists(username: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = ?;", (username,))
        return cur.fetchone() is not None

def register_user(username: str, plain_password: str) -> None:
    # hash με bcrypt
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?);",
            (username, hashed),
        )
        conn.commit()

def verify_user(username: str, plain_password: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT password_hash FROM users WHERE username = ?;",
            (username,),
        )
        row = cur.fetchone()

    if not row:
        return False

    stored_hash = row[0].encode("utf-8")
    return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash)
