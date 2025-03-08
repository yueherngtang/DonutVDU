import streamlit as st 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

data_page = st.Page("data.py", title ="Saved Data")
scan_doc_page = st.Page("scan_doc.py", title ="Main Page")

if st.session_state.logged_in:
    pg = st.navigation([logout_page, scan_doc_page, data_page])
else:
    pg = st.navigation([login_page])


pg.run()


