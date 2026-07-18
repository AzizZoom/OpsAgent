# 📊 OpsAgent

**Headless Cloud ERP & Live Analytics Platform**

OpsAgent is a decoupled, microservice-based Headless ERP system that bridges conversational natural language interfaces with automated small-and-medium business (SMB) operations tracking. By integrating conversational messaging with cloud ledger engines, OpsAgent completely eliminates manual data-entry overhead—allowing business owners to restock inventory, log transactions, track expenses, and view real-time operations metrics entirely through WhatsApp and an automated business dashboard.

---

## 🏗️ System Architecture & Data Flow

```
📱 WhatsApp (User Input)
       │
       ▼
💬 Twilio Gateway (Webhook forwarding via HTTP POST)
       │
       ▼
🚀 FastAPI Backend (Render Cloud Service Container)
       ├── 🧠 Google Gemini AI Engine (Processes text & image receipts into JSON Arrays)
       ├── 💾 MongoDB Atlas (Authenticates profile mapping, active session keys)
       └── 📄 Google Sheets API Ledger (Appends entries via authenticated gspread engine)
               │
               ▼
📊 Streamlit Analytics Frontend (Live Visual Dashboard Loop with Auto-Refresh)
```

---

## ✨ Key Features

| Feature | Description |
| --- | --- |
| **Natural Language Command Processing** | Ingests unstructured conversational parameters (e.g., *"Bought 50 packets of chips for Rs. 1000 and sold 10 cokes for Rs. 400"*) and utilizes Google Gemini to split, clean, and map transactions simultaneously. |
| **Multimodal Receipt Downloads** | Features an authenticated binary image fetch loop to download invoice media directly from Twilio's payload attachments for OCR parsing and automated price totals verification. |
| **Live Real-Time Dashboards** | A lightweight, microservice-decoupled Streamlit UI tracking financial metrics, product volumes, ledger records, and customer accounts using reactive Plotly data visual components. |
| **Persistent OAuth2 Token Syncing** | Conquers container storage constraints by mapping temporary Google access tokens straight into cloud document clusters for bulletproof automated background transactions. |
| **TwiML Gateway Compliance** | Serves runtime requests using strict XML markup response media-types to fulfill global protocol rules across Twilio systems. |

---

## 🛠️ Tech Stack

| Layer | Tools & Technologies |
| --- | --- |
| **Backend API Core** | Python, FastAPI, Uvicorn, Requests |
| **Artificial Intelligence** | Google Generative AI (Gemini 2.5 Flash / NLP Engine), Pillow (PIL) |
| **Communications Gateway** | Twilio Messaging API Webhooks, TwiML XML Schema |
| **Storage & Data Management** | MongoDB Atlas Cloud Cluster (PyMongo), Google Sheets API (GSpread) |
| **Data Visualization UI** | Streamlit, Plotly Express, Streamlit Autorefresh |
| **Cloud Deployment Infrastructure** | Render (Web Services Hosting), Streamlit Community Cloud |

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory of your project (or load these directly inside your cloud management configuration interfaces on Render):

```env
# 🔑 Core Database & State Configurations
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/OpsAgentDB

# 🧠 Generative AI Credentials
GEMINI_API_KEY=AIzaSy...YourGeminiKeyHere

# 💬 Twilio Gateway Authentications
TWILIO_SID=AC...YourTwilioAccountSid
TWILIO_AUTH=your_twilio_auth_token

# 🔒 Google Cloud Platform API Access Keys
GOOGLE_CLIENT_ID=your_gcp_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_gcp_client_secret
```

> **Note:** Never commit your `.env` file or real credentials to version control.

---

## 🚀 Quick Setup & Installation

Follow these steps to configure your local execution container workspace:

### 1. Clone the Workspace

```bash
git clone https://github.com/AzizZoom/OpsAgent.git
cd OpsAgent
```

### 2. Configure Virtual Environment & Dependencies

```bash
python -m venv venv
```

**Windows PowerShell activation:**

```powershell
.\venv\Scripts\Activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

### 3. Initialize Server Systems

OpsAgent uses a decoupled operational loop. For standard local sandbox development testing, execute both engines simultaneously:

**Fire up the Backend Microservice Engine:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Launch the Interactive Live Visual Frontend Dashboard:**

```bash
streamlit run dashboard.py
```

---

## 🛰️ Core API Endpoints

### `POST /whatsapp`

The target routing engine connected to Twilio's incoming messaging webhook.

| Property | Value |
| --- | --- |
| **Payload Format** | `application/x-www-form-urlencoded` |
| **Response Format** | `application/xml` (Valid structural TwiML Root tags) |

**Execution logic flow:**

```
Checks sender origin → Pulls unique cloud token map profiles → Transmits text to semantic parser → Appends transaction datasets cleanly across targeted spreadsheet tabs
```

### `GET /login`

Initiates the centralized secure state tracking verification challenge process via standard Google Cloud Platform routing prompts.

### `GET /callback`

The standard cloud endpoint handling incoming auth responses, parsing callback authorization tokens, and capturing state properties to map variables safely into MongoDB document records.