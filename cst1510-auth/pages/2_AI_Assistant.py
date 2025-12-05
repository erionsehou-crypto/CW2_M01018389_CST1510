# pages/2_AI_Assistant.py

import streamlit as st
import pandas as pd
from models import ITTicket, ensure_it_tickets_table
from ai_helper import ask_ai


# ---------- Streamlit Config ----------
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")


# ---------- Sidebar Logout Button ----------
with st.sidebar:
    st.markdown("---")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")


# ---------- Auth Guard ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must log in first.")
    st.stop()


# ---------- Title ----------
st.title("🤖 AI Assistant for IT Tickets")
st.write("Ask the AI anything about trends, risks or improvements.")


# ---------- Load Ticket Context ----------
ensure_it_tickets_table()
tickets = ITTicket.get_all()

if tickets:
    df = pd.DataFrame([t.to_dict() for t in tickets])

    context = f"There are {len(df)} tickets. "

    if "status" in df:
        context += f"Status counts: {df['status'].value_counts().to_dict()}. "

    if "priority" in df:
        context += f"Priority counts: {df['priority'].value_counts().to_dict()}. "
else:
    df = pd.DataFrame()
    context = "There are no tickets currently in the system."


# ---------- UI ----------
st.divider()

col1, col2 = st.columns([2, 3])

with col1:
    question = st.text_area(
        "Your question:",
        placeholder="Example: Why do we have so many high priority tickets?"
    )
    ask = st.button("Ask AI", use_container_width=True)

with col2:
    st.markdown("### AI Answer")
    answer_box = st.empty()

    if ask:
        if not question.strip():
            answer_box.warning("Please type a question first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    answer = ask_ai(question, context=context)
                    answer_box.success(answer)
                except Exception as e:
                    answer_box.error(str(e))

st.divider()
