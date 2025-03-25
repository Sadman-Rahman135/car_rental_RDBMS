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
        ["View Car Lists", "View Driver Lists", "Reports" "Profile"],
        #label_visibility="collapsed"  # Hides the "Select Option" label
    )

    if page == "View Car Lists":
        view_cars()
    elif page == "View Driver Lists":
        view_drivers()
    elif page == "Reports":
        reports()
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
    st.header("Booking Reports")

    conn=connect()
    cur=conn.cursor()
    cur.execute("""
        SELECT
    """)
