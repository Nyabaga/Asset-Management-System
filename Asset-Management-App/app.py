import streamlit as st
import pandas as pd
import os

# Load datasets
EMPLOYEE_FILE = 'employees.xlsx'
ASSET_FILE = 'cleaned_asset_register.xlsx'

# Ensure files exist
if not os.path.exists(EMPLOYEE_FILE):
    df_employees = pd.DataFrame(columns=['Employee ID', 'Name', 'Department', 'Phone', 'Email'])
    df_employees.to_excel(EMPLOYEE_FILE, index=False)

if not os.path.exists(ASSET_FILE):
    st.error(f"Missing file: {ASSET_FILE}. Please upload the cleaned asset file.")
    st.stop()

# Load Data
df_employees = pd.read_excel(EMPLOYEE_FILE)
df_assets = pd.read_excel(ASSET_FILE)

# Sidebar navigation
menu = st.sidebar.selectbox("Select Page", ["Home", "Employee Management", "Asset Reports"])

# ----------------- HOME PAGE -----------------
if menu == "Home":
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="header_logo.png" width="700">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Welcome to Asset Management System")

    st.write("""
    ### About the Organization
    **Ministry of East African Community, the ASALs and Regional Development**  
    State Department for the ASALs and Regional Development is responsible for asset management and tracking to ensure accountability and proper resource utilization.

    ### About This App
    This Asset Management System allows you to:
    - Track your organization's assets (where they are, who’s responsible for them)
    - Monitor asset conditions (which assets are in poor condition)
    - Analyze financing (which source financed which asset)
    - Manage employee records (add, search, and delete employees)

    This system works on both **desktop** and **mobile devices**.

    ### Contact Us
    📧 Email: ps@asals.go.ke  
    📞 Phone: +254-3317641-7 
    🌐 Website: https://www.asalrd.go.ke/
    """)

    st.info("Use the sidebar to navigate to Employee Management or Asset Reports.")

# ----------------- EMPLOYEE MANAGEMENT PAGE -----------------
elif menu == "Employee Management":
    st.header("Employee Management")

    action = st.radio("Choose Action", ["View Employees", "Add Employee", "Delete Employee"])

    if action == "View Employees":
        st.write(df_employees)

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

    elif action == "Delete Employee":
        emp_id = st.selectbox("Select Employee ID to Delete", df_employees['Employee ID'])
        if st.button("Delete Employee"):
            df_employees = df_employees[df_employees['Employee ID'] != emp_id]
            df_employees.to_excel(EMPLOYEE_FILE, index=False)
            st.success(f"Employee {emp_id} deleted successfully!")

# ----------------- ASSET REPORTS PAGE -----------------
elif menu == "Asset Reports":
    st.header("Asset Reports")

    # Asset Tracking
    st.subheader("Asset Tracking - Where are the assets?")
    st.write(df_assets[['Asset Description', 'Current Location', 'Responsible officer']])

    # Condition Monitoring
    st.subheader("Condition Monitoring - Assets in Poor Condition")
    poor_assets = df_assets[df_assets['Asset condition'].str.lower() == 'poor']
    st.write(poor_assets[['Asset Description', 'Current Location', 'Responsible officer']])

    # Financing Insights
    st.subheader("Financing Insights - Asset Funding Sources")
    financing_report = df_assets.groupby('Financed by/ source of funds')['Asset Description'].count().reset_index()
    financing_report.columns = ['Source of Funds', 'Number of Assets']
    st.write(financing_report)

    # Optional - Simple Visualization
    st.bar_chart(financing_report.set_index('Source of Funds'))

