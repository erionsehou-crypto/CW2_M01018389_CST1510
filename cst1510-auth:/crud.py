from db_manager import DatabaseManager

# -----------------------------------
#  CYBER INCIDENTS CRUD
# -----------------------------------

def create_cyber_incident(db: DatabaseManager):
    print("\n--- CREATE CYBER INCIDENT ---")
    incident_type = input("Incident type (e.g. phishing, malware): ").strip()
    severity = input("Severity (low/medium/high): ").strip()
    response_time = input("Response time in hours (number): ").strip()
    status = input("Status (open/closed/investigating): ").strip()
    reported_at = input("Reported at (YYYY-MM-DD or text): ").strip()

    if not response_time:
        response_time = None
    else:
        response_time = float(response_time)

    db.execute(
        """
        INSERT INTO cyber_incidents (incident_type, severity, response_time_hours, status, reported_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (incident_type, severity, response_time, status, reported_at)
    )
    print(" Cyber incident created!")


def list_cyber_incidents(db: DatabaseManager):
    print("\n--- LIST CYBER INCIDENTS ---")
    rows = db.execute(
        "SELECT id, incident_type, severity, response_time_hours, status, reported_at FROM cyber_incidents;",
        fetchall=True
    )
    if not rows:
        print("No cyber incidents found.")
        return

    for row in rows:
        id_, incident_type, severity, resp, status, reported_at = row
        print(f"[{id_}] {incident_type} | {severity} | {resp}h | {status} | {reported_at}")


def update_cyber_incident(db: DatabaseManager):
    print("\n--- UPDATE CYBER INCIDENT ---")
    list_cyber_incidents(db)
    incident_id = input("Enter ID of incident to update: ").strip()
    if not incident_id:
        print("No ID provided.")
        return

    new_status = input("New status: ").strip()
    db.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?;",
        (new_status, incident_id)
    )
    print(" Incident updated!")


def delete_cyber_incident(db: DatabaseManager):
    print("\n--- DELETE CYBER INCIDENT ---")
    list_cyber_incidents(db)
    incident_id = input("Enter ID of incident to delete: ").strip()
    if not incident_id:
        print("No ID provided.")
        return

    db.execute("DELETE FROM cyber_incidents WHERE id = ?;", (incident_id,))
    print(" Incident deleted!")


# -----------------------------------
#  MAIN MENU
# -----------------------------------

def display_menu():
    print("\n" + "=" * 50)
    print("   MULTI-DOMAIN INTELLIGENCE PLATFORM - CRUD")
    print("=" * 50)
    print("[1] Create cyber incident")
    print("[2] List cyber incidents")
    print("[3] Update cyber incident status")
    print("[4] Delete cyber incident")
    print("[5] Exit")
    print("-" * 50)


def main():
    db = DatabaseManager("database.db")
    print("\nConnected to SQLite database for CRUD operations.")

    try:
        while True:
            display_menu()
            choice = input("Select an option (1-5): ").strip()

            if choice == "1":
                create_cyber_incident(db)
            elif choice == "2":
                list_cyber_incidents(db)
            elif choice == "3":
                update_cyber_incident(db)
            elif choice == "4":
                delete_cyber_incident(db)
            elif choice == "5":
                print("Exiting CRUD menu...")
                break
            else:
                print("Invalid option. Please choose 1–5.")
    finally:
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
