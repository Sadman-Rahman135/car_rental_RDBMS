import streamlit as st
import psycopg2
from database import connect
import uuid


def show_dashboard():
    st.title("Admin Dashboard")

    # Back to Home button
    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.session_state.logged_in = False  # Optionally log out
        st.session_state.role = None

    # Navigation within Customer Dashboard
    page = st.sidebar.selectbox("Select Option", ["View Car Lists", "View Driver Lists", "Profile"])

    if page == "View Car Lists":
        view_cars()
    elif page == "View Driver Lists":
        view_drivers()
    elif page == "Profile":
        st.write("Customer Profile Page (Coming Soon).")
    
def view_drivers():
    st.header("🚕 Driver Management")
    st.markdown("---")
    
    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch drivers data
        cur.execute("""
            SELECT first_name, last_name, email, phone, address, 
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
            filtered_drivers = [d for d in filtered_drivers if d[7] == "active"]
        elif filter_status =="Inactive":
            filtered_drivers = [d for d in filtered_drivers if d[7] == "inactive"]




        if search_term:
            search_term = search_term.lower()
            filtered_drivers = [
                d for d in filtered_drivers
                if search_term in d[0].lower() or 
                   search_term in d[1].lower() or
                   search_term in d[2].lower()
            ]

        # Display stats
        st.metric("Total Drivers", len(drivers))
        st.metric("Active Drivers", len([d for d in drivers if d[7] == "active"]))
        st.metric("Inactive Drivers", len([d for d in drivers if d[7] == "inactive"]))

        # Display drivers in cards
        for idx, driver in enumerate(filtered_drivers, 1):
            first_name, last_name, email, phone, address, location, license_number, account_status = driver

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
                            pass

                st.markdown("---")

        # Detailed view when a driver is selected
        if 'selected_driver' in st.session_state:
            driver = st.session_state.selected_driver
            st.subheader("Driver Details")
            cols = st.columns(2)
            
            with cols[0]:
                st.markdown(f"""
                **Full Name:** {driver[0]} {driver[1]}  
                **License Number:** {driver[6]}  
                **Status:** {"🟢 Active" if driver[7] == "active" else "🔴 Inactive"}   
                **Registration Date:** (add this field to your DB)
                """)
                
            with cols[1]:
                st.markdown(f"""
                **Contact Information**  
                Email: {driver[2]}  
                Phone: {driver[3]}  
                Location: {driver[5]}  
                Address: {driver[4]}
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
    st.header("Cars List")

    try:
        conn = connect()
        cur = conn.cursor()

        # Fetch all cars 
        cur.execute("SELECT car_number, model, seats, car_owner_id, availability_status FROM car")
        cars = cur.fetchall()

        if cars:
            count = 1
            
            for car_number, model, seats, car_owner_id, availability_status in cars:
                st.write(f"{count}. Car Number: {car_number}")
                st.write(f"   Model: {model}")
                st.write(f"   Seats: {seats}")
                st.write(f"   Car Owner ID: {car_owner_id}")
                st.write(f"   Status: {availability_status}")
                st.markdown("---")
                count += 1
           
               
                      
        else:
            st.info("No cars available.")
        conn.close()
    except Exception as e:                        
        st.error(f"An error occurred: {e}")
