import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.credentials import Credentials
import json
import database
import warnings
import altair as alt
import pandas as pd

# --- CLOUD CONFIGURATION ---
warnings.filterwarnings("ignore")
st.set_page_config(page_title="OpsAgent Dashboard", page_icon="📊", layout="wide")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def get_sheet_client(user):
    """Safely extracts Google credentials from the adaptive user record."""
    token_str = ""
    # Self-Healing: Probe both possible DB columns to find the auth token safely
    if user[4] and "token" in str(user[4]):
        token_str = user[4]
    elif user[3] and "token" in str(user[3]):
        token_str = user[3]
    
    if not token_str:
        st.error("No Google Authorization token found. Please log in via the main web app again.")
        return None
        
    try:
        token_info = json.loads(token_str)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to parse Google Credentials: {e}")
        return None

# --- MAIN DASHBOARD LOGIC ---

# 1. Handle URL Authentication securely
if "email" in st.query_params:
    email_from_url = st.query_params["email"]
    
    # Use the adaptive database module we pushed earlier
    user = database.get_user_by_email(email_from_url)
    
    if not user:
        st.error(f"Could not find account for {email_from_url}. Please register on the main site.")
        st.stop()
        
    # 2. Authenticate Google Sheets
    client = get_sheet_client(user)
    if not client:
        st.stop()
        
    try:
        # Open the standard hackathon database sheet
        sheet = client.open("OpsAgent_DB_v1")
    except Exception as e:
        st.error(f"Could not open 'OpsAgent_DB_v1'. Ensure it exists in your Google Drive. Error: {e}")
        st.stop()

    # --- UI RENDER ENGINE ---
    st.title(f"📊 OpsAgent Live Analytics")
    st.markdown(f"**Connected Account:** `{email_from_url}`")
    st.divider()
    
    col1, col2 = st.columns(2)

    with col1:
            try:
                inv_ws = sheet.worksheet("Inventory")
                inv_data = inv_ws.get_all_records()
                if inv_data:
                    df_inv = pd.DataFrame(inv_data)
                    st.subheader("📦 Real-Time Inventory")
                    
                    # 1. Clean quantities for graphing
                    df_inv['Quantity'] = pd.to_numeric(df_inv.iloc[:, 1], errors='coerce').fillna(0)
                    
                    # 2. Map absolute thresholds to business categories
                    def get_stock_status(qty):
                        if qty < 10: return "Critical (<10)"
                        elif qty < 30: return "Low (10-29)"
                        elif qty < 60: return "Medium (30-59)"
                        elif qty < 120: return "Healthy (60-119)"
                        else: return "Surplus (120+)"
                    
                    df_inv['Stock Status'] = df_inv['Quantity'].apply(get_stock_status)
                    
                    # 3. Explicitly define the exact color mapping
                    status_colors = {
                        "Critical (<10)": "#FF4B4B",     # Red
                        "Low (10-29)": "#FFA500",        # Orange
                        "Medium (30-59)": "#FFD700",     # Yellow
                        "Healthy (60-119)": "#28A745",   # Green
                        "Surplus (120+)": "#007BFF"      # Blue
                    }
                    
                    # 4. Render the Plotly chart with the discrete map and ordered legend
                    fig_inv = px.bar(
                        df_inv, 
                        x=df_inv.columns[0], 
                        y='Quantity', 
                        color='Stock Status',
                        color_discrete_map=status_colors,
                        category_orders={
                            "Stock Status": [
                                "Critical (<10)", 
                                "Low (10-29)", 
                                "Medium (30-59)", 
                                "Healthy (60-119)", 
                                "Surplus (120+)"
                            ]
                        }
                    )
                    
                    # Clean up the axis titles for a more professional look
                    fig_inv.update_layout(xaxis_title="Item Name", yaxis_title="Quantity (Units)")
                    
                    st.plotly_chart(fig_inv, use_container_width=True)
                else:
                    st.info("Inventory table is empty. Send a WhatsApp message to restock!")
            except Exception:
                st.warning("Could not load Inventory data. Send a message to AI to generate it.")

    with col2:
        try:
            khata_ws = sheet.worksheet("Khata")
            khata_data = khata_ws.get_all_records()
            if khata_data:
                df_khata = pd.DataFrame(khata_data)
                st.subheader("💸 Cash Flow & Khata")
                st.dataframe(df_khata, use_container_width=True, height=350)
            else:
                st.info("Khata table is empty. Send a WhatsApp message to record a transaction!")
        except Exception:
            st.warning("Could not load Khata data. Send a message to AI to generate it.")
            
    st.divider()
    try:
        staff_ws = sheet.worksheet("Staff")
        staff_data = staff_ws.get_all_records()
        if staff_data:
            df_staff = pd.DataFrame(staff_data)
            st.subheader("👥 Staff Overview")
            st.dataframe(df_staff, use_container_width=True)
    except Exception:
        pass # Silently pass if Staff sheet isn't needed yet

else:
    st.warning("⚠️ No active session detected. Please log in via the main Render application.")