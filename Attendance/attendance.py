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

# Function to reset the attendance data
def reset_attendance_data():
    if os.path.exists("attendance_sheet.csv"):
        os.remove("attendance_sheet.csv")
    return pd.DataFrame(columns=["DATE", "NAME OF AGENT", "POSITION", "STATUS", "TYPE OF ABSENT", "TIME", "OT TIME"])

# Streamlit UI
st.title("SBC INSURANCE ATTENDANCE")

# Button to reset the data
reset_button = st.button("Reset")

# Reset the data if button is pressed
if reset_button:
    attendance_df = reset_attendance_data()
    st.success("Attendance data has been reset!")

else:
    # Load existing attendance data if available
    attendance_df = load_attendance_data()

# Get today's date using datetime module
today_date = datetime.today().date()

# User input form for attendance
with st.form(key="attendance_form"):
    # Display today's date in a non-editable field (read-only)
    st.subheader(f"**Date**: {today_date}")  # Displaying today's date as text, not editable
    
    name_of_agent = st.text_input("Name of Agent")
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

# Display the updated attendance sheet
st.subheader("Attendance Sheet")
st.dataframe(attendance_df)

file_name = f"Attendace {today_date}.csv"

# Option to download the updated attendance sheet
st.download_button(
    label="Download Attendace",
    data=attendance_df.to_csv(index=False),
    file_name=file_name,
    mime="text/csv",
)
