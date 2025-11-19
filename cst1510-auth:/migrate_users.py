from db_manager import DatabaseManager

def migrate_users():
    db = DatabaseManager("database.db")

    print("Starting migration from users.txt  SQLite users table...")

    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                username, password_hash = line.split(",")

                # Insert into SQLite
                db.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash)
                )
                print(f"Inserted user → {username}")

        print("Migration completed successfully!")

    except FileNotFoundError:
        print("ERROR: users.txt not found. Run Week 7 first.")

    db.close()


if __name__ == "__main__":
    migrate_users()
