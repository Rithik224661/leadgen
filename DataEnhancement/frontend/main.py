import streamlit as st

# Set page config first before any other Streamlit commands
st.set_page_config(page_title="Company Intelligence Tool", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        import requests
        
        response = requests.post(
            "http://localhost:5000/api/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.token = data["token"]
            st.session_state.username = data["username"]
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
else:
    st.sidebar.title("🔍 Navigation")
    st.sidebar.markdown("Choose a feature to use:")
    
    if st.sidebar.button("📤 Upload CSV"):
        st.switch_page("pages/upload.py")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.username = None
        st.rerun()
    
    st.title(f"Welcome to Company Intelligence Tool, {st.session_state.username}!")
    st.markdown("""
    This tool helps you gather intelligence about companies from various sources.
    Use the sidebar navigation to access different features.
    """)
