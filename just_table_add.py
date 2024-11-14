import streamlit as st
import psycopg2
from psycopg2 import sql

# Connect to PostgreSQL server
try:
    connection = psycopg2.connect(
        host="localhost",
        database="car_rent",
        user="postgres",
        password="sahil",
        port = 5000
    )
    cursor = connection.cursor()
    st.write("Connected to the database successfully.")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")


def create_tables():
    try:
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

        # Create Car table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Car (
                car_id VARCHAR(50) PRIMARY KEY,
                model VARCHAR(100),
                seats INT,
                availability_status VARCHAR(20)
            )
        ''')

        # Commit the changes
        connection.commit()
        st.write("Tables created successfully.")

    except Exception as e:
        st.error(f"An error occurred while creating tables: {e}")
        connection.rollback()

# Create tables
create_tables()

# Continue with the rest of your Streamlit app...
