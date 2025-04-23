# ⚡ ERCOT Rolling LMP Tracker

A Streamlit-based dashboard that visualizes **7-day rolling averages** and **daily LMP volatility** for ERCOT electricity prices by **settlement point type** (Hub, Load Zone, or Resource Node).

---

## 🔍 Features

- 📈 **Rolling 7-Day Averages**: Line chart grouped by settlement point with strokeDash for type clarity.
- 📉 **Daily LMP Volatility**: Standard deviation of prices, visualized by day.
- 🧭 **Smart Filters**:
  - Settlement Point Type → Points
  - Custom Date Range Slider
- 💾 **Data Export**:
  - Latest 25 records table with CSV download
  - Altair chart PNG output for sharing/reporting
- 🖼️ **Clean UI**: Responsive layout, color-coded trends, and GitHub badge link
- 🕒 **Live Timestamp**: Displays when data was last updated from CSV file

---

## 📷 Screenshot

![ERCOT Tracker Screenshot](outputs/rolling_avg_chart.png)

---

## 🚀 How to Run Locally

```bash
# Clone this repo
https://github.com/YOUR_USERNAME/ercot-tracker.git
cd ercot-tracker

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

---

## 📦 Project Structure

```
energy-market-tracker/
├── streamlit_app.py           # Main app
├── src/
│   └── mapping_loader.py      # Mapping logic for ERCOT types
├── scripts/
│   └── load_to_db.py          # Loads CSVs into Postgres
├── data/
│   └── mapping/               # ERCOT settlement point metadata
├── outputs/
│   └── rolling_7_day_avg.csv  # Cleaned + transformed data
├── static/
│   └── logo.png               # Dashboard logo
├── .streamlit/
│   └── config.toml            # Light theme config
└── requirements.txt
```

---

## 🛠 Built With

- Python
- Streamlit
- Altair
- Pandas
- PostgreSQL (optional for data loading)

---

## 👨‍💻 Author

**Chris Ruiz**  
🔧 Built with purpose — to explore, visualize, and share market-level insights from ERCOT data.

---

## 📁 License

MIT License (see `LICENSE` file if included)

