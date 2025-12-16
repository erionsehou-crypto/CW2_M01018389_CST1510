import streamlit as st
import pandas as pd
import plotly.express as px

from models import SecurityIncident
from load_data import load_cyber_incidents_from_csv

st.set_page_config(page_title="Cybersecurity Incidents", page_icon="🛡️", layout="wide")

# Guard login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in.")
    st.stop()

st.title("🛡️ Cybersecurity Incident Dashboard")
SecurityIncident.ensure_table()

# ---- Load sample data ----
with st.expander("📥 Load sample data (CSV)", expanded=False):
    st.caption("Loads Data/cyber_incidents.csv into the database only if the table is empty.")
    if st.button("Load cyber_incidents.csv"):
        try:
            n = load_cyber_incidents_from_csv("Data/cyber_incidents.csv")
            if n == 0:
                st.info("No rows inserted (table already had data).")
            else:
                st.success(f"Inserted {n} incidents from CSV.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")

# ---- Fetch data ----
incidents = SecurityIncident.get_all()
df = pd.DataFrame([i.__dict__ for i in incidents])

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)

total = len(df)
open_count = int((df["status"] == "Open").sum()) if not df.empty else 0
resolved_count = int((df["status"] == "Resolved").sum()) if not df.empty else 0
phishing_count = int((df["incident_type"] == "Phishing").sum()) if not df.empty else 0

k1.metric("Total Incidents", total)
k2.metric("Open", open_count)
k3.metric("Resolved", resolved_count)
k4.metric("Phishing", phishing_count)

st.divider()

# ---- Table ----
st.subheader("All Cybersecurity Incidents")
if df.empty:
    st.info("No incidents yet. Load sample data or create a new incident below.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ---- Create ----
st.subheader("Report New Incident (Create)")
with st.form("new_incident"):
    c1, c2, c3 = st.columns(3)
    with c1:
        incident_type = st.selectbox("Incident Type", ["Malware", "Phishing", "DoS Attack", "Insider Threat", "Other"])
    with c2:
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    with c3:
        analyst = st.text_input("Assigned Analyst (optional)")

    description = st.text_area("Description")
    submit = st.form_submit_button("Create Incident")

if submit:
    if not description.strip():
        st.warning("Description cannot be empty.")
    else:
        SecurityIncident.create(incident_type, severity, description, analyst if analyst.strip() else None)
        st.success("Incident created successfully.")
        st.rerun()

st.divider()

# ---- Update/Delete ----
st.subheader("Update / Delete Incident")
if df.empty:
    st.info("No incidents to update/delete.")
else:
    ids = df["id"].tolist()
    selected_id = st.selectbox("Select Incident ID", ids)

    incident = SecurityIncident.get_by_id(int(selected_id))
    if incident is None:
        st.error("Incident not found.")
    else:
        with st.form("update_incident"):
            u1, u2, u3 = st.columns(3)
            with u1:
                u_type = st.selectbox(
                    "Incident Type",
                    ["Malware", "Phishing", "DoS Attack", "Insider Threat", "Other"],
                    index=["Malware", "Phishing", "DoS Attack", "Insider Threat", "Other"].index(incident.incident_type)
                    if incident.incident_type in ["Malware", "Phishing", "DoS Attack", "Insider Threat", "Other"] else 4
                )
            with u2:
                u_sev = st.selectbox(
                    "Severity",
                    ["Low", "Medium", "High", "Critical"],
                    index=["Low", "Medium", "High", "Critical"].index(incident.severity)
                    if incident.severity in ["Low", "Medium", "High", "Critical"] else 0
                )
            with u3:
                u_status = st.selectbox(
                    "Status",
                    ["Open", "Resolved"],
                    index=0 if incident.status == "Open" else 1
                )

            u_analyst = st.text_input("Assigned Analyst (optional)", value=incident.analyst or "")
            u_desc = st.text_area("Description", value=incident.description)

            updated = st.form_submit_button("Update Incident")

        if updated:
            if not u_desc.strip():
                st.warning("Description cannot be empty.")
            else:
                SecurityIncident.update(
                    incident_id=int(selected_id),
                    incident_type=u_type,
                    severity=u_sev,
                    description=u_desc,
                    status=u_status,
                    analyst=u_analyst.strip() if u_analyst.strip() else None
                )
                st.success("Incident updated.")
                st.rerun()

        st.markdown("### Delete")
        confirm = st.checkbox("I understand this will permanently delete the incident.")
        if st.button("Delete Incident", disabled=not confirm):
            SecurityIncident.delete(int(selected_id))
            st.success("Incident deleted.")
            st.rerun()

st.divider()

# ---- Insights / Charts (Tier 2 high-value) ----
st.subheader("Insights & Visualizations")

if df.empty:
    st.info("No data for charts yet.")
else:
    # Parse timestamps safely
    df2 = df.copy()
    df2["detected_at_dt"] = pd.to_datetime(df2["detected_at"], errors="coerce")
    df2["resolved_at_dt"] = pd.to_datetime(df2["resolved_at"], errors="coerce")

    # Resolution time in minutes (bottleneck)
    df2["resolution_minutes"] = (df2["resolved_at_dt"] - df2["detected_at_dt"]).dt.total_seconds() / 60
    # Keep only resolved with valid times
    resolved_df = df2[(df2["status"] == "Resolved") & (df2["resolution_minutes"].notna()) & (df2["resolution_minutes"] >= 0)]

    left, right = st.columns(2)

    with left:
        st.markdown("#### Incidents by Severity")
        fig1 = px.bar(df2, x="severity", title="Severity Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        st.markdown("#### Incidents by Type")
        fig2 = px.pie(df2, names="incident_type", title="Incident Types")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Phishing Trend (Spike Detection)")
    # Group by day for trend
    trend = df2.dropna(subset=["detected_at_dt"]).copy()
    trend["day"] = trend["detected_at_dt"].dt.date
    phishing_trend = trend[trend["incident_type"] == "Phishing"].groupby("day").size().reset_index(name="count")
    if phishing_trend.empty:
        st.info("No phishing incidents yet to show a trend.")
    else:
        fig3 = px.line(phishing_trend, x="day", y="count", title="Phishing Incidents Over Time (Daily)")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Response Bottleneck (Avg Resolution Time)")
    if resolved_df.empty:
        st.info("No resolved incidents yet to calculate resolution time bottlenecks.")
    else:
        bottleneck = resolved_df.groupby("incident_type")["resolution_minutes"].mean().reset_index()
        fig4 = px.bar(bottleneck, x="incident_type", y="resolution_minutes",
                      title="Average Resolution Time by Incident Type (minutes)")
        st.plotly_chart(fig4, use_container_width=True)
