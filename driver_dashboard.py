import streamlit as st
from database import connect
from customer_dashboard import car_rate
from utils import display_profile_update, phone_from_id

def show_dashboard():
    st.title("Driver Dashboard")
    conn = connect()
    cur = conn.cursor()

    # Back to Home button
    if st.sidebar.button("Back to Home"):
        st.session_state.current_page = "home"
        st.session_state.logged_in = False
        st.session_state.role = None

    if st.button("Refresh Dashboard"):
        st.rerun()

    if "user_id" not in st.session_state:
        st.error("Please log in to access the driver dashboard.")
        conn.close()
        return
    driver_id = st.session_state.user_id
    page = st.sidebar.radio(
        "Navigation",
        [
            "Driver Profile",
            "Available Bookings",
            "Current Assignments",
            "Earnings",
            "Booking History Chain",
            "Performance Analytics",
            "Past Completed Bookings",
        ]
    )

    if page == "Driver Profile":
        display_profile_update('driver')
        #show_driver_profile(cur, driver_id)
    elif page == "Available Bookings":
        show_available_bookings(cur, driver_id, conn)
    elif page == "Current Assignments":
        show_current_assignments(cur, driver_id, conn)
    elif page == "Earnings":
        show_earnings(cur, driver_id)
    elif page == "Booking History Chain":
        show_booking_chain(cur, driver_id)
    elif page == "Performance Analytics":
        show_performance_analytics(cur, driver_id)
    elif page == "Past Completed Bookings":
        show_past_completed_bookings(cur, driver_id)

    conn.close()

def show_driver_profile(cur, driver_id):
    st.header("👤 Driver Profile")
    cur.execute("""
        SELECT CONCAT(first_name, ' ', last_name) AS full_name, 
               email, phone, license_number, account_status 
        FROM Driver 
        WHERE driver_id = %s
    """, (driver_id,))
    profile = cur.fetchone()
    if profile:
        full_name, email, phone, license_number, status = profile
        st.write(f"**Name:** {full_name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone:** {phone}")
        st.write(f"**License Number:** {license_number}")
        st.write(f"**Status:** {'🟢 Active' if status == 'active' else '🔴 Inactive'}")
    else:
        st.error("Driver profile not found.")

def show_available_bookings(cur, driver_id, conn):
    st.header("📋 Available Bookings")
    cur.execute("""
        SELECT request_id, customer_id, car_type, pickup_date, dropoff_date, 
               pickup_location, dropoff_location, duration, payment_status, 
               car_number_plate, status
        FROM Request
        WHERE assigned_driver IS NULL AND status = 'Pending'
    """)
    bookings = cur.fetchall()

    if bookings:
        for request in bookings:
            request_id, customer_id, car_type, pickup_date, dropoff_date, pickup_location, dropoff_location, duration, payment_status, car_number_plate, status = request
            rate=car_rate(car_type)
            payment=float(rate)*float(duration)*0.3
            with st.expander(f"Request ID: {request_id} - {car_type}"):
                with st.container():
                    st.markdown(f"<h5 style='color: #34495e;'>🆔 Basic Information</h5>", unsafe_allow_html=True)
                    st.markdown(f"<b>Customer ID:</b> {customer_id}", unsafe_allow_html=True)
                    st.markdown("---")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"<h5 style='color: #34495e;'>🚘 Car & Booking Details</h5>", unsafe_allow_html=True)
                        st.markdown(f"**Car Type:** {car_type}")
                        st.markdown(f"**Pickup Date:** {pickup_date}")
                        st.markdown(f"**Dropoff Date:** {dropoff_date}")
                        st.markdown(f"**Pickup Location:** {pickup_location}")
                        st.markdown(f"**Dropoff Location:** {dropoff_location}")

                    with col2:
                        st.markdown(f"<h5 style='color: #34495e;'>💳 Payment & Status</h5>", unsafe_allow_html=True)
                        st.markdown(f"**Duration:** {duration} hours")
                        st.markdown(f"**Payment:** ${payment}")
                        st.markdown(f"**Payment Status:** {payment_status}")
                        st.markdown(f"**Car Number Plate:** {car_number_plate if car_number_plate else 'Not Assigned'}")
                        st.markdown(f"**Status:** {status}")

                if st.button("Accept Booking", key=f"accept-{request_id}"):
                    try:
                        cur.execute("CALL assign_driver_booking(%s, %s)", (driver_id, request_id))
                        conn.commit()
                        st.success(f"Booking {request_id} accepted!")
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Error accepting booking: {str(e)}")
            st.markdown("---")
    else:
        st.info("No available bookings.")

