import streamlit as st
import bcrypt
from database import create_user_customer, create_user_driver, create_user_CarOwner, authenticate_user
from email_verify import send_verification_email,verify_code,generate_verification_code
from utils import validate_email, validate_phone
def registerCustomer():  #Customer Registration
    st.title("Customer Registration")
     # Input fields for customer data
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    account_status = st.selectbox("Account Status", ["active", "inactive"])



    if st.button("Register"):
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"Hashed Password length : {len(hashed_pw)}")
        print(f"Hashed Password : {hashed_pw}")
        if not all([first_name, last_name, email, password, phone, address, account_status]):
            st.error("Please fill in all the fields.")
        elif not validate_phone(phone):
            st.error("Incorrect phone format")
        elif not validate_email(email):
            st.error("Incorrect email format")
        else:
            try:
                create_user_customer(first_name, last_name, email, hashed_pw, phone, address, account_status)
                st.success("Customer registered successfully!")
                st.session_state.logged_in = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

def registerDriver():  #Driver registration
    st.title("Driver Registration")
     # Input fields for customer data
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    location = st.text_input("Location(City)")
    license_number = st.text_input("License Number")
    account_status = st.selectbox("Account Status", ["active", "inactive"])



    if st.button("Register"):
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        st.write(f"Hashed Password Length: {len(hashed_pw)}")

        if not all([first_name, last_name, email, password, phone, address, location, license_number, account_status]):
                st.error("Please fill in all the fields.")
        elif not validate_phone(phone):
            st.error("Incorrect phone format")
        elif not validate_email(email):
            st.error("Incorrect email format")
        else:
            try:
                create_user_customer(first_name, last_name, email, hashed_pw, phone, address,
                                        account_status)
                st.success("Customer registered successfully!")
                st.session_state.logged_in = True
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
        # else:
        #     try:
        #         create_user_driver(first_name, last_name, email, hashed_pw, phone, address, location, license_number, account_status)
        #         st.success("Driver registered successfully!")
        #         st.session_state.logged_in = True
        #     except Exception as e:
        #         st.error(f"An error occurred: {e}")

def registerCarOwner(): # Car owner registration
    st.title("Car Owner Registration")
     # Input fields for customer data
    first_name = st.text_input("First Name ")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    location = st.text_input("Location(City)")
    account_status = st.selectbox("Account Status", ["active", "inactive"])



    if st.button("Register"):
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        st.write(f"Hashed Password Length: {len(hashed_pw)}")
        if not all([first_name, last_name, email, password, phone, address, location, account_status]):
                st.error("Please fill in all the fields.")
        elif not validate_phone(phone):
            st.error("Incorrect phone format")
        elif not validate_email(email):
            st.error("Incorrect email format")
        else:
            try:
                create_user_CarOwner(first_name, last_name, email, hashed_pw, phone, address, location, account_status)
                st.success("Car Owner registered successfully!")
                st.session_state.logged_in = True
            except Exception as e:
                st.error(f"An error occurred: {e}")

def login(role):
    st.title(f"{role} Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        table_name = get_table_name(role)
        user = authenticate_user(table_name, email, password)

        if user is None:
            st.error("User not found")
            return
        
        stored_hash = user[1]
        if not stored_hash:
            st.error("Stored password hash is missing")
            return
        
        if table_name == 'admin':
            if user and user[1] == password:
                st.session_state.user_id = user[0]
                st.session_state.role = role
                st.session_state.logged_in = True
                st.session_state.current_page = "dashboard"  # Set to dashboard
                st.success("Logged in as Admin!")
            else:
                st.error("Invalid credentials.")
            return
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                st.session_state.user_id = user[0]
                st.session_state.role = role
                st.session_state.logged_in = True
                st.session_state.current_page = "dashboard"  # Set to dashboard
                st.success(f"Logged in as {role}!")
            else:
                st.error("Invalid credentials.")
        except ValueError as e:
            st.error(f"Password verification error: {e}")

def get_table_name(role):
    return {
        "👨‍💼 Admin": "admin",
        "🚗 Car Owner": "car_owner",
        "🧑‍🤝‍🧑 Customer": "customer",
        "🚚 Driver": "driver"
    }[role]
