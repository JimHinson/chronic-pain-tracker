# 🩺 Chronic Pain Tracker

A personal web application for logging chronic pain entries and identifying trends, built with **Python** and **Streamlit**.

---

## Features

| Feature | Details |
|---|---|
| **Log Entry** | Record pain location, level (0–10), timestamp, and free-text notes |
| **Dashboard** | Summary metrics, filterable entry table, and CSV export |
| **Trends** | Interactive Plotly charts: pain over time, average by location, daily heatmap |
| **Local Storage** | Data is stored in a local SQLite database – nothing is sent to any server |
| **Expandable Schema** | Database columns reserved for weather, activity, and diet data |

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone https://github.com/JimHinson/chronic-pain-tracker.git
cd chronic-pain-tracker
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Project Structure

```
chronic-pain-tracker/
├── app.py              # Streamlit front-end (all pages)
├── database.py         # SQLite persistence layer
├── requirements.txt    # Python dependencies
└── README.md
```

The SQLite database file (`pain_tracker.db`) is created automatically on first run and is excluded from version control via `.gitignore` so your personal health data stays private.

---

## Roadmap / Future Enhancements

- 🌦️ **Weather Integration** – auto-fetch temperature & humidity via a weather API
- 🏃 **Activity Log** – record exercise type and intensity alongside pain data
- 🥗 **Diet Notes** – log meals to correlate food choices with pain levels
- 📊 **Correlation Analysis** – statistical correlation between lifestyle factors and pain
- 📱 **Mobile-Responsive UI** – larger inputs optimised for phone use

The database schema already includes placeholder columns for all of these features.

---

## Exporting Data

On the **Dashboard** page, click **⬇️ Download All Entries as CSV** to export your full pain log as a CSV file you can open in Excel or share with a healthcare provider.

---

## Tech Stack

- [Streamlit](https://streamlit.io/) – web UI
- [Pandas](https://pandas.pydata.org/) – data manipulation
- [Plotly Express](https://plotly.com/python/plotly-express/) – interactive charts
- [SQLite](https://www.sqlite.org/) – local database (via Python `sqlite3` stdlib)