# pages/1_Dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from models import ITTicket, ensure_it_tickets_table


# ---------- Streamlit Config ----------
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")


# ---------- Sidebar Logout Button ----------
with st.sidebar:
    st.markdown("---")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")


# ---------- Auth Guard ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.error("You must log in first.")
    st.stop()


# ---------- Page Title ----------
st.title("🧑‍💻 IT Tickets Dashboard")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")
st.divider()


# ---------- Load Tickets ----------
ensure_it_tickets_table()
tickets = ITTicket.get_all()
tickets_df = pd.DataFrame([t.to_dict() for t in tickets])


# ---------- No Data Case ----------
if tickets_df.empty:
    st.info("No tickets found. Create one using the form below.")
else:
    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tickets", len(tickets_df))
    col2.metric("Open Tickets", (tickets_df["status"] == "Open").sum())
    col3.metric("High Priority", (tickets_df["priority"] == "High").sum())

    st.divider()

    # Table
    st.subheader("All Tickets")
    st.dataframe(tickets_df, use_container_width=True)

    # Charts
    st.subheader("Tickets by Status")
    status_count = tickets_df["status"].value_counts().reset_index()
    status_count.columns = ["status", "count"]
    st.plotly_chart(px.bar(status_count, x="status", y="count"), use_container_width=True)

    st.subheader("Tickets by Priority")
    pr_count = tickets_df["priority"].value_counts().reset_index()
    pr_count.columns = ["priority", "count"]
    st.plotly_chart(px.pie(pr_count, names="priority", values="count"), use_container_width=True)


st.divider()


# ---------- Create Ticket ----------
st.subheader("Create New Ticket")
with st.form("create_ticket_form"):
    title = st.text_input("Title")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
    submitted = st.form_submit_button("Create")

    if submitted:
        if not title.strip():
            st.warning("Title cannot be empty.")
        else:
            new_ticket = ITTicket.create(title, priority, status)
            st.success(f"Ticket created (ID {new_ticket.id}).")
            st.rerun()

st.divider()


# ---------- Update Ticket ----------
st.subheader("Update an Existing Ticket")

if len(tickets) > 0:
    ticket_ids = [t.id for t in tickets]
    selected = st.selectbox("Select Ticket ID to update", ticket_ids, key="update_ticket_id")

    selected_ticket = ITTicket.get_by_id(int(selected))

    if selected_ticket:
        # Dynamic priority list (includes both default and existing values)
        base_priorities = ["Low", "Medium", "High"]
        priority_options = sorted(set(base_priorities + [t.priority for t in tickets]))

        if selected_ticket.priority not in priority_options:
            priority_options.append(selected_ticket.priority)

        new_priority = st.selectbox(
            "New Priority",
            priority_options,
            index=priority_options.index(selected_ticket.priority),
            key="update_priority",
        )

        # Dynamic status list (includes both default and existing values)
        base_statuses = ["Open", "In Progress", "Closed"]
        status_options = sorted(set(base_statuses + [t.status for t in tickets]))

        if selected_ticket.status not in status_options:
            status_options.append(selected_ticket.status)

        new_status = st.selectbox(
            "New Status",
            status_options,
            index=status_options.index(selected_ticket.status),
            key="update_status",
        )

        if st.button("Update Ticket"):
            selected_ticket.update(new_priority, new_status)
            st.success("Ticket updated successfully!")
            st.rerun()
else:
    st.info("No tickets to update.")


st.divider()

# ---------- Delete Ticket ----------
st.subheader("Delete Ticket")

if len(tickets) > 0:
    del_id = st.selectbox(
        "Select Ticket ID to delete",
        [t.id for t in tickets],
        key="delete_ticket_id",
    )

    confirm = st.checkbox(
        "I understand this action cannot be undone.",
        key="delete_confirm",
    )

    if st.button("Delete Ticket", key="delete_button"):
        if confirm:
            t = ITTicket.get_by_id(int(del_id))
            if t:
                t.delete()
                st.success(f"Ticket {del_id} deleted.")
                st.rerun()
        else:
            st.warning("You must confirm deletion.")
else:
    st.info("No tickets to delete.")

