import streamlit as st
import psycopg2
from database import connect
import uuid
from utils import display_profile_update

def show_dashboard():
    st.title("Admin Dashboard")

    # Back to Home button
    if st.sidebar.button("Back to Home"):
        st.session_state.current_page = "home"
        st.session_state.logged_in = False  # Optionally log out
        st.session_state.role = None

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
        display_profile_update('admin')
    
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

    conn = connect()
    cur = conn.cursor()

    report_options = [
        "Car Reports",
        "Owner Reports",
        "Driver Reports",
        "Monthly Income",
        "Yearly Income",
        "Driver Salary Report"
    ]
    selected_report = st.selectbox("Select Report Type", report_options)

    try:
        if selected_report == "Car Reports":
            #st.subheader("Car Reports")
            st.markdown("**Car Reports Overview**")
            cur.execute("""
                SELECT c.car_id, c.car_number, c.model, c.car_type, COUNT(r.request_id) as booking_count
                FROM Car c
                LEFT JOIN Request r ON c.car_number = r.car_number_plate
                GROUP BY c.car_id, c.car_number, c.model, c.car_type
                ORDER BY booking_count DESC
            """)
            cars = cur.fetchall()
            if cars:
                #st.write("Debug: Car Reports Data", cars)  # Debug output
                col1,col2,col3,col4,col5=st.columns([1,2,2,2,1])
                col1.markdown("**ID**")
                col2.markdown("**Number**")
                col3.markdown("**Model**")
                col4.markdown("**Type**")
                col5.markdown("**Booking Count**")
                st.markdown("---")
                for car in cars:
                    col1,col2,col3,col4,col5=st.columns([1,2,2,2,1])
                    col1.write(car[0])
                    col2.write(car[1])
                    col3.write(car[2])
                    col4.write(car[3])
                    col5.write(car[4])
                    #st.write(f"Car ID: {car[0]}, Number: {car[1]}, Model: {car[2]}, Type: {car[3]}, Bookings: {car[4]}")
            else:
                st.info("No car data available.")

        elif selected_report == "Owner Reports":
            #st.subheader("Owner Reports")
            st.markdown("**Owner Reports Overview**")
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
                #st.write("Debug: Owner Reports Data", owners)  # Debug output
                col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                col1.markdown("**Owner ID**")
                col2.markdown("**Name**")
                col3.markdown("**Cars Owned**")
                col4.markdown("**Bookings**")
                st.markdown("---")
                for owner in owners:
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                    col1.write(owner[0])
                    col2.write(owner[1])
                    col3.write(owner[2])
                    col4.write(owner[3])
                #for owner in owners:
                    #st.write(f"Owner ID: {owner[0]}, Name: {owner[1]}, Cars Owned: {owner[2]}, Bookings: {owner[3]}")
            else:
                st.info("No owner data available.")

        elif selected_report == "Driver Reports":
            st.markdown("**Driver Report Overview**")
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
                #st.write("Debug: Driver Reports Data", drivers)  # Debug output
                
                col1, col2, col3 = st.columns([3, 3, 2])
                col1.markdown("**Driver ID**")
                col2.markdown("**Name**")
                col3.markdown("**Bookings**")
                st.markdown("---")
                for driver in drivers:
                    col1, col2, col3 = st.columns([3, 3, 2])
                    col1.write(driver[0])
                    col2.write(driver[1])
                    col3.write(driver[2])
                #for driver in drivers:
                 #   st.write(f"Driver ID: {driver[0]}, Name: {driver[1]}, Bookings: {driver[2]}")
            else:
                st.info("No driver data available.")

        elif selected_report == "Monthly Income":
            #st.subheader("Monthly Income")
            st.markdown("**Monthly Income Overview**")
            year = st.number_input("Select Year", min_value=2020, max_value=2025, value=2025)
            cur.execute("""
                SELECT EXTRACT(MONTH FROM r.pickup_date) AS month, 
                       COALESCE(SUM(rental.total_amount), 0) AS total_income
                FROM Request r
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE EXTRACT(YEAR FROM r.pickup_date) = %s AND r.status = 'Completed'
                GROUP BY EXTRACT(MONTH FROM r.pickup_date)
                ORDER BY month
            """, (year,))
            income = cur.fetchall()
            if income:
                #st.write("Debug: Monthly Income Data", income)  # Debug output
                st.markdown(f"**Monthly Income for {year}**")
                col1, col2 = st.columns([2, 2])
                col1.markdown("**Month**")
                col2.markdown("**Income ($)**")
                st.markdown("---")
                for row in income:
                    if isinstance(row, (tuple, list)) and len(row) == 2:
                        month, amount = row
                        col1, col2 = st.columns([2, 2])
                        col1.write(f"{int(month)}")
                        col2.write(f"{float(amount):.2f}")
                    else:
                        st.error(f"Unexpected data format: {row}")
            else:
                st.info("No income data for this year.")

        elif selected_report == "Yearly Income":
            #st.subheader("Yearly Income")
            st.markdown("**Yearly Income Overview**")
            cur.execute("""
                SELECT EXTRACT(YEAR FROM r.pickup_date) AS year, 
                       COALESCE(SUM(rental.total_amount), 0) AS total_income
                FROM Request r
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE r.status = 'Completed'
                GROUP BY EXTRACT(YEAR FROM r.pickup_date)
                ORDER BY year
            """)
            income = cur.fetchall()
            if income:
                #st.write("Debug: Yearly Income Data", income)  # Debug output
                st.markdown(f"**Monthly Income for {year}**")
                col1, col2 = st.columns([2, 2])
                col1.markdown("**Month**")
                col2.markdown("**Income ($)**")
                st.markdown("---")
                for row in income:
                    if isinstance(row, (tuple, list)) and len(row) == 2:
                        month, amount = row
                        col1, col2 = st.columns([2, 2])
                        col1.write(f"{int(month)}")
                        col2.write(f"{float(amount):.2f}")
                    else:
                        st.error(f"Unexpected data format: {row}")
            else:
                st.info("No yearly income data available.")

        elif selected_report == "Driver Salary Report":
           # st.subheader("Driver Salary Report")
            st.markdown("**Driver Salary Report**")
            year = st.number_input("Select Year", min_value=2020, max_value=2025, value=2025)
            cur.execute("""
                SELECT d.driver_id, d.first_name || ' ' || d.last_name AS driver_name,
                       COUNT(r.request_id) AS bookings, 
                       COALESCE(SUM(rental.total_amount * 0.3), 0) AS salary
                FROM Driver d
                LEFT JOIN Request r ON d.driver_id = r.assigned_driver
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE EXTRACT(YEAR FROM r.pickup_date) = %s AND r.status = 'Completed'
                GROUP BY d.driver_id, d.first_name, d.last_name
                ORDER BY salary DESC
            """, (year,))
            salaries = cur.fetchall()
            if salaries:
                #st.write("Debug: Driver Salary Data", salaries)  # Debug output
                st.markdown(f"**Driver Salary Report for {year}**")
                col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                col1.markdown("**Driver ID**")
                col2.markdown("**Name**")
                col3.markdown("**Bookings**")
                col4.markdown("**Salary ($)**")
                st.markdown("---")
                for driver in salaries:
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
                    col1.write(driver[0])
                    col2.write(driver[1])
                    col3.write(driver[2])
                    col4.write(f"{float(driver[3]):.2f}")
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
    conn.close()

