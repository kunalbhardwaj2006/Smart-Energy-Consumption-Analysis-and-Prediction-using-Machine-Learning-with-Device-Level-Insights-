# =========================================================
# SMART ENERGY STREAMLIT DASHBOARD
# =========================================================

import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests

st.set_page_config(
    page_title="Smart Energy Dashboard",
    layout="wide"
)

st.title("⚡ Smart Energy Consumption Dashboard")
st.markdown("End-to-End Energy Analysis & Prediction System")

# ---------------------------------------------------------
# LOAD DATA SAFELY (ABSOLUTE PATH)
# ---------------------------------------------------------

@st.cache_data
def load_data():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    data_path = os.path.join(project_root, "data", "household_power_consumption.txt")

    if not os.path.exists(data_path):
        st.error(f"Dataset not found at: {data_path}")
        st.stop()

    df = pd.read_csv(
        data_path,
        sep=";",
        na_values="?",
        low_memory=False
    )

    df["Datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True,
        errors="coerce"
    )

    df["Global_active_power"] = pd.to_numeric(
        df["Global_active_power"],
        errors="coerce"
    )

    df = df.dropna(subset=["Datetime", "Global_active_power"])
    df = df.set_index("Datetime")

    return df


df = load_data()

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------

st.sidebar.header("📊 Visualization Controls")

time_view = st.sidebar.selectbox(
    "Select Time Granularity",
    ["Hourly", "Daily", "Weekly"]
)

if time_view == "Hourly":
    data = df["Global_active_power"].resample("H").mean()
elif time_view == "Daily":
    data = df["Global_active_power"].resample("D").mean()
else:
    data = df["Global_active_power"].resample("W").mean()

# ---------------------------------------------------------
# PLOT
# ---------------------------------------------------------

st.subheader(f"{time_view} Energy Consumption Trend")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(data.index, data.values)
ax.set_xlabel("Time")
ax.set_ylabel("Global Active Power (kW)")
ax.set_title(f"{time_view} Consumption Trend")
plt.tight_layout()

st.pyplot(fig)

# ---------------------------------------------------------
# INSIGHTS
# ---------------------------------------------------------

st.markdown("## 💡 Energy Insights")

hourly_avg = df["Global_active_power"].resample("H").mean()
daily_avg = df["Global_active_power"].resample("D").mean()

peak_hour = hourly_avg.idxmax().hour
avg_daily = daily_avg.mean()
max_daily = daily_avg.max()

st.write(f"⚡ Peak usage occurs around **{peak_hour}:00 hours**.")
st.write("🔁 Shifting heavy appliance usage to off-peak hours reduces cost.")

if max_daily > avg_daily * 1.5:
    st.warning("🚨 Significant daily spikes detected.")

# ---------------------------------------------------------
# FLASK PREDICTION
# ---------------------------------------------------------

st.markdown("## 🔮 Future Forecast")

hours = st.number_input(
    "Hours to Forecast",
    min_value=1,
    max_value=168,
    value=24
)

if st.button("Predict Future Consumption"):

    try:
        response = requests.post(
            "http://127.0.0.1:5000/predict",
            json={"hours_ahead": int(hours)}
        )

        if response.status_code == 200:
            result = response.json()
            predictions = result["predictions"]

            st.success("Prediction received from backend ✅")
            st.line_chart(predictions)

        else:
            st.error("Backend error. Ensure Flask server is running.")

    except Exception as e:
        st.error(f"Connection failed: {e}")

st.markdown("---")
st.success("Dashboard Loaded Successfully 🚀")
