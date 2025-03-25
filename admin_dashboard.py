import streamlit as st
import psycopg2
from database import connect
import uuid


def show_dashboard():
    st.title("Admin Dashboard")

    # Navigation within Customer Dashboard
    # st.sidebar.header("Select Option")
    # page = st.sidebar.button("View Car Lists")
    # page = st.sidebar.button("View Driver Lists")
    # page = st.sidebar.button("Profile")
    #page = st.sidebar.selectbox("Select Option", ["View Car Lists", "View Driver Lists", "Profile"])
    page = st.sidebar.radio(
        "Select Option",
        ["View Car Lists", "View Driver Lists", "Reports", "Manage Requests", "Ranking", "Profile"],
        #label_visibility="collapsed"  # Hides the "Select Option" label
    )

    if page == "View Car Lists":
        view_cars()
    elif page == "View Driver Lists":
        view_drivers()
    elif page == "Reports":
        reports()
    elif page == "Manage Requests":
        manage_requests()
    elif page == "Ranking":
        ranking()
    elif page == "Profile":
        st.write("Customer Profile Page (Coming Soon).")
    
def view_drivers():
    st.header("🧑‍🔧 Driver Management")
    #st.markdown("---")
    
    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch drivers data
        cur.execute("""
            SELECT driver_id, first_name, last_name, email, phone, address, 
                   location, license_number, account_status 
            FROM driver
            ORDER BY account_status, last_name
        """)
        drivers = cur.fetchall()

        if not drivers:
            st.warning("No drivers found in the database.")
            return

        # Filter section
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Active", "Inactive"] 
            )
        with col2:
            search_term = st.text_input("Search by Name/Email")

        # Apply filters
        filtered_drivers = drivers
        if filter_status == "Active":
            filtered_drivers = [d for d in filtered_drivers if d[8] == "active"]
        elif filter_status =="Inactive":
            filtered_drivers = [d for d in filtered_drivers if d[8] == "inactive"]




        if search_term:
            search_term = search_term.lower()
            filtered_drivers = [
                d for d in filtered_drivers
                if search_term in d[1].lower() or 
                   search_term in d[2].lower() or
                   search_term in d[3].lower()
            ]

        # Display stats
        total_drivers = len(drivers)
        active_drivers = len([d for d in drivers if d[8]=="active"])
        inactive_drivers=total_drivers-active_drivers

        col1,col2,col3=st.columns(3)
        col1.metric("Total Drivers", total_drivers)
        col2.metric("Active Drivers", active_drivers)
        col3.metric("Inactive Drivers", inactive_drivers)

        # Display drivers in cards
        for idx, driver in enumerate(filtered_drivers, 1):
            driver_id, first_name, last_name, email, phone, address, location, license_number, account_status = driver

            #color status
            status_color="🟢" if account_status == "active" else "🔴"
            
            with st.expander(f"{idx}. {first_name} {last_name} {status_color}({account_status})", expanded=False):
                cols = st.columns([1, 3])
                
                with cols[0]:
                    # Avatar placeholder (you could add actual photos to your DB)
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", 
                            width=100, 
                            caption=f"License: {license_number}")
                    
                with cols[1]:
                    st.markdown(f"""
                    **📧 Email:** {email}  
                    **📞 Phone:** {phone}  
                    **📍 Location:** {location}  
                    **🏠 Address:** {address}  
                    **🟢 Status:** {status_color}`{account_status}`
                    """)
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Details", key=f"view_{idx}"):
                            st.session_state.selected_driver = driver
                    with col2:
                        
                        if st.button("Deactivate" if account_status == "active" else "Activate", 
                                   key=f"toggle_{idx}"):
                            # Add activation/deactivation logic
                            new_status = "inactive" if account_status.lower() == "active" else "active"
                            try:
                                cur.execute("""
                                    UPDATE driver 
                                    SET account_status = %s 
                                    WHERE driver_id = %s
                                """, (new_status, driver_id))
                                conn.commit()
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error updating status: {e}")# Add activation logic
                            pass

                st.markdown("---")

        # Detailed view when a driver is selected
        if 'selected_driver' in st.session_state:
            driver = st.session_state.selected_driver
            st.subheader("Driver Details")
            cols = st.columns(2)
            
            with cols[0]:
                st.markdown(f"""
                **Full Name:** {driver[1]} {driver[2]}  
                **License Number:** {driver[7]}  
                **Status:** {"🟢 Active" if driver[8] == "active" else "🔴 Inactive"}   
                **Registration Date:** (add this field to your DB)
                """)
                
            with cols[1]:
                st.markdown(f"""
                **Contact Information**  
                Email: {driver[3]}  
                Phone: {driver[4]}  
                Location: {driver[6]}  
                Address: {driver[5]}
                """)
                
            # Map placeholder (would need actual coordinates)
            # st.map(pd.DataFrame({
            #     'lat': [0],  # Replace with actual coordinates
            #     'lon': [0],
            #     'name': [f"{driver[0]} {driver[1]}"]
            # }), zoom=12)
            
            if st.button("Close Details"):
                del st.session_state['selected_driver']

    except Exception as e:                        
        st.error(f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


def view_cars():
    st.header("🚗 Car List")

    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch all cars 
        cur.execute("SELECT car_id, car_number, model, seats, car_owner_id, availability_status, car_type FROM car ORDER BY car_id")
        cars = cur.fetchall()

        if not cars:
            st.warning("No cars found in the database.")
            return

        # --- Filter Section ---
        col1, col2 = st.columns(2)
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "Available", "Not Available"]  # Only these 3 options
            )
        with col2:
            search_term = st.text_input("Search by Number/Model/Seats/Type")

        # Apply filters
        filtered_cars = cars
        if filter_status == "Available":
            filtered_cars = [c for c in cars if c[5] == "available"]
        elif filter_status == "Not Available":
            filtered_cars = [c for c in cars if c[5] == "not available"]  # Assuming 'inactive' is the DB value
        
        if search_term:
            search_term = search_term.lower()
            filtered_cars = [
                c for c in filtered_cars
                if search_term in c[1].lower() or 
                   search_term in c[2].lower() or
                   search_term in c[3].lower() or
                   search_term in c[6].lower()
            ]

        # --- Stats ---
        total_cars = len(cars)
        available_cars = len([c for c in cars if c[5] == "available"])
        not_available_cars = total_cars - available_cars

        col1, col2, col3 = st.columns(3)
        col1.metric("Total cars", total_cars)
        col2.metric("Available cars", available_cars)
        col3.metric("Not available cars", not_available_cars)

        # --- Display Drivers ---
        for idx, cars in enumerate(filtered_cars, 1):
            car_id, car_number, model, seats, car_owner_id, availability_status, car_type = cars
            
            # Color code status
            status_color = "🟢" if availability_status == "available" else "🔴"
            
            with st.expander(f"{idx}. {car_id} {model} {status_color}({availability_status})", expanded=False):
                cols = st.columns([1, 3])
                
                with cols[0]:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", 
                            width=100, 
                            caption=f"Car Number Plate: {car_number}")
                    
                with cols[1]:
                    st.markdown(f"""
                    **📧 Car ID:** {car_id}  
                    **📞 Car Number:** {car_number}  
                    **📍 Model:** {model}  
                    **🏠 Seats:** {seats}  
                    **Status:** {status_color} `{availability_status}`
                    """)
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Details", key=f"view_{idx}"):
                            st.session_state.selected_car = cars
                    with col2:
                        if st.button("Mark Not Available" if availability_status.lower() == "available" else "Not available", 
                                   key=f"toggle_{idx}"):
                            # Toggle availability
                            new_status = "not available" if availability_status.lower() == "available" else "available"
                            try:
                                cur.execute("""
                                    UPDATE car 
                                    SET availability_status = %s 
                                    WHERE car_id = %s
                                """, (new_status, car_id))
                                conn.commit()
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error updating status: {e}")# Add activation logic

                st.markdown("---")

        # --- Detailed View ---
        if 'selected_car' in st.session_state:
            cars = st.session_state.selected_car
            st.subheader("Car Details")
            
            cols = st.columns(1)
            with cols[0]:
                st.markdown(f"""
                    **Car ID:** {car_id}  
                    **Car Number:** {car_number}  
                    **Model:** {model}  
                    **Seats:** {seats}  
                    **Car Owner ID:** {car_owner_id}
                    **Car Type:** {car_type}
                **Status:** {"🟢 Available" if cars[5] == "Available" else "🔴 Not Available"}  
                """)
                
            
            
            if st.button("Close Details"):
                del st.session_state['selected_car']

    except Exception as e:                        
        st.error(f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

       
def reports():
    st.header("Reports")

    conn=connect()
    cur=conn.cursor()

    report_options =[
        "Car Reports",
        "Owner Reports",
        "Driver Reports",
        "Monthly Income",
        "Yearly Income",
        "Driver Salary Report"
    ]

    selected_report=st.selectbox("Select Report Type", report_options)

    try:
        if selected_report=="Car Reports":
            st.subheader("Car Reports")
            cur.execute("""
                SELECT c.car_id, c.car_number, c.model, c.car_type, c.seats, COUNT(r.request_id) as booking_count
                FROM Car c
                LEFT JOIN Request r ON c.car_number=r.car_number_plate
                GROUP BY c.car_id, c.car_number, c.model, c.car_type, c.seats
                ORDER BY booking_count DESC
                        """)
            cars=cur.fetchall()
            for idx, cars in enumerate(cars, 1):
                car_id, car_number, model, car_type,  seats, booking_count = cars
            
            # Color code status
           
            with st.expander(f"{idx}. {car_id} {model} ({booking_count})", expanded=False):
                cols = st.columns([1, 3])
                
                with cols[0]:
                    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", 
                            width=100, 
                            caption=f"Car Number Plate: {car_number}")
                    
                with cols[1]:
                    st.markdown(f"""
                    **📧 Car ID:** {car_id}  
                    **📞 Car Number:** {car_number}  
                    **📍 Model:** {model}  
                    **🏠 Seats:** {seats}  
                    **🏠 Type:** {car_type}  
                    **Count:** {booking_count}
                    """)
            if cars:
                for car in cars:
                    st.write(f"Car ID: {car[0]}, Number: {car[1]}, Model: {car[2]}, Type: {car[3]}, Seats: {car[4]}, Booking: {car[5]}")
            else:
                st.info("No car data available")
        elif selected_report == "Owner Reports":
            st.subheader("Owner Reports")
            cur.execute("""
                SELECT co.car_owner_id, co.first_name || ' ' || co.last_name AS owner_name, 
                       COUNT(c.car_id) as car_count, COUNT(r.request_id) as booking_count
                FROM Car_Owner co
                LEFT JOIN Car c ON co.car_owner_id = c.car_owner_id
                LEFT JOIN Request r ON c.car_number = r.car_number_plate
                GROUP BY co.car_owner_id, co.first_name, co.last_name
                ORDER BY booking_count DESC
            """)
            owners = cur.fetchall()
            if owners:
                for owner in owners:
                    st.write(f"Owner ID: {owner[0]}, Name: {owner[1]}, Cars Owned: {owner[2]}, Bookings: {owner[3]}")
            else:
                st.info("No owner data available.")

        elif selected_report == "Driver Reports":
            st.subheader("Driver Reports")
            cur.execute("""
                SELECT d.driver_id, d.first_name || ' ' || d.last_name AS driver_name, 
                       COUNT(r.request_id) as booking_count
                FROM Driver d
                LEFT JOIN Request r ON d.driver_id = r.assigned_driver
                GROUP BY d.driver_id, d.first_name, d.last_name
                ORDER BY booking_count DESC
            """)
            drivers = cur.fetchall()
            if drivers:
                for driver in drivers:
                    st.write(f"Driver ID: {driver[0]}, Name: {driver[1]}, Bookings: {driver[2]}")
            else:
                st.info("No driver data available.")

        elif selected_report == "Monthly Income":
            st.subheader("Monthly Income")
            year = st.number_input("Select Year", min_value=2020, max_value=2025, value=2025)
            cur.execute("""
                SELECT EXTRACT(MONTH FROM r.pickup_date) AS month, 
                       SUM(rental.total_amount) AS total_income
                FROM Request r
                JOIN Rental rental ON r.request_id = rental.request_id
                WHERE EXTRACT(YEAR FROM r.pickup_date) = %s AND r.status = 'Completed'
                GROUP BY EXTRACT(MONTH FROM r.pickup_date)
                ORDER BY month
            """, (year,))
            income = cur.fetchall()
            if income:
                for month, amount in income:
                    st.write(f"Month: {int(month)}, Income: ${amount:.2f}")
            else:
                st.info("No income data for this year.")

        elif selected_report == "Yearly Income":
            st.subheader("Yearly Income")
            cur.execute("""
                SELECT EXTRACT(YEAR FROM r.pickup_date) AS year, 
                       SUM(rental.total_amount) AS total_income
                FROM Request r
                JOIN Rental rental ON r.request_id = rental.request_id
                WHERE r.status = 'Completed'
                GROUP BY EXTRACT(YEAR FROM r.pickup_date)
                ORDER BY year
            """)
            income = cur.fetchall()
            if income:
                for year, amount in income:
                    st.write(f"Year: {int(year)}, Income: ${amount:.2f}")
            else:
                st.info("No yearly income data available.")

        elif selected_report == "Driver Salary Report":
            st.subheader("Driver Salary Report")
            year = st.number_input("Select Year", min_value=2020, max_value=2025, value=2025)
            cur.execute("""
                SELECT d.driver_id, d.first_name || ' ' || d.last_name AS driver_name,
                       COUNT(r.request_id) AS bookings, SUM(rental.total_amount * 0.3) AS salary
                FROM Driver d
                LEFT JOIN Request r ON d.driver_id = r.assigned_driver
                JOIN Rental rental ON r.request_id = rental.request_id
                WHERE EXTRACT(YEAR FROM r.pickup_date) = %s AND r.status = 'Completed'
                GROUP BY d.driver_id, d.first_name, d.last_name
                ORDER BY salary DESC
            """, (year,))
            salaries = cur.fetchall()
            if salaries:
                for driver in salaries:
                    st.write(f"Driver ID: {driver[0]}, Name: {driver[1]}, Bookings: {driver[2]}, Salary: ${driver[3]:.2f}")
            else:
                st.info("No salary data for this year.")
    except Exception as e:
        st.error(f"Error generating report: {e}")
    finally:
        conn.close()

