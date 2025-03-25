import psycopg2
import os
import uuid

def connect():
    return psycopg2.connect(
        host="localhost",
        database="car_rent_RDBMS",
        user="postgres",
        password="sahil",
        port=5000
    )

def create_user_customer(first_name, last_name, email, password, phone, address, account_status):
    conn = connect()
    cur = conn.cursor()
    customer_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Customer (customer_id, first_name, last_name, email, password, phone, address, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
        (customer_id, first_name, last_name, email, password, phone, address,  account_status)
        )
    #user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

def create_user_driver(first_name, last_name, email, password, phone, address, location,license_number, account_status):
    conn = connect()
    cur = conn.cursor()
    driver_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Driver (driver_id, first_name, last_name, email, password, phone, address, location, license_number, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (driver_id, first_name, last_name, email, password, phone, address, location, license_number, account_status)
        )
    #user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

def create_user_CarOwner(first_name, last_name, email, password, phone, address, location, account_status):
    conn = connect()
    cur = conn.cursor()
    car_owner_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Car_Owner (car_owner_id, first_name, last_name, email, password, phone, address, location, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (car_owner_id, first_name, last_name, email, password, phone, address, location, account_status)
        )
    #user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

def authenticate_user(table_name, email, password):
    conn = connect()
    cur = conn.cursor()
    id_column = f"{table_name}_id"
    query = f"SELECT {id_column}, password FROM {table_name} WHERE email = %s"
    cur.execute(query, (email,))
    user = cur.fetchone()
    conn.close()
    return user
