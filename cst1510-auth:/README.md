# Multi-Domain Intilligenge Platform - Week 8
## Data Pipeline,Database Migration & Full CRUD (SQlite)

This project implements a full pipeline using **SQlite**, inluding:
- Database schema design  
- Migration of existing users  
- CSV → SQLite data loading  
- Full CRUD operations for all three domains:
  - Cyber Incidents
  - Datasets Metadata
  - IT Tickets

This work follows the Week 8 requirements of CST1510.

---

## 📁 Project Structure

cst1510-auth/
│
├── auth.py              # Authentication system from Week 7 (used for user migration)
├── db_manager.py        # Creates all SQLite tables for Week 8
├── migrate_users.py     # Migrates Week 7 users.txt → SQLite users table
├── load_data.py         # Loads CSV data from /Data into SQLite (Week 8)
├── crud.py              # Full CRUD menu for all 3 domains
├── database.db          # SQLite database
│
├── Data/
│   ├── cyber_incidents.csv
│   ├── datasets_metadata.csv
│   ├── it_tickets.csv
│
└── README.md


## Setup Instructions

### Install dependencies

pip install bcrypt pandas 

(Optional) If using a virtual environment:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


---

##  Step 1 — Create All Tables
This script creates all four database tables:

users

cyber_incidents

datasets_metadata

it_tickets

Run:

python3 db_manager.py

Expected output:

All tables created (users,cyber_incidents,datasets_metadata,it_tickets).

---

##  Step 2 — Migrate Users from Week 7
This loads users from `users.txt` into the new SQLite table:

python3 migrate_users.py

---

##  Step 3 — Load CSV Data into SQLite
Loads all CSV files from `/Data`:

python3 load_data.py

Expected:
- 115 cyber incidents inserted  
- 5 dataset metadata rows inserted  
- 150 IT tickets inserted  

---

##  Step 4 — Run CRUD Menu  
This program provides full CRUD operations for **all three domains**.

python3 crud.py

You will see:
Connected to SQLite database for CRUD operations.
==================================================
MULTI-DOMAIN INTELLIGENCE PLATFORM – CRUD

CYBER INCIDENTS
[1] Create cyber incident
[2] List cyber incidents
[3] Update cyber incident status
[4] Delete cyber incident
--------------------------------------------------

DATASETS METADATA
[5] Create dataset metadata
[6] List datasets
[7] Update dataset (owner/department)
[8] Delete dataset
--------------------------------------------------

IT TICKETS
[9]  Create IT ticket
[10] List IT tickets
[11] Update IT ticket status
[12] Delete IT ticket
--------------------------------------------------

[13] Exit
==================================================


## Database Schema Overview

The database **database.db** contains:

### ✔ users  
- id  
- username  
- password_hash  

### ✔ cyber_incidents  
- id  
- incident_type  
- severity  
- response_time_hours  
- status  
- reported_at  

### ✔ datasets_metadata  
- id  
- dataset_name  
- owner  
- size_mb  
- department  
- created_at  

### ✔ it_tickets  
- id  
- ticket_id  
- priority  
- description  
- status  
- assigned_to  
- created_at  
- resolution_time_hours  

---

## 🎉 Completion

This submission includes:

✔ Full SQLite schema  
✔ User migration from Week 7  
✔ CSV → SQLite data import  
✔ CRUD for all 3 domains  
✔ Command-line interface  
✔ Clean project structure  
✔ README (this file)










