import streamlit as st
import psycopg2
from database import connect
import uuid


def show_dashboard():
    st.title("Admin Dashboard")

    # Navigation within Customer Dashboard
    page = st.sidebar.selectbox("Select Option", ["View Car Lists", "View Driver Lists", "Profile"])

    if page == "View Car Lists":
        view_cars()
    elif page == "View Driver Lists":
        view_drivers()
    elif page == "Profile":
        st.write("Customer Profile Page (Coming Soon).")
    
def view_drivers():
    st.header("All Cars")

    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch cars with availability status "Available"
        cur.execute("SELECT first_name, last_name, email, phone, address, location, license_number, account_status FROM driver")
        drivers = cur.fetchall()

        if drivers:
            count = 1
            
            for first_name, last_name, email, phone, address, location, license_number, account_status in drivers:
                st.write(f"{count}. Driver Name: {first_name} {last_name}")
                st.write(f"         E-mail: {email}")
                st.write(f"         Phone Number: {phone}")
                st.write(f"         Address: {address}")
                st.write(f"         Location: {location}")
                st.write(f"         License Number: {license_number}")
                st.write(f"         Account Status: {account_status}")
                st.markdown("-----------")
                count += 1           
        else:
            st.info("No Drivers available.")
        conn.close()
    except Exception as e:                        
        st.error(f"An error occurred: {e}")



def view_cars():
    st.header("All Cars")

    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch cars with availability status "Available"
        cur.execute("SELECT car_number, model, car_type, seats FROM car")
        cars = cur.fetchall()

        if cars:
            count = 1
            
            for car_number, model, seats, availability_status, car_type in cars:
                st.write(f"{count}. Car Number: {car_number}")
                st.write(f"   Model: {model}")
                st.write(f"   Type: {car_type}")
                st.write(f"   Seats: {seats}")
                st.write(f"   Status: {availability_status}")
                st.markdown("---")
                count += 1
           
               
                      
        else:
            st.info("No cars available.")
        conn.close()
    except Exception as e:                        
        st.error(f"An error occurred: {e}")
