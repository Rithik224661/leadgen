import streamlit as st
from streamlit_cookies_controller import CookieController
import pandas as pd
import requests
import jwt

JWT_SECRET = "fallback_secret_change_me_in_production"
JWT_ALGORITHM = "HS256"
BACKEND_URL = "http://localhost:5000"

cookies = CookieController()
token = cookies.get("auth_token")

if token and "logged_in" not in st.session_state:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        st.session_state.token = token
        st.session_state.logged_in = True
        st.session_state.username = decoded.get("username")
    except jwt.ExpiredSignatureError:
        cookies.delete("auth_token")
        st.warning("Session expired.")
        st.stop()
    except jwt.InvalidTokenError:
        cookies.delete("auth_token")
        st.warning("Invalid session.")
        st.stop()

if not st.session_state.get("logged_in"):
    st.warning("Please log in first.")
    st.stop()

def auth_headers():
    token = st.session_state.get("token")
    if not token:
        st.error("Missing token. Please log in again.")
        st.stop()
    return {"Authorization": f"Bearer {token}"}

def normalize_name(name):
    return name.strip().lower().replace(" ", "").replace("-", "").replace(".", "") if name else ""

def generate_linkedin_lookup(response_json):
    return {
        normalize_name(r.get("Business Name")): r
        for r in response_json
        if r.get("Business Name")
    }

def split_name(full_name):
    parts = full_name.strip().split()
    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], " ".join(parts[1:])

STANDARD_COLUMNS = [
    'Company', 'City', 'State', 'First Name', 'Last Name', 'Email', 'Title', 'Website',
    'LinkedIn URL', 'Industry', 'Revenue', 'Product/Service Category',
    'Business Type (B2B, B2B2C)', 'Associated Members', 'Employees range', 'Rev Source', 'Year Founded',
    "Owner's LinkedIn", 'Owner Age', 'Phone Number', 'Additional Notes', 'Score',
    'Email customization #1', 'Subject Line #1', 'Email Customization #2', 'Subject Line #2',
    'LinkedIn Customization #1', 'LinkedIn Customization #2', 'Reasoning for r//y/g'
]

COLUMN_MAPPING = {
    'company': 'Company',
    'company name': 'Company',
    'business name': 'Company',
    'organization': 'Company',
    'city': 'City',
    'state': 'State',
    'first name': 'First Name',
    'firstname': 'First Name',
    'last name': 'Last Name',
    'lastname': 'Last Name',
    'email': 'Email',
    'title': 'Title',
    'website': 'Website',
    'linkedin url': 'LinkedIn URL',
    'linkedin': 'LinkedIn URL',
    'industry': 'Industry',
    'revenue': 'Revenue',
    'category': 'Product/Service Category',
    'business type': 'Business Type (B2B, B2B2C)',
    'members': 'Associated Members',
    'employees': 'Employees range',
    'revenue source': 'Rev Source',
    'founded': 'Year Founded',
    'owner linkedin': "Owner's LinkedIn",
    'owner age': 'Owner Age',
    'phone': 'Phone Number',
    'notes': 'Additional Notes',
    'score': 'Score'
}

def normalize_column_name(col):
    """Normalize column names to match standard format"""
    col = str(col).lower().strip()
    col = col.replace(' ', '').replace('_', '').replace('-', '')
    return col

def normalize_dataframe(df):
    """Normalize the dataframe columns to match standard format"""
    # Create a new dataframe with standard columns
    normalized = pd.DataFrame(columns=STANDARD_COLUMNS)
    
    # Map input columns to standard columns
    for col in df.columns:
        normalized_col = normalize_column_name(col)
        if normalized_col in COLUMN_MAPPING:
            standard_col = COLUMN_MAPPING[normalized_col]
            normalized[standard_col] = df[col]
    
    # Ensure all columns exist (fill with empty strings if missing)
    for col in STANDARD_COLUMNS:
        if col not in normalized.columns:
            normalized[col] = ''
    
    return normalized

st.set_page_config(page_title="📤 Upload CSV & Normalize", layout="wide")
st.title("📤 Upload & Normalize Lead Data")
st.markdown("""
Welcome! This tool allows you to upload a CSV file and normalize its structure 
to match our standard format, and enrich it with Apollo, LinkedIn, and Growjo data.
""")

if "normalized_df" not in st.session_state:
    st.session_state.normalized_df = None
if "confirmed_selection_df" not in st.session_state:
    st.session_state.confirmed_selection_df = None

st.markdown("### 📎 Step 1: Upload Your CSV")
uploaded_file = st.file_uploader("Choose a CSV file to upload", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")

        # Normalize the dataframe
        normalized_df = normalize_dataframe(df)
        st.session_state.normalized_df = normalized_df

        st.markdown("### 🔍 Normalized Data Preview")
        st.dataframe(normalized_df, use_container_width=True)
        
        if st.button("📥 Download Normalized CSV"):
            csv = normalized_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Normalized CSV",
                csv,
                file_name="normalized.csv",
                mime="text/csv"
            )

        if st.button("🚀 Enhance with Apollo, LinkedIn, and Growjo Data"):
            st.markdown("⏳ Please wait while we enrich company data...")
            
            # Get the companies to enhance
            companies = normalized_df['Company'].dropna().tolist()
            
            if not companies:
                st.error("❌ No company names found in the data")
                st.stop()

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare headers for API calls
            headers = auth_headers()
            
            try:
                # Enhance with Apollo
                status_text.text("🔍 Fetching data from Apollo...")
                apollo_response = requests.post(
                    f"{BACKEND_URL}/api/apollo-info",
                    json=[{"domain": company} for company in companies],
                    headers=headers
                )
                apollo_data = apollo_response.json() if apollo_response.ok else []
                
                # Enhance with LinkedIn and Growjo
                status_text.text("🔍 Fetching data from LinkedIn and Growjo...")
                for idx, company in enumerate(companies):
                    # Get company website
                    website_response = requests.get(
                        f"{BACKEND_URL}/api/find-website",
                        params={"company": company},
                        headers=headers
                    )
                    
                    if website_response.ok:
                        website_data = website_response.json()
                        normalized_df.loc[normalized_df['Company'] == company, 'Website'] = website_data.get('website', '')
                    
                    # Get company revenue
                    revenue_response = requests.get(
                        f"{BACKEND_URL}/api/get-revenue",
                        params={"company": company},
                        headers=headers
                    )
                    
                    if revenue_response.ok:
                        revenue_data = revenue_response.json()
                        normalized_df.loc[normalized_df['Company'] == company, 'Revenue'] = revenue_data.get('revenue', '')
                    
                    progress = (idx + 1) / len(companies)
                    progress_bar.progress(progress)
                
                st.success("✅ Data enhancement complete!")
                st.dataframe(normalized_df, use_container_width=True)
                
                # Download enhanced data
                csv = normalized_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Enhanced CSV",
                    csv,
                    file_name="enhanced_data.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"❌ Error during enhancement: {str(e)}")
                
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
