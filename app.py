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
# Load Url
csv_url = st.secrets["links"]["responses_csv"]
students_url = st.secrets["links"]["students_csv"]
owner_form_url = st.secrets["links"]["activity_form"]
df["Registration Number"] = df["Registration Number"].astype(str).str.strip()
all_students_df["Registration Number"] = all_students_df["Registration Number"].astype(str).str.strip()

for c in ["Club 1", "Club 2"]:
    if c in df.columns:
        df[c] = df[c].astype(str).str.strip()
        df.loc[df[c].str.lower().isin(["nan", "none", "nan.0", "na"]), c] = pd.NA
if "Year" in all_students_df.columns:
    all_students_df["Year"] = pd.to_numeric(all_students_df["Year"], errors="coerce").astype("Int64")
    
#--------------data config------------------
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip()

    all_students_df = pd.read_csv(students_url)
    all_students_df.columns = all_students_df.columns.str.strip()

    return df, all_students_df

# Call the function
df, all_students_df = load_data()


# Read data
df.columns = df.columns.str.strip()
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
        "🌀 Duplicate Registrations",
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

        # ----- Club Participation Pie Chart -----
        st.subheader("🥧 Club Participation (Pie Chart)")
        pie_chart = (
            alt.Chart(club_counts)
            .mark_arc()
            .encode(
                theta="Count",
                color="Club",
                tooltip=["Club", "Count"]
            )
        )
        st.altair_chart(pie_chart, use_container_width=True)

    # ----- One vs Two Club Participation -----
    st.subheader("🥧 Students Joining One vs Two Clubs")
    if "Club 1" in df.columns and "Club 2" in df.columns:
        df["Club Count"] = df[["Club 1", "Club 2"]].notna().sum(axis=1)
        club_count_stats = df["Club Count"].value_counts().reset_index()
        club_count_stats.columns = ["Clubs Joined", "Students"]

        club_count_pie = (
            alt.Chart(club_count_stats)
            .mark_arc()
            .encode(
                theta="Students",
                color="Clubs Joined:N",
                tooltip=["Clubs Joined", "Students"]
            )
        )
        st.altair_chart(club_count_pie, use_container_width=True)

    # ----- Department-wise Participation -----
    if "Department" in df.columns:
        st.subheader("🥧 Department-wise Club Participation")
        dept_counts = df["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]

        dept_pie = (
            alt.Chart(dept_counts)
            .mark_arc()
            .encode(
                theta="Count",
                color="Department",
                tooltip=["Department", "Count"]
            )
        )
        st.altair_chart(dept_pie, use_container_width=True)

    # ----- Year-wise Participation -----
    if "Year" in all_students_df.columns:
        st.subheader("🥧 Year-wise Club Participation")

        # Merge responses with all students to get year info
        merged = df.merge(
            all_students_df[["Registration Number", "Year"]],
            on="Registration Number",
            how="left"
        )

        year_counts = merged["Year"].value_counts().reset_index()
        year_counts.columns = ["Year", "Count"]

        year_pie = (
            alt.Chart(year_counts)
            .mark_arc()
            .encode(
                theta="Count",
                color="Year:N",
                tooltip=["Year", "Count"]
            )
        )
        st.altair_chart(year_pie, use_container_width=True)
    # ----- Year-wise Participation Percentage -----
    if "Year" in all_students_df.columns and "Registration Number" in all_students_df.columns:
        st.subheader("🥧 Year-wise Participation Percentage")

        # Mark joined students
        responded_reg_nos = df["Registration Number"].astype(str).unique()
        all_students_df["Joined"] = all_students_df["Registration Number"].astype(str).isin(responded_reg_nos)

        # Group by year
        year_stats = all_students_df.groupby("Year")["Joined"].value_counts().unstack(fill_value=0)

        # Prepare data for pie charts (one pie per year)
        for year in year_stats.index:
            year_data = pd.DataFrame({
                "Status": ["Joined at least one club", "Not joined any club"],
                "Count": [
                    year_stats.loc[year, True] if True in year_stats.columns else 0,
                    year_stats.loc[year, False] if False in year_stats.columns else 0
                ]
            })

            total = year_data["Count"].sum()
            joined_pct = (year_data.loc[year_data["Status"] == "Joined at least one club", "Count"].values[0] / total * 100) if total > 0 else 0
            not_joined_pct = 100 - joined_pct

            st.markdown(f"### 📌 Year {year}")
            year_pie = (
                alt.Chart(year_data)
                .mark_arc()
                .encode(
                    theta="Count",
                    color="Status",
                    tooltip=["Status", "Count"]
                )
            )
            st.altair_chart(year_pie, use_container_width=True)

            st.info(
                f"✅ {year_data.loc[0, 'Count']} students ({joined_pct:.2f}%) joined in Year {year}.\n\n"
                f"🚫 {year_data.loc[1, 'Count']} students ({not_joined_pct:.2f}%) did not join in Year {year}."
            )    
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
        # build club list reliably
        clubs_1 = df["Club 1"].dropna().unique().tolist()
        clubs_2 = df["Club 2"].dropna().unique().tolist()
        all_clubs = sorted({c for c in (clubs_1 + clubs_2) if c and str(c).strip().lower() not in ["nan", "none", "na"]})

        selected_club = st.selectbox("Choose a Club:", ["-- Select Club --"] + all_clubs)

        # year options (from all_students_df) as clean strings
        years = sorted(all_students_df["Year"].dropna().unique()) if "Year" in all_students_df.columns else []
        year_options = ["-- All Years --"] + [str(int(y)) for y in years]
        selected_year = st.selectbox("Filter by Year (optional):", year_options)

        if selected_club != "-- Select Club --":
            # Filter by club (normalize comparison)
            club_mask = (
                df["Club 1"].fillna("").str.strip() == selected_club
            ) | (
                df["Club 2"].fillna("").str.strip() == selected_club
            )
            club_data = df[club_mask].copy()

            # Merge with Year info from all_students_df (bring Year into responses)
            if "Registration Number" in all_students_df.columns and "Year" in all_students_df.columns:
                # ensure both Registration Number columns are stripped strings (done above)
                club_data = club_data.merge(
                    all_students_df[["Registration Number", "Year"]],
                    on="Registration Number",
                    how="left",
                    validate="m:1"  # many responses -> one student record
                )

                # normalize Year in merged frame too
                club_data["Year"] = pd.to_numeric(club_data["Year"], errors="coerce").astype("Int64")

            # Apply year filter (compare numerically where possible)
            if selected_year != "-- All Years --":
                try:
                    sel_year_int = int(selected_year)
                    club_data = club_data[club_data["Year"] == sel_year_int]
                except Exception:
                    # fallback to string compare (shouldn't be needed if Year numeric conversion worked)
                    club_data = club_data[club_data["Year"].astype(str) == selected_year]

            # Show results / message
            if not club_data.empty:
                    # Keep only required columns
                display_cols = ["Name", "Registration Number", "Department", "Year"]

                # Some rows may miss a column -> safe filter
                display_data = club_data[[c for c in display_cols if c in club_data.columns]].drop_duplicates()

                st.dataframe(display_data, use_container_width=True)

                st.info(f"👥 Total Unique Members in **{selected_club}** "
                       f"{'(Year ' + selected_year + ')' if selected_year != '-- All Years --' else ''}: "
                       f"{len(display_data)}")

               # Download filtered CSV (only selected columns)
                csv = display_data.to_csv(index=False).encode("utf-8")
                st.download_button(
                   label="📥 Download Filtered Club Members",
                   data=csv,
                   file_name=f"{selected_club}_members{'_year_' + selected_year if selected_year != '-- All Years --' else ''}.csv",
                   mime="text/csv"
                )
            else:
                st.warning(f"No students found in {selected_club} "
                           f"{'(Year ' + selected_year + ')' if selected_year != '-- All Years --' else ''}.")

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

# ---------------------- NOT RESPONDED (YEAR-WISE) ----------------------
elif menu == "🚫 Students Who Have Not Responded":
    st.title("🚫 Students Who Have Not Responded (Year-wise)")

    if not all_students_df.empty and "Registration Number" in all_students_df.columns and "Year" in all_students_df.columns:
        responded_reg_nos = df["Registration Number"].astype(str).unique()
        non_responded = all_students_df[
            ~all_students_df["Registration Number"].astype(str).isin(responded_reg_nos)
        ]

        if not non_responded.empty:
            years = sorted(non_responded["Year"].dropna().unique())
            for year in years:
                st.subheader(f"📌 Year {year}")
                year_students = non_responded[non_responded["Year"] == year]

                if not year_students.empty:
                    st.dataframe(
                        year_students[["Name", "Registration Number", "Department", "Year"]],
                        width="stretch"
                    )

                    # Download button for each year
                    csv = year_students.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=f"📥 Download Year {year} Not Responded List",
                        data=csv,
                        file_name=f"non_responded_year_{year}.csv",
                        mime="text/csv"
                    )
                    if(year==1):
                        st.success(f"Total students from 1st year have not responded: {len(year_students)}")
                    elif(year==2):
                        st.success(f"Total students from 2nd year have not responded: {len(year_students)}")
                    elif(year==3):
                        st.success(f"Total students from 3rd year have not responded: {len(year_students)}")
                        
                else:
                    st.info(f"✅ All students from Year {year} have responded.")

            # Total summary
            st.success(f"📊 Total Students Not Responded: {len(non_responded)}")

            # Optional: download all non-responded students together
            all_csv = non_responded.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download All Years (Combined)",
                data=all_csv,
                file_name="non_responded_all_years.csv",
                mime="text/csv"
            )
        else:
            st.success("🎉 All students have responded!")
    else:
        st.error("⚠️ Could not load All Students sheet. Please check that 'Year' and 'Registration Number' columns exist.")
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
