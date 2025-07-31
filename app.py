import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# Page config
st.set_page_config(page_title="🌫️ Real-Time AQI Tracker", layout="wide")

# Inject custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title
st.title("🌫️ Real-Time Air Quality Index (AQI) - India")
st.markdown("This dashboard visualizes AQI trends using historical CPCB data from `city_day.csv`.")

# Load data
@st.cache_data

def load_data():
    df = pd.read_csv("city_day.csv")
    df.dropna(subset=["AQI", "City"], inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

if df.empty:
    st.error("Data not loaded. Check 'city_day.csv'.")
    st.stop()

# Sidebar - City and Date range
cities = sorted(df['City'].unique())
selected_city = st.sidebar.selectbox("🏙️ Choose a City", cities, index=cities.index("Delhi") if "Delhi" in cities else 0)

city_df = df[df['City'] == selected_city].copy()

start_date, end_date = st.sidebar.date_input("📆 Select Date Range", [city_df['Date'].min(), city_df['Date'].max()])
filtered_df = city_df[(city_df['Date'] >= pd.to_datetime(start_date)) & (city_df['Date'] <= pd.to_datetime(end_date))]

# AQI Category Function
def get_aqi_category(aqi):
    if aqi <= 50:
        return "🟢 Good"
    elif aqi <= 100:
        return "🟡 Moderate"
    elif aqi <= 200:
        return "🟠 Unhealthy for Sensitive"
    elif aqi <= 300:
        return "🔴 Unhealthy"
    elif aqi <= 400:
        return "🟣 Very Unhealthy"
    else:
        return "⚫ Hazardous"

# Latest AQI Display
latest_date = filtered_df['Date'].max()
latest_data = filtered_df[filtered_df['Date'] == latest_date]

if not latest_data.empty:
    latest_aqi = latest_data.iloc[0]['AQI']
    col1, col2 = st.columns([2, 3])
    col1.metric(label=f"Latest AQI in {selected_city} ({latest_date.date()})", value=int(latest_aqi))
    col1.markdown(f"**AQI Category:** {get_aqi_category(latest_aqi)}")
else:
    st.warning("No recent AQI data available.")

# KPIs
col1, col2, col3 = st.columns(3)
avg_aqi = filtered_df['AQI'].mean()
col1.metric("📊 Average AQI", f"{avg_aqi:.2f}")
col2.metric("📅 Total Days", len(filtered_df))
col3.metric("😷 Max AQI", int(filtered_df['AQI'].max()))

# Line Chart
st.subheader(f"📈 AQI Trend Over Time for {selected_city}")
fig_line = px.line(filtered_df, x="Date", y="AQI", markers=True, title="Daily AQI Over Time")
st.plotly_chart(fig_line, use_container_width=True)

# Heatmap
st.subheader("🌡️ Monthly AQI Heatmap")
heatmap_data = filtered_df.pivot_table(index=filtered_df["Date"].dt.month,
                                       columns=filtered_df["Date"].dt.day,
                                       values="AQI", aggfunc="mean")
fig, ax = plt.subplots(figsize=(16, 5))
sns.heatmap(heatmap_data, cmap="RdYlGn_r", linewidths=.5, ax=ax)
ax.set_title("Monthly AQI Heatmap")
st.pyplot(fig)

# Download button
st.download_button(
    label="⬇️ Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"AQI_{selected_city}.csv",
    mime='text/csv'
)

# Raw Data
with st.expander("📋 Show Raw Data Table"):
    st.dataframe(filtered_df.tail(100), use_container_width=True)

# AI-Powered Insight
if not filtered_df.empty:
    insights = f"Between {start_date} and {end_date}, the average AQI in {selected_city} was {avg_aqi:.1f}. The worst AQI was {int(filtered_df['AQI'].max())} on {filtered_df.loc[filtered_df['AQI'].idxmax()]['Date'].date()}."
    st.success(insights)
else:
    st.info("No data available for the selected range.")



