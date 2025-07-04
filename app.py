import os
import base64
import streamlit as st
from datetime import datetime, timedelta
import uuid

st.set_page_config(page_title="Task Management Tool", layout="wide")

# --- Init Session State ---
if "role" not in st.session_state:
    st.session_state.role = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "pdf_data" not in st.session_state:
    st.session_state.pdf_data = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# --- Role Switcher Button ---
if st.session_state.role:
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🔁 Switch User", use_container_width=True):
            st.session_state.role = None
            st.rerun()

# --- Login Screen ---
if st.session_state.role is None:
    st.title("🔐 Select User Type")
    role = st.radio("Login as:", ["Admin", "User"])
    if st.button("Enter"):
        st.session_state.role = role
        st.rerun()

# --- Admin View ---
elif st.session_state.role == "Admin":
    st.title("🧑‍💼 Admin Panel")

    st.subheader("📤 Upload PDF to Display")
    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_pdf:
        st.session_state.pdf_data = uploaded_pdf.getvalue()
        st.session_state.pdf_name = uploaded_pdf.name
        st.success("PDF uploaded and ready for user view!")

    st.subheader("📋 Add New Task")
    task_title = st.text_input("Task Title")
    task_deadline = st.date_input("Deadline", value=datetime.today() + timedelta(days=3))
    assigned_to = st.text_input("Assign to (Email or Name)")

    if st.button("➕ Add Task"):
        if task_title and assigned_to:
            task = {
                "id": str(uuid.uuid4()),
                "title": task_title,
                "deadline": str(task_deadline),
                "assigned_to": assigned_to,
                "status": "Pending",
                "submission": None,
                "review": None,
                "feedback": None
            }
            st.session_state.tasks.append(task)
            st.success("Task added!")
            st.rerun()
        else:
            st.warning("Please fill in all fields")

    st.divider()
    st.subheader("🗂 Current Tasks")

    for i, task in enumerate(st.session_state.tasks):
        st.markdown(f"**📌 {task['title']}**")
        st.write(f"Assigned to: {task['assigned_to']}")
        st.write(f"Deadline: {task['deadline']}")
        st.write(f"Status: {task['status']}")

        if task["submission"]:
            with st.expander("📥 View Submission"):
                st.write(f"Submitted File: {task['submission'].name}")
                st.download_button("Download", task["submission"].getvalue(), file_name=task["submission"].name)

                if task["status"] == "Submitted":
                    accept = st.button("✅ Accept", key=f"accept_{task['id']}")
                    reject = st.button("❌ Reject", key=f"reject_{task['id']}")

                    if accept:
                        task["status"] = "Completed"
                        st.success("Task marked as completed.")
                        st.rerun()

                    if reject:
                        task["status"] = "Rejection_Pending"
                        st.rerun()

                elif task["status"] == "Rejection_Pending":
                    feedback = st.text_area("💬 Enter Feedback", key=f"feedback_input_{task['id']}")
                    if st.button("Submit Feedback", key=f"submit_feedback_{task['id']}"):
                        task["feedback"] = feedback
                        task["status"] = "Rejected"
                        st.success("Feedback submitted. Task rejected.")
                        st.rerun()

                elif task["status"] == "Rejected":
                    st.warning(f"❌ Task was rejected.")
                    st.info(f"💬 Feedback: {task['feedback']}")

        st.divider()

# --- User View ---
elif st.session_state.role == "User":
    st.title("🙋‍♂️ User Panel")

    st.subheader("📑 View Presentation")
    if st.session_state.pdf_data:
        base64_pdf = base64.b64encode(st.session_state.pdf_data).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("No PDF uploaded yet.")

    st.divider()
    st.subheader("📋 Assigned Tasks")

    assigned_user = st.text_input("Enter your name or email to see your tasks:")

    if assigned_user:
        found = False
        for task in st.session_state.tasks:
            if task["assigned_to"].lower() == assigned_user.lower():
                found = True
                st.markdown(f"**📌 {task['title']}**")
                st.write(f"Deadline: {task['deadline']}")
                st.write(f"Status: {task['status']}")

                if task["status"] == "Rejected":
                    if task["feedback"]:
                        st.warning(f"Feedback: {task['feedback']}")
                    else:
                        st.warning("This task was rejected, but no feedback was provided.")

                if task["status"] != "Completed":
                    uploaded = st.file_uploader("📤 Submit Your Work (PDF/DOCX)", type=["pdf", "docx"], key=task["id"])
                    if uploaded:
                        task["submission"] = uploaded
                        task["status"] = "Submitted"
                        task["feedback"] = None
                        st.success("Submitted successfully!")
                        st.rerun()
                st.divider()

        if not found:
            st.info("No tasks found for this user.")
