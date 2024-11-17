import psycopg2
import os
import uuid

def connect():
    return psycopg2.connect(
        host="localhost",
        database="car_rent_RDBMS",
        user="postgres",
    )

def create_user_CarOwner(first_name, last_name, email, password, phone, address, location, account_status):
    conn = connect()
    cur = conn.cursor()
    owner_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Car_Owner (owner_id, first_name, last_name, email, password, phone, address, location, account_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (owner_id, first_name, last_name, email, password, phone, address, location, account_status)
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
