import streamlit as st
import pandas as pd
import os

# File paths
EMPLOYEE_FILE = "employees.xlsx"
ASSET_FILE = "cleaned_asset_register.xlsx"

# Load Employees Data
if os.path.exists(EMPLOYEE_FILE):
    employees = pd.read_excel(EMPLOYEE_FILE)
else:
    employees = pd.DataFrame(columns=["Employee ID", "Name", "Position", "Department", "Phone", "Email"])
    employees.to_excel(EMPLOYEE_FILE, index=False)

# Load Assets Data
if os.path.exists(ASSET_FILE):
    assets = pd.read_excel(ASSET_FILE)
else:
    st.error(f"{ASSET_FILE} not found! Please upload the cleaned asset file.")
    st.stop()

# Page Title
st.title("Asset Management System")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", [
    "View Employees",
    "Add Employee",
    "Delete Employee",
    "Search Employee",
    "View Asset Register",
    "Asset Condition Report",
    "Financing Insights"
])

### Employee Management Section
if menu == "View Employees":
    st.subheader("All Employees")
    st.dataframe(employees)

elif menu == "Add Employee":
    st.subheader("Add New Employee")

    employee_id = st.text_input("Employee ID")
    name = st.text_input("Name")
    position = st.text_input("Position")
    department = st.text_input("Department")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Add Employee"):
        new_employee = {
            "Employee ID": employee_id,
            "Name": name,
            "Position": position,
            "Department": department,
            "Phone": phone,
            "Email": email
        }
        employees = pd.concat([employees, pd.DataFrame([new_employee])], ignore_index=True)
        employees.to_excel(EMPLOYEE_FILE, index=False)
        st.success(f"Employee {name} added successfully!")

elif menu == "Delete Employee":
    st.subheader("Delete Employee")
    emp_id_to_delete = st.text_input("Enter Employee ID to Delete")

    if st.button("Delete Employee"):
        employees = employees[employees["Employee ID"] != emp_id_to_delete]
        employees.to_excel(EMPLOYEE_FILE, index=False)
        st.success(f"Employee with ID {emp_id_to_delete} has been deleted.")

elif menu == "Search Employee":
    st.subheader("Search Employee")
    search_term = st.text_input("Enter Employee Name or ID")

    if st.button("Search"):
        results = employees[
            (employees["Name"].str.contains(search_term, case=False, na=False)) |
            (employees["Employee ID"].str.contains(search_term, case=False, na=False))
        ]
        if not results.empty:
            st.write("Search Results:")
            st.dataframe(results)
        else:
            st.warning("No employee found with that Name or ID.")

### Asset Tracking Section
elif menu == "View Asset Register":
    st.subheader("Asset Register")
    st.dataframe(assets)

elif menu == "Asset Condition Report":
    st.subheader("Condition Monitoring Report")

    # Count assets by condition
    condition_summary = assets["Asset condition"].value_counts().reset_index()
    condition_summary.columns = ["Condition", "Count"]

    st.write("Summary of Asset Conditions:")
    st.dataframe(condition_summary)

    # Optional Chart
    st.bar_chart(condition_summary.set_index("Condition"))

    # Show details of poor condition assets
    st.write("Assets in Poor Condition:")
    poor_assets = assets[assets["Asset condition"].str.contains("poor", case=False, na=False)]
    st.dataframe(poor_assets[["Asset Description", "Current Location", "Responsible officer"]])

elif menu == "Financing Insights":
    st.subheader("Financing Insights")

    # Count assets by financing source
    financing_summary = assets["Financed by/ source of funds"].value_counts().reset_index()
    financing_summary.columns = ["Financing Source", "Count"]

    st.write("Assets by Financing Source:")
    st.dataframe(financing_summary)

    # Optional Chart
    st.bar_chart(financing_summary.set_index("Financing Source"))