def show_current_assignments(cur, driver_id, conn):
    st.header("🚗 Current Assignments")
    cur.execute("""
        SELECT request_id, customer_id, car_type, pickup_date, dropoff_date, 
               pickup_location, dropoff_location, duration, payment_status, 
               car_number_plate, status
        FROM Request
        WHERE assigned_driver = %s AND status IN ('Accepted', 'In Progress')
    """, (driver_id,))
    assignments = cur.fetchall()
    if assignments:
        for request in assignments:
            request_id, customer_id, car_type, pickup_date, dropoff_date, pickup_location, dropoff_location, duration, payment_status, car_number_plate, status = request
            rate=car_rate(car_type)
            payment=float(rate)*float(duration)*0.3
            phone=phone_from_id('customer', customer_id)
            # Main container with some nice styling
            with st.expander(f"Request ID: {request_id} - {car_type}"):
                with st.container():
                    
                    # Basic Info
                    st.markdown(f"<h5 style='color: #34495e;'>🆔 Basic Information</h5>", unsafe_allow_html=True)
                    st.markdown(f"<b>Request ID:</b> {request_id}<br><b>Customer ID:</b> {customer_id}", unsafe_allow_html=True)
                    st.markdown("---")

                    # Split detailed info
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"<h5 style='color: #34495e;'>🚘 Car & Booking Details</h5>", unsafe_allow_html=True)
                        st.markdown(f"**Phone:** {phone}")
                        st.markdown(f"**Car Type:** {car_type}")
                        st.markdown(f"**Pickup Date:** {pickup_date}")
                        st.markdown(f"**Dropoff Date:** {dropoff_date}")
                        st.markdown(f"**Pickup Location:** {pickup_location}")
                        st.markdown(f"**Dropoff Location:** {dropoff_location}")

                    with col2:
                        st.markdown(f"<h5 style='color: #34495e;'>💳 Payment & Status</h5>", unsafe_allow_html=True)
                        st.markdown(f"**Duration:** {duration} hours")
                        st.markdown(f"**Payment:** ${payment}")
                        st.markdown(f"**Payment Status:** {payment_status}")
                        st.markdown(f"**Car Number Plate:** {car_number_plate if car_number_plate else 'Not Assigned'}")
                        st.markdown(f"**Status:** {status}")

                    st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Mark as Completed", key=f"complete-{request_id}"):
            try:
                cur.execute("""
                    UPDATE Request 
                    SET status = 'Completed' 
                    WHERE request_id = %s
                    RETURNING car_number_plate
                """, (request_id,))
                car_number = cur.fetchone()[0]
                cur.execute("CALL finalize_booking(%s, %s, %s)", (request_id, driver_id, car_number))
                conn.commit()
                st.success(f"Booking {request_id} marked as completed!")
            except Exception as e:
                conn.rollback()
                st.error(f"Error: {str(e)}")
        st.markdown("---")
    else:
        st.info("No current assignments.")

def show_earnings(cur, driver_id):
    st.header("💰 Earnings")
    cur.execute("SELECT calculate_driver_earnings(%s)", (driver_id,))
    earnings = cur.fetchone()[0]
    st.metric("Total Earnings", f"${earnings or 0:.2f}")

def show_booking_chain(cur, driver_id):
    st.header("📅 Booking History Chain")
    if st.button("Show Booking Chain"):
        cur.execute("SELECT * FROM get_booking_chain(%s)", (driver_id,))
        chain = cur.fetchall()
        if chain:
            for req_id, pickup, dropoff in chain:
                st.write(f"Request ID: {req_id}, From: {pickup}, To: {dropoff}")
        else:
            st.info("No booking history chain found.")

def show_performance_analytics(cur, driver_id):
    st.header("📊 Performance Analytics")
    cur.execute("SELECT * FROM driver_performance_summary(%s)", (driver_id,))
    metrics = cur.fetchall()
    if metrics:
        for metric, value in metrics:
            st.write(f"{metric}: {value}")
    else:
        st.info("No performance data available.")

def show_past_completed_bookings(cur, driver_id):
    st.header("📜 Past Completed Bookings")
    cur.execute("""
        SELECT request_id, customer_id, car_type, pickup_date, dropoff_date, 
               pickup_location, dropoff_location, duration, payment_status, 
               car_number_plate, status
        FROM Request
        WHERE assigned_driver = %s AND status = 'Completed'
        ORDER BY dropoff_date DESC
    """, (driver_id,))
    bookings = cur.fetchall()
    if bookings:
        for request in bookings:
            request_id, customer_id, car_type, pickup_date, dropoff_date, pickup_location, dropoff_location, duration, payment_status, car_number_plate, status = request
            with st.expander(f"Request ID: {request_id} - {car_type}"):
                st.write(f"Customer ID: {customer_id}")
                st.write(f"Car Type: {car_type}")
                st.write(f"Pickup Date: {pickup_date}")
                st.write(f"Dropoff Date: {dropoff_date}")
                st.write(f"Pickup Location: {pickup_location}")
                st.write(f"Dropoff Location: {dropoff_location}")
                st.write(f"Duration: {duration} hours")
                st.write(f"Payment Status: {payment_status}")
                st.write(f"Car Number Plate: {car_number_plate if car_number_plate else 'Not Assigned'}")
                st.write(f"Status: {status}")
            st.markdown("---")
    else:
        st.info("No past completed bookings found.")

if __name__ == "__main__":
    show_dashboard()
