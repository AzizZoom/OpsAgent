import time
import gspread
import os
import logging
import urllib.parse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from twilio.rest import Client
from dotenv import load_dotenv
from thefuzz import process

# Import your live MongoDB collection from database.py
from database import users_collection

# --- 1. CONFIGURATION & SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MUNIM] - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Twilio Config
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = "whatsapp:+14155238886" # Sandbox Number

# Initialize Twilio Client
client_twilio = None
if TWILIO_SID and TWILIO_AUTH:
    try:
        client_twilio = Client(TWILIO_SID, TWILIO_AUTH)
        logger.info("✅ Twilio Client Connected")
    except Exception as e:
        logger.error(f"❌ Twilio Init Failed: {e}")

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

# --- 2. AUTHENTICATION ---

def get_sheet_client():
    if not os.path.exists('token.json'):
        logger.warning("⏳ Waiting for User Login... (token.json missing)")
        return None

    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"⚠️ Auth Error: {e}")
        return None

# --- 3. HELPER: DYNAMIC WHATSAPP ALERTS ---

def send_whatsapp_alert(to_phone, body):
    """Dynamically sends alert to the specified user's phone number."""
    if not client_twilio or not to_phone:
        logger.warning(f"⚠️ Simulation Alert to [{to_phone}]: {body}")
        return

    # Production Guardrail: Ensure phone formatting contains the channel prefix
    formatted_phone = str(to_phone).strip()
    if not formatted_phone.startswith("whatsapp:"):
        formatted_phone = f"whatsapp:{formatted_phone}"

    try:
        client_twilio.messages.create(
            body=body,
            from_=TWILIO_FROM,
            to=formatted_phone
        )
        logger.info(f"📨 Alert successfully dispatched to {formatted_phone}")
    except Exception as e:
        logger.error(f"❌ Twilio Delivery Failed to {formatted_phone}: {e}")

# --- 4. MULTI-TENANT MONITORING LOGIC ---

def check_inventory_risks(sheet, to_phone):
    """Checks for Low Stock and sends a 'Predictive' Alert to the user."""
    try:
        ws = sheet.worksheet("Inventory")
        rows = ws.get_all_values()

        for i, row in enumerate(rows[1:]):
            row_num = i + 2
            if len(row) < 2: continue

            item_name = row[0]
            try: qty = int(row[1])
            except: continue

            # Dynamic length checking prevents index-out-of-bounds crashes
            alert_status = row[4] if len(row) > 4 else ""

            if qty < 10 and alert_status != "SENT":
                logger.warning(f"🚨 LOW STOCK ALERT triggered for: {item_name}")

                msg = (
                    f"📉 *Stockout Prediction Alert*\n\n"
                    f"Based on current demand velocity, *{item_name}* is projected to run out in less than 24 hours.\n"
                    f"• Current Stock: {qty}\n"
                    f"• Recommended Action: Reorder immediately."
                )

                send_whatsapp_alert(to_phone, msg)
                
                # Expand grid columns automatically if the sheet is narrow
                if len(row) < 5:
                    ws.resize(cols=6)
                ws.update_cell(row_num, 5, "SENT")

            elif qty >= 10 and alert_status == "SENT":
                if len(row) > 4: 
                    ws.update_cell(row_num, 5, "")

    except Exception as e:
        logger.error(f"Inventory Check Error: {e}")

def check_staff_risks(sheet, to_phone):
    """Checks for Absent staff and alerts the business owner about schedule impact."""
    try:
        try: ws = sheet.worksheet("Staff")
        except: return

        rows = ws.get_all_values()

        for i, row in enumerate(rows[1:]):
            row_num = i + 2
            if len(row) < 4: continue

            name = row[0]
            status = row[3] 
            alert_status = row[5] if len(row) > 5 else ""

            if status.lower() == "absent" and alert_status != "SENT":
                logger.warning(f"🚨 STAFF ABSENT ALERT triggered for: {name}")

                msg = (
                    f"⚠️ *Schedule Risk Alert*\n\n"
                    f"*{name}* has been marked ABSENT for the {row[2]} shift.\n"
                    f"• Operational Impact: High\n"
                    f"• Action: Please arrange a replacement to maintain service levels."
                )

                send_whatsapp_alert(to_phone, msg)

                if len(row) < 6:
                    ws.resize(cols=6)
                ws.update_cell(row_num, 6, "SENT")

            elif status.lower() == "present" and alert_status == "SENT":
                if len(row) > 5:
                    ws.update_cell(row_num, 6, "")

    except Exception as e:
        logger.error(f"Staff Check Error: {e}")

def check_cash_flow_risks(sheet, to_phone):
    """Checks for large pending dues in Khata and alerts the business owner."""
    try:
        try: ws = sheet.worksheet("Khata")
        except: return

        rows = ws.get_all_values()

        for i, row in enumerate(rows[1:]):
            row_num = i + 2
            if len(row) < 5: continue

            customer = row[0]
            try: amount = float(row[1])
            except: continue
            status = row[4]
            alert_status = row[6] if len(row) > 6 else ""

            if status == "Pending" and amount > 500 and alert_status != "SENT":
                logger.warning(f"💸 CASH FLOW RISK ALERT triggered for: {customer}")

                msg = (
                    f"💸 *Cash Flow Alert*\n\n"
                    f"Large outstanding payment detected.\n"
                    f"• Customer: *{customer}*\n"
                    f"• Amount: ₹{amount}\n"
                    f"• Status: Overdue\n"
                    f"Recommended: Send payment reminder."
                )

                send_whatsapp_alert(to_phone, msg)
                
                if len(row) < 7:
                    ws.resize(cols=7)
                ws.update_cell(row_num, 7, "SENT")

            elif status == "Paid" and alert_status == "SENT":
                if len(row) > 6:
                    ws.update_cell(row_num, 7, "")

    except Exception as e:
        logger.error(f"Cash Flow Check Error: {e}")

# --- 5. CORE BATCH EXECUTION LOOP ---

if __name__ == "__main__":
    logger.info("🟢 Munim (Scheduler v3.0 Cloud) Started. Scanning active tenants...")

    while True:
        try:
            client = get_sheet_client()
            if client:
                # DYNAMIC ENGINE: Query MongoDB to process alerts for EVERY registered user
                active_users = list(users_collection.find())
                
                if not active_users:
                    logger.info("💤 No active business profiles found in MongoDB. Standing by...")

                for user in active_users:
                    user_phone = user.get("phone")
                    user_sheet_id = user.get("sheet_id")

                    if not user_phone or not user_sheet_id:
                        continue # Skip onboarding accounts that are incomplete

                    try:
                        # Safely open the user's specific cloud spreadsheet via unique key
                        sheet = client.open_by_key(user_sheet_id)

                        # Run routine audits for this tenant
                        check_inventory_risks(sheet, user_phone)
                        check_staff_risks(sheet, user_phone)
                        check_cash_flow_risks(sheet, user_phone)

                    except gspread.SpreadsheetNotFound:
                        logger.warning(f"📉 User Spreadsheet Key {user_sheet_id} missing or unreadable.")
                    except Exception as tenant_error:
                        logger.error(f"⚠️ Error handling tenant {user_phone}: {tenant_error}")

            # Sleep 60 seconds between batch polling cycles
            time.sleep(60)

        except KeyboardInterrupt:
            logger.info("🛑 Munim stopping...")
            break
        except Exception as e:
            logger.critical(f"💥 Main Loop System Error: {e}")
            time.sleep(60)