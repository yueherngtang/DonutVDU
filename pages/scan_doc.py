import streamlit as st
import numpy as np
from PIL import Image
from main import mongo_login, hash_password
import time
from mongoDB import test_mongo_connection, MongoDBHandlerUser
import pandas as pd
from datetime import datetime
# from main import donut
from io import BytesIO
import base64

if "force_main_redirect" not in st.session_state:
    st.session_state.force_main_redirect = True
    st.session_state.clear()
    st.switch_page("main.py")

def greet_based_on_time():
    now = datetime.now()
    current_hour = now.hour

    if 5 <= current_hour < 12:
        return "Good Morning,"
    elif 12 <= current_hour < 18:
        return "Good Afternoon,"
    else:
        return "Good Evening,"
    
image_path = 'DokuScan_logo.png'
image = Image.open(image_path)
buffered = BytesIO()
image.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()
html_code = f"""
    <div style="display: flex; justify-content: flex-end;">
        <img src="data:image/png;base64,{img_base64}" width="70" style="display: block; margin: 0 auto;" />
    </div>
"""
st.markdown(html_code, unsafe_allow_html=True)

greeting = greet_based_on_time()
st.title(greeting + " " + st.session_state.log_in_user)

tab1, tab2, tab3 = st.tabs(["Scanner", "Search", "Profile"])

