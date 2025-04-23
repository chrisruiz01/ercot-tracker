import streamlit as st
import pandas as pd 
import altair as alt
import os
from datetime import datetime
from src.mapping_loader import load_settlement_point_mapping

st.set_page_config(
    page_title="ERCOT Rolling LMP Tracker",
    layout="wide"
)

# Title & Branding
st.sidebar.image("static/logo.png", caption="ERCOT Tracker", use_container_width=True)
st.sidebar.caption("🔧 Built by Chris Ruiz")

st.title("⚡ ERCOT Rolling LMP Tracker")
st.caption("Updated daily from ERCOT settlement data. Select nodes to compare price trends and volatility.")

# Timestamp from CSV file modification
csv_path = "outputs/rolling_7_day_avg.csv"

try:
    last_modified = os.path.getmtime(csv_path)
    last_updated = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"📅 Data last updated: {last_updated}")
except FileNotFoundError:
    st.caption("⚠️ Data file not found - app is running without it.")

# Load and Clean Data
df = pd.read_csv(csv_path)
df = df.dropna(subset=["delivery_date"])
df["delivery_date"] = pd.to_datetime(df["delivery_date"])

# Load mapping
mapping = load_settlement_point_mapping("data/mapping/Settlement_Points.csv")
df = df.merge(mapping, on="settlement_point", how="left")


# Sidebar filters
st.sidebar.header("Select Settlement Points")
available_types = df["settlement_point_type"].dropna().unique()
selected_type = st.sidebar.selectbox("Settlement Point Type", sorted(available_types))
filtered_points = df[df["settlement_point_type"] == selected_type]["settlement_point"].unique()
selected_points = st.sidebar.multiselect(
    "Select Settlement Points", 
    sorted(filtered_points),
    default=sorted(filtered_points)[:5]
)

# Filter final dataset
filtered = df[df["settlement_point"].isin(selected_points)]

# Date slider filter
date_min = filtered["delivery_date"].min().to_pydatetime()
date_max = filtered["delivery_date"].max().to_pydatetime()
date_range = st.slider(
    "Select Date Range",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max)
)
filtered = filtered[
    (filtered["delivery_date"] >= pd.to_datetime(date_range[0])) &
    (filtered["delivery_date"] <= pd.to_datetime(date_range[1]))
]

# Latest data table
st.subheader("Latest Data")
display_df = filtered.sort_values("delivery_date", ascending=False).tail(25)
st.dataframe(display_df.style.format({
    "settlement_point_price": "{:.2f}",
    "rolling_7_day_avg": "{:.2f}"
}))

# Download Button
csv_download = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download CSV", csv_download, "ercot_rolling_avg.csv", "text/csv")

# Days shown summary
days_shown = (pd.to_datetime(date_range[1]) - pd.to_datetime(date_range[0])).days + 1
st.markdown(f"**Viewing {days_shown} days from** `{date_range[0].date()}` **to** `{date_range[1].date()}`")

#  Rolling Avg Chart
st.subheader("Rolling Average by Settlement Point")
st.caption("7-day average; number of days shown based on selected range.")
plot_data = filtered.groupby(
    ["delivery_date", "settlement_point", "settlement_point_type"]
)["rolling_7_day_avg"].mean().reset_index()

chart = alt.Chart(plot_data).mark_line(point=True).encode(
    x=alt.X("delivery_date:T", title="Date"),
    y=alt.Y("rolling_7_day_avg:Q", title="7-Day Rolling Avg"),
    color=alt.Color("settlement_point:N", title="Settlement Point"),
    strokeDash=alt.StrokeDash("settlement_point_type:N", title="Type"),
    tooltip=[
        "settlement_point:N",
        "settlement_point_type:N",
        "delivery_date:T",
        alt.Tooltip("rolling_7_day_avg:Q", format=".2f")
    ]
).properties(width=900, height=400).interactive()

# Display chart and save as PNG for external use
st.altair_chart(chart, use_container_width=True)
try:
    chart.save("outputs/rolling_avg_chart.png")
except Exception as e:
    st.warning(f"Could not save chart image: {e}")

# Volatility chart
st.subheader("Daily LMP Volatility by Settlement Point")
volatility = (
    filtered.groupby(["delivery_date", "settlement_point"])["settlement_point_price"]
    .std()
    .reset_index(name="daily_std")
)
vol_chart = alt.Chart(volatility).mark_line(point=True).encode(
    x=alt.X("delivery_date:T", title="Date"),
    y=alt.Y("daily_std:Q", title="Standard Deviation (Volatility)"),
    color=alt.Color("settlement_point:N", title="Settlement Point"),
    tooltip=["settlement_point", "delivery_date", alt.Tooltip("daily_std", format=".2f")]
).properties(width=900, height=400).interactive()

st.altair_chart(vol_chart, use_container_width=True)

# Footer with GitHub link
st.markdown("---")
st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-View%20Project-black?logo=github)](https://github.com/chrisruiz01/ercot-tracker)")