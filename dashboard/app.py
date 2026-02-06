import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Energy Dashboard",
    layout="wide"
)

st.title("⚡ Smart Energy Consumption Dashboard")
st.markdown(
    "Visual analysis of household energy consumption with actionable insights."
)

# -------------------------------------------------
# Data loading (cached)
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/household_power_consumption.txt",
        sep=";",
        na_values="?"
    )

    # Combine Date and Time into Datetime
    df["Datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True,
        errors="coerce"
    )

    # Convert power to numeric
    df["Global_active_power"] = pd.to_numeric(
        df["Global_active_power"],
        errors="coerce"
    )

    # Drop invalid rows
    df = df.dropna(subset=["Datetime", "Global_active_power"])

    # Set datetime index (CRITICAL)
    df = df.set_index("Datetime")

    return df


df = load_data()

# -------------------------------------------------
# Sidebar controls
# -------------------------------------------------
st.sidebar.header("📊 View Options")

time_view = st.sidebar.selectbox(
    "Select Time Granularity",
    ["Hourly", "Daily", "Weekly"]
)

# -------------------------------------------------
# Resampling logic (SAFE & CLEAN)
# -------------------------------------------------
# -------------------------------------------------
# Insights section (data-driven)
# -------------------------------------------------
st.markdown("## 💡 Energy-Saving Insights")

peak_hour = df["Global_active_power"].resample("h").mean().idxmax().hour
avg_daily = df["Global_active_power"].resample("D").mean().mean()
max_daily = df["Global_active_power"].resample("D").mean().max()

st.write(f"⚡ Peak energy usage occurs around **{peak_hour}:00 hours**.")
st.write("🔁 Consider shifting heavy appliance usage to off-peak hours.")

if max_daily > avg_daily * 1.5:
    st.write("🚨 Sudden high daily consumption detected — inefficient appliances may be present.")

st.write("📊 Weekly trend analysis helps identify abnormal consumption spikes.")

# -------------------------------------------------
# Resampling logic (MUST COME BEFORE PLOT)
# -------------------------------------------------
data = df["Global_active_power"].resample("h").mean()

# -------------------------------------------------
# Plot
# -------------------------------------------------
st.subheader(f"Energy Consumption ({time_view})")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(data.index, data.values, linewidth=1)
ax.set_xlabel("Time")
ax.set_ylabel("Global Active Power (kW)")
ax.set_title(f"{time_view} Energy Consumption Trend")
plt.tight_layout()

st.pyplot(fig)

# -------------------------------------------------
# Insights section
# -------------------------------------------------
st.markdown("## 💡 Energy-Saving Insights")

st.markdown(
    """
- Peak consumption often occurs during **evening hours**
- Shifting appliance usage to **off-peak hours** can reduce energy cost
- Consistently high daily usage may indicate **inefficient appliances**
- Weekly trend analysis helps detect **abnormal spikes**
"""
)

st.success("Dashboard loaded successfully 🚀")
@st.cache_data
def load_data():
    df = pd.read_csv(
        "../data/household_power_consumption.txt",
        sep=";",
        na_values="?"
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
