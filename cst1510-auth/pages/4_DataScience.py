import streamlit as st
import pandas as pd
import plotly.express as px

from models import DatasetMetadata
from load_data import load_datasets_metadata_from_csv

st.set_page_config(page_title="Data Science", page_icon="📊", layout="wide")

# Guard login
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in.")
    st.stop()

st.title("📊 Data Science Dataset Dashboard")
DatasetMetadata.ensure_table()

# ---- Load sample data ----
with st.expander("📥 Load sample data (CSV)", expanded=False):
    st.caption("Loads Data/datasets_metadata.csv into the database only if the table is empty.")
    if st.button("Load datasets_metadata.csv"):
        try:
            n = load_datasets_metadata_from_csv("Data/datasets_metadata.csv")
            if n == 0:
                st.info("No rows inserted (table already had data).")
            else:
                st.success(f"Inserted {n} datasets from CSV.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")

# ---- Fetch data ----
items = DatasetMetadata.get_all()
df = pd.DataFrame([i.__dict__ for i in items])

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)

total = len(df)
total_size = float(df["size_mb"].sum()) if not df.empty else 0.0
active = int((df["status"] == "Active").sum()) if not df.empty else 0
sensitive = int((df["sensitivity"].astype(str).str.lower().isin(["high", "confidential", "pii", "restricted"])).sum()) if not df.empty else 0

k1.metric("Total Datasets", total)
k2.metric("Total Size (MB)", round(total_size, 2))
k3.metric("Active", active)
k4.metric("High Sensitivity", sensitive)

st.divider()

# ---- Table ----
st.subheader("All Datasets")
if df.empty:
    st.info("No datasets yet. Load sample data or create a new dataset below.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ---- Create ----
st.subheader("Add New Dataset (Create)")
with st.form("new_dataset"):
    c1, c2, c3 = st.columns(3)
    with c1:
        dataset_name = st.text_input("Dataset Name")
        source = st.text_input("Source / Department")
    with c2:
        owner = st.text_input("Owner / Steward")
        sensitivity = st.selectbox("Sensitivity", ["Low", "Medium", "High", "Confidential"])
    with c3:
        rows = st.number_input("Rows", min_value=0, value=0, step=1000)
        size_mb = st.number_input("Size (MB)", min_value=0.0, value=0.0, step=10.0)

    status = st.selectbox("Status", ["Active", "Archived"])
    submit = st.form_submit_button("Create Dataset")

if submit:
    if not dataset_name.strip() or not source.strip() or not owner.strip():
        st.warning("Dataset Name, Source, and Owner are required.")
    else:
        DatasetMetadata.create(dataset_name, source, owner, int(rows), float(size_mb), sensitivity, status=status)
        st.success("Dataset created successfully.")
        st.rerun()

st.divider()

# ---- Update/Delete ----
st.subheader("Update / Delete Dataset")
if df.empty:
    st.info("No datasets to update/delete.")
else:
    ids = df["id"].tolist()
    selected_id = st.selectbox("Select Dataset ID", ids)

    item = DatasetMetadata.get_by_id(int(selected_id))
    if item is None:
        st.error("Dataset not found.")
    else:
        with st.form("update_dataset"):
            u1, u2, u3 = st.columns(3)
            with u1:
                u_name = st.text_input("Dataset Name", value=item.dataset_name)
                u_source = st.text_input("Source / Department", value=item.source)
            with u2:
                u_owner = st.text_input("Owner / Steward", value=item.owner)
                u_sens = st.selectbox("Sensitivity", ["Low", "Medium", "High", "Confidential"],
                                      index=["Low", "Medium", "High", "Confidential"].index(item.sensitivity)
                                      if item.sensitivity in ["Low", "Medium", "High", "Confidential"] else 0)
            with u3:
                u_rows = st.number_input("Rows", min_value=0, value=int(item.rows), step=1000)
                u_size = st.number_input("Size (MB)", min_value=0.0, value=float(item.size_mb), step=10.0)

            u_status = st.selectbox("Status", ["Active", "Archived"], index=0 if item.status == "Active" else 1)
            updated = st.form_submit_button("Update Dataset")

        if updated:
            if not u_name.strip() or not u_source.strip() or not u_owner.strip():
                st.warning("Dataset Name, Source, and Owner are required.")
            else:
                DatasetMetadata.update(int(selected_id), u_name, u_source, u_owner, int(u_rows), float(u_size), u_sens, u_status)
                st.success("Dataset updated.")
                st.rerun()

        st.markdown("### Delete")
        confirm = st.checkbox("I understand this will permanently delete the dataset.")
        if st.button("Delete Dataset", disabled=not confirm):
            DatasetMetadata.delete(int(selected_id))
            st.success("Dataset deleted.")
            st.rerun()

st.divider()

# ---- Insights / Visualizations ----
st.subheader("Insights & Visualizations")

if df.empty:
    st.info("No data for charts yet.")
else:
    left, right = st.columns(2)

    with left:
        st.markdown("#### Top Datasets by Size (MB)")
        top_size = df.sort_values("size_mb", ascending=False).head(10)
        fig1 = px.bar(top_size, x="dataset_name", y="size_mb", title="Top 10 Datasets by Size (MB)")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        st.markdown("#### Top Datasets by Rows")
        top_rows = df.sort_values("rows", ascending=False).head(10)
        fig2 = px.bar(top_rows, x="dataset_name", y="rows", title="Top 10 Datasets by Row Count")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Source Dependency (Datasets by Source)")
    by_source = df.groupby("source").size().reset_index(name="count").sort_values("count", ascending=False)
    fig3 = px.bar(by_source, x="source", y="count", title="Datasets by Source / Department")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Governance / Archiving Signal")
    # simple rule: large + low sensitivity -> candidates for archiving or tiered storage
    candidates = df[(df["size_mb"] > df["size_mb"].median()) & (df["sensitivity"].isin(["Low", "Medium"]))].copy()
    st.caption("Heuristic: large datasets with Low/Medium sensitivity may be candidates for tiered storage or archiving.")
    st.dataframe(candidates[["id", "dataset_name", "source", "owner", "size_mb", "sensitivity", "status"]].head(20),
                 use_container_width=True, hide_index=True)
