import streamlit as st
from database import connect
from utils import display_profile_update

def show_dashboard():
    st.title("Car Owner Dashboard")
    conn = connect()
    cur = conn.cursor()
    # Back to Home button
    if st.sidebar.button("Back to Home"):
        st.session_state.current_page = "home"
        st.session_state.logged_in = False
        st.session_state.role = None
   

    if st.button("Refresh Dashboard"):
        st.rerun()

    page = st.sidebar.selectbox(
        "Navigation",
        [
            "Owner Profile",
            "Add a Car",
            "View Your Cars",
            "Rental History",
            "Earnings",
            "Car Performance Analytics",
            "Past Completed Rentals",
            "Car Usage Trends"
        ]
    )

    if page == "Owner Profile":
        show_owner_profile(cur, st.session_state.user_id)
    elif page == "Add a Car":
        add_car(cur, conn)
    elif page == "View Your Cars":
        view_cars(cur, st.session_state.user_id, conn)
    elif page == "Rental History":
        show_rental_history(cur, st.session_state.user_id)
    elif page == "Earnings":
        show_earnings(cur, st.session_state.user_id)
    elif page == "Car Performance Analytics":
        show_performance_analytics(cur, st.session_state.user_id)
    elif page == "Past Completed Rentals":
        show_past_completed_rentals(cur, st.session_state.user_id)
    elif page == "Car Usage Trends":
        show_car_usage_trends(cur, st.session_state.user_id)

    conn.close()

def show_owner_profile(cur, owner_id):
    st.header("👤 Owner Profile")
    cur.execute("""
        SELECT CONCAT(first_name, ' ', last_name) AS full_name, 
               email, phone, address, location, account_status 
        FROM Car_Owner 
        WHERE car_owner_id = %s
    """, (owner_id,))
    profile = cur.fetchone()
    if profile:
        full_name, email, phone, address, location, status = profile
        st.write(f"**Name:** {full_name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone:** {phone}")
        st.write(f"**Address:** {address}")
        st.write(f"**Location:** {location}")
        st.write(f"**Status:** {'🟢 Active' if status == 'active' else '🔴 Inactive'}")
    else:
        st.error("Owner profile not found.")

