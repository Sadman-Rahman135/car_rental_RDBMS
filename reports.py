import streamlit as st
import psycopg2
from database import connect
import uuid

def new_reports():
    st.header("📊 Reports")

    conn = connect()
    cur = conn.cursor()

    report_options = [
        "Car Reports", "Owner Reports", "Driver Reports",
        "Monthly Income", "Yearly Income", "Driver Salary Report"
    ]
    selected_report = st.selectbox("Select Report Type", report_options)
    search_term = st.text_input("Search by ID/Name/Email (Optional)")

    try:
        if selected_report == "Car Reports":
            st.subheader("Car Reports")
            query = """
                SELECT c.car_id, c.car_number, c.model, c.car_type, c.seats, 
                       c.availability_status, COUNT(r.request_id) AS booking_count,
                       COALESCE(SUM(rental.total_amount * 0.6), 0) AS revenue
                FROM Car c
                LEFT JOIN Request r ON c.car_number = r.car_number_plate
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE (%s IS NULL OR c.car_id = %s OR c.car_number ILIKE %s OR c.model ILIKE %s)
                GROUP BY c.car_id, c.car_number, c.model, c.car_type, c.seats, c.availability_status
                ORDER BY booking_count DESC
            """
            search_param = None if not search_term else search_term
            like_search = f'%{search_term}%' if search_term else None
            cur.execute(query, (search_param, search_param, like_search, like_search))
            cars = cur.fetchall()

            if cars:
                for car in cars:
                    with st.expander(f"Car ID: {car[0]} - {car[2]} ({car[3]})"):
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown(f"""
                            **Car Number:** {car[1]}  
                            **Model:** {car[2]}  
                            **Type:** {car[3]}  
                            **Seats:** {car[4]}
                            """)
                        with cols[1]:
                            st.markdown(f"""
                            **Availability:** {"🟢 Available" if car[5] == "Available" else "🔴 Not Available"}  
                            **Total Bookings:** {car[6]}  
                            **Revenue:** ${car[7]:.2f}
                            """)
                        # Booking History
                        st.markdown("**Booking History**")
                        cur.execute("""
                            SELECT r.request_id, r.pickup_date, r.dropoff_date, r.status
                            FROM Request r
                            WHERE r.car_number_plate = %s
                            ORDER BY r.pickup_date DESC
                        """, (car[1],))
                        bookings = cur.fetchall()
                        if bookings:
                            for b in bookings:
                                st.write(f"Request ID: {b[0]}, Dates: {b[1]} to {b[2]}, Status: {b[3]}")
                        else:
                            st.info("No bookings for this car.")
            else:
                st.info("No car data available.")

        elif selected_report == "Owner Reports":
            st.subheader("Owner Reports")
            query = """
                SELECT co.car_owner_id, co.first_name || ' ' || co.last_name AS owner_name, 
                       co.email, co.phone, co.account_status, COUNT(c.car_id) AS car_count, 
                       COUNT(r.request_id) AS booking_count, 
                       COALESCE(SUM(rental.owner_share), 0) AS earnings
                FROM Car_Owner co
                LEFT JOIN Car c ON co.car_owner_id = c.car_owner_id
                LEFT JOIN Request r ON c.car_number = r.car_number_plate
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE (%s IS NULL OR co.car_owner_id = %s OR co.email ILIKE %s OR 
                       (co.first_name || ' ' || co.last_name) ILIKE %s)
                GROUP BY co.car_owner_id, co.first_name, co.last_name, co.email, co.phone, co.account_status
                ORDER BY booking_count DESC
            """
            search_param = None if not search_term else search_term
            like_search = f'%{search_term}%' if search_term else None
            cur.execute(query, (search_param, search_param, like_search, like_search))
            owners = cur.fetchall()

            if owners:
                for owner in owners:
                    with st.expander(f"Owner: {owner[1]} (ID: {owner[0]})"):
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown(f"""
                            **Email:** {owner[2]}  
                            **Phone:** {owner[3]}  
                            **Status:** {"🟢 Active" if owner[4] == "active" else "🔴 Inactive"}
                            """)
                        with cols[1]:
                            st.markdown(f"""
                            **Cars Owned:** {owner[5]}  
                            **Total Bookings:** {owner[6]}  
                            **Earnings:** ${owner[7]:.2f}
                            """)
                        # Car List
                        st.markdown("**Owned Cars**")
                        cur.execute("""
                            SELECT car_number, model, car_type, availability_status
                            FROM Car
                            WHERE car_owner_id = %s
                        """, (owner[0],))
                        cars = cur.fetchall()
                        if cars:
                            for c in cars:
                                st.write(f"Car Number: {c[0]}, Model: {c[1]}, Type: {c[2]}, Status: {c[3]}")
                        else:
                            st.info("No cars owned.")
            else:
                st.info("No owner data available.")

        elif selected_report == "Driver Reports":
            st.subheader("Driver Reports")
            query = """
                SELECT d.driver_id, d.first_name || ' ' || d.last_name AS driver_name, 
                       d.email, d.phone, d.account_status, d.license_number, 
                       COUNT(r.request_id) AS booking_count, 
                       COALESCE(SUM(rental.total_amount * 0.3), 0) AS earnings
                FROM Driver d
                LEFT JOIN Request r ON d.driver_id = r.assigned_driver
                LEFT JOIN Rental rental ON r.request_id = rental.request_id
                WHERE (%s IS NULL OR d.driver_id = %s OR d.email ILIKE %s OR 
                       (d.first_name || ' ' || d.last_name) ILIKE %s)
                GROUP BY d.driver_id, d.first_name, d.last_name, d.email, d.phone, 
                         d.account_status, d.license_number
                ORDER BY booking_count DESC
            """
            search_param = None if not search_term else search_term
            like_search = f'%{search_term}%' if search_term else None
            cur.execute(query, (search_param, search_param, like_search, like_search))
            drivers = cur.fetchall()

            if drivers:
                for driver in drivers:
                    with st.expander(f"Driver: {driver[1]} (ID: {driver[0]})"):
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown(f"""
                            **Email:** {driver[2]}  
                            **Phone:** {driver[3]}  
                            **Status:** {"🟢 Active" if driver[4] == "active" else "🔴 Inactive"}  
                            **License:** {driver[5]}
                            """)
                        with cols[1]:
                            st.markdown(f"""
                            **Total Bookings:** {driver[6]}  
                            **Earnings:** ${driver[7]:.2f}
                            """)
                        # Performance Analytics
                        st.markdown("**Performance Analytics**")
                        cur.execute("SELECT * FROM driver_performance_summary(%s)", (driver[0],))
                        metrics = cur.fetchall()
                        if metrics:
                            for metric, value in metrics:
                                st.write(f"{metric}: {value}")
                        else:
                            st.info("No performance data available.")
                        # Booking Chain
                        st.markdown("**Booking History Chain**")
                        cur.execute("SELECT * FROM get_booking_chain(%s)", (driver[0],))
                        chain = cur.fetchall()
                        if chain:
                            for req_id, pickup, dropoff in chain:
                                st.write(f"Request ID: {req_id}, From: {pickup}, To: {dropoff}")
                        else:
                            st.info("No booking history chain found.")
            else:
                st.info("No driver data available.")

        elif selected_report == "Monthly Income":
            st.subheader("Monthly Income")
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
                total_yearly = sum(row[1] for row in income)
                st.metric("Total Income for Year", f"${total_yearly:.2f}")
                col1, col2 = st.columns(2)
                col1.markdown("**Month**")
                col2.markdown("**Income ($)**")
                st.markdown("---")
                for month, amount in income:
                    col1, col2 = st.columns(2)
                    col1.write(f"{int(month)}")
                    col2.write(f"{float(amount):.2f}")
            else:
                st.info("No income data for this year.")

        elif selected_report == "Yearly Income":
            st.subheader("Yearly Income")
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
                col1, col2 = st.columns(2)
                col1.markdown("**Year**")
                col2.markdown("**Income ($)**")
                st.markdown("---")
                for year, amount in income:
                    col1, col2 = st.columns(2)
                    col1.write(f"{int(year)}")
                    col2.write(f"{float(amount):.2f}")
            else:
                st.info("No yearly income data available.")

        elif selected_report == "Driver Salary Report":
            st.subheader("Driver Salary Report")
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
