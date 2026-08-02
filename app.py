"""
app.py – Chronic Pain Tracker
A Streamlit web application for logging and visualising chronic pain data.
"""

import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import database as db

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Pain Tracker",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Bootstrap the database ────────────────────────────────────────────────────

db.init_db()

# ── Constants ─────────────────────────────────────────────────────────────────

PAIN_LOCATIONS = [
    "Neck",
    "Back (Upper)",
    "Back (Lower / Lumbar)",
    "Radiating Down Leg",
    "Shoulder",
    "Hip",
    "Other",
]

PAIN_LEVEL_LABELS = {
    0: "0 – No Pain",
    1: "1 – Minimal",
    2: "2 – Mild",
    3: "3 – Uncomfortable",
    4: "4 – Moderate",
    5: "5 – Distracting",
    6: "6 – Distressing",
    7: "7 – Severe",
    8: "8 – Intense",
    9: "9 – Excruciating",
    10: "10 – Worst Possible",
}

# ── Sidebar – navigation ──────────────────────────────────────────────────────

st.sidebar.title("🩺 Pain Tracker")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["📝 Log Entry", "📊 Dashboard", "📈 Trends"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Your data is stored locally in `pain_tracker.db`. "
    "No data is sent to any server."
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _pain_level_color(level: int) -> str:
    """Return a hex colour that grades from green (0) → yellow (5) → red (10)."""
    if level <= 3:
        return "#2ecc71"
    if level <= 6:
        return "#f39c12"
    return "#e74c3c"


def _df_from_entries(entries: list[dict]) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame(
            columns=["id", "timestamp", "pain_location", "pain_level", "notes"]
        )
    df = pd.DataFrame(entries)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ── Page: Log Entry ───────────────────────────────────────────────────────────

if page == "📝 Log Entry":
    st.title("📝 Log a Pain Entry")
    st.markdown("Fill in the form below and press **Save Entry** to record your pain.")

    with st.form("pain_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            pain_location = st.selectbox(
                "📍 Pain Location",
                PAIN_LOCATIONS,
                help="Where is the pain located?",
            )

        with col2:
            use_now = st.checkbox("Use current time", value=True)
            if use_now:
                entry_dt = datetime.now()
                st.info(f"Timestamp: **{entry_dt.strftime('%Y-%m-%d %H:%M')}**")
            else:
                entry_date = st.date_input("Date", value=datetime.today())
                entry_time = st.time_input("Time", value=datetime.now().time())
                entry_dt = datetime.combine(entry_date, entry_time)

        pain_level = st.slider(
            "🔢 Pain Level",
            min_value=0,
            max_value=10,
            value=5,
            step=1,
            help="0 = No pain, 10 = Worst imaginable pain",
        )

        level_label = PAIN_LEVEL_LABELS.get(pain_level, str(pain_level))
        color = _pain_level_color(pain_level)
        st.markdown(
            f"<h3 style='color:{color}; margin-top:0'>Pain Level: {level_label}</h3>",
            unsafe_allow_html=True,
        )

        notes = st.text_area(
            "📝 Notes",
            placeholder="Describe the pain, triggers, activities, how you're feeling…",
            height=120,
        )

        submitted = st.form_submit_button(
            "💾 Save Entry",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        ts = entry_dt.strftime("%Y-%m-%d %H:%M:%S")
        db.add_entry(
            timestamp=ts,
            pain_location=pain_location,
            pain_level=pain_level,
            notes=notes,
        )
        st.success(
            f"✅ Entry saved! **{pain_location}** – Level **{pain_level}** at {ts}"
        )
        st.balloons()

# ── Page: Dashboard ───────────────────────────────────────────────────────────

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    all_entries = db.get_all_entries()
    df_all = _df_from_entries(all_entries)

    if df_all.empty:
        st.info("No entries yet. Head over to **📝 Log Entry** to add your first record.")
        st.stop()

    # ── Summary metrics ──────────────────────────────────────────────────────
    st.subheader("Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Entries", len(df_all))
    m2.metric("Average Pain Level", f"{df_all['pain_level'].mean():.1f}")
    m3.metric("Highest Pain Level", int(df_all["pain_level"].max()))
    m4.metric("Most Common Location", df_all["pain_location"].mode()[0])

    st.markdown("---")

    # ── Filters ──────────────────────────────────────────────────────────────
    st.subheader("Recent Entries")
    col_filter1, col_filter2 = st.columns([2, 1])
    with col_filter1:
        location_filter = st.multiselect(
            "Filter by location",
            options=df_all["pain_location"].unique().tolist(),
            default=[],
            placeholder="All locations",
        )
    with col_filter2:
        show_n = st.selectbox("Show last N entries", [10, 25, 50, 100, "All"], index=0)

    df_view = df_all.copy()
    if location_filter:
        df_view = df_view[df_view["pain_location"].isin(location_filter)]

    # Newest first for the table
    df_view = df_view.sort_values("timestamp", ascending=False)
    if show_n != "All":
        df_view = df_view.head(int(show_n))

    display_df = df_view[["timestamp", "pain_location", "pain_level", "notes"]].copy()
    display_df.columns = ["Timestamp", "Location", "Pain Level", "Notes"]
    display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Export ───────────────────────────────────────────────────────────────
    st.subheader("📤 Export Data")
    export_df = df_all[["timestamp", "pain_location", "pain_level", "notes"]].copy()
    export_df.columns = ["Timestamp", "Location", "Pain Level", "Notes"]
    export_df["Timestamp"] = export_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="⬇️ Download All Entries as CSV",
        data=csv_bytes,
        file_name=f"pain_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ── Delete entry ─────────────────────────────────────────────────────────
    with st.expander("🗑️ Delete an Entry"):
        st.warning("Select an entry ID to permanently delete it.")
        recent_ids = df_all.sort_values("timestamp", ascending=False).head(50)
        id_options = recent_ids["id"].tolist()
        if id_options:
            del_id = st.selectbox("Entry ID to delete", id_options)
            if st.button("Delete", type="secondary"):
                db.delete_entry(del_id)
                st.success(f"Entry {del_id} deleted.")
                st.rerun()

# ── Page: Trends ─────────────────────────────────────────────────────────────

elif page == "📈 Trends":
    st.title("📈 Pain Trends")

    all_entries = db.get_all_entries()
    df = _df_from_entries(all_entries)

    if df.empty:
        st.info("No entries yet. Head over to **📝 Log Entry** to add your first record.")
        st.stop()

    # ── Date range filter ────────────────────────────────────────────────────
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
    with col_d2:
        end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

    mask = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
    df_filtered = df[mask].copy()

    if df_filtered.empty:
        st.warning("No entries in the selected date range.")
        st.stop()

    # ── Location filter ──────────────────────────────────────────────────────
    location_opts = df_filtered["pain_location"].unique().tolist()
    selected_locations = st.multiselect(
        "Filter by location",
        options=location_opts,
        default=location_opts,
    )
    if selected_locations:
        df_filtered = df_filtered[df_filtered["pain_location"].isin(selected_locations)]

    if df_filtered.empty:
        st.warning("No entries for the selected locations.")
        st.stop()

    st.markdown("---")

    # ── Pain Level Over Time ─────────────────────────────────────────────────
    st.subheader("Pain Level Over Time")
    fig_line = px.line(
        df_filtered.sort_values("timestamp"),
        x="timestamp",
        y="pain_level",
        color="pain_location",
        markers=True,
        labels={"timestamp": "Date / Time", "pain_level": "Pain Level (0–10)", "pain_location": "Location"},
        title="Pain Level Over Time by Location",
        range_y=[0, 10],
    )
    fig_line.update_layout(
        hovermode="x unified",
        legend_title_text="Location",
        xaxis_title="Date / Time",
        yaxis_title="Pain Level (0–10)",
    )
    fig_line.add_hline(
        y=df_filtered["pain_level"].mean(),
        line_dash="dot",
        annotation_text=f"Avg {df_filtered['pain_level'].mean():.1f}",
        annotation_position="bottom right",
        line_color="gray",
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Average pain per location (bar chart) ────────────────────────────────
    st.subheader("Average Pain Level by Location")
    avg_by_loc = (
        df_filtered.groupby("pain_location")["pain_level"]
        .mean()
        .reset_index()
        .rename(columns={"pain_location": "Location", "pain_level": "Average Pain Level"})
        .sort_values("Average Pain Level", ascending=False)
    )
    fig_bar = px.bar(
        avg_by_loc,
        x="Location",
        y="Average Pain Level",
        color="Average Pain Level",
        color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
        range_color=[0, 10],
        range_y=[0, 10],
        title="Average Pain Level per Location",
        text_auto=".1f",
    )
    fig_bar.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Daily average heat-map ───────────────────────────────────────────────
    st.subheader("Daily Pain Heatmap")
    df_filtered["date"] = df_filtered["timestamp"].dt.date
    daily_avg = (
        df_filtered.groupby("date")["pain_level"]
        .mean()
        .reset_index()
        .rename(columns={"date": "Date", "pain_level": "Avg Pain Level"})
    )
    daily_avg["Date"] = pd.to_datetime(daily_avg["Date"])
    fig_heat = px.density_heatmap(
        daily_avg,
        x="Date",
        y="Avg Pain Level",
        nbinsx=min(len(daily_avg), 30),
        title="Pain Intensity Calendar",
        labels={"Avg Pain Level": "Avg Pain"},
        color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
        range_color=[0, 10],
    )
    st.plotly_chart(fig_heat, use_container_width=True)
