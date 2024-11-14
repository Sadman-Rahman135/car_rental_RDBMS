import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB server
connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)

# Access the database and collections
db = client['car_rent']
customer_collection = db['Customer']
driver_collection = db['Driver']
admin_collection = db['Admin']

# Streamlit UI for Role Selection
st.title("Car Rental System 🚗")

# Sidebar for role selection
st.sidebar.title("User Role Selection")
role = st.sidebar.selectbox("Select your role", ["👨‍💼 Admin", "🧑‍🤝‍🧑 Customer", "🚚 Driver"])

if role == "🧑‍🤝‍🧑 Customer":
    # Customer Login or Registration
    st.markdown("### Welcome to our car rental app! 🧑‍🤝‍🧑")
    st.markdown("<small>If you have an account, then Login or select Registration.</small>", unsafe_allow_html=True)

    customer_action = st.radio("Choose an action", ["Login", "Registration"])

    if customer_action == "Registration":
        st.header("Customer Registration")

        # Input fields for customer data
        customer_id = st.text_input("Customer ID")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        account_status = st.selectbox("Account Status", ["active", "inactive"])

        # Submit button
        if st.button("Register"):
            # Check if all fields are filled
            if not all([customer_id, first_name, last_name, email, password, phone, address, account_status]):
                st.error("Please fill in all the fields.")
            else:
                # Create a dictionary for the customer data
                customer_data = {
                    "customer_id": customer_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password,
                    "phone": phone,
                    "address": address,
                    "account_status": account_status
                }

                # Insert the data into the Customer collection
                try:
                    customer_collection.insert_one(customer_data)
                    st.success("Customer registered successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif customer_action == "Login":
        st.header("Customer Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Check credentials in the database
            customer = customer_collection.find_one({"email": login_email, "password": login_password})
            if customer:
                st.success(f"Welcome back, {customer['first_name']}!")
            else:
                st.error("Invalid email or password.")

elif role == "🚚 Driver":
    # Driver Login or Registration
    st.markdown("### Welcome to our car rental app! 🚚")
    st.markdown("You will be providing service for the customers who are travelling long distance.")
    st.markdown("<small>If you have an account, then Login or select Registration.</small>", unsafe_allow_html=True)

    driver_action = st.radio("Choose an action", ["Login", "Registration"])

    if driver_action == "Registration":
        st.header("Driver Registration")

        # Input fields for driver data
        driver_id = st.text_input("Driver ID")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        location = st.text_input("Location")
        license_number = st.text_input("License Number")
        account_status = st.selectbox("Account Status", ["active", "inactive"])

        # Submit button
        if st.button("Register"):
            # Check if all fields are filled
            if not all([driver_id, first_name, last_name, email, password, phone, address, location, license_number, account_status]):
                st.error("Please fill in all the fields.")
            else:
                # Create a dictionary for the driver data
                driver_data = {
                    "driver_id": driver_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password,
                    "phone": phone,
                    "address": address,
                    "location": location,
                    "license_number": license_number,
                    "account_status": account_status
                }

                # Insert the data into the Driver collection
                try:
                    driver_collection.insert_one(driver_data)
                    st.success("Driver registered successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif driver_action == "Login":
        st.header("Driver Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Check credentials in the database
            driver = driver_collection.find_one({"email": login_email, "password": login_password})
            if driver:
                st.success(f"Welcome back, {driver['first_name']}!")
            else:
                st.error("Invalid email or password.")

elif role == "👨‍💼 Admin":
    # Admin Login
    st.header("Admin Login")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check credentials in the database
        admin = admin_collection.find_one({"email": login_email, "password": login_password})
        if admin:
            st.success(f"Welcome back, Admin {admin['username']}!")
        else:
            st.error("Invalid email or password.")
