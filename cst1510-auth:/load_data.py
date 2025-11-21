import os
import pandas as pd
from db_manager import DatabaseManager

# -----------------------------------
# Helper: base path for CSV files
# -----------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "Data")


# -----------------------------------
# Load cyber_incidents.csv
# -----------------------------------
def load_cyber_incidents(db: DatabaseManager) -> None:
    """
    Loads cyber_incidents.csv into the cyber_incidents table.
    CSV columns expected:
        incident_id, timestamp, severity, category, status, description
    Mapped to:
        incident_type  <- category
        severity       <- severity
        response_time_hours <- None (not provided in CSV)
        status         <- status
        reported_at    <- timestamp
    """
    path = os.path.join(DATA_DIR, "cyber_incidents.csv")

    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return

    print(f"\n[INFO] Loading cyber incidents from: {path}")
    df = pd.read_csv(path)

    # Clear table before loading new data
    db.execute("DELETE FROM cyber_incidents;")

    inserted = 0
    for _, row in df.iterrows():
        incident_type = row.get("category")
        severity = row.get("severity")
        response_time_hours = None  # Not available in CSV
        status = row.get("status")
        reported_at = row.get("timestamp")

        db.execute(
            """
            INSERT INTO cyber_incidents
            (incident_type, severity, response_time_hours, status, reported_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (incident_type, severity, response_time_hours, status, reported_at),
        )
        inserted += 1

    print(f"[OK] Inserted {inserted} cyber incidents.")


# -----------------------------------
# Load datasets_metadata.csv
# -----------------------------------
def load_datasets_metadata(db: DatabaseManager) -> None:
    """
    Loads datasets_metadata.csv into the datasets_metadata table.
    CSV columns expected:
        dataset_id, name, rows, columns, uploaded_by, upload_date
    Mapped to:
        dataset_name <- name
        owner        <- uploaded_by
        size_mb      <- None (not provided in CSV)
        department   <- None (not provided in CSV)
        created_at   <- upload_date
    """
    path = os.path.join(DATA_DIR, "datasets_metadata.csv")

    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return

    print(f"\n[INFO] Loading datasets metadata from: {path}")
    df = pd.read_csv(path)

    # Clear table before loading new data
    db.execute("DELETE FROM datasets_metadata;")

    inserted = 0
    for _, row in df.iterrows():
        dataset_name = row.get("name")
        owner = row.get("uploaded_by")
        size_mb = None       # Not available in CSV
        department = None    # Not available in CSV
        created_at = row.get("upload_date")

        db.execute(
            """
            INSERT INTO datasets_metadata
            (dataset_name, owner, size_mb, department, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (dataset_name, owner, size_mb, department, created_at),
        )
        inserted += 1

    print(f"[OK] Inserted {inserted} dataset metadata rows.")


# -----------------------------------
# Load it_tickets.csv
# -----------------------------------
def load_it_tickets(db: DatabaseManager):
    path = os.path.join(DATA_DIR, "it_tickets.csv")
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return

    print(f"\n[INFO] Loading IT tickets from: {path}")
    df = pd.read_csv(path)

    # clear existing data
    db.execute("DELETE FROM it_tickets;")

    for _, row in df.iterrows():
        ticket_id = row.get("ticket_id")
        priority = row.get("priority")
        description = row.get("description")
        status = row.get("status")
        assigned_to = row.get("assigned_to")
        created_at = row.get("created_at")
        resolution_time = row.get("resolution_time_hours")

        db.execute(
            """
            INSERT INTO it_tickets
            (ticket_id, priority, description, status, assigned_to, created_at, resolution_time_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                ticket_id,
                priority,
                description,
                status,
                assigned_to,
                created_at,
                resolution_time,
            ),
        )

    print(f"[OK] Inserted {len(df)} IT tickets.")



# -----------------------------------
# main()
# -----------------------------------
def main():
    db = DatabaseManager("database.db")
    print("\n[INFO] Starting CSV → SQLite data load...")

    try:
        load_cyber_incidents(db)
        load_datasets_metadata(db)
        load_it_tickets(db)
        print("\n All CSV data loaded successfully into SQLite!")
    finally:
        db.close()
        print("[INFO] Database connection closed.")


if __name__ == "__main__":
    main()
