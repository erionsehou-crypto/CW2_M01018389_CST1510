Multi-Domain Intelligence Platform
Streamlit Application with Authentication, IT Ticket Dashboard & AI Assistant

This project is a multi-page Streamlit web application developed as part of CST1510 – Programming for Data Communication and Networks.
It includes secure authentication, a full CRUD dashboard for IT tickets, data visualisation, an OOP refactor, and an AI assistant powered by OpenAI’s API.

🚀 Features Overview
🔐 1. User Authentication

User registration and login

Password hashing using bcrypt

Session management with st.session_state

Secure login required before accessing dashboards

Authentication logic and user storage handled in auth_db.py (SQLite)

📊 2. IT Tickets Dashboard (CRUD + Analytics)

Create, read, update and delete IT support tickets

Full OOP implementation using the ITTicket class (models.py)

SQLite used as the persistent database (database.db)

KPIs: total tickets, open tickets, high-priority tickets

Interactive charts created using Plotly:

Bar chart: Tickets by Status

Pie chart: Tickets by Priority

Dynamic table view of all tickets

🤖 3. AI Assistant for IT Tickets

A dedicated page where users can ask questions about ticket trends, risks or recommendations

The AI assistant uses summarised context extracted from stored tickets

Integrated with the OpenAI API (GPT models)

Uses the OPENAI_API_KEY environment variable (no API key is stored inside the code)

Friendly error messages for missing/invalid keys or insufficient quota

🧱 4. Object-Oriented Refactor (Week 11 Requirement)

All ticket database logic is encapsulated in the OOP-based ITTicket class:

The class provides:

get_all()

get_by_id()

create()

update()

delete()

to_dict()

from_row()

This removes raw SQL from the Streamlit UI pages, ensuring clean separation between UI, logic, and database operations.

📁 Project Structure
/project-root
│
├── Home.py                 # Main entry point (login/register)
├── auth_db.py              # Authentication system (SQLite + bcrypt)
├── models.py               # OOP model for ITTicket + DB methods
├── ai_helper.py            # OpenAI wrapper for AI Assistant page
├── README.md
├── requirements.txt
│
├── pages/
│   ├── 1_Dashboard.py      # CRUD + charts
│   └── 2_AI_Assistant.py   # AI ticket assistant
│
└── Data/
    ├── it_tickets.csv
    ├── datasets_metadata.csv
    └── cyber_incidents.csv

🧠 UML Class Diagram (Week 11 Requirement)
classDiagram
    class ITTicket {
        +id: int
        +title: str
        +priority: str
        +status: str
        +created_date: str
        ---
        +get_all()
        +get_by_id(id)
        +create(title, priority, status)
        +update(priority, status)
        +delete()
        +to_dict()
        +from_row(row)
    }

    class User {
        +id: int
        +username: str
        +password_hash: str
    }

    ITTicket --> "stored in" SQLite
    User --> "stored in" SQLite

🔧 Installation Guide
1️ Install dependencies
pip install -r requirements.txt

2️ Set OpenAI API Key

The app expects the key in the OPENAI_API_KEY environment variable.

Mac / Linux:

export OPENAI_API_KEY="your_key_here"


Windows (PowerShell):

setx OPENAI_API_KEY "your_key_here"


Restart PowerShell after using setx so the variable loads.

3️ Run the application
streamlit run Home.py


Open the URL shown in the terminal (usually:
http://localhost:8501
)