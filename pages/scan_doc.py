import streamlit as st
import numpy as np
from PIL import Image
from main import mongo_login, hash_password
import time
from mongoDB import test_mongo_connection, MongoDBHandlerUser
import pandas as pd
from datetime import datetime, date
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
    
    def clean_donut_output(x):
        if isinstance(x, list):
            ret = {}
            ret["uncategorized"] = []
            for obj in x:
                ret["uncategorized"].append(obj)
            return ret
        return x

    def clean_final_preview(output):
        allow_saving = True
        if not isinstance(output, dict):
            st.toast("Preview is not a Dict!")
            allow_saving = False

        if "date" in output.keys() and not isinstance(output["date"], datetime):
            try:
                output["date"] = datetime.combine(output["date"], datetime.min.time())
            except ValueError:
                st.toast("Date Format is Incorrect, Please Check the Date Field.")
                allow_saving = False
        
        if "subtotal" in output.keys():
            if "subtotal_price" in output["subtotal"].keys():
                try:
                    output["subtotal"]["subtotal_price"] = float(output["subtotal"]["subtotal_price"].replace(",",""))
                except (ValueError, TypeError):
                    st.toast("subtotal_price Format is Incorrect, Please make sure there are no spaces or currencies.")
                    allow_saving = False
            else:
                output["subtotal"]["subtotal_price"] =  0

        if "total" in output.keys():
            if "total_price" in output["total"]:
                try:
                    output["total"]["total_price"] = float(output["total"]["total_price"].replace(",",""))
                except (ValueError, TypeError):
                    st.toast("total_price Format is Incorrect, Please make sure there are no spaces or currencies.")
                    allow_saving = False
            else:
                output["total"]["total_price"] = 0

            if  "cashprice" in output["total"]:
                try:
                    output["total"]["cashprice"] = float(output["total"]["cashprice"].replace(",",""))
                except (ValueError, TypeError):
                    st.toast("cashprice Format is Incorrect, Please make sure there are no spaces or currencies.")
                    allow_saving = False
            
            if  "changeprice" in output["total"]:
                try:
                    output["total"]["changeprice"] = float(output["total"]["changeprice"].replace(",",""))
                except (ValueError, TypeError):
                    st.toast("changeprice Format is Incorrect, Please make sure there are no spaces or currencies.")
                    allow_saving = False
                
            if  "menuqty_cnt" in output["total"]:
                try:
                    output["total"]["menuqty_cnt"] = float(output["total"]["menuqty_cnt"].replace(",",""))
                except (ValueError, TypeError):
                    st.toast("menuqty_cnt Format is Incorrect, Please make sure there are no spaces or currencies.")
                    allow_saving = False
        
        if "menu" in output.keys():
            for menu in output["menu"]:
                if "cnt" in menu:
                    try:
                        menu["cnt"] = float(menu["cnt"].replace(",", ""))
                    except (ValueError, TypeError):
                        st.toast("Menu cnt not in numerical format")
                        allow_saving = False
                if "unitprice" in menu:
                    try:
                        menu["unitprice"] = float(menu["unitprice"].replace(",", ""))
                    except (ValueError, TypeError):
                        st.toast("Menu unitprice not in numerical format")
                        allow_saving = False
                
                if "discountprice" in menu:
                    try:
                        menu["discountprice"] = float(menu["discountprice"].replace(",", ""))
                    except (ValueError, TypeError):
                        st.toast("Menu discountprice not in numerical format")
                        allow_saving = False
                if "price" in menu:
                    try:
                        menu["price"] = float(menu["price"].replace(",", ""))
                    except (ValueError, TypeError):
                        st.toast("Menu price not in numerical format")
                        allow_saving = False
                
                if "itemsubtotal" in menu:
                    try:
                        menu["itemsubtotal"] = float(menu["itemsubtotal"].replace(",", ""))
                    except (ValueError, TypeError):
                        st.toast("Menu itemsubtotal not in numerical format")
                        allow_saving = False

        return output, allow_saving
 

                


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
                st.session_state.run_donut_result = clean_donut_output(run_donut)
        
        if st.session_state.run_donut_result:
            st.write("Extracted result:", st.session_state.run_donut_result)
            # save_button = st.button("Save result")
            edit_button = st.button("Edit result")
            if "edit_clicked" not in st.session_state:
                st.session_state.edit_clicked = False
            # if save_button:
            #     if st.session_state.db_user is not None:
            #         st.session_state.db_user.save_inference_result(filename, "cord-v2", st.session_state.run_donut_result) 
            #         st.success("Result saved to database!")
            #     else:
            #         st.error("Result failed to save. Please check your database configurations in 'Profile' tab")
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
            raw_date = st.session_state.run_donut_result.get("date","")

            edited_output["merchant"] = st.text_input("Merchant", value=st.session_state.run_donut_result.get("merchant", ""))
            try:
                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y").date()
            except Exception:
                parsed_date = date.today()
            edited_output["date"] = st.date_input("Date", value=parsed_date)
            edited_output["recipient"] = st.text_input("Recipient", value=st.session_state.run_donut_result.get("recipient", ""))

            # --- MENU ---
            st.subheader("Menu")
            predefined_menu_columns = ["nm", "cnt", "num", "unitprice", "discountprice", "itemsubtotal", "etc"]
            new_menu_col = st.selectbox("Add new column to Menu", options = predefined_menu_columns, key="new_menu_col")
            if st.button("Add Column to Menu") and new_menu_col:
                if new_menu_col in st.session_state.edited_menu_df.columns:
                    st.toast("This column already exists!")
                elif new_menu_col not in st.session_state.edited_menu_df.columns:
                    st.session_state.edited_menu_df[new_menu_col] = ""

            st.session_state.edited_menu_df = st.data_editor(
                st.session_state.edited_menu_df, num_rows="dynamic", use_container_width=True, key = "key1"
            )
            edited_output["menu"] = st.session_state.edited_menu_df.to_dict(orient="records")

            # --- TOTAL ---
            st.subheader("Total")
            predefined_total_columns = ["total_price", "total_etc", "cashprice", "changeprice", "menuqty_cnt"]
            new_total_col = st.selectbox("Add new column to Total", options = predefined_total_columns, key="new_total_col")
            if st.button("Add Column to Total") and new_total_col:
                if new_total_col in st.session_state.edited_total_df.columns:
                    st.toast("This column already exists!")
                elif new_total_col not in st.session_state.edited_total_df.columns:
                    st.session_state.edited_total_df[new_total_col] = ""

            st.session_state.edited_total_df = st.data_editor(
                st.session_state.edited_total_df, num_rows=1, use_container_width=True, key = "key2"
            )
            edited_output["total"] = st.session_state.edited_total_df.iloc[0].to_dict()

            # --- SUBTOTAL ---
            st.subheader("Subtotal")
            predefined_subtotal_columns = ["subtotal_price", "discount_price", "service_price", "othersvc_price", "tax_price", "subtotal_etc"]
            new_subtotal_col = st.selectbox("Add new column to Subtotal", options = predefined_subtotal_columns, key="new_subtotal_col")
            if st.button("Add Column to Subtotal") and new_subtotal_col:
                if new_subtotal_col in st.session_state.edited_subtotal_df.columns:
                    st.toast("This column already exists!")
                elif new_subtotal_col not in st.session_state.edited_subtotal_df.columns:
                    st.session_state.edited_subtotal_df[new_subtotal_col] = ""

            st.session_state.edited_subtotal_df = st.data_editor(
                st.session_state.edited_subtotal_df, num_rows=1, use_container_width=True, key = "key3"
            )
            edited_output["subtotal"] = st.session_state.edited_subtotal_df.iloc[0].to_dict()

            # --- SAVE ---
            
            if st.button("Preview result"):
                st.session_state.pop("preview", None)
                # st.write(edited_output)
                cleaned = clean_data(edited_output)
                # st.write(cleaned)
                st.session_state.allow_save = False
                if "preview" not in st.session_state:
                    st.session_state.preview, st.session_state.allow_save  = clean_final_preview(cleaned)
                    st.write(st.session_state.preview)

            if st.session_state.preview and st.session_state.allow_save:
                save_edited_button = st.button("Save edited result")
                if save_edited_button:
                    if st.session_state.db_user is not None:
                        st.session_state.db_user.save_inference_result(filename, "cord-v2", st.session_state.preview) 
                        st.success("Result saved to database!")
                        st.session_state.preview = None
                        # time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Result failed to save. Please check your database configurations in 'Profile' tab")
                        st.session_state.preview = None
                        # time.sleep(2)
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
            results = st.session_state.db_user.search_results(keys = keys, values = values)
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