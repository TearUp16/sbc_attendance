import streamlit as st
import pandas as pd
import os
from datetime import datetime, time

def fmt_hour(h: int) -> str:
    if h == 0:
        return "12:00 AM"
    elif 1 <= h < 12:
        return f"{h:02d}:00 AM"
    elif h == 12:
        return "12:00 PM"
    else:
        return f"{h-12:02d}:00 PM"

names_positions = {
    "HANNAH DALUDADO":    "MIS",
    "JOAN VILLANUEVA":        "TL",
    "JOANNA NICOLE AINZA":    "AGENT",
    "NAOMI CAROLINE ASIS":    "AGENT",
    "JONATHAN LAPAYA":        "AGENT",
    "JECELYN LOROZO":         "AGENT",
    "JOAN MERCADO":           "AGENT",
    "CELSA MONTENEGRO":       "AGENT",
    "LEVI JR. QUEROL":        "AGENT",
    "HANS DAVID QUIJANO":     "AGENT",
    "MIRIAM RESUELLO":        "AGENT",
    "MARY LUZBHEL ROYOL":     "AGENT",
    "KEISHA MAE SUMBANG":     "AGENT",
    "CHYNNE JASMINE LANUZO":    "AGENT",
    "JAYVEE MACAHIA":   "AGENT"
}

def load_attendance_data():
    if os.path.exists("attendance_sheet.csv"):
        df = pd.read_csv("attendance_sheet.csv")
        df["DATE"] = pd.to_datetime(df["DATE"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=[
            "DATE","NAME OF AGENT","POSITION",
            "STATUS","TYPE OF ABSENT","TIME","OT TIME"
        ])

def save_attendance_data(df):
    df.to_csv("attendance_sheet.csv", index=False)

st.title("SBC INSURANCE ATTENDANCE")
attendance_df = load_attendance_data()
today_date   = datetime.today().date()
current_time = datetime.now().time()

# auto-mark absent after 9:00
if current_time >= time(9, 0):
    missing = [
        name for name in names_positions
        if not (
            (attendance_df["DATE"] == today_date) &
            (attendance_df["NAME OF AGENT"] == name)
        ).any()
    ]
    if missing:
        for name in missing:
            attendance_df = pd.concat([attendance_df, pd.DataFrame({
                "DATE":          [today_date],
                "NAME OF AGENT": [name],
                "POSITION":      [names_positions[name]],
                "STATUS":        ["ABSENT"],
                "TYPE OF ABSENT":[""],
                "TIME":          [""],
                "OT TIME":       [""]
            })], ignore_index=True)
        save_attendance_data(attendance_df)

with st.form(key="attendance_form"):
    st.subheader(f"**Date**: {today_date}")

    # 1) Name dropdown
    name_of_agent = st.selectbox("Name", list(names_positions.keys()))

    # 2) Editable Position dropdown (defaults to the mapped role)
    pos_options = ["AGENT", "TL", "MIS", "FIELD"]
    default_idx = pos_options.index(names_positions[name_of_agent])
    position    = st.selectbox("Position", pos_options, index=default_idx)

    status         = st.selectbox("Status (Present/Absent)", ["PRESENT", "ABSENT"]).upper()
    type_of_absent = st.selectbox("Type of Absence (Leave blank if none)", ["", "SL", "VL", "EL"]).upper()

    start_h = st.slider("Time in",  0, 24,  8, format="%02d:00")
    end_h   = st.slider("Time out", start_h, 24, 17, format="%02d:00")
    time_str = f"{fmt_hour(start_h)} – {fmt_hour(end_h)}"

    ot_time = st.selectbox("OT Time (Leave blank if none)", ["", "1 HOUR", "2 HOURS", "3 HOURS"]).upper()

    submit_button = st.form_submit_button("Submit")
    if submit_button:
        # remove any auto-ABSENT row for this agent today
        attendance_df = attendance_df[~(
            (attendance_df["DATE"] == today_date) &
            (attendance_df["NAME OF AGENT"] == name_of_agent)
        )]
        # add their real submission
        new_entry = pd.DataFrame({
            "DATE":          [today_date],
            "NAME OF AGENT": [name_of_agent],
            "POSITION":      [position],
            "STATUS":        [status],
            "TYPE OF ABSENT":[type_of_absent],
            "TIME":          [time_str],
            "OT TIME":       [ot_time]
        })
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        save_attendance_data(attendance_df)
        st.success("Attendance has been recorded successfully!")

# ─── Date Filter & Display ────────────────────────────────────────────────
date_filter = st.date_input("Select a date to filter", today_date)
st.subheader("Attendance Sheet " + str(date_filter))

filtered_df = attendance_df[
    attendance_df["DATE"] == date_filter
].reset_index(drop=True)

# Delete option
rows_to_delete = st.multiselect(
    "Select rows to delete",
    options=filtered_df.index.tolist(),
    format_func=lambda x: (
        f"Entry {x+1}: {filtered_df.iloc[x]['NAME OF AGENT']} - "
        f"{filtered_df.iloc[x]['POSITION']}"
    )
)
if rows_to_delete and st.button("Confirm Delete"):
    filtered_df = filtered_df.drop(rows_to_delete).reset_index(drop=True)
    save_attendance_data(filtered_df)
    st.success(
        f"Deleted selected entries: {', '.join(str(r+1) for r in rows_to_delete)}"
    )

st.dataframe(filtered_df)

# Download button
file_name = f"Filtered_Attendance_{date_filter}.csv"
st.download_button(
    label="Download Attendance",
    data=filtered_df.to_csv(index=False),
    file_name=file_name,
    mime="text/csv",
)

