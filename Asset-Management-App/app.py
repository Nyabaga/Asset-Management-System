import streamlit as st
import pandas as pd
import os
from pathlib import Path
from PIL import Image
import chardet
import requests
from io import StringIO

# ===================== LOAD DATA FILES =====================
EMPLOYEE_FILE = Path("employees.xlsx")

# Ensure Employee File Exists
if not EMPLOYEE_FILE.exists():
    df_employees = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Phone', 'Email'])
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
st.markdown("""
    <style>
        .nav-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Home"):
        st.query_params.clear()
        st.rerun()
with col2:
    if st.button("👥 Employee Management"):
        st.query_params["page"] = "employees"
        st.rerun()
with col3:
    if st.button("📊 Asset Reports"):
        st.query_params["page"] = "assets"
        st.rerun()

# Get current page
default_page = "home"
current_page = st.query_params.get("page", default_page)

# ===================== HOME PAGE =====================
if current_page == "home":
    st.title("Welcome to Asset Management System")
    st.write("""
        ### About the Organization
        **Ministry of East African Community, the ASALs and Regional Development**  
        Responsible for asset management and tracking to ensure accountability and proper resource utilization.

        ### About This App
        - 📍 **Track Assets:** See where assets are and who is responsible.  
        - 🏢 **Monitor Asset Condition:** Identify assets in poor condition.  
        - 💰 **Analyze Financing:** Check asset funding sources.  
        - 👥 **Manage Employees:** Add, search, and delete employees.  
        - 📈 **Works on desktop & mobile**  

        ### Contact Us
        📧 Email: ps@asals.go.ke  
        📞 Phone: +254-3317641-7  
        🌐 [Visit Our Website](https://www.asalrd.go.ke/)
    """)

# ===================== EMPLOYEE MANAGEMENT PAGE =====================
if current_page == "employees":
    st.header("Employee Management")

    action = st.radio("Choose Action", ["View Employees", "Add Employee", "Delete Employee"])

    if action == "View Employees":
        st.dataframe(df_employees)

    elif action == "Add Employee":
        with st.form("Add Employee Form"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            department = st.text_input("Department")
            phone = st.text_input("Phone")
            email = st.text_input("Email")

            submitted = st.form_submit_button("Add Employee")
            if submitted:
                new_employee = pd.DataFrame([{ 'Employee ID': emp_id, 'Name': name, 'Department': department, 'Phone': phone, 'Email': email }])
                df_employees = pd.concat([df_employees, new_employee], ignore_index=True)
                df_employees.to_excel(EMPLOYEE_FILE, index=False)
                st.success(f"Employee {name} added successfully!")
                st.rerun()

    elif action == "Delete Employee":
        emp_id = st.selectbox("Select Employee ID to Delete", df_employees['Employee ID'])
        if st.button("Delete Employee"):
            df_employees = df_employees[df_employees['Employee ID'] != emp_id]
            df_employees.to_excel(EMPLOYEE_FILE, index=False)
            st.success(f"Employee {emp_id} deleted successfully!")
            st.rerun()

# ===================== ASSET REPORTS PAGE =====================
if current_page == "assets":
    st.header("Asset Reports")

    if df_assets is not None:
        # Asset Tracking
        st.subheader("📍 Asset Tracking - Search for an Employee")
        search_query = st.text_input("Enter Employee Name or ID")
        if search_query and 'Responsible officer' in df_assets.columns:
            filtered_assets = df_assets[(df_assets['Responsible officer'].str.contains(search_query, case=False, na=False)) | 
                                        (df_assets['Employee ID'].astype(str) == search_query)]
            if not filtered_assets.empty:
                st.dataframe(filtered_assets[['Asset Description', 'Current Location', 'Responsible officer']])
            else:
                st.warning("No assets found for this employee.")

        # Condition Monitoring
        st.subheader("⚠️ Condition Monitoring - Assets in Poor Condition")
        if 'Asset condition' in df_assets.columns:
            poor_assets = df_assets[df_assets['Asset condition'].str.lower() == 'poor']
            st.dataframe(poor_assets[['Asset Description', 'Current Location', 'Responsible officer']])
        else:
            st.warning("Column 'Asset condition' not found in dataset.")

        # Financing Insights
        st.subheader("💰 Financing Insights - Asset Funding Sources")
        if 'Financed by/ source of funds' in df_assets.columns:
            financing_report = df_assets.groupby('Financed by/ source of funds')['Asset Description'].count().reset_index()
            financing_report.columns = ['Source of Funds', 'Number of Assets']
            st.dataframe(financing_report)
            st.bar_chart(financing_report.set_index('Source of Funds'))
        else:
            st.warning("Column 'Financed by/ source of funds' not found in dataset.")
    else:
        st.error("Failed to load asset register data.")