# potentially explore st.data_editor
with tab1:
    
    def clean_data(obj):
        if isinstance(obj, dict):
            cleaned = {
                k: clean_data(v)
                for k, v in obj.items()
                if not is_empty(v)
            }
            return cleaned if cleaned else None

        elif isinstance(obj, list):
            cleaned = [clean_data(item) for item in obj]
            cleaned = [item for item in cleaned if not is_empty(item)]
            return cleaned if cleaned else None

        else:
            return obj if not is_empty(obj) else None

    def is_empty(value):
        # Catch None, empty string, empty list/dict, NaN
        return (
            value is None
            or value == ""
            or value == []
            or value == {}
            or (isinstance(value, float) and pd.isna(value))
        )

    if st.session_state.db_user is None:
        st.error(f"Failed to connect to MongoDB. Scanner output will not be saved.")
        
    document = st.camera_input(label = "Take a Photo", help = "Take a photo of a document")

    uploaded_document = st.file_uploader(label = "Upload a Photo", type = ["jpg", "jpeg", "png"], accept_multiple_files = False, help = "Upload a photo document")

    # if document is not None:
    #     img = Image.open(document)
    #     img_array = np.array(img)
    #     st.image(img)
    #     st.write(img_array.shape)
        

    #     # To change the image to other formats: visit this link https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input

    # if uploaded_document is not None:
    #     img = Image.open(uploaded_document)
    #     img_array = np.array(img)
    #     st.image(img)
    #     st.write(img_array.shape)
    #     with st.spinner("Running inference..."):
    #         run_donut = donut.run_inference(img, image_name="testing.jpg")
    #     st.success("Inference complete!")

    img = None
    if document is not None:
        img = Image.open(document)
        filename = None
    elif uploaded_document is not None:
        img = Image.open(uploaded_document)
        filename = uploaded_document.name

    # If we have an image, show it and the Extract button
    if img is not None:
        img_array = np.array(img)
        st.image(img, caption="Input Image")
        st.write("Image shape:", img_array.shape)
        if filename is None:
            filename = st.text_input("Enter a filename for the image", value="untitled.png")
        
        if "run_donut_result" not in st.session_state:
            st.session_state.run_donut_result = None

        if st.button("Extract"):
            with st.spinner("Running inference..."):
                st.session_state.pop("preview", None)
                st.session_state.pop("edit_clicked", None)
                donut = st.session_state.donut
                run_donut = donut.run_inference(img, image_name= filename)
                st.session_state.run_donut_result = run_donut
        
        if st.session_state.run_donut_result:
            st.write("Extracted result:", st.session_state.run_donut_result)
            save_button = st.button("Save result")
            edit_button = st.button("Edit result")
            if "edit_clicked" not in st.session_state:
                st.session_state.edit_clicked = False
            if save_button:
                if st.session_state.db_user is not None:
                    st.session_state.db_user.save_inference_result(filename, "cord-v2", st.session_state.run_donut_result) 
                    st.success("Result saved to database!")
                else:
                    st.error("Result failed to save. Please check your database configurations in 'Profile' tab")
            if edit_button:
                st.session_state.preview = None
                st.session_state.edit_clicked = True

            if "edited_menu_df" not in st.session_state:
                st.session_state.edited_menu_df = pd.DataFrame(st.session_state.run_donut_result.get("menu", []))

            if "edited_total_df" not in st.session_state:
                st.session_state.edited_total_df = pd.DataFrame([st.session_state.run_donut_result.get("total", {})])

            if "edited_subtotal_df" not in st.session_state:
                st.session_state.edited_subtotal_df = pd.DataFrame([st.session_state.run_donut_result.get("subtotal", {})])

        if st.session_state.run_donut_result and st.session_state.edit_clicked is True:
            st.subheader("Basic Info")
            edited_output = {}

            edited_output["merchant"] = st.text_input("Merchant", value=st.session_state.run_donut_result.get("merchant", ""))
            edited_output["date"] = st.text_input("Date", value=st.session_state.run_donut_result.get("date", ""))
            edited_output["recipient"] = st.text_input("Recipient", value=st.session_state.run_donut_result.get("recipient", ""))

            # --- MENU ---
            st.subheader("Menu")
            new_menu_col = st.text_input("Add new column to Menu", key="new_menu_col")
            if st.button("Add Column to Menu") and new_menu_col:
                if new_menu_col not in st.session_state.edited_menu_df.columns:
                    st.session_state.edited_menu_df[new_menu_col] = ""

            st.session_state.edited_menu_df = st.data_editor(
                st.session_state.edited_menu_df, num_rows="dynamic", use_container_width=True
            )
            edited_output["menu"] = st.session_state.edited_menu_df.to_dict(orient="records")

            # --- TOTAL ---
            st.subheader("Total")
            new_total_col = st.text_input("Add new column to Total", key="new_total_col")
            if st.button("Add Column to Total") and new_total_col:
                if new_total_col not in st.session_state.edited_total_df.columns:
                    st.session_state.edited_total_df[new_total_col] = ""

            st.session_state.edited_total_df = st.data_editor(
                st.session_state.edited_total_df, num_rows=1, use_container_width=True
            )
            edited_output["total"] = st.session_state.edited_total_df.iloc[0].to_dict()

            # --- SUBTOTAL ---
            st.subheader("Subtotal")
            new_subtotal_col = st.text_input("Add new column to Subtotal", key="new_subtotal_col")
            if st.button("Add Column to Subtotal") and new_subtotal_col:
                if new_subtotal_col not in st.session_state.edited_subtotal_df.columns:
                    st.session_state.edited_subtotal_df[new_subtotal_col] = ""

            st.session_state.edited_subtotal_df = st.data_editor(
                st.session_state.edited_subtotal_df, num_rows=1, use_container_width=True
            )
            edited_output["subtotal"] = st.session_state.edited_subtotal_df.iloc[0].to_dict()

            # --- SAVE ---
            
            if st.button("Preview result"):
                st.session_state.pop("preview", None)
                # st.write(edited_output)
                cleaned = clean_data(edited_output)
                st.write(cleaned)
                if "preview" not in st.session_state:
                    st.session_state.preview =cleaned

            if st.session_state.preview:
                save_edited_button = st.button("Save edited result")
                if save_edited_button:
                    if st.session_state.db_user is not None:
                        st.session_state.db_user.save_inference_result(filename, "cord-v2", st.session_state.preview) 
                        st.success("Result saved to database!")
                        st.session_state.preview = None
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Result failed to save. Please check your database configurations in 'Profile' tab")
                        st.session_state.preview = None
                        time.sleep(2)
                        st.rerun()

                    # if st.session_state.db_user is not None:
                    #     st.session_state.db_user.save_inference_result(filename, "cord-v2", edited_output) 
                    #     st.success("Result saved to database!")
                    # else:
                    #     st.error("Result failed to save. Please check your database configurations in 'Profile' tab")



