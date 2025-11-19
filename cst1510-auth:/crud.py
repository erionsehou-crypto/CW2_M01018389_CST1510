from db_manager import DatabaseManager

# -----------------------------------
#  CYBER INCIDENTS CRUD
# -----------------------------------
def create_cyber_incident(db: DatabaseManager):
    print("\n--- CREATE CYBER INCIDENT ---")
    incident_type = input("Incident type (e.g. phishing, malware): ").strip()
    severity = input("Severity (low/medium/high): ").strip()
    response_time = input("Response time in hours (number, empty if unknown): ").strip()
    status = input("Status (open/closed/investigating): ").strip()
    reported_at = input("Reported at (YYYY-MM-DD or text): ").strip()

    if response_time == "":
        response_time = None
    else:
        try:
            response_time = float(response_time)
        except ValueError:
            print("Invalid number for response time, setting to NULL.")
            response_time = None

    db.execute(
        """
        INSERT INTO cyber_incidents
        (incident_type, severity, response_time_hours, status, reported_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (incident_type, severity, response_time, status, reported_at),
    )
    print("✓ Cyber incident created!")


def list_cyber_incidents(db: DatabaseManager):
    print("\n--- LIST CYBER INCIDENTS ---")
    rows = db.execute(
        "SELECT id, incident_type, severity, response_time_hours, status, reported_at "
        "FROM cyber_incidents;",
        fetchall=True,
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
        (new_status, incident_id),
    )
    print("✓ Incident updated!")


def delete_cyber_incident(db: DatabaseManager):
    print("\n--- DELETE CYBER INCIDENT ---")
    list_cyber_incidents(db)
    incident_id = input("Enter ID of incident to delete: ").strip()
    if not incident_id:
        print("No ID provided.")
        return

    db.execute("DELETE FROM cyber_incidents WHERE id = ?;", (incident_id,))
    print("✓ Incident deleted!")


# -----------------------------------
#  DATASETS_METADATA CRUD
# -----------------------------------
def create_dataset(db: DatabaseManager):
    print("\n--- CREATE DATASET METADATA ---")
    name = input("Dataset name: ").strip()
    owner = input("Owner / uploaded by: ").strip()
    size_mb = input("Size in MB (number, empty if unknown): ").strip()
    department = input("Department (text, optional): ").strip()
    created_at = input("Created / uploaded at (YYYY-MM-DD or text): ").strip()

    if size_mb == "":
        size_value = None
    else:
        try:
            size_value = float(size_mb)
        except ValueError:
            print("Invalid number for size, setting to NULL.")
            size_value = None

    db.execute(
        """
        INSERT INTO datasets_metadata
        (dataset_name, owner, size_mb, department, created_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (name, owner, size_value, department, created_at),
    )
    print("✓ Dataset metadata created!")


def list_datasets(db: DatabaseManager):
    print("\n--- LIST DATASETS METADATA ---")
    rows = db.execute(
        "SELECT id, dataset_name, owner, size_mb, department, created_at "
        "FROM datasets_metadata;",
        fetchall=True,
    )
    if not rows:
        print("No datasets found.")
        return

    for row in rows:
        id_, name, owner, size_mb, dept, created_at = row
        print(f"[{id_}] {name} | owner: {owner} | size: {size_mb} MB | {dept} | {created_at}")


def update_dataset(db: DatabaseManager):
    print("\n--- UPDATE DATASET METADATA ---")
    list_datasets(db)
    dataset_id = input("Enter ID of dataset to update: ").strip()
    if not dataset_id:
        print("No ID provided.")
        return

    new_owner = input("New owner (leave empty to keep current): ").strip()
    new_dept = input("New department (leave empty to keep current): ").strip()

    if new_owner:
        db.execute("UPDATE datasets_metadata SET owner = ? WHERE id = ?;", (new_owner, dataset_id))
    if new_dept:
        db.execute("UPDATE datasets_metadata SET department = ? WHERE id = ?;", (new_dept, dataset_id))

    print("✓ Dataset metadata updated!")


def delete_dataset(db: DatabaseManager):
    print("\n--- DELETE DATASET METADATA ---")
    list_datasets(db)
    dataset_id = input("Enter ID of dataset to delete: ").strip()
    if not dataset_id:
        print("No ID provided.")
        return

    db.execute("DELETE FROM datasets_metadata WHERE id = ?;", (dataset_id,))
    print("✓ Dataset deleted!")


# -----------------------------------
#  IT_TICKETS CRUD
# -----------------------------------
def create_ticket(db: DatabaseManager):
    print("\n--- CREATE IT TICKET ---")
    ticket_number = input("Ticket number (string or ID): ").strip()
    issue_type = input("Issue description / type: ").strip()
    severity = input("Priority (low/medium/high, or number): ").strip()
    assigned_to = input("Assigned to: ").strip()
    opened_at = input("Opened at (YYYY-MM-DD or text): ").strip()
    status = input("Status (open/in progress/resolved/closed): ").strip()

    db.execute(
        """
        INSERT INTO it_tickets
        (ticket_number, issue_type, severity, assigned_to, opened_at, status)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (ticket_number, issue_type, severity, assigned_to, opened_at, status),
    )
    print("✓ IT ticket created!")


def list_tickets(db: DatabaseManager):
    print("\n--- LIST IT TICKETS ---")
    rows = db.execute(
        "SELECT id, ticket_number, issue_type, severity, assigned_to, opened_at, status "
        "FROM it_tickets;",
        fetchall=True,
    )
    if not rows:
        print("No IT tickets found.")
        return

    for row in rows:
        id_, number, issue, sev, assigned, opened_at, status = row
        print(f"[{id_}] #{number} | {issue} | {sev} | {assigned} | {opened_at} | {status}")


def update_ticket(db: DatabaseManager):
    print("\n--- UPDATE IT TICKET ---")
    list_tickets(db)
    ticket_id = input("Enter ID of ticket to update: ").strip()
    if not ticket_id:
        print("No ID provided.")
        return

    new_status = input("New status: ").strip()
    db.execute(
        "UPDATE it_tickets SET status = ? WHERE id = ?;",
        (new_status, ticket_id),
    )
    print("✓ Ticket updated!")


def delete_ticket(db: DatabaseManager):
    print("\n--- DELETE IT TICKET ---")
    list_tickets(db)
    ticket_id = input("Enter ID of ticket to delete: ").strip()
    if not ticket_id:
        print("No ID provided.")
        return

    db.execute("DELETE FROM it_tickets WHERE id = ?;", (ticket_id,))
    print("✓ Ticket deleted!")


# -----------------------------------
#  MAIN MENU
# -----------------------------------
def display_menu():
    print("\n" + "=" * 60)
    print("   MULTI-DOMAIN INTELLIGENCE PLATFORM - CRUD")
    print("=" * 60)
    print("CYBER INCIDENTS")
    print("[ 1] Create cyber incident")
    print("[ 2] List cyber incidents")
    print("[ 3] Update cyber incident status")
    print("[ 4] Delete cyber incident")
    print("-" * 60)
    print("DATASETS METADATA")
    print("[ 5] Create dataset metadata")
    print("[ 6] List datasets")
    print("[ 7] Update dataset (owner/department)")
    print("[ 8] Delete dataset")
    print("-" * 60)
    print("IT TICKETS")
    print("[ 9] Create IT ticket")
    print("[10] List IT tickets")
    print("[11] Update IT ticket status")
    print("[12] Delete IT ticket")
    print("-" * 60)
    print("[13] Exit")
    print("-" * 60)


def main():
    db = DatabaseManager("database.db")
    print("\nConnected to SQLite database for CRUD operations.")

    try:
        while True:
            display_menu()
            choice = input("Select an option (1-13): ").strip()

            # Cyber incidents
            if choice == "1":
                create_cyber_incident(db)
            elif choice == "2":
                list_cyber_incidents(db)
            elif choice == "3":
                update_cyber_incident(db)
            elif choice == "4":
                delete_cyber_incident(db)

            # Datasets
            elif choice == "5":
                create_dataset(db)
            elif choice == "6":
                list_datasets(db)
            elif choice == "7":
                update_dataset(db)
            elif choice == "8":
                delete_dataset(db)

            # IT tickets
            elif choice == "9":
                create_ticket(db)
            elif choice == "10":
                list_tickets(db)
            elif choice == "11":
                update_ticket(db)
            elif choice == "12":
                delete_ticket(db)

            elif choice == "13":
                print("Exiting CRUD menu...")
                break
            else:
                print("Invalid option. Please choose 1–13.")
    finally:
        db.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()
