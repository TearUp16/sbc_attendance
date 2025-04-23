import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Function to load existing attendance data if available
def load_attendance_data():
    if os.path.exists("attendance_sheet.csv"):
        return pd.read_csv("attendance_sheet.csv")
    else:
        return pd.DataFrame(columns=["DATE", "NAME OF AGENT", "POSITION", "STATUS", "TYPE OF ABSENT", "TIME", "OT TIME"])

# Function to save the attendance data to a CSV file
def save_attendance_data(df):
    df.to_csv("attendance_sheet.csv", index=False)

# Streamlit UI
st.title("SBC INSURANCE ATTENDANCE")

# Load existing attendance data if available
attendance_df = load_attendance_data()

# Get today's date using datetime module
today_date = datetime.today().date()

# User input form for attendance
with st.form(key="attendance_form"):
    # Display today's date in a non-editable field (read-only)
    st.subheader(f"**Date**: {today_date}")  # Displaying today's date as text, not editable
    
    name_of_agent = st.text_input("Name")
    position = st.selectbox("Position", ["Agent", "TL", "MIS", "Field"])
    status = st.selectbox("Status (Present/Absent)", ["Present", "Absent"])
    type_of_absent = st.selectbox("Type of Absence (Leave blank if none)", ["","SL", "VL", "EL"])
    time = st.text_input("Time (8AM to 5PM)", "8AM to 5PM")
    ot_time = st.selectbox("OT Time (Leave blank if none)", ["", "1 HOUR", "2 HOURS", "3 HOURS"])

    # Submit button for the form
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if name_of_agent:
            new_entry = pd.DataFrame({
                "DATE": [today_date],  # Automatically set the date to today
                "NAME OF AGENT": [name_of_agent],
                "POSITION": [position],
                "STATUS": [status],
                "TYPE OF ABSENT": [type_of_absent],
                "TIME": [time],
                "OT TIME": [ot_time]
            })
            # Append the new entry to the existing data
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)

            # Save updated attendance data to CSV
            save_attendance_data(attendance_df)

            st.success("Attendance has been recorded successfully!")

# Display the full attendance sheet (no filtering applied)
st.subheader("Attendance Sheet")

# Reset the index to avoid out-of-bounds errors
attendance_df = attendance_df.reset_index(drop=True)

# Option to delete a row
rows_to_delete = st.multiselect("Delete Row", options=attendance_df.index.tolist(), format_func=lambda x: f"Entry {x+1}: {attendance_df.iloc[x]['NAME OF AGENT']} - {attendance_df.iloc[x]['POSITION']}")

# Confirm delete button
if rows_to_delete:
    confirm_delete_button = st.button("Confirm Delete")
    
    if confirm_delete_button:
        # Delete selected rows and reset the index
        attendance_df = attendance_df.drop(rows_to_delete).reset_index(drop=True)
        save_attendance_data(attendance_df)
        st.success(f"Deleted selected entries: {', '.join(str(row + 1) for row in rows_to_delete)}")

# Display the updated attendance sheet
st.dataframe(attendance_df)

# Option to download the updated attendance sheet
file_name = f"Attendance {today_date}.csv"
st.download_button(
    label="Download Attendance",
    data=attendance_df.to_csv(index=False),
    file_name=file_name,
    mime="text/csv",
)
