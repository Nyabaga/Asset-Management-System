import streamlit as st
import pandas as pd
import os
from pathlib import Path
from PIL import Image
import chardet
import requests

# ===================== LOAD DATA FILES =====================
EMPLOYEE_FILE = Path("employees.xlsx")

# Ensure Employee File Exists
if not EMPLOYEE_FILE.exists():
    df_employees = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Phone', 'Email'])
    df_employees.to_excel(EMPLOYEE_FILE, index=False)

# Detect Encoding for Assets File
with open("Cleaned_Asset_Register.csv", "rb") as f:
    raw_data = f.read()
    detected_encoding = chardet.detect(raw_data)["encoding"]

# Google Drive file ID for Assets
file_id = "1a7FV29v03RPc6gzfCUkNyKov-lhvjVSr"
gdrive_url = f"https://drive.google.com/uc?export=download&id={file_id}"

@st.cache_data
def load_data(url, encoding):
    """ Load asset register data from Google Drive """
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(pd.io.common.StringIO(response.text), encoding=encoding)
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

# Load Employees
df_employees = pd.read_excel(EMPLOYEE_FILE)

# Load Assets
df_assets = load_data(gdrive_url, detected_encoding)

# ===================== NAVIGATION TABS AT THE TOP =====================
tabs = st.tabs(["🏠 Home", "👥 Employee Management", "📊 Asset Reports"])

# ----------------- HOME PAGE -----------------
with tabs[0]:
    st.title("Welcome to Asset Management System")

    image_path = Path("header_logo.png")
    if image_path.exists():
        st.image(image_path, use_container_width=True)
    else:
        st.error("Image file not found! Please check the path.")

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

    st.info("Use the tabs at the top to navigate.")

# ----------------- EMPLOYEE MANAGEMENT PAGE -----------------
with tabs[1]:
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
                new_employee = pd.DataFrame([{
                    'Employee ID': emp_id,
                    'Name': name,
                    'Department': department,
                    'Phone': phone,
                    'Email': email
                }])

                df_employees = pd.concat([df_employees, new_employee], ignore_index=True)
                df_employees.to_excel(EMPLOYEE_FILE, index=False)
                st.success(f"Employee {name} added successfully!")

                # Reload the updated file
                df_employees = pd.read_excel(EMPLOYEE_FILE)
                st.dataframe(df_employees)

    elif action == "Delete Employee":
        emp_id = st.selectbox("Select Employee ID to Delete", df_emp
