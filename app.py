import streamlit as st
import pandas as pd
import sqlite3

from database import(
    create_table,
    add_application,
    get_application,
    update_application,
    delete_application,
    create_unique_index,
    application_exists
)

if st.session_state.get("update_success", False):
    st.success("Application updated successfully!")

st.set_page_config(
    page_title = "Job Application Tracker",
    layout = "wide"
)

create_table()
create_unique_index()

st.title("Job Application Tracker")
st.write("Manage and analyze your job applications")

tab1, tab2, tab3 = st.tabs([
    "Dashboard",
    "Add Application",
    "Edit Application"
])

with tab2:
    st.subheader("New Application")

    with st.form("application_form", clear_on_submit=True):

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

    # Process submission outside the form
    if submitted:

        if not company.strip() or not position.strip():
            st.error(
                "Company and position are required."
            )

        elif application_exists(company, position):
            st.warning(
                "This application already exists! "
                "Please use Manage Applications "
                "to update the existing entry."
            )

        else:
            try:
                add_application(
                    company.strip(),
                    position.strip(),
                    date_applied.isoformat(),
                    status,
                    job_url.strip(),
                    notes.strip()
                )

            except sqlite3.IntegrityError:
                st.warning(
                    "An application with this company "
                    "and position already exists."
                )

            else:
                st.success(
                    "Application saved successfully!"
                )

with tab1:
    applications = get_application()
    df = pd.DataFrame(applications)

    # All possible application statuses
    statuses = [
        "Applied",
        "Interviewing",
        "Offer",
        "Rejected",
        "Withdrawn"
    ]

    st.subheader("Application Overview")

    if df.empty:
        st.info("No applications yet. Add your first one!")
        status_counts = pd.Series(dtype=int)

    else:
        status_counts = df["status"].value_counts()

    # Include every status, even those with zero entries
    status_counts = status_counts.reindex(
        statuses,
        fill_value=0
    )

    total = len(df)
    interviews = int(status_counts["Interviewing"])
    offers = int(status_counts["Offer"])
    rejected = int(status_counts["Rejected"])

    # --------------------------------------------------
    # Dashboard Metrics
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Applications", total)
    col2.metric("Interviewing", interviews)
    col3.metric("Offers", offers)
    col4.metric("Rejected", rejected)

    # --------------------------------------------------
    # Application Status Chart
    # --------------------------------------------------

    st.subheader("Application Status")

    chart_data = status_counts.rename_axis(
        "Status"
    ).reset_index(name="Count")

    st.bar_chart(
        chart_data,
        x="Status",
        y="Count",
        sort=False
    )

    # --------------------------------------------------
    # All Applications
    # --------------------------------------------------

    st.subheader("All Applications")

    if not df.empty:
        st.dataframe(
            df,
            hide_index=True,
            width="stretch"
        )

with tab3:
    st.subheader("Manage Applications")

    # Retrieve all applications
    applications = get_application()

    if not applications:
        st.info("No applications available to edit or delete.")

    else:
        # Select Application

        application_options = {
            app["id"]: (
                f'{app["company"]} - {app["position"]} '
                f'(ID: {app["id"]})'
            )
            for app in applications
        }

        selected_id = st.selectbox(
            "Select an Application",
            options=list(application_options.keys()),
            format_func=lambda app_id: application_options[app_id]
        )

        selected_app = next(
            app for app in applications
            if app["id"] == selected_id
        )
        # Edit Application Form
        st.subheader("Edit Application Details")

        with st.form(f"edit_application_form_{selected_id}"):

            company = st.text_input(
                "Company",
                value=selected_app["company"]
            )

            position = st.text_input(
                "Job Position",
                value=selected_app["position"]
            )

            date_applied = st.date_input(
                "Date Applied",
                value=pd.to_datetime(
                    selected_app["date_applied"]
                ).date()
            )

            statuses = [
                "Applied",
                "Interviewing",
                "Offer",
                "Rejected",
                "Withdrawn"
            ]

            current_status = selected_app["status"]

            status = st.selectbox(
                "Application Status",
                options=statuses,
                index=(
                    statuses.index(current_status)
                    if current_status in statuses
                    else 0
                )
            )

            job_url = st.text_input(
                "Job Posting URL",
                value=selected_app["job_url"] or ""
            )

            notes = st.text_area(
                "Notes",
                value=selected_app["notes"] or ""
            )

            # Save changes
            submitted = st.form_submit_button("Save Changes")

            if submitted:
                if not company.strip() or not position.strip():
                    st.error("Company and position are required.")

                else:
                    try:
                        rows_updated = update_application(
                            selected_id,
                            company.strip(),
                            position.strip(),
                            date_applied.isoformat(),
                            status,
                            job_url.strip(),
                            notes.strip()
                        )

                    except sqlite3.IntegrityError:
                        st.error(
                            "Another application already exists "
                            "with this company and position."
                        )

                    except sqlite3.DatabaseError as error:
                        st.error(f"Database error: {error}")

                    else:
                        if rows_updated == 0:
                            st.warning(
                                "No application was found with the selected ID."
                            )
                        else:
                            st.session_state["update_success"] = True
                            st.rerun()        # Delete Application
        st.divider()
        st.subheader("Delete Application")

        st.warning(
            "Deleting an application is permanent "
            "and cannot be undone."
        )

        confirm_delete = st.checkbox(
            "I understand that this application will be deleted.",
            key=f"confirm_delete_{selected_id}"
        )

        if st.button(
            "Delete Application",
            type="primary",
            disabled=not confirm_delete,
            key=f"delete_{selected_id}"
        ):
            delete_application(selected_id)

            st.success(
                "Application deleted successfully!"
            )

            st.rerun()

st.stop()