import streamlit as st
import psycopg2
import uuid  # To generate unique IDs

# Connect to PostgreSQL server
#try:
connection = psycopg2.connect(
        host="localhost",
        database="car_rent_RDBMS",
        user="postgres",
        password="nfm143786007",
        port=5432
    )
cursor = connection.cursor()
   # st.write("Connected to the database successfully.")
#except Exception as e:
    #st.error(f"Error connecting to the database: {e}")


def create_tables():
    #try:
        # Create Customer table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customer (
                customer_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                account_status VARCHAR(20)
            )
        ''')

        # Create Driver table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Driver (
                driver_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                location VARCHAR(100),
                license_number VARCHAR(50),
                account_status VARCHAR(20)
            )
        ''')

        # Create Admin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Admin (
                admin_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100)
            )
        ''')

        
        # Create Car_OWNER table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Car_Owner (
                car_owner_id VARCHAR(50) PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(200),
                phone VARCHAR(20),
                address TEXT,
                location VARCHAR(100),
                account_status VARCHAR(20),
                car_type VARCHAR(50),  -- New attribute
                car_id VARCHAR(50)     -- New attribute
    
            )
        ''')
        
        # Create Car table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Car (
                car_number VARCHAR(50) PRIMARY KEY,
                model VARCHAR(100),
                seats INT,
                car_owner_id VARCHAR(100),
                availability_status VARCHAR(20),
                FOREIGN KEY (car_owner_id) REFERENCES Car_Owner(car_owner_id)
            )
        ''')

        # Create RENTAL  table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Request (
               request_id VARCHAR(50) PRIMARY KEY,
               customer_id VARCHAR(50),
               car_type VARCHAR(50),
               pickup_date TIMESTAMP,
               dropoff_date TIMESTAMP,
               pickup_location VARCHAR(100),
               dropoff_location VARCHAR(100),
               duration NUMERIC,
               payment_status VARCHAR(20),
               assigned_driver VARCHAR(50),
               car_number_plate VARCHAR(20),
               status VARCHAR(20),
               FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
               FOREIGN KEY (assigned_driver) REFERENCES Driver(driver_id),
               FOREIGN KEY (car_number_plate) REFERENCES Car(car_number)
            )
        ''')
        # Create REQUEST  table
        cursor.execute('''
           CREATE TABLE IF NOT EXISTS Rental (
               rental_id VARCHAR(50) PRIMARY KEY,
               request_id VARCHAR(50),
               driver_id VARCHAR(50),
               car_number_plate VARCHAR(20),
               pickup_date TIMESTAMP,
               dropoff_date TIMESTAMP,
               status VARCHAR(20),
               total_amount NUMERIC,
               payment_id VARCHAR(50),
               FOREIGN KEY (request_id) REFERENCES Request(request_id),
               FOREIGN KEY (driver_id) REFERENCES Driver(driver_id),
               FOREIGN KEY (car_number_plate) REFERENCES Car(car_number)
            )
        ''')


        # Commit the changes
        connection.commit()
        #st.write("Tables created successfully.")

    #except Exception as e:
        #st.error(f"An error occurred while creating tables: {e}")
        connection.rollback()

create_tables()






# # Function to insert data into the Admin table
# def insert_admin(username, password, email):
#     try:
#         # Generate a random UUID for admin_id
#         admin_id = str(uuid.uuid4())

#         # Insert query including admin_id
#         insert_query = """
#         INSERT INTO admin (admin_id, username, password, email) VALUES (%s, %s, %s, %s);
#         """
#         cursor.execute(insert_query, (admin_id, username, password, email))
#         connection.commit()  # Commit the transaction
#         st.success(f"Admin '{username}' added successfully with ID: {admin_id}")
#     except Exception as e:
#         st.error(f"An error occurred while inserting data: {e}")
#         connection.rollback()

# # Streamlit UI for user input
# st.title("Insert Admin Data with UUID")

# # Input fields
# admin_username = st.text_input("Username", placeholder="Enter admin username")
# admin_password = st.text_input("Password", placeholder="Enter password", type="password")
# admin_email = st.text_input("Email", placeholder="Enter admin email")

# # Insert data on button click
# if st.button("Insert Admin"):
#     if admin_username and admin_password and admin_email:
#         insert_admin(admin_username, admin_password, admin_email)
#     else:
#         st.warning("Please fill out all fields before inserting.")