def manage_requests():
    st.header("Manage Booking Requests")
    
    # Database connection
    conn = connect()
    cur = conn.cursor()

    # Section 1: View Pending and Overdue Requests
    st.subheader("Pending and Overdue Requests")
    cur.execute("""
            -- Procedure: Cancel Overdue Requests
            CREATE OR REPLACE PROCEDURE cancel_overdue_requests()
            AS $$
            DECLARE
                v_request RECORD;
            BEGIN
                FOR v_request IN (SELECT request_id FROM Request WHERE dropoff_date < NOW() AND status = 'Pending')
                LOOP
                    UPDATE Request
                    SET status = 'Canceled'
                    WHERE request_id = v_request.request_id;
                    RAISE NOTICE 'Request % canceled due to overdue', v_request.request_id;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        """)
    cur.execute("""
        SELECT request_id, customer_id, car_type, pickup_date, dropoff_date, 
               pickup_location, dropoff_location, duration, status
        FROM Request 
        WHERE status = 'Pending' AND dropoff_date < NOW()
    """)
    overdue_requests = cur.fetchall()

    if overdue_requests:
        st.write("The following requests are overdue:")
        for req in overdue_requests:
            st.write(f"Request ID: {req[0]}")
            st.write(f"Customer ID: {req[1]}")
            st.write(f"Car Type: {req[2]}")
            st.write(f"Pickup Date: {req[3]}")
            st.write(f"Dropoff Date: {req[4]}")
            st.write(f"Pickup Location: {req[5]}")
            st.write(f"Dropoff Location: {req[6]}")
            st.write(f"Duration: {req[7]} hours")
            st.write(f"Status: {req[8]}")
            st.markdown("---")
        
        if st.button("Cancel All Overdue Requests"):
            try:
                cur.execute("CALL cancel_overdue_requests()")
                conn.commit()
                st.success("All overdue requests canceled successfully!")
            except Exception as e:
                conn.rollback()
                st.error(f"Error canceling overdue requests: {str(e)}")
    else:
        st.info("No overdue requests found.")


    