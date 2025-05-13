import streamlit as st
from donut_model import DonutInference
from mongoDB import MongoDBHandlerLogin, MongoDBHandlerUser
import time
import bcrypt
from PIL import Image
from io import BytesIO
import base64

st.session_state.force_main_redirect = False

mongo_login = MongoDBHandlerLogin()

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

users = {
    "test_user": "098f6bcd4621d373cade4e832627b4f6"  # password is "test"
}

if "donut" not in st.session_state:
    st.session_state.donut = DonutInference()

def navigate_to_signup():
    st.session_state.page = "signup"

def navigate_to_login():
    st.session_state.page = "login"

if "login" not in st.session_state:
    st.session_state.login = True
    

if st.session_state.login:
    image_path = 'DokuScan_logo.png'
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    html_code = f"""
        <div style="display: flex; justify-content: flex-end;">
            <img src="data:image/png;base64,{img_base64}" width="100" style="display: block; margin: 0 auto;" />
        </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)


    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        st.markdown("<h1 style='text-align: center;'>Welcome to DokuScan</h1><br><br>", unsafe_allow_html=True)


        # Login section
        st.subheader("Please Login To Retrieve Your MongoDB Configurations")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2, col3 = st.columns([2, 2, 1])
        with col2:
            login_button = st.button("Log In")
            st.button("Sign Up", on_click=navigate_to_signup)
        
        if login_button:
            if mongo_login.login(username, password):
                st.success(f"Welcome {username}")
                user = mongo_login.get_user(username)
                try:
                    st.session_state.db_user = MongoDBHandlerUser(
                        user['db_name'],
                        user['collection_name'],
                        user['mongo_client']
                    )
                except Exception as e:
                    st.session_state.db_user = None
                # time.sleep(2)
                st.session_state.log_in_user = username
                st.session_state.login = False
                st.switch_page("pages/scan_doc.py")

            else:
                st.error("Invalid username or password")

        # Navigate to sign-up page
        

    elif st.session_state.page == "signup":
        st.title("Getting Started")

        # Sign Up section
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_db_name = st.text_input("MongoDB Database Name")
        new_collection_name = st.text_input("Database Collection Name")
        new_mongo_client = st.text_input("MongoDB Connection String", type="password")

        signup_button = st.button("Sign Up Now")

        if signup_button:
            if mongo_login.add_user(new_user, hash_password(new_password), new_db_name, new_collection_name, new_mongo_client):
                st.success("You have successfully created an account!")

            else:
                st.error("Username already exists")

        # Navigate back to login page
        st.button("Back to Login", on_click=navigate_to_login)


# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# def login():
#     if st.button("Log in"):
#         st.session_state.logged_in = True
#         st.rerun()

# def logout():
#     if st.button("Log out"):
#         st.session_state.logged_in = False
#         st.rerun()

# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# data_page = st.Page("data.py", title ="Saved Data")
# scan_doc_page = st.Page("scan_doc.py", title ="Main Page")

# if st.session_state.logged_in:
#     pg = st.navigation([logout_page, scan_doc_page, data_page])
# else:
#     pg = st.navigation([login_page])
