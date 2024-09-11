import json

import firebase_admin
import streamlit as st
from firebase_admin import credentials


@st.cache_resource(show_spinner=True)
def init_server():
    key_dict = json.loads(st.secrets["firebase"]["textkey"])
    cred = credentials.Certificate(key_dict)
    bucket_name = 'chat-lt.appspot.com'
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {'storageBucket': bucket_name})