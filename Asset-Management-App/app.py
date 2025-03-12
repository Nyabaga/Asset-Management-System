import streamlit as st
import pandas as pd
import os
from pathlib import Path
from io import StringIO
import requests

# ===================== LOAD DATA FILES =====================
EMPLOYEE_FILE = Path("employees.xlsx")

# Ensure Employee File Exists
if not EMPLOYEE_FILE.exists():
    df_employees = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Phone', 'Email', 'Assigned Assets'])
    df_employees.to_excel(EMPLOYEE_FILE, index=False)

file_id = "1a7FV29v03RPc6gzfCUkNyKov-lhvjVSr"
gdrive_url = f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    else:
        st.error("Failed to fetch data from Google Drive")

# Load Employees
df_employees = pd.read_excel(EMPLOYEE_FILE)

# Load Assets
df_assets = load_data(gdrive_url)

# ===================== NAVIGATION MENU =====================
st.image("header_logo.png", use_container_width=True)
st.title("Asset Management System")
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "👥 Employee Management", "📊 Asset Reports"])

# ===================== HOME PAGE =====================
if page == "🏠 Home":
    st.header("Welcome to Asset Management System")
    st.write("""
        ### About the Organization
        **Ministry of East African Community, the ASALs and Regional Development**  
        Responsible for asset management and tracking to ensure accountability and proper resource utilization.

        ### About This App
        - 📍 **Track Assets:** See where assets are and who is responsible.  
        - 🏢 **Monitor Asset Condition:** Identify assets in poor condition.  
        - 💰 **Analyze Financing:** Check asset funding sources.  
        - 👥 **Manage Employees:** Add, edit, search, and delete employees.  
        - 📈 **Works on desktop & mobile**  

        ### Contact Us
        📧 Email: ps@asals.go.ke  
        📞 Phone: +254-3317641-7  
        🌐 [Visit Our Website](https://www.asalrd.go.ke/)
    """)

# ===================== EMPLOYEE MANAGEMENT PAGE =====================
if page == "👥 Employee Management":
    st.header("Employee Management")
    action = st.radio("Choose Action", ["View Employees", "Add Employee", "Edit Employee", "Delete Employee"])

    if action == "View Employees":
        st.subheader("Employee List")
        st.dataframe(df_employees)
    
    elif action == "Add Employee":
        with st.form("Add Employee Form"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            department = st.text_input("Department")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            assigned_assets = st.text_input("Assigned Assets")
            submitted = st.form_submit_button("Add Employee")
            if submitted:
                new_employee = pd.DataFrame([{ 'Employee ID': emp_id, 'Name': name, 'Department': department, 'Phone': phone, 'Email': email, 'Assigned Assets': assigned_assets }])
                df_employees = pd.concat([df_employees, new_employee], ignore_index=True)
                df_employees.to_excel(EMPLOYEE_FILE, index=False)
                st.success(f"Employee {name} added successfully!")
                st.rerun()

    elif action == "Edit Employee":
        st.subheader("Edit Employee Details")
        employee_ids = df_employees["Employee ID"].astype(str).tolist()
        selected_id = st.selectbox("Select Employee ID", employee_ids)
        employee = df_employees[df_employees["Employee ID"].astype(str) == selected_id].iloc[0]
        name = st.text_input("Name", employee["Name"])
        department = st.text_input("Department", employee["Department"])
        phone = st.text_input("Phone", str(employee["Phone"]))
        email = st.text_input("Email", employee["Email"])
        assigned_assets = st.text_input("Assigned Assets", employee["Assigned Assets"])
        if st.button("Save Changes"):
            df_employees.loc[df_employees["Employee ID"].astype(str) == selected_id, ["Name", "Department", "Phone", "Email", "Assigned Assets"]] = [name, department, phone, email, assigned_assets]
            df_employees.to_excel(EMPLOYEE_FILE, index=False)
            st.success("Employee details updated successfully!")
            st.rerun()

    elif action == "Delete Employee":
        emp_id = st.selectbox("Select Employee ID to Delete", df_employees['Employee ID'])
        if st.button("Delete Employee"):
            df_employees = df_employees[df_employees['Employee ID'] != emp_id]
            df_employees.to_excel(EMPLOYEE_FILE, index=False)
            st.success(f"Employee {emp_id} deleted successfully!")
            st.rerun()

# ===================== ASSET REPORTS PAGE =====================
if page == "📊 Asset Reports":
    st.header("Asset Reports")
    if df_assets is not None:
        st.subheader("📍 Asset Tracking - Search for an Employee")
        search_query = st.text_input("Enter Employee Name or ID")
        if search_query:
            if 'Responsible officer' in df_assets.columns and 'Employee ID' in df_assets.columns:
                filtered_assets = df_assets[(df_assets['Responsible officer'].str.contains(search_query, case=False, na=False)) | 
                                            (df_assets['Employee ID'].astype(str) == search_query)]
                if not filtered_assets.empty:
                    st.dataframe(filtered_assets[['Asset Description', 'Current Location', 'Responsible officer']])
                else:
                    st.warning("No assets found for this employee.")
            else:
                st.error("Missing 'Employee ID' or 'Responsible officer' column in the dataset.")
    else:
        st.error("Failed to load asset register data.")
