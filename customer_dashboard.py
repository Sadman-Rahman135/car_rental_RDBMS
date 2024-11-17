import streamlit as st
from database import connect

def show_dashboard():
    st.title("Owner Dashboard")
    conn = connect()
    cur = conn.cursor()

    st.header("Add a Car")
    model = st.text_input("Car Model")
    if st.button("Add Car"):
        cur.execute("""
            INSERT INTO cars (owner_id, model)
            VALUES (%s, %s)
        """, (st.session_state.user_id, model))
        conn.commit()
        st.success(f"Car {model} added!")

    st.header("Orders for Your Cars")
    cur.execute("""
        SELECT o.id, o.status, c.model, u.username 
        FROM orders o 
        JOIN cars c ON o.car_id = c.id
        JOIN users u ON o.renter_id = u.id
        WHERE c.owner_id = %s
    """, (st.session_state.user_id,))
    orders = cur.fetchall()
    
    for order_id, status, model, renter in orders:
        st.write(f"Order {order_id}: {model} (by {renter}) - {status}")
        if status == "pending":
            if st.button("Approve", key=f"approve-{order_id}"):
                cur.execute("UPDATE orders SET status = 'approved' WHERE id = %s", (order_id,))
                conn.commit()
                st.success("Order approved!")
            if st.button("Reject", key=f"reject-{order_id}"):
                cur.execute("UPDATE orders SET status = 'rejected' WHERE id = %s", (order_id,))
                conn.commit()
                st.warning("Order rejected!")
    conn.close()
