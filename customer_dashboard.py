import streamlit as st
import psycopg2
from database import connect
import uuid


def show_dashboard():
    st.title("Customer Dashboard")
    # Back to Home button
    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.session_state.logged_in = False  # Optionally log out
        st.session_state.role = None

    # Navigation within Customer Dashboard
    page = st.sidebar.selectbox("Select Option", ["Make a Booking", "View Bookings", "Profile", "Cars","Advanced Reports"])

    if page == "Make a Booking":
        make_booking()
    elif page == "View Bookings":
        view_bookings()
    elif page == "Profile":
        st.write("Customer Profile Page (Coming Soon).")
    elif page == "Cars":
        view_cars()
    elif page == "Advanced Reports":
        advanced_reports()

def make_booking():
    st.header("Make a Booking")

    # Booking form
    car_type = st.selectbox("Car Type", ["Premio", "Corolla", "X Corolla", "Noah", "Wagon", "Truck"])
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
        customer_id = st.session_state.user_id
        cur.execute("""
            SELECT r.request_id, r.car_type, r.pickup_date, r.dropoff_date, r.pickup_location, 
                   r.dropoff_location, r.duration, r.payment_status, r.status, 
                   car.model, d.first_name || ' ' || d.last_name AS driver_name
            FROM Request r
            LEFT JOIN Car car ON r.car_number_plate = car.car_number
            LEFT JOIN Driver d ON r.assigned_driver = d.driver_id
            WHERE r.customer_id = %s
        """, (customer_id,))
        bookings = cur.fetchall()
        if bookings:
            for b in bookings:
                st.write(f"Booking ID: {b[0]}")
                st.write(f"Car Type: {b[1]} (Model: {b[9] or 'Not Assigned'})")
                st.write(f"Pickup Date: {b[2]}")
                st.write(f"Dropoff Date: {b[3]}")
                st.write(f"Pickup Location: {b[4]}")
                st.write(f"Dropoff Location: {b[5]}")
                st.write(f"Duration: {b[6]} hours")
                st.write(f"Payment Status: {b[7]}")
                st.write(f"Status: {b[8]}")
                st.write(f"Driver: {b[10] or 'Not Assigned'}")
                st.markdown("---")
        else:
            st.info("No bookings found.")
        conn.close()
    except Exception as e:
        st.error(f"An error occurred: {e}")

def view_cars():
    st.header("Available Cars")
    search_term = st.text_input("Search by Model")
    try:
        conn = connect()
        cur = conn.cursor()
        query = """
            SELECT car_number, model, car_type, seats
            FROM Car
            WHERE availability_status = 'Available'
            AND LOWER(model) LIKE LOWER(%s)
        """
        cur.execute(query, (f'%{search_term}%',))
        cars = cur.fetchall()
        if cars:
            car_options = [f"{car[0]} - {car[1]} ({car[2]}, {car[3]} seats)" for car in cars]
            selected_car = st.selectbox("Select a Car to Book", car_options)
            selected_car_number = selected_car.split(" - ")[0]
            if st.button("Confirm Selection"):
                try:
                    customer_id = st.session_state.user_id
                    cur.execute("""
                        UPDATE Request
                        SET car_number_plate = %s
                        WHERE customer_id = %s AND car_number_plate IS NULL AND status = 'Pending'
                    """, (selected_car_number, customer_id))
                    conn.commit()
                    st.success(f"Car {selected_car_number} assigned to your booking!")
                except Exception as e:
                    conn.rollback()
                    st.error(f"An error occurred: {e}")
        else:
            st.info("No cars available.")
        conn.close()
    except Exception as e:
        st.error(f"An error occurred: {e}")

