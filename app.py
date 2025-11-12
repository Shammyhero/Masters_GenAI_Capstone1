import streamlit as st
from agent import run_agent
import sqlite3
import pandas as pd
import json

# --- Streamlit setup ---
st.set_page_config(page_title="🚗 Data Insights App", page_icon="📊", layout="wide")

st.title("🚗 Car Sales Data Insights App")
st.caption("Ask questions about your car sales data or report an issue. Powered by OpenAI + SQLite.")

# --- Helper to get basic DB stats quickly ---
@st.cache_data
def get_db_stats():
    try:
        conn = sqlite3.connect("data_insights.db")
        df = pd.read_sql_query(
            """
            SELECT 
                COUNT(*) AS total_rows,
                ROUND(AVG("Price"), 2) AS avg_price,
                COUNT(DISTINCT "Car Make") AS unique_makes,
                MIN("YEAR") AS min_year,
                MAX("YEAR") AS max_year
            FROM car_sales;
            """, conn
        )
        conn.close()
        return int(df["total_rows"][0]), float(df["avg_price"][0]), int(df["unique_makes"][0]), int(df["min_year"][0]), int(df["max_year"][0])
    except Exception as e:
        return 0, 0.0, 0, 0, 0

total_rows, avg_price, makes, min_year, max_year = get_db_stats()

# --- Summary section ---
st.markdown(f"""
### 📊 Dataset Overview
- **Total records:** {total_rows:,}
- **Average price:** ${avg_price:,.2f}
- **Unique car makes(brands):** {makes}
- **Min year:** {min_year}
- **Max year:** {max_year}
""")

st.divider()

if "agent_response" not in st.session_state:
    st.session_state.agent_response = None

# --- Chat section ---
st.subheader("💬 Ask a question about the car sales data")

user_query = st.text_input(
    "Enter your question:",
    placeholder="e.g., What is the average price of electric cars?"
)


if st.button("Ask"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            st.session_state.agent_response = run_agent(user_query)
        st.success("Result:")
        
        # Try JSON → show dataframe
        try:
            parsed = json.loads(st.session_state.agent_response)
            if isinstance(parsed, list):
                st.dataframe(pd.DataFrame(parsed))
            else:
                st.write(st.session_state.agent_response)
        except:
            st.write(st.session_state.agent_response)
    else:
        st.warning("Please type a question first.")

st.divider()

# -----------------------
#  Support Ticket Section
# -----------------------

if st.session_state.agent_response:
    st.subheader("🚨 Not satisfied with the result?")
    st.write("Raise a support ticket and our developers will investigate.")

    issue_text = st.text_area("Describe the problem:", height=120)

    if st.button("Raise Ticket"):
        if issue_text.strip():
            with st.spinner("Sending to agent to create a ticket..."):
                agent_prompt = f"Create a support ticket with this issue: {issue_text}"
                ticket_response = run_agent(agent_prompt)
            st.success("Ticket Created:")
            st.write(ticket_response)
        else:
            st.warning("Please describe the issue before submitting.")
st.divider()

st.caption("Capstone Project by Shammy | Powered by OpenAI and Streamlit")