import streamlit as st
from database import connect

def show_dashboard():
    st.title("Owner Dashboard")
    conn = connect()
    cur = conn.cursor()

    st.header("Add a Car")
    model = st.text_input("Car Model")
    if st.button("Add Car"):
        cur.execute("""
            INSERT INTO cars (owner_id, model)
            VALUES (%s, %s)
        """, (st.session_state.user_id, model))
        conn.commit()
        st.success(f"Car {model} added!")

    st.header("Orders for Your Cars")
    cur.execute("""
        SELECT o.id, o.status, c.model, u.username 
        FROM orders o 
        JOIN cars c ON o.car_id = c.id
        JOIN users u ON o.renter_id = u.id
        WHERE c.owner_id = %s
    """, (st.session_state.user_id,))
    orders = cur.fetchall()
    
    for order_id, status, model, renter in orders:
        st.write(f"Order {order_id}: {model} (by {renter}) - {status}")
        if status == "pending":
            if st.button("Approve", key=f"approve-{order_id}"):
                cur.execute("UPDATE orders SET status = 'approved' WHERE id = %s", (order_id,))
                conn.commit()
                st.success("Order approved!")
            if st.button("Reject", key=f"reject-{order_id}"):
                cur.execute("UPDATE orders SET status = 'rejected' WHERE id = %s", (order_id,))
                conn.commit()
                st.warning("Order rejected!")
    conn.close()
# import streamlit as st
# from database import connect

# def show_dashboard():
#     st.title("Owner Dashboard")
#     conn = connect()
#     cur = conn.cursor()

#     st.header("Add a Car")
#     model = st.text_input("Car Model")
#     if st.button("Add Car"):
#         cur.execute("""
#             INSERT INTO cars (owner_id, model)
#             VALUES (%s, %s)
#         """, (st.session_state.user_id, model))
#         conn.commit()
#         st.success(f"Car {model} added!")

#     st.header("Orders for Your Cars")
#     cur.execute("""
#         SELECT o.id, o.status, c.model, u.username 
#         FROM orders o 
#         JOIN cars c ON o.car_id = c.id
#         JOIN users u ON o.renter_id = u.id
#         WHERE c.owner_id = %s
#     """, (st.session_state.user_id,))
#     orders = cur.fetchall()
    
#     for order_id, status, model, renter in orders:
#         st.write(f"Order {order_id}: {model} (by {renter}) - {status}")
#         if status == "pending":
#             if st.button("Approve", key=f"approve-{order_id}"):
#                 cur.execute("UPDATE orders SET status = 'approved' WHERE id = %s", (order_id,))
#                 conn.commit()
#                 st.success("Order approved!")
#             if st.button("Reject", key=f"reject-{order_id}"):
#                 cur.execute("UPDATE orders SET status = 'rejected' WHERE id = %s", (order_id,))
#                 conn.commit()
#                 st.warning("Order rejected!")
#     conn.close()
import streamlit as st
import psycopg2
from database import connect
import uuid

def show_dashboard():
    st.title("Customer Dashboard")

    # Navigation within Customer Dashboard
    page = st.sidebar.selectbox("Select Option", ["Make a Booking", "View Bookings", "Profile"])

    if page == "Make a Booking":
        make_booking()
    elif page == "View Bookings":
        view_bookings()
    elif page == "Profile":
        st.write("Customer Profile Page (Coming Soon).")


def make_booking():
    st.header("Make a Booking")

    # Booking form
    car_type = st.selectbox("Car Type",["Premio","Corolla","X Corolla","Noah","Wagon","Truck"])
    pickup_date = st.date_input("Pickup Date")
    dropoff_date = st.date_input("Dropoff Date")
    pickup_location = st.text_input("Pickup Location")
    dropoff_location = st.text_input("Dropoff Location")
    duration = st.number_input("Duration (in hours)", min_value=1, step=1)
    payment_status = st.selectbox("Payment Status", ["Pending", "Paid"])
    
    if st.button("Submit Booking"):
        if not all([car_type, pickup_date, dropoff_date, pickup_location, dropoff_location, duration]):
            st.error("Please fill in all fields.")
        else:
            try:
                conn = connect()
                cur = conn.cursor()

                # Generate unique request ID
                request_id = str(uuid.uuid4())
                customer_id = st.session_state.user_id  # Assuming user_id is stored in session state

                # Insert into Request table
                cur.execute(
                    '''
                    INSERT INTO Request (
                        request_id, customer_id, car_type, pickup_date, dropoff_date, 
                        pickup_location, dropoff_location, duration, payment_status, 
                        assigned_driver, car_number_plate, status
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s)
                    ''',
                    (
                        request_id, customer_id, car_type, pickup_date, dropoff_date,
                        pickup_location, dropoff_location, duration, payment_status, "Pending"
                    )
                )

                conn.commit()
                conn.close()
                st.success("Booking submitted successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")


def view_bookings():
    st.header("Your Bookings")

    try:
        conn = connect()
        cur = conn.cursor()
        customer_id = st.session_state.user_id  # Assuming user_id is stored in session state

        # Fetch bookings for the logged-in customer
        cur.execute("SELECT * FROM Request WHERE customer_id = %s", (customer_id,))
        bookings = cur.fetchall()
        conn.close()

        if bookings:
            for booking in bookings:
                st.write(f"**Booking ID:** {booking[0]}")
                st.write(f"Car Type: {booking[2]}")
                st.write(f"Pickup Date: {booking[3]}")
                st.write(f"Dropoff Date: {booking[4]}")
                st.write(f"Pickup Location: {booking[5]}")
                st.write(f"Dropoff Location: {booking[6]}")
                st.write(f"Duration: {booking[7]} hours")
                st.write(f"Payment Status: {booking[8]}")
                st.write(f"Status: {booking[11]}")
                st.markdown("---")
        else:
            st.info("No bookings found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

