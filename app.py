#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
College Club Management Tool
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="🎓 College Club Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
<style>
/* General UI tweaks */
.stApp {
    background-color: #f9f9f9;
    color: #222;
    font-family: "Helvetica Neue", sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
}

/* Table responsiveness */
[data-testid="stDataFrame"] table {
    font-size: 0.9rem !important;
}

@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 70% !important;
        min-width: 250px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------- DATA LOAD ----------------------
# Google Form response sheet (replace with yours)
csv_url = "https://docs.google.com/spreadsheets/d/1ZgOV7SHOX8XzK7EzgVTzDC8okXTPE_sCm1CRCq5Qdjs/gviz/tq?tqx=out:csv&sheet=Form%20responses%201"

df = pd.read_csv(csv_url)
df.columns = df.columns.str.strip()

# ---------------------- OWNER CONFIG ----------------------
OWNER_ACTIVITY_FORM_URL = "https://forms.gle/uWH3JUhz1jMh8t4PA"
USE_SHEETS_API_FOR_ACTIVITY_POST = False  # keep False unless you want API posting

# All students data (Excel from Google Drive link)


# Replace this link with your uploaded Drive Excel link
all_students_link = "https://docs.google.com/spreadsheets/d/1iXn5B9vmizIpOp_1LAjKjLxyTiEf67b1/gviz/tq?tqx=out:csv&sheet=Form%20responses%201"
all_students_df = pd.read_csv(all_students_link)
all_students_df.columns = all_students_df.columns.str.strip()

# ---------------------- SIDEBAR MENU ----------------------
menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "🏠 Dashboard",
        "🔎 Search by Registration Number",
        "🏆 Search by Club",
        "✅ Students Joined At Least One Club",
        "🚫 Students Who Have Not Responded",
        "🔁 Duplicate Registrations", 
        "💬 Message Panel "
    ]
)

# ---------------------- DASHBOARD ----------------------
if menu == "🏠 Dashboard":
    st.title("🎓 College Club Dashboard")
    st.write("Welcome to the College Club Management Tool!")

    total_responses = len(df)
    total_students = len(all_students_df) if not all_students_df.empty else "N/A"

    st.metric("📥 Total Student joined Any Club", total_responses)
    st.metric("👥 Total Students", total_students)
    st.subheader("📊 Club Participation Comparison")

    if "Club 1" in df.columns and "Club 2" in df.columns:
        clubs = pd.concat([df["Club 1"], df["Club 2"]]).dropna()
        club_counts = clubs.value_counts().reset_index()
        club_counts.columns = ["Club", "Count"]

        # ✅ Matplotlib static chart
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(club_counts["Club"], club_counts["Count"])
        ax.set_xlabel("Club")
        ax.set_ylabel("Number of Students")
        ax.set_title("Club Participation")
        plt.xticks(rotation=45, ha="right")

        st.pyplot(fig)  # render in Streamlit
    else:
        st.warning("⚠️ Club columns not found in the sheet.")

    if not df.empty:
        st.subheader("📊 Latest Responses")
        st.dataframe(df.tail(5), use_container_width=True)
        

# ---------------------- SEARCH BY REG NO ----------------------
elif menu == "🔎 Search by Registration Number":
    st.title("🔎 Search by Registration Number")
    reg_no = st.text_input("Enter Registration Number:")

    

    if st.button("🔍 Search"):
        if reg_no:
            if "Registration Number" in df.columns:
                student_data = df[df["Registration Number"].astype(str) == reg_no]

                if not student_data.empty:
                    st.success(f"✅ Found {len(student_data)} record(s)")
                    st.dataframe(
                        student_data[["Name", "Department", "Phone Number", "Club 1", "Club 2"]],
                        use_container_width=True,
                        height=(len(student_data) + 1) * 35
                        )
            else:
                st.error("❌ No student found with this Registration Number.")
        else:
            st.error("⚠️ Column 'Registration Number' not found in sheet.")
    else:
        st.warning("⚠️ Please enter a Registration Number before searching.")


# ---------------------- SEARCH BY CLUB ----------------------
elif menu == "🏆 Search by Club":
    st.title("🏆 Search by Club")

    if "Club 1" in df.columns and "Club 2" in df.columns:
        all_clubs = pd.unique(df[["Club 1", "Club 2"]].values.ravel("K"))
        all_clubs = [c for c in all_clubs if pd.notna(c)]

        selected_club = st.selectbox("Choose a Club:", ["-- Select Club --"] + sorted(all_clubs))

        if selected_club != "-- Select Club --":
            club_data = df[(df["Club 1"] == selected_club) | (df["Club 2"] == selected_club)]

            if not club_data.empty:
               # st.success(f"✅ Found {len(club_data)} student(s) in {selected_club}")
                st.table(club_data[["Name", "Registration Number", "Department"]])
                unique_members = club_data.drop_duplicates(subset=["Registration Number"])
                st.info(f"👥 Total Unique Members in **{selected_club}**: {len(unique_members)}")
            else:
                st.warning(f"No students found in {selected_club}.")
    else:
        st.error("⚠️ Club columns not found in sheet.")

# ---------------------- JOINED AT LEAST ONE CLUB ----------------------
elif menu == "✅ Students Joined At Least One Club":
    st.title("✅ Students Joined At Least One Club")

    joined = df[(df["Club 1"].notna()) | (df["Club 2"].notna())]
    if not joined.empty:
        st.dataframe(joined[["Name", "Registration Number", "Department", "Club 1", "Club 2"]],
                     use_container_width=True)
        st.info(f"👥 Total Students Joined At Least One Club: {len(joined)}")
    else:
        st.warning("No students have joined any club.")

# ---------------------- NOT RESPONDED ----------------------
elif menu == "🚫 Students Who Have Not Responded":
    st.title("🚫 Students Who Have Not Responded")

    if not all_students_df.empty and "Registration Number" in all_students_df.columns:
        responded_reg_nos = df["Registration Number"].astype(str).unique()
        non_responded = all_students_df[
            ~all_students_df["Registration Number"].astype(str).isin(responded_reg_nos)
        ]

        if not non_responded.empty:
            st.dataframe(non_responded[["Name", "Registration Number", "Department"]],
                         use_container_width=True)
            st.info(f"👥 Total Students Not Responded: {len(non_responded)}")

            # Download option
            csv = non_responded.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Non-Responded List", data=csv,
                               file_name="non_responded_students.csv", mime="text/csv")
        else:
            st.success("🎉 All students have responded!")
    else:
        st.error("⚠️ Could not load All Students Excel. Please check the Drive link.")
# ---------------------- DUPLICATE REGISTRATIONS ----------------------
elif menu == "🔁 Duplicate Registrations":
    st.title("🔁 Duplicate Registrations")

    if "Registration Number" in df.columns:
        duplicates = df[df.duplicated(subset=["Registration Number"], keep=False)]
        
        if not duplicates.empty:
            st.warning("⚠️ Found students with duplicate registrations")
            st.dataframe(
                duplicates.sort_values("Registration Number"),
                use_container_width=True
            )

            # Group to show how many times each reg no appears
            dup_counts = duplicates["Registration Number"].value_counts().reset_index()
            dup_counts.columns = ["Registration Number", "Count"]

            st.subheader("📊 Duplicate Counts")
            st.table(dup_counts)

        else:
            st.success("🎉 No duplicate registrations found!")
    else:
        st.error("⚠️ Column 'Registration Number' not found in the sheet.")        
# ---------------------- CLUB OWNER PANEL ----------------------
elif menu == "💬 Message Panel ":
    st.title("💬 Message Panel")

   
    if st.button("📝 Open Activity Form"):
        st.markdown(f"[Click here to fill the form]({OWNER_ACTIVITY_FORM_URL})", unsafe_allow_html=True)