def add_car(cur, conn):
    st.header("🚗 Add a Car")
    car_number = st.text_input("Car Number Plate")
    model = st.text_input("Car Model")
    seats = st.number_input("No. Of Seats", min_value=1, step=1)
    car_type = st.selectbox("Car Type", ["Premio", "Corolla", "X Corolla", "Noah", "Wagon", "Truck"])
    availability_status = st.selectbox("Availability Status", ["Available", "Not Available"])

    if st.button("Add Car"):
        if not all([car_number, model, seats, car_type, availability_status]):
            st.error("Please fill in all the fields.")
        else:
            try:
                cur.execute("""
                    INSERT INTO Car (car_number, model, seats, car_owner_id, availability_status, car_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (car_number, model, seats, st.session_state.user_id, availability_status, car_type))
                conn.commit()
                st.success(f"Car {model} ({car_type}) added successfully with status {availability_status}!")
            except Exception as e:
                conn.rollback()
                st.error(f"An error occurred: {e}")

def view_cars(cur, owner_id, conn):
    st.header("🚗 View Your Cars")
    cur.execute("""
        SELECT car_number, model, seats, availability_status, car_type
        FROM Car 
        WHERE car_owner_id = %s
    """, (owner_id,))
    cars = cur.fetchall()

    if cars:
        count = 1
        for car_number, model, seats, availability_status, car_type in cars:
            st.write(f"{count}. Car Number: {car_number}")
            st.write(f"   Model: {model}")
            st.write(f"   Type: {car_type}")
            st.write(f"   Seats: {seats}")
            st.write(f"   Status: {availability_status}")
            new_status = st.selectbox(
                "Change Availability",
                ["Available", "Not Available"],
                index=0 if availability_status == "Available" else 1,
                key=f"status_{car_number}"
            )
            if st.button("Update Availability", key=f"update_{car_number}"):
                try:
                    cur.execute("CALL update_car_availability(%s, %s)", (car_number, new_status))
                    conn.commit()
                    st.success(f"Car {car_number} availability updated to {new_status}!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error: {str(e)}")
            st.markdown("---")
            count += 1
    else:
        st.info("No cars found.")

def show_rental_history(cur, owner_id):
    st.header("📅 Rental History")
    cur.execute("SELECT car_number, model FROM Car WHERE car_owner_id = %s", (owner_id,))
    cars = cur.fetchall()
    car_options = [f"{car[0]} - {car[1]}" for car in cars]
    selected_car = st.selectbox("Select Car", car_options) if cars else None

    if selected_car and st.button("Show Rental History"):
        car_number = selected_car.split(" - ")[0]
        cur.execute("""
            WITH RECURSIVE rental_history AS (
                SELECT rental_id, request_id, car_number_plate, pickup_date, dropoff_date
                FROM Rental
                WHERE car_number_plate = %s
                UNION ALL
                SELECT r.rental_id, r.request_id, r.car_number_plate, r.pickup_date, r.dropoff_date
                FROM Rental r
                INNER JOIN rental_history rh ON r.car_number_plate = rh.car_number_plate
                WHERE r.pickup_date > rh.dropoff_date
            )
            SELECT * FROM rental_history ORDER BY pickup_date
        """, (car_number,))
        history = cur.fetchall()
        if history:
            for row in history:
                st.write(f"Rental ID: {row[0]}, Request ID: {row[1]}, Dates: {row[3]} to {row[4]}")
        else:
            st.info(f"No rental history found for car {car_number}.")

def show_earnings(cur, owner_id):
    st.header("💰 Earnings")
    cur.execute("SELECT calculate_owner_earnings(%s)", (owner_id,))
    earnings = cur.fetchone()[0]
    st.metric("Total Earnings", f"${earnings or 0:.2f}")

def show_performance_analytics(cur, owner_id):
    st.header("📊 Car Performance Analytics")
    cur.execute("SELECT * FROM car_performance_summary(%s)", (owner_id,))
    metrics = cur.fetchall()
    if metrics:
        for metric, value in metrics:
            st.write(f"{metric}: {value}")
    else:
        st.info("No performance data available.")

def show_past_completed_rentals(cur, owner_id):
    st.header("📜 Past Completed Rentals")
    cur.execute("""
        SELECT r.request_id, c.first_name || ' ' || c.last_name AS customer_name, 
               car.model, r.pickup_date, r.dropoff_date, r.duration
        FROM Request r
        JOIN Car car ON r.car_number_plate = car.car_number
        JOIN Customer c ON r.customer_id = c.customer_id
        WHERE car.car_owner_id = %s AND r.status = 'Completed'
        ORDER BY r.dropoff_date DESC
    """, (owner_id,))
    rentals = cur.fetchall()
    if rentals:
        for request in rentals:
            with st.expander(f"Request ID: {request[0]} - {request[2]}"):
                st.write(f"Customer: {request[1]}")
                st.write(f"Car Model: {request[2]}")
                st.write(f"Pickup Date: {request[3]}")
                st.write(f"Dropoff Date: {request[4]}")
                st.write(f"Duration: {request[5]} hours")
            st.markdown("---")
    else:
        st.info("No past completed rentals found.")

def show_car_usage_trends(cur, owner_id):
    st.header("📈 Car Usage Trends")
    cur.execute("""
        SELECT car.car_type, r.pickup_location, COUNT(r.request_id) AS booking_count
        FROM Car car
        LEFT JOIN Request r ON car.car_number = r.car_number_plate
        WHERE car.car_owner_id = %s
        GROUP BY CUBE(car.car_type, r.pickup_location)
        HAVING COUNT(r.request_id) > 0
        ORDER BY car.car_type, r.pickup_location
    """, (owner_id,))
    trends = cur.fetchall()
    if trends:
        for car_type, location, count in trends:
            st.write(f"Car Type: {car_type or 'All'}, Location: {location or 'All'}, Bookings: {count}")
    else:
        st.info("No usage trends available.")

if __name__ == "__main__":
    show_dashboard()
