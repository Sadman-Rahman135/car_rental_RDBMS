import streamlit as st
from auth import login, registerCarOwner
from admin_dashboard import show_dashboard as admin_dashboard
from owner_dashboard import show_dashboard as owner_dashboard
from customer_dashboard import show_dashboard as customer_dashboard
from driver_dashboard import show_dashboard as driver_dashboard

st.sidebar.title("Navigation")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    role = st.session_state.role
    if role == "👨‍💼 Admin":
        admin_dashboard()
    elif role == "🧑‍🤝‍🧑 Car Owner":
        owner_dashboard()
    elif role == "🧑‍🤝‍🧑 Customer":
        customer_dashboard()
    elif role == "🚚 Driver":
        driver_dashboard()
else:
    role = st.sidebar.selectbox("Select your role", ["👨‍💼 Admin", "🧑‍🤝‍🧑 Car Owner", "🧑‍🤝‍🧑 Customer", "🚚 Driver"])
    action = st.sidebar.selectbox("Action", ["Login", "Register"])
    if action == "Login":
        login(role)
    elif action == "Register":
        if role == "👨‍💼 Admin":
            admin_dashboard()
        elif role == "🧑‍🤝‍🧑 Car Owner":
            registerCarOwner()
        elif role == "🧑‍🤝‍🧑 Customer":
            customer_dashboard()
        elif role == "🚚 Driver":
            driver_dashboard()
        