with tab2:
    st.header("Search")
    if st.session_state.db_user is not None:
        if "trigger_search" not in st.session_state:
            st.session_state.trigger_search = False

        with st.expander("Advanced Filters"):
            col1, col2, col3 = st.columns(3)
            with col1:
                merchant_filter = st.text_input("Merchant contains")
                recipient_filter = st.text_input("Recipient contains")

            with col2:
                min_date = st.date_input("From date")
                max_date = st.date_input("To date")

            with col3:
                min_price = st.number_input("Min total price")
                max_price = st.number_input("Max total price")
            
            if st.button("🔎 Search"):
                st.session_state.trigger_search = True

        
        if st.session_state.trigger_search:
            keys = []
            values = []
            if merchant_filter:
                keys.append("merchant")
                values.append(merchant_filter)
            if recipient_filter:
                keys.append("recipient")
                values.append(recipient_filter)

            min_price_val = min_price if min_price else None
            max_price_val = max_price if max_price else None

            results = st.session_state.db_user.search_results(
                keys=keys,
                values=values,
                min_price=min_price_val,
                max_price=max_price_val
            )
        else:
            results = st.session_state.db_user.get_all_results()
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width= True)

        

with tab3:
    st.header("Profile")
    st.markdown(f"""Username: {st.session_state.log_in_user}""")
    st.markdown("<br>", unsafe_allow_html=True)


    st.subheader("Change Password")

    # Initialize a session state variable to control the visibility of the password fields
    if 'change_password_active' not in st.session_state:
        st.session_state['change_password_active'] = True

    if st.session_state['change_password_active']:
        old_pw = st.text_input("Old Password", type="password", key="old_pw")
        new_pw = st.text_input("New Password", type="password", key="new_pw")
        new_pw_retype = st.text_input("Retype New Password", type="password", key="new_pw_retype")

        change_pw_button = st.button("Change Password")

        if change_pw_button:
            if new_pw != new_pw_retype:
                st.error("Retyped Password Does Not Match")
            else:
                if mongo_login.login(st.session_state.log_in_user, old_pw):
                    mongo_login.change_password(st.session_state.log_in_user, hash_password(new_pw_retype))
                    st.success("Password Changed Successfully!")
                    time.sleep(2)
                    # Set the session state to False to hide the inputs after a successful change
                    st.session_state['change_password_active'] = False
                    st.rerun()
                else:
                    st.error("Old Password Is Incorrect")
    else:
        st.write("Reset the form to update password again.")
        if st.button("Reset Password Form"):
            st.session_state['change_password_active'] = True

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Update Database Configurations")
    new_db_name = st.text_input("MongoDB Database Name")
    new_collection_name = st.text_input("Database Collection Name")
    new_mongo_client = st.text_input("MongoDB Connection String", type="password")

    if not new_db_name or not new_collection_name or not new_mongo_client:
        st.warning("Please fill in all required fields.")
        submit_disabled = True
    else:
        submit_disabled = False

    if st.button("Submit", disabled=submit_disabled):
        if test_mongo_connection(new_mongo_client):
            if mongo_login.change_db_config(st.session_state.log_in_user, new_db_name, new_collection_name, new_mongo_client):
                user = mongo_login.get_user(st.session_state.log_in_user)
                st.session_state.db_user = MongoDBHandlerUser(user['db_name'], user['collection_name'], user['mongo_client'])
                st.success("Database Configuration Successfully!")
            else:
                st.error("Database Configuration Update Failed")

        else:
            st.error("Ping unnsuccessful. Please check your MongoDB configutation & ensure the Connection String entered is correct.")


    st.subheader("Account Management")
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state.clear()  # Optionally clear all session state on logout
        st.switch_page("main.py")