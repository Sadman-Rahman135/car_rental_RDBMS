import streamlit as st
from database import connect

def show_dashboard():
    st.title("Driver Dashboard")
    conn = connect()
    cur = conn.cursor()

    # Section: View All Booking Requests
    st.header("View All Booking Requests")
    cur.execute("""
        SELECT request_id, customer_id, car_type, pickup_date, dropoff_date, 
               pickup_location, dropoff_location, duration, payment_status, 
               car_number_plate, status
        FROM Request
    """)
    requests = cur.fetchall()

    if requests:
        for request in requests:
            st.write(f"*Request ID:* {request[0]}")
            st.write(f"Customer ID: {request[1]}")
            st.write(f"Car Type: {request[2]}")
            st.write(f"Pickup Date: {request[3]}")
            st.write(f"Dropoff Date: {request[4]}")
            st.write(f"Pickup Location: {request[5]}")
            st.write(f"Dropoff Location: {request[6]}")
            st.write(f"Duration: {request[7]} hours")
            st.write(f"Payment Status: {request[8]}")
            st.write(f"Car Number Plate: {request[9]}")
            st.write(f"Status: {request[10]}")
            if st.button("Accept Booking", key=f"accept-{request[0]}"):
                try:
                    cur.execute(
                        """
                        UPDATE Request
                        SET status = 'Accepted', assigned_driver = %s
                        WHERE request_id = %s
                        """,
                        (st.session_state.user_id, request[0])
                    )
                    conn.commit()
                    st.success(f"Booking ID {request[0]} has been accepted!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"An error occurred while accepting the booking: {e}")
            st.markdown("---")
    else:
        st.info("No booking requests found.")

    conn.close()
