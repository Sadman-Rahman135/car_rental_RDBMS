import bcrypt
import re
import psycopg2
import streamlit as st
from database import connect

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'),hashed)

def validate_email(email):
    pattern = r'^[a-zA-z0-9._%+-]+@[a-zA-z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\+?[\d\s-]{10,15}$'
    return bool(re.match(pattern, phone))

def validate_password(password):
    return len(password)>=6

table_map={
        'admin': 'Admin',
        'car_owner': 'Car_Owner',
        'driver': 'Driver',
        'customer': 'Customer'
    }

def check_email_unique(email, user_id, role, conn):
    table=table_map.get(role)

    if not table:
        return False
    
    id_field=f"{role}_id"
    query = f"""
        SELECT COUNT(*)
        FROM {table}
        WHERE email = %s AND {id_field} != %s
    """

    try:
        cur = conn.cursor()
        cur.execute(query, (email, user_id))
        count = cur.fetchone()[0]
        cur.close()
        return count==0
    except Exception:
        return False
    
def display_profile_update(old_role):
    #role = st.session_state.get('role')
    user_id= st.session_state.user_id
    role = old_role
    #user_id= f"{role}_id"
    if not role or not user_id:
        st.error("You must be logged in to update your profile.")
        return
    
    st.subheader("👤Profile Information")
    conn=connect()
    try:
        cur = conn.cursor()
        table=table_map[role]
        id_field=f"{role}_id"
        #print("Table is :" + f"{table, user_id}")

        # Fetch current user details
        if table == 'Admin':
            fields = ['username', 'email', 'password']
            #print("use ??")
        else:
            fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'password']
            if table == 'Driver':
                fields.extend(['location', 'license_number'])
            fields.append('account_status')
        query = f"""
            SELECT {', '.join(fields)}
            FROM {table}
            WHERE {id_field} = %s
        """
        print("L1")
        cur.execute(query, (user_id,))
        print("L2")
        user = cur.fetchone()
        print("Luke")
        if not user:
            st.error("User not found.")
            return
        
        #if table == 'Admin':
        #    username, email, hashed_password = user
        #    print("use: " + f"{username}")
        #else:
        #    first_name, last_name, email, phone, address, hashed_password = user

        # Display current details
        user_data = dict(zip(fields, user))
        if table == 'Admin':
            username = user_data['username']
            email = user_data['email']
            print("use22: " + f"{username}")
        else:
            first_name = user_data['first_name']
            last_name = user_data['last_name']
            email = user_data['email']
            phone = user_data['phone']
            address = user_data['address']
            account_status = user_data['account_status']
            location = user_data.get('location', '')
            license_number = user_data.get('license_number', '')

        st.markdown("**Account Details**")
        if table == 'Admin':
            st.write(f"**Username**: {username}")
            st.write(f"**Email**: {email}")
            print("use66: " + f"{username}")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**First Name**: {first_name}")
                st.write(f"**Email**: {email}")
                st.write(f"**Phone**: {phone}")
                if table == 'Driver':
                    st.write(f"**Location**: {location}")
            with col2:
                st.write(f"**Last Name**: {last_name}")
                st.write(f"**Address**: {address}")
                st.write(f"**Status**: {'🟢 Active' if account_status == 'active' else '🔴 Inactive'}")
                if table == 'Driver':
                    st.write(f"**License Number**: {license_number}")
           
        st.markdown("---")
        # Toggle form visibility
        if 'show_profile_form' not in st.session_state:
            st.session_state.show_profile_form = False

        if table !='Admin':
            if st.button("Change Information"):
                st.session_state.show_profile_form = True

        if st.session_state.show_profile_form:
            st.subheader("Update Profile")
            with st.form("profile_update_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_first_name = st.text_input("First Name", value=first_name, placeholder="Leave blank to keep unchanged")
                    new_email = st.text_input("Email", value=email, placeholder="Leave blank to keep unchanged")
                    new_phone = st.text_input("Phone Number", value=phone, placeholder="Leave blank to keep unchanged")
                    if table == 'Driver':
                        new_location = st.text_input("Location", value=location, placeholder="Leave blank to keep unchanged")
                   
                with col2:
                    new_last_name = st.text_input("Last Name", value=last_name, placeholder="Leave blank to keep unchanged")
                    new_address = st.text_area("Address", value=address, placeholder="Leave blank to keep unchanged")
                    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                    if table == 'Driver':
                        new_license_number = st.text_input("License Number", value=license_number, placeholder="Leave blank to keep unchanged")
                    
                submit = st.form_submit_button("Submit Changes")

                if submit:
                    # Collect changed fields
                    update_fields = []
                    params = []
                    errors = []

                    if new_first_name and new_first_name != first_name:
                        update_fields.append("first_name = %s")
                        params.append(new_first_name)
                    if new_last_name and new_last_name != last_name:
                        update_fields.append("last_name = %s")
                        params.append(new_last_name)
                    if new_email and new_email != email:
                        if not validate_email(new_email):
                            errors.append("Invalid email format.")
                        elif not check_email_unique(new_email, user_id, table, conn):
                            errors.append("Email is already in use by another user.")
                        else:
                            update_fields.append("email = %s")
                            params.append(new_email)
                    if new_phone and new_phone != phone:
                        if not validate_phone(new_phone):
                            errors.append("Invalid phone number (10-15 characters, digits, +, -, spaces).")
                        else:
                            update_fields.append("phone = %s")
                            params.append(new_phone)
                    if new_address and new_address != address:
                        update_fields.append("address = %s")
                        params.append(new_address)
                    if new_password:
                        if not validate_password(new_password):
                            errors.append("Password must be at least 6 characters.")
                        else:
                            update_fields.append("password = %s")
                            params.append(hash_password(new_password))
                    if table == 'Driver':
                        if new_location and new_location != location:
                            update_fields.append("location = %s")
                            params.append(new_location)
                        if new_license_number and new_license_number != license_number:
                            update_fields.append("license_number = %s")
                            params.append(new_license_number)

                    if errors:
                        for error in errors:
                            st.error(error)
                        return

                    if not update_fields:
                        st.warning("No changes detected.")
                        return

                    # Update database
                    update_query = f"""
                        UPDATE {table}
                        SET {', '.join(update_fields)}
                        WHERE {id_field} = %s
                    """
                    params.append(user_id)

                    try:
                        cur.execute(update_query, params)
                        conn.commit()
                        st.success("Profile updated successfully!")
                        st.session_state.show_profile_form = False
                        st.rerun()  # Refresh to show updated details
                    except psycopg2.Error as e:
                        conn.rollback()
                        st.error(f"Error updating profile: {e}")

    except Exception as e:
        st.error(f"Error fetching profile: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()