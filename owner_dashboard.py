import streamlit as st
from database import connect


def show_dashboard():
    st.title("Owner Dashboard")
    conn = connect()
    cur = conn.cursor()

    # Section: Add a Car
    st.header("Add a Car")
    car_number = st.text_input("Car Number Plate")
    model = st.text_input("Car Model")
    seats = st.number_input("No. Of Seats", min_value=1, step=1)
    car_type = st.selectbox("Car Type", ["Premio", "Corolla", "X Corolla", "Noah", "Wagon", "Truck"])  # Added Car Type Selection
    availability_status = st.selectbox("Availability Status", ["Available", "Not Available"])  # Added Availability Status Selection

    if st.button("Add Car"):
        if not all([car_number, model, seats, car_type, availability_status]):
            st.error("Please fill in all the fields.")
        else:
            try:
                # Insert car details into the Car table
                cur.execute("""
                    INSERT INTO car (car_number, model, seats, car_owner_id, availability_status, car_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (car_number, model, seats, st.session_state.user_id, availability_status, car_type))
                conn.commit()
                st.success(f"Car {model} ({car_type}) added successfully with status {availability_status}!")
            except Exception as e:
                conn.rollback()
                st.error(f"An error occurred: {e}")

    # Section: View Your Cars
    st.header("View Your Cars")
    cur.execute("""
        SELECT car_number, model, seats, availability_status
        FROM car 
        WHERE car_owner_id = %s
    """, (st.session_state.user_id,))
    cars = cur.fetchall()

    # Display the cars
    count = 1
    for car_number, model, seats, availability_status, car_type in cars:
        st.write(f"{count}. Car Number: {car_number}")
        st.write(f"   Model: {model}")
        st.write(f"   Type: {car_type}")
        st.write(f"   Seats: {seats}")
        st.write(f"   Status: {availability_status}")
        st.markdown("---")
        count += 1

    conn.close()