def advanced_reports():
    st.header("Advanced Reports")
    report_options = [
        "Booking Cost Trend",
        "Driver Assignment History",
        "Recursive Car Usage Chain",
        "Popular Pickup Locations",
        "Booking Status Summary"
    ]
    selected_report = st.selectbox("Select Report", report_options)

    conn = connect()
    cur = conn.cursor()
    customer_id = st.session_state.user_id

    # if selected_report == "Booking Cost Trend":
    #     st.subheader("Booking Cost Trend")
    #     cur.execute("""
    #         SELECT pickup_date, calculate_rental_cost(duration, car_type) AS cost
    #         FROM Request
    #         WHERE customer_id = %s AND status IN ('Accepted', 'Completed')
    #         ORDER BY pickup_date
    #     """, (customer_id,))
    #     costs = cur.fetchall()
    #     if costs:
    #         for date, cost in costs:
    #             st.write(f"Date: {date}, Cost: ${cost}")
    #     else:
    #         st.info("No cost data available.")

    if selected_report == "Driver Assignment History":
        st.subheader("Driver Assignment History")
        cur.execute("""
            SELECT r.request_id, r.pickup_date, d.first_name || ' ' || d.last_name AS driver_name
            FROM Request r
            LEFT JOIN Driver d ON r.assigned_driver = d.driver_id
            WHERE r.customer_id = %s AND r.assigned_driver IS NOT NULL
            ORDER BY r.pickup_date
        """, (customer_id,))
        history = cur.fetchall()
        if history:
            for req_id, date, driver in history:
                st.write(f"Request ID: {req_id}, Date: {date}, Driver: {driver}")
        else:
            st.info("No driver assignment history.")

    elif selected_report == "Recursive Car Usage Chain":

        st.subheader("Recursive Car Usage Chain by Car Type")

        car_type = st.selectbox("Select Car Type", ["Premio", "Corolla", "X Corolla", "Noah", "Wagon", "Truck"])

        if st.button("Show Chain"):

            cur.execute("""
        
                    WITH RECURSIVE car_usage AS (
        
                        SELECT request_id, car_type, pickup_date, dropoff_date
        
                        FROM Request
        
                        WHERE customer_id = %s AND car_type = %s AND status = 'Accepted'
        
                        UNION ALL
        
                        SELECT r.request_id, r.car_type, r.pickup_date, r.dropoff_date
        
                        FROM Request r
        
                        INNER JOIN car_usage cu ON r.car_type = cu.car_type
        
                        WHERE r.pickup_date > cu.dropoff_date AND r.customer_id = %s
        
                    )
        
                    SELECT * FROM car_usage ORDER BY pickup_date
        
                """, (customer_id, car_type, customer_id))

            chain = cur.fetchall()

            if chain:

                for row in chain:
                    st.write(f"Request ID: {row[0]}, Car Type: {row[1]}, Dates: {row[2]} to {row[3]}")

            else:

                st.info(f"No usage chain found for car type '{car_type}'.")

    elif selected_report == "Popular Pickup Locations":
        st.subheader("Popular Pickup Locations")
        cur.execute("""
            SELECT pickup_location, COUNT(*) AS booking_count
            FROM Request
            WHERE customer_id = %s
            GROUP BY pickup_location
            HAVING COUNT(*) > 1
            ORDER BY booking_count DESC
        """, (customer_id,))
        locations = cur.fetchall()
        if locations:
            for loc, count in locations:
                st.write(f"Location: {loc}, Bookings: {count}")
        else:
            st.info("No popular pickup locations found.")

    elif selected_report == "Booking Status Summary":
        st.subheader("Booking Status Summary")
        cur.execute("""
            SELECT status, COUNT(*) AS count,
                   STRING_AGG(request_id, ', ') AS request_ids
            FROM Request
            WHERE customer_id = %s
            GROUP BY status
        """, (customer_id,))
        summary = cur.fetchall()
        if summary:
            for status, count, ids in summary:
                st.write(f"Status: {status}, Count: {count}, Request IDs: {ids}")
        else:
            st.info("No bookings to summarize.")

    conn.close()

    # except Exception as e:
    #     st.error(f"An error occurred in advanced reports: {e}")