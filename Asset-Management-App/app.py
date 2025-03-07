import streamlit as st
import pandas as pd

# Paths
employee_file = 'employees.xlsx'

# Initialize or load employee file
@st.cache_data
def load_employees():
    try:
        return pd.read_excel(employee_file)
    except FileNotFoundError:
        columns = ['Employee ID', 'Name', 'Department', 'Phone', 'Email', 'Assigned Assets']
        return pd.DataFrame(columns=columns)

def save_employees(df):
    df.to_excel(employee_file, index=False)

# Load employees data
employees = load_employees()

# Streamlit App Layout
st.title("Employee Management System")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["View Employees", "Add Employee", "Delete Employee"])

if menu == "View Employees":
    st.header("📋 Employee Register")
    st.dataframe(employees)

    search_option = st.selectbox("Search by", ["Employee ID", "Name", "Department"])
    search_value = st.text_input(f"Enter {search_option}")

    if st.button("Search"):
        filtered_employees = employees[employees[search_option].astype(str).str.contains(search_value, case=False, na=False)]
        st.write(f"Search Results for {search_option}: {search_value}")
        st.dataframe(filtered_employees)

elif menu == "Add Employee":
    st.header("➕ Add New Employee")
    new_employee = {}
    for col in ['Employee ID', 'Name', 'Department', 'Phone', 'Email', 'Assigned Assets']:
        new_employee[col] = st.text_input(f"{col}")

    if st.button("Add Employee"):
        employees = employees.append(new_employee, ignore_index=True)
        save_employees(employees)
        st.success("✅ Employee added successfully!")

elif menu == "Delete Employee":
    st.header("❌ Delete Employee")
    employee_id = st.text_input("Enter Employee ID to Delete")

    if st.button("Delete Employee"):
        initial_rows = len(employees)
        employees = employees[employees['Employee ID'] != employee_id]
        if len(employees) < initial_rows:
            save_employees(employees)
            st.success(f"✅ Employee with ID {employee_id} deleted.")
        else:
            st.warning(f"⚠️ Employee with ID {employee_id} not found.")

st.sidebar.text("Employee Management App v1.0")