def ranking():
    st.header("🏆 Rankings")

    conn = connect()
    cur = conn.cursor()

    try:
        # Selection for entity and criteria
        col1, col2 = st.columns(2)
        with col1:
            entity= st.selectbox("Select Entity", ["Drivers", "Cars", "Customers"])
        with col2:
            criteria = st.selectbox("Select Criteria", ["Bookings", "Money"])

        # Selection for entity and criteria
        criteria_param = 'bookings' if criteria== "Bookings" else 'money'

        # Map entity to procedure and display function
        if entity == "Drivers":
            display_driver_rankings(cur, criteria_param)
        elif entity == "Cars":
            display_car_rankings(cur, criteria_param)
        elif entity == "Customers":
            display_customer_rankings(cur, criteria_param)
    except Exception as e:
        st.error(f"Error generating rankings: {e}")
    finally:
        conn.close()

def display_driver_rankings(cur, criteria):
    st.subheader(f"Driver Rankings by {criteria.title()}")
    cur.execute("BEGIN; CALL get_driver_rankings(%s, 'cursor'); FETCH ALL IN cursor;", (criteria,))
    rankings = cur.fetchall()
    cur.execute("COMMIT;")

    if rankings:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        col1.markdown("**Rank**")
        col2.markdown("**Driver ID**")
        col3.markdown("**Name**")
        col4.markdown(f"**{criteria.title()}**")
        st.markdown("---")
        for driver_id, name, value, rank in rankings:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.write(rank)
            col2.write(driver_id)
            col3.write(name)
            col4.write(f"{value:.2f}" if criteria == "money" else value)
    else:
        st.info(f"No driver rankings available for {criteria}.")

def display_car_rankings(cur, criteria):
    st.subheader(f"Car Rankings by {criteria.title()}")
    cur.execute("BEGIN; CALL get_car_rankings(%s, 'cursor'); FETCH ALL IN cursor;", (criteria,))
    rankings = cur.fetchall()
    cur.execute("COMMIT;")

    if rankings:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])
        col1.markdown("**Rank**")
        col2.markdown("**Car ID**")
        col3.markdown("**Number Plate**")
        col4.markdown("**Model**")
        col5.markdown(f"**{criteria.title()}**")
        st.markdown("---")
        for car_id, car_number, model, value, rank in rankings:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])
            col1.write(rank)
            col2.write(car_id)
            col3.write(car_number)
            col4.write(model)
            col5.write(f"{value:.2f}" if criteria == "money" else value)
    else:
        st.info(f"No car rankings available for {criteria}.")

def display_customer_rankings(cur, criteria):
    st.subheader(f"Customer Rankings by {criteria.title()}")
    cur.execute("BEGIN; CALL get_customer_rankings(%s, 'cursor'); FETCH ALL IN cursor;", (criteria,))
    rankings = cur.fetchall()
    cur.execute("COMMIT;")

    if rankings:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        col1.markdown("**Rank**")
        col2.markdown("**Customer ID**")
        col3.markdown("**Name**")
        col4.markdown(f"**{criteria.title()}**")
        st.markdown("---")
        for customer_id, name, value, rank in rankings:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
            col1.write(rank)
            col2.write(customer_id)
            col3.write(name)
            col4.write(f"{value:.2f}" if criteria == "money" else value)
    else:
        st.info(f"No customer rankings available for {criteria}.")


    