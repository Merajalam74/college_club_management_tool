#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
College Club Management Tool
"""

import streamlit as st
import pandas as pd
import altair as alt

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="🎓 College Club Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- DATA LOAD ----------------------
# Load secrets
csv_url = st.secrets["links"]["responses_csv"]
students_url = st.secrets["links"]["students_csv"]
owner_form_url = st.secrets["links"]["activity_form"]

# Read data
df = pd.read_csv(csv_url)
df.columns = df.columns.str.strip()

all_students_df = pd.read_csv(students_url)
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
        "💬 Message Panel"
    ]
)

# ---------------------- DASHBOARD ----------------------
if menu == "🏠 Dashboard":
    st.title("🎓 College Club Dashboard")
    st.write("Welcome to the College Club Management Tool!")

    total_responses = len(df)
    total_students = len(all_students_df) if not all_students_df.empty else "N/A"

    col1, col2 = st.columns(2)
    col1.metric("📥 Total Student joined Any Club", total_responses)
    col2.metric("👥 Total Students", total_students)

    st.subheader("📊 Club Participation Comparison")
    if "Club 1" in df.columns and "Club 2" in df.columns:
        clubs = pd.concat([df["Club 1"], df["Club 2"]]).dropna()
        club_counts = clubs.value_counts().reset_index()
        club_counts.columns = ["Club", "Count"]

        chart = (
            alt.Chart(club_counts)
            .mark_bar()
            .encode(
                x=alt.X("Club", sort="-y"),
                y="Count",
                tooltip=["Club", "Count"]
            )
            .properties(width=600, height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    if not df.empty:
        st.subheader("📊 Latest Responses")
        st.dataframe(df.tail(5), width="stretch")

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
                        width="stretch"
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
                     width="stretch")
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
                         width="stretch")
            st.info(f"👥 Total Students Not Responded: {len(non_responded)}")

            csv = non_responded.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Non-Responded List", data=csv,
                               file_name="non_responded_students.csv", mime="text/csv")
        else:
            st.success("🎉 All students have responded!")
    else:
        st.error("⚠️ Could not load All Students sheet. Please check the link.")
# ---------------------- DUPLICATE REGISTRATIONS ----------------------
elif menu == "🌀 Duplicate Registrations":
    st.title("🌀 Duplicate Registrations")

    if "Registration Number" in df.columns:
        duplicates = df[df.duplicated(subset=["Registration Number"], keep=False)]
        if not duplicates.empty:
            st.warning(f"⚠️ Found {len(duplicates)} duplicate records!")
            st.dataframe(
                duplicates[["Name", "Registration Number", "Department", "Club 1", "Club 2"]],
                width="stretch"
            )

            # Show grouped duplicate summary
            dup_summary = (
                duplicates.groupby("Registration Number")
                .size()
                .reset_index(name="Count")
                .query("Count > 1")
            )
            st.subheader("📊 Duplicate Summary")
            st.table(dup_summary)

            # Allow CSV download
            csv = duplicates.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Duplicate Records",
                data=csv,
                file_name="duplicate_students.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ No duplicate registrations found!")
    else:
        st.error("⚠️ 'Registration Number' column not found in the data.")
# ---------------------- MESSAGE PANEL ----------------------
elif menu == "💬 Message Panel":
    st.title("💬 Message Panel")
    st.markdown(f"[Click here to fill the form]({owner_form_url})", unsafe_allow_html=True)
