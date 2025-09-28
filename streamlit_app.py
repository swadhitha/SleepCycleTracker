import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Sleep Cycle Tracker", layout="wide")

st.title("🛌 Sleep Cycle Tracker (Simulation)")
st.caption("Generate sleep data, view insights, and ask for advice with RAG.")

# Sidebar configuration
st.sidebar.header("Backend Settings")
backend_url = st.sidebar.text_input("FastAPI URL", BACKEND_URL)

# Sleep Data Input Section
st.header("1) Generate Sleep Data")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    days = st.number_input("Days to simulate", min_value=1, max_value=60, value=7, step=1)
with col2:
    mode = st.selectbox("Bedtime Mode", ["Random", "Time Range"]) 
with col3:
    seed = st.number_input("Seed (optional)", min_value=0, value=0, step=1)
    seed_value = int(seed) if seed != 0 else None

start_range = None
if mode == "Time Range":
    c1, c2 = st.columns(2)
    with c1:
        start = st.time_input("Earliest bedtime", value=pd.to_datetime("22:00").time())
    with c2:
        end = st.time_input("Latest bedtime", value=pd.to_datetime("00:30").time())
    start_range = {"start": start.strftime("%H:%M"), "end": end.strftime("%H:%M")}

if st.button("Generate Sleep Data", type="primary"):
    payload = {"days": int(days)}
    if seed_value is not None:
        payload["seed"] = seed_value
    if start_range:
        payload["start_time_range"] = start_range

    with st.spinner("Generating sleep data..."):
        try:
            resp = requests.post(f"{backend_url}/generate-sleep-data", json=payload, timeout=30)
            resp.raise_for_status()
            st.session_state["sleep_data"] = resp.json()["sleep_data"]
            st.success("Sleep data generated!")
        except Exception as e:
            st.error(f"Failed to generate: {e}")

# Sleep Summary Section
st.header("2) Sleep Summary & Visuals")
if "sleep_data" in st.session_state and st.session_state["sleep_data"]:
    df = pd.DataFrame(st.session_state["sleep_data"])  # date, start_time, wake_time, duration_hours, mood
    st.dataframe(df, use_container_width=True)

    with st.spinner("Fetching summary..."):
        try:
            sresp = requests.get(f"{backend_url}/get-sleep-summary", timeout=30)
            sresp.raise_for_status()
            summary = sresp.json()["summary"]
        except Exception as e:
            st.error(f"Failed to get summary: {e}")
            summary = None

    if summary:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Hours", f"{summary['total_hours']}")
        m2.metric("Average Duration", f"{summary['average_duration']} h")
        m3.metric("Min Duration", f"{summary['min_duration']} h")
        m4.metric("Max Duration", f"{summary['max_duration']} h")
        st.caption(f"Duration-Mood Corr: {summary['duration_mood_correlation']:.2f}  |  Trend: {summary['duration_trend']}")

        # Charts
        df_plot = df.copy()
        df_plot["date"] = pd.to_datetime(df_plot["date"]) 
        fig1 = px.line(df_plot, x="date", y="duration_hours", markers=True, title="Sleep Duration Over Time (h)")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(df_plot, x="date", y="mood", title="Mood (1-5)")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No data yet. Generate sleep data above.")

# Sleep Advice Section
st.header("3) Sleep Advice (RAG)")
user_q = st.text_input("Ask a sleep-related question")
if st.button("Get Advice"):
    if not user_q.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving advice..."):
            try:
                aresp = requests.post(f"{backend_url}/query-advice", json={"question": user_q}, timeout=30)
                aresp.raise_for_status()
                data = aresp.json()
                st.subheader("Advice")
                st.write(data.get("answer", ""))
                with st.expander("Sources"):
                    st.json(data.get("sources", []))
            except Exception as e:
                st.error(f"Failed to get advice: {e}")

st.divider()
with st.expander("LangChain Workflow Hints"):
    st.markdown(
        "- The backend structures prompts and retrieved tips.\n"
        "- If your question is vague, try adding timing, duration, or constraints.\n"
        "- The system uses vector search plus fuzzy matching for robust retrieval."
    )
