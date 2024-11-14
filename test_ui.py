import streamlit as st

# Function to display the Login page
def show_login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.success(f"Welcome back, {username}!")
        # Add your authentication logic here.

# Function to display the Registration page
def show_register_page():
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password:
            st.success(f"Account created for {username}!")
            # Add your registration logic here.
        else:
            st.error("Passwords do not match. Please try again.")

# Main Homepage
def main():
    st.set_page_config(page_title="Welcome", page_icon="🌟")
    st.title("Welcome to the Application")

    # Navigation: Login or Register
    action = st.radio("Choose an option:", ["Login", "Register"])

    # Display the corresponding page based on the selection
    if action == "Login":
        show_login_page()
    elif action == "Register":
        show_register_page()

# Run the Streamlit app
if __name__ == "__main__":
    main()
