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


@dataclass
class SecurityIncident:
    id: Optional[int]
    incident_type: str
    severity: str
    description: str
    status: str
    detected_at: str
    resolved_at: Optional[str]
    analyst: Optional[str]

    @classmethod
    def ensure_table(cls):
        conn = get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cyber_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Open',
                    detected_at TEXT NOT NULL,
                    resolved_at TEXT,
                    analyst TEXT
                );
            """)
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def _dict_row_factory(cls, cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    @staticmethod
    def from_row(row):
        return SecurityIncident(
            id=row.get("id"),
            incident_type=row.get("incident_type") or "Other",
            severity=row.get("severity") or "Low",
            description=row.get("description") or "",
            status=row.get("status") or "Open",
            detected_at=row.get("detected_at") or "",
            resolved_at=row.get("resolved_at"),
            analyst=row.get("analyst"),
        )



    @classmethod
    def get_all(cls) -> List["SecurityIncident"]:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.row_factory = cls._dict_row_factory
            rows = conn.execute("SELECT * FROM cyber_incidents ORDER BY id DESC").fetchall()
            return [cls.from_row(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, incident_id: int) -> Optional["SecurityIncident"]:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.row_factory = cls._dict_row_factory
            row = conn.execute(
                "SELECT * FROM cyber_incidents WHERE id = ?",
                (incident_id,)
            ).fetchone()
            return cls.from_row(row) if row else None
        finally:
            conn.close()

    @classmethod
    def count(cls) -> int:
        cls.ensure_table()
        conn = get_connection()
        try:
            (n,) = conn.execute("SELECT COUNT(*) FROM cyber_incidents").fetchone()
            return int(n)
        finally:
            conn.close()

    @classmethod
    def create(cls, incident_type: str, severity: str, description: str, analyst: Optional[str] = None) -> "SecurityIncident":
        cls.ensure_table()
        ts = datetime.utcnow().isoformat(timespec="seconds")
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO cyber_incidents (incident_type, severity, description, status, detected_at, resolved_at, analyst)
                VALUES (?, ?, ?, 'Open', ?, NULL, ?)
            """, (incident_type, severity, description, ts, analyst))
            conn.commit()
            new_id = cur.lastrowid
            return cls(new_id, incident_type, severity, description, "Open", ts, None, analyst)
        finally:
            conn.close()

    @classmethod
    def update(
        cls,
        incident_id: int,
        incident_type: str,
        severity: str,
        description: str,
        status: str,
        analyst: Optional[str] = None
    ) -> None:
        cls.ensure_table()
        conn = get_connection()
        try:
            
            current = cls.get_by_id(incident_id)
            resolved_at = current.resolved_at if current else None

            if status == "Resolved" and not resolved_at:
                resolved_at = datetime.utcnow().isoformat(timespec="seconds")
            if status != "Resolved":
                resolved_at = None

            conn.execute("""
                UPDATE cyber_incidents
                SET incident_type = ?, severity = ?, description = ?, status = ?, resolved_at = ?, analyst = ?
                WHERE id = ?
            """, (incident_type, severity, description, status, resolved_at, analyst, incident_id))
            conn.commit()
        finally:
            conn.close()

    @classmethod
    def delete(cls, incident_id: int) -> None:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
            conn.commit()
        finally:
            conn.close()

