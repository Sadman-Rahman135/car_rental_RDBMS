import streamlit as st
import psycopg2
from psycopg2 import sql
import uuid


# Connect to PostgreSQL server
connection = psycopg2.connect(
    host="localhost",
    database="car_rent",
    user="postgres",
    password="sahil",
    port=5000
)
cursor = connection.cursor()

# Custom CSS for background
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"]
{

background-color: #1e0d0d;
opacity: 1;
background-size: 5px 5px;
background-image: repeating-linear-gradient(45deg, #360b0b 0, #360b0b 0.5px, #1e0d0d 0, #1e0d0d 50%);
}

</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Streamlit UI for Role Selection
st.title("Car Rental System 🚗")

# Sidebar for role selection
st.sidebar.title("User Role Selection")
role = st.sidebar.selectbox("Select your role", ["👨‍💼 Admin","🧑‍🤝‍🧑 Car Owner", "🧑‍🤝‍🧑 Customer", "🚚 Driver"])

if role == "🧑‍🤝‍🧑 Car Owner":
    # Customer Login or Registration
    st.markdown("### Welcome to our car rental app! 🧑‍🤝‍🧑")
    st.markdown("<small>If you have an account, then Login or select Registration.</small>", unsafe_allow_html=True)

    carOwner_action = st.radio("Choose an action", ["Login", "Registration"])

    if carOwner_action == "Registration":
        st.header("Customer Registration")

        # Input fields for customer data
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        location = st.text_area("Location(City)")
        account_status = st.selectbox("Account Status", ["active", "inactive"])

        # Submit button
        if st.button("Register"):
            # Check if all fields are filled
            if not all([first_name, last_name, email, password, phone, address, location, account_status]):
                st.error("Please fill in all the fields.")
            else:
                # Generate a unique customer ID
                owner_id = str(uuid.uuid4())

                # Insert the data into the Customer table
                try:
                    cursor.execute(
                        "INSERT INTO Car_Owner (owner_id, first_name, last_name, email, password, phone, address, location, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (owner_id, first_name, last_name, email, password, phone, address, account_status)
                    )
                    connection.commit()
                    st.success("Car Owner registered successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif carOwner_action == "Login":
        st.header("Car Owner Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Check credentials in the database
            cursor.execute("SELECT * FROM Car_Owner WHERE email=%s AND password=%s", (login_email, login_password))
            carOwner = cursor.fetchone()
            if carOwner:
                st.success(f"Welcome back, {carOwner[1]}!")
            else:
                st.error("Invalid email or password.")

elif role == "🧑‍🤝‍🧑 Customer":
    # Customer Login or Registration
    st.markdown("### Welcome to our car rental app! 🧑‍🤝‍🧑")
    st.markdown("<small>If you have an account, then Login or select Registration.</small>", unsafe_allow_html=True)

    customer_action = st.radio("Choose an action", ["Login", "Registration"])

    if customer_action == "Registration":
        st.header("Customer Registration")

        # Input fields for customer data
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
            if not all([first_name, last_name, email, password, phone, address, account_status]):
                st.error("Please fill in all the fields.")
            else:
                # Generate a unique customer ID
                customer_id = str(uuid.uuid4())

                # Insert the data into the Customer table
                try:
                    cursor.execute(
                        "INSERT INTO Customer (customer_id, first_name, last_name, email, password, phone, address, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (customer_id, first_name, last_name, email, password, phone, address, account_status)
                    )
                    connection.commit()
                    st.success("Customer registered successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif customer_action == "Login":
        st.header("Customer Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Check credentials in the database
            cursor.execute("SELECT * FROM Customer WHERE email=%s AND password=%s", (login_email, login_password))
            customer = cursor.fetchone()
            if customer:
                st.success(f"Welcome back, {customer[1]}!")
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
            if not all([first_name, last_name, email, password, phone, address, location, license_number, account_status]):
                st.error("Please fill in all the fields.")
            else:
                # Generate a unique driver ID
                driver_id = str(uuid.uuid4())

                # Insert the data into the Driver table
                try:
                    cursor.execute(
                        "INSERT INTO Driver (driver_id, first_name, last_name, email, password, phone, address, location, license_number, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (driver_id, first_name, last_name, email, password, phone, address, location, license_number, account_status)
                    )
                    connection.commit()
                    st.success("Driver registered successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    elif driver_action == "Login":
        st.header("Driver Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Check credentials in the database
            cursor.execute("SELECT * FROM Driver WHERE email=%s AND password=%s", (login_email, login_password))
            driver = cursor.fetchone()
            if driver:
                st.success(f"Welcome back, {driver[1]}!")
            else:
                st.error("Invalid email or password.")

elif role == "👨‍💼 Admin":
    # Admin Login
    st.header("Admin Login")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check credentials in the database
        cursor.execute("SELECT * FROM Admin WHERE email=%s AND password=%s", (login_email, login_password))
        admin = cursor.fetchone()
        if admin:
            st.success(f"Welcome back, Admin {admin[1]}!")
        else:
            st.error("Invalid email or password.")

# Close the database connection when done
cursor.close()
connection.close()


