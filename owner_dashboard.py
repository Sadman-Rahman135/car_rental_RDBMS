import streamlit as st
from database import connect

def show_dashboard():
    st.title("Owner Dashboard")
    conn = connect()
    cur = conn.cursor()

    st.header("Add a Car")
    car_number = st.text_input("Car Number Plate")
    model = st.text_input("Car Model")
    seats = st.number_input("No. Of Seats")

    
    status="active"
    if st.button("Add Car"):
        cur.execute("""
            INSERT INTO car (car_number, model, seats, car_owner_id, availability_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (car_number, model, seats, st.session_state.user_id, status))
        conn.commit()
        
        st.success(f"Car {model} added!")

    st.header("View Your Cars")
    cur.execute("""
        SELECT car_number, model, seats, availability_status
        FROM car 
        WHERE car_owner_id = %s
    """, (st.session_state.user_id,))
    orders = cur.fetchall()
    
    count=1
    for car_number, model, seats, availability_status in orders:
        st.write(f"{count} Car {car_number}: {model} {seats} seater is {availability_status}")
        count+=1
        # if status == "pending":
        #     if st.button("Approve", key=f"approve-{order_id}"):
        #         cur.execute("UPDATE orders SET status = 'approved' WHERE id = %s", (order_id,))
        #         conn.commit()
        #         st.success("Order approved!")
        #     if st.button("Reject", key=f"reject-{order_id}"):
        #         cur.execute("UPDATE orders SET status = 'rejected' WHERE id = %s", (order_id,))
        #         conn.commit()
        #         st.warning("Order rejected!")
    conn.close()