@staticmethod
def from_row(row: Dict[str, Any]) -> "DatasetMetadata":
    def safe_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    def safe_float(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    return DatasetMetadata(
        id=row.get("id"),
        dataset_name=row.get("dataset_name"),
        source=row.get("source"),
        owner=row.get("owner"),
        rows=safe_int(row.get("rows")),
        size_mb=safe_float(row.get("size_mb")),
        sensitivity=row.get("sensitivity", "Low"),
        last_updated=row.get("last_updated"),
        status=row.get("status", "Active"),
    )


        
        
@dataclass
class DatasetMetadata:
    id: Optional[int]
    dataset_name: str
    source: str
    owner: str
    rows: int
    size_mb: float
    sensitivity: str
    last_updated: str
    status: str  # Active / Archived

    # ---------- TABLE ----------
    @classmethod
    def ensure_table(cls):
        conn = get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS datasets_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    size_mb REAL NOT NULL,
                    sensitivity TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active'
                );
            """)
            conn.commit()
        finally:
            conn.close()

    # ---------- ROW FACTORY ----------
    @classmethod
    def _dict_row_factory(cls, cursor, row):
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    # ---------- SAFE CAST HELPERS ----------
    @staticmethod
    def _safe_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_float(v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    # ---------- FROM ROW ----------
    @staticmethod
    def from_row(row: Dict[str, Any]) -> "DatasetMetadata":
        return DatasetMetadata(
            id=row.get("id"),
            dataset_name=row.get("dataset_name") or "Unnamed Dataset",
            source=row.get("source") or "Unknown",
            owner=row.get("owner") or "Unknown",
            rows=DatasetMetadata._safe_int(row.get("rows")),
            size_mb=DatasetMetadata._safe_float(row.get("size_mb")),
            sensitivity=row.get("sensitivity") or "Low",
            last_updated=row.get("last_updated") or "",
            status=row.get("status") or "Active",
        )

    # ---------- COUNT ----------
    @classmethod
    def count(cls) -> int:
        cls.ensure_table()
        conn = get_connection()
        try:
            (n,) = conn.execute("SELECT COUNT(*) FROM datasets_metadata").fetchone()
            return int(n)
        finally:
            conn.close()

    # ---------- READ ----------
    @classmethod
    def get_all(cls) -> List["DatasetMetadata"]:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.row_factory = cls._dict_row_factory
            rows = conn.execute(
                "SELECT * FROM datasets_metadata ORDER BY id DESC"
            ).fetchall()
            return [cls.from_row(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, dataset_id: int) -> Optional["DatasetMetadata"]:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.row_factory = cls._dict_row_factory
            row = conn.execute(
                "SELECT * FROM datasets_metadata WHERE id = ?",
                (dataset_id,)
            ).fetchone()
            return cls.from_row(row) if row else None
        finally:
            conn.close()

    # ---------- CREATE ----------
    @classmethod
    def create(
        cls,
        dataset_name: str,
        source: str,
        owner: str,
        rows: int,
        size_mb: float,
        sensitivity: str,
        status: str = "Active",
        last_updated: Optional[str] = None
    ) -> "DatasetMetadata":
        cls.ensure_table()
        ts = last_updated or datetime.utcnow().isoformat(timespec="seconds")

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO datasets_metadata
                (dataset_name, source, owner, rows, size_mb, sensitivity, last_updated, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset_name,
                source,
                owner,
                cls._safe_int(rows),
                cls._safe_float(size_mb),
                sensitivity,
                ts,
                status
            ))
            conn.commit()
            new_id = cur.lastrowid

            return cls(
                new_id,
                dataset_name,
                source,
                owner,
                cls._safe_int(rows),
                cls._safe_float(size_mb),
                sensitivity,
                ts,
                status
            )
        finally:
            conn.close()

    # ---------- UPDATE ----------
    @classmethod
    def update(
        cls,
        dataset_id: int,
        dataset_name: str,
        source: str,
        owner: str,
        rows: int,
        size_mb: float,
        sensitivity: str,
        status: str
    ) -> None:
        cls.ensure_table()
        ts = datetime.utcnow().isoformat(timespec="seconds")

        conn = get_connection()
        try:
            conn.execute("""
                UPDATE datasets_metadata
                SET dataset_name = ?,
                    source = ?,
                    owner = ?,
                    rows = ?,
                    size_mb = ?,
                    sensitivity = ?,
                    last_updated = ?,
                    status = ?
                WHERE id = ?
            """, (
                dataset_name,
                source,
                owner,
                cls._safe_int(rows),
                cls._safe_float(size_mb),
                sensitivity,
                ts,
                status,
                dataset_id
            ))
            conn.commit()
        finally:
            conn.close()

    # ---------- DELETE ----------
    @classmethod
    def delete(cls, dataset_id: int) -> None:
        cls.ensure_table()
        conn = get_connection()
        try:
            conn.execute(
                "DELETE FROM datasets_metadata WHERE id = ?",
                (dataset_id,)
            )
            conn.commit()
        finally:
            conn.close()