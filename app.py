import streamlit as st
import pandas as pd

from database import(
    create_table,
    add_application,
    get_application,
)

st.set_page_config(
    page_title = "Job Application Tracker",
    layout = "wide"
)

create_table()

st.title("Job Application Tracker")
st.write("Manage and analyze your job applications")

tab1, tab2 = st.tabs([
    "Dashboard",
    "Add Application"
])

with tab2:
    st.subheader("New Application")
    with st.form("application_form"):
        company = st.text_input("Company")
        position = st.text_input("Job Position")
        date_applied = st.date_input("Date Applied")

        status = st.selectbox(
            "Application Status",
            [
                "Applied",
                "Interviewing",
                "Offer",
                "Rejected",
                "Withdrawn"
            ]
        )

        job_url = st.text_input("Job Posting URL")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Save Application"
        )

        if submitted:
            if not company.strip() or not position.strip():
                st.error(
                    "Company and position are required."
                )
            else:
                add_application(
                    company.strip(),
                    position.strip(),
                    date_applied.isoformat(),
                    status,
                    job_url.strip(),
                    notes.strip()
                )
                st.success("Application saved!")

with tab1:
    applications = get_application()
    df = pd.DataFrame(applications)

    if df.empty:
        st.info("No applications yet. Add your first one!")
    else:
        total = len(df)
        interviews = (df["status"] == "Interviewing").sum()
        offers = (df["status"] == "Offer").sum()
        rejected = (df["status"] == "Rejected").sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Applications", total)
        col2.metric("Interviewing", interviews)
        col3.metric("Offers", offers)
        col4.metric("Rejected", rejected)

        st.subheader("Application Status")

        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

        st.subheader("All Applications")

        st.dataframe(
            df,
            hide_index=True,
            width="stretch"
        )

st.stop()