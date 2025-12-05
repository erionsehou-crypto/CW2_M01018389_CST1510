import sqlite3

# -----------------------------------
#  Database Manager Class
# -----------------------------------
class DatabaseManager:
    def __init__(self, db_file="database.db"):
        """
        Simple wrapper around sqlite3 to manage the database connection.
        """
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None, fetchone=False, fetchall=False):
        """
        Execute a SQL query with optional parameters.
        Automatically commits changes.

        Returns:
            - one row (tuple) if fetchone=True
            - list of rows if fetchall=True
            - None otherwise
        """
        if params is None:
            params = ()

        self.cursor.execute(query, params)
        self.conn.commit()

        if fetchone:
            return self.cursor.fetchone()
        if fetchall:
            return self.cursor.fetchall()

        return None

    def close(self):
        """Close the database connection."""
        self.conn.close()

    # -----------------------------------
    #  Table creation
    # -----------------------------------
    def create_tables(self):
        """
        Create all required tables if they do not already exist:
        - users
        - cyber_incidents
        - datasets_metadata
        - it_tickets
        """

        # Users table (from Week 7 users.txt)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
            """
        )

        # Cybersecurity incidents
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS cyber_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                severity TEXT,
                response_time_hours REAL,
                status TEXT,
                reported_at TEXT
            );
            """
        )

        # Datasets metadata (Data Science)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                owner TEXT,
                size_mb REAL,
                department TEXT,
                created_at TEXT
            );
            """
        )

                # IT tickets table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS it_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                priority TEXT,
                description TEXT,
                status TEXT,
                assigned_to TEXT,
                created_at TEXT,
                resolution_time_hours REAL
            );
        """)


        print(" All tables created (users, cyber_incidents, datasets_metadata, it_tickets).")


# -----------------------------------
#  Quick test when running this file
# -----------------------------------
if __name__ == "__main__":
    db = DatabaseManager("database.db")
    db.create_tables()
    db.close()
