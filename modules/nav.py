import streamlit as st
from streamlit import session_state as ss

st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 8px;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)


def HomeNav():
    st.sidebar.page_link("Home_page.py", label="Home", icon='🏠')


def LoginNav():
    st.sidebar.page_link("pages/account.py", label="Account", icon='🔐')


def DebugNav():
    st.sidebar.page_link("pages/debug.py", label="Debug", icon='🪲')


def ConfigNav():
    st.sidebar.page_link("pages/configuration.py", label="Page 2", icon='⚙️')


def MenuButtons(user_roles=None):

    logo_url = './img/logo.png'
    st.sidebar.image(logo_url, use_column_width=True)

    if user_roles is None:
        user_roles = {}

    if 'authentication_status' not in ss:
        ss.authentication_status = False

    # Always show the home and login navigators.
    HomeNav()
    LoginNav()

    # Show the other page navigators depending on the users' role.
    if ss["authentication_status"]:

        # (1) Only the admin role can access page 1 and other pages.
        # In a user roles get all the usernames with admin role.
        admins = [k for k, v in user_roles.items() if v == 'admin']

        # Show page 1 if the username that logged in is an admin.
        if ss.username in admins:
            ConfigNav()
            DebugNav()