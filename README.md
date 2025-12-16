Multi-Domain Intelligence Platform
Streamlit Application with Authentication, Multi-Domain Dashboards & AI Assistant

This project is a multi-page Streamlit web application developed as part of CST1510 – Programming for Data Communication and Networks.
It includes secure authentication, three complete operational domains (IT Operations, Cybersecurity, Data Science), full CRUD dashboards with analytics, an object-oriented refactor, and an AI assistant powered by OpenAI’s API.

🚀 Features Overview
🔐 1. User Authentication

User registration and login

Password hashing using bcrypt

Session management with st.session_state

Secure login required before accessing dashboards

Authentication logic and user storage handled in auth_db.py (SQLite)

📊 2. IT Operations Dashboard (IT Tickets)

Create, read, update and delete IT support tickets (Full CRUD)

Full OOP implementation using the ITTicket class (models.py)

SQLite used as the persistent database (database.db)

KPIs: total tickets, open tickets, high-priority tickets

Interactive charts created using Plotly:

Bar chart: Tickets by Status

Pie chart: Tickets by Priority

Dynamic table view of all tickets

🛡️ 3. Cybersecurity Dashboard (Incidents)

Full CRUD management of cybersecurity incidents

OOP implementation using the SecurityIncident class (models.py)

KPIs such as total incidents, open vs resolved incidents, and phishing count

Visual analytics using Plotly:

Incidents by Severity

Incidents by Type

Supports loading sample data from Data/cyber_incidents.csv

📈 4. Data Science Dashboard (Datasets Metadata)

Full CRUD management of dataset metadata

OOP implementation using the DatasetMetadata class (models.py)

KPIs including:

Total datasets

Total dataset size (MB)

Active datasets

High-sensitivity datasets

Visualisations using Plotly:

Top datasets by size (MB)

Top datasets by row count

Source dependency (datasets by department/source)

Governance / archiving signal table

Supports loading sample data from Data/datasets_metadata.csv

🤖 5. AI Assistant

Dedicated page where users can ask questions about stored operational data

Integrated with the OpenAI API (GPT models)

Uses the OPENAI_API_KEY environment variable

No API keys are stored in the repository

Friendly error handling for missing or invalid API keys and quota limits

🧱 6. Object-Oriented Refactor (Week 11 Requirement)

All database logic is encapsulated in OOP model classes defined in models.py, including:

ITTicket

SecurityIncident

DatasetMetadata

Each class provides methods such as:

get_all(), get_by_id()

create(), update(), delete()

from_row() with safe data handling

This design removes raw SQL from Streamlit UI pages and ensures clear separation between UI, logic, and database layers.

📁 Project Structure
cst1510-auth/
│
├── Home.py                  # Main entry point (login/register)
├── auth_db.py               # Authentication system (SQLite + bcrypt)
├── db_manager.py            # Database connection helper
├── models.py                # OOP models (ITTicket, SecurityIncident, DatasetMetadata)
├── ai_helper.py             # OpenAI wrapper for AI Assistant
├── database.db              # SQLite database (local)
├── requirements.txt
│
├── assets/
│   └── home_hero.jpg        # Home page hero image
│
├── pages/
│   ├── 1_Dashboard.py       # IT Operations dashboard
│   ├── 2_AI_Assistant.py    # AI Assistant
│   ├── 3_Cybersecurity.py   # Cybersecurity dashboard
│   └── 4_DataScience.py     # Data Science dashboard
│
└── Data/
    ├── it_tickets.csv
    ├── cyber_incidents.csv
    └── datasets_metadata.csv

🧠 UML Class Diagram (Mermaid)
classDiagram
    class ITTicket
    class SecurityIncident
    class DatasetMetadata
    class User

    ITTicket --> SQLite
    SecurityIncident --> SQLite
    DatasetMetadata --> SQLite
    User --> SQLite

🔧 Installation Guide
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Set OpenAI API Key

The AI Assistant requires an API key set as an environment variable.

Mac / Linux

export OPENAI_API_KEY="your_key_here"


Windows (PowerShell)

setx OPENAI_API_KEY "your_key_here"


Restart the terminal after setting the variable.

3️⃣ Run the application
streamlit run Home.py


Open the URL shown in the terminal (usually http://localhost:8501).

✅ Notes

No API keys or secrets are stored in the repository

Database and virtual environment files are excluded via .gitignore

The application satisfies Tier 3 (Multi-Domain Intelligence Platform) requirements