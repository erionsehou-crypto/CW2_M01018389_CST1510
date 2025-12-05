# models.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import sqlite3

DB_PATH = "database.db"


# ---------- Database connection ----------

def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_it_tickets_table() -> None:
    """
    Ensure that the it_tickets table exists AND that it has the columns
    title and created_date, even if the database is from the old schema
    (with description / created_at).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # If the table does not exist at all, create it with the new schema
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                priority TEXT,
                status TEXT,
                created_date TEXT
            )
            """
        )

        # Check which columns the table already has
        cur.execute("PRAGMA table_info(it_tickets)")
        rows = cur.fetchall()
        col_names = [r["name"] if isinstance(r, sqlite3.Row) else r[1] for r in rows]

        # If the 'title' column is missing, add it
        if "title" not in col_names:
            cur.execute("ALTER TABLE it_tickets ADD COLUMN title TEXT")

        # If the 'created_date' column is missing, add it
        if "created_date" not in col_names:
            cur.execute("ALTER TABLE it_tickets ADD COLUMN created_date TEXT")

        # Optional: populate the new columns from the old ones
        # so that old tickets still look correct
        cur.execute("PRAGMA table_info(it_tickets)")
        col_names = [r["name"] if isinstance(r, sqlite3.Row) else r[1] for r in cur.fetchall()]

        if "description" in col_names:
            cur.execute(
                """
                UPDATE it_tickets
                SET title = description
                WHERE (title IS NULL OR title = '')
                  AND description IS NOT NULL
                """
            )

        if "created_at" in col_names:
            cur.execute(
                """
                UPDATE it_tickets
                SET created_date = created_at
                WHERE (created_date IS NULL OR created_date = '')
                  AND created_at IS NOT NULL
                """
            )

        conn.commit()
    finally:
        conn.close()


# ---------- Entity classes ----------

@dataclass
class User:
    """Represents an authenticated user."""
    id: Optional[int]
    username: str
    password_hash: str


@dataclass
class ITTicket:
    """Represents an IT support ticket."""
    id: Optional[int]
    title: str
    priority: str
    status: str
    created_date: str

    # ---------- Factory / query methods ----------

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ITTicket":
        """Create an ITTicket instance from a SQLite row (old or new schema)."""
        keys = row.keys() if hasattr(row, "keys") else []

        def get(col: str, default=None):
            return row[col] if col in keys else default

        ticket_id = get("id") or get("ticket_id")

        title = (
            get("title")
            or get("description")
            or f"Ticket {ticket_id} problem description"
        )

        created = (
            get("created_date")
            or get("created_at")
            or get("created")
            or datetime.utcnow().isoformat(timespec="seconds")
        )

        priority = get("priority", "Unknown")
        status = get("status", "Unknown")

        return cls(
            id=get("id"),
            title=title,
            priority=priority,
            status=status,
            created_date=created,
        )

    @classmethod
    def get_all(cls) -> List["ITTicket"]:
        """Return all IT tickets from the database."""
        ensure_it_tickets_table()
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM it_tickets").fetchall()
            return [cls.from_row(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, ticket_id: int) -> Optional["ITTicket"]:
        """Return a single ticket by id."""
        ensure_it_tickets_table()
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM it_tickets WHERE id = ?", (ticket_id,)
            ).fetchone()
            return cls.from_row(row) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, title: str, priority: str, status: str) -> "ITTicket":
        """Create a new ticket and store it in the database."""
        ensure_it_tickets_table()
        created = datetime.utcnow().isoformat(timespec="seconds")

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO it_tickets (title, priority, status, created_date)
                VALUES (?, ?, ?, ?)
                """,
                (title, priority, status, created),
            )
            conn.commit()
            new_id = cur.lastrowid
        finally:
            conn.close()

        return cls(
            id=new_id,
            title=title,
            priority=priority,
            status=status,
            created_date=created,
        )

    # ---------- Instance methods ----------

    def update(self, priority: str, status: str) -> None:
        """Update this ticket in the database."""
        if self.id is None:
            raise ValueError("Cannot update ticket without id.")

        ensure_it_tickets_table()
        conn = get_connection()
        try:
            conn.execute(
                """
                UPDATE it_tickets
                SET priority = ?, status = ?
                WHERE id = ?
                """,
                (priority, status, self.id),
            )
            conn.commit()
        finally:
            conn.close()

        self.priority = priority
        self.status = status

    def delete(self) -> None:
        """Delete this ticket from the database."""
        if self.id is None:
            raise ValueError("Cannot delete ticket without id.")

        ensure_it_tickets_table()
        conn = get_connection()
        try:
            conn.execute("DELETE FROM it_tickets WHERE id = ?", (self.id,))
            conn.commit()
        finally:
            conn.close()

    # ---------- Helper ----------

    def to_dict(self) -> dict:
        """Return a plain dict representation of the ticket."""
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "created_date": self.created_date,
        }
