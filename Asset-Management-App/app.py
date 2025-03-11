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

df_assets = load_data(gdrive_url)
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
        emp_id = st.selectbox("Select Employee ID to Delete", df_employees['Employee ID'])
        if st.button("Delete Employee"):
            df_employees = df_employees[df_employees['Employee ID'] != emp_id]
            df_employees.to_excel(EMPLOYEE_FILE, index=False)
            st.success(f"Employee {emp_id} deleted successfully!")

            # Reload the updated file
            df_employees = pd.read_excel(EMPLOYEE_FILE)
            st.dataframe(df_employees)

# ----------------- ASSET REPORTS PAGE -----------------
with tabs[2]:
    st.header("Asset Reports")

    if df_assets is not None:
        # Asset Tracking
        st.subheader("📍 Asset Tracking - Where are the assets?")
        st.dataframe(df_assets[['Asset Description', 'Current Location', 'Responsible officer']])

        # Condition Monitoring
        st.subheader("⚠️ Condition Monitoring - Assets in Poor Condition")
        poor_assets = df_assets[df_assets['Asset condition'].str.lower() == 'poor']
        st.dataframe(poor_assets[['Asset Description', 'Current Location', 'Responsible officer']])

        # Financing Insights
        st.subheader("💰 Financing Insights - Asset Funding Sources")
        financing_report = df_assets.groupby('Financed by/ source of funds')['Asset Description'].count().reset_index()
        financing_report.columns = ['Source of Funds', 'Number of Assets']
        st.dataframe(financing_report)

        # Optional - Simple Visualization
        st.bar_chart(financing_report.set_index('Source of Funds'))
    else:
        st.error("Failed to load asset register data.")
