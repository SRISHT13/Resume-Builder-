import streamlit as st
from main import main
from main2 import ats_scanner


st.set_page_config(
    page_title="ResumeBuilder",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp {
            background:linear-gradient(to right top, #1e1e2f, #2a1f3d, #402647, #5b2b4d, #7a2e4e);
        }

        .stButton>button {
            background-color: #E5DEFF;
            color: #333;
            border: none;
            padding: 15px 20px;
            font-size: 18px;
            border-radius: 25px;
            width: 100%;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }

        .stButton>button:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        

        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

if 'page' not in st.session_state:
    st.session_state.page = 'home'

def back_button():
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        if st.button("← Back", key="back_button"):
            st.session_state.page = 'home'
            st.rerun()

def home_page():
    st.title("Smart Resume Builder")
    if st.button("Build my Resume"):
        st.session_state.page="resume_builder"
        st.rerun()
    if st.button("Ats Scanner"):
        st.session_state.page="ats_scanner"
        st.rerun()

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "resume_builder":
    back_button()
    main()
elif st.session_state.page == "ats_scanner":
    back_button()
    ats_scanner()
