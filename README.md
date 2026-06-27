# TIA - Touchless Invoice Agent

A smart invoice processing system that automates timesheet extraction, validation, and invoice generation with AI-powered field extraction and intelligent matching.

## 📋 Project Overview

**TIA** (Touchless Invoice Agent) is an enterprise solution for automating invoice processing workflows. It intelligently extracts employee timesheets from multiple input formats (PDF, Email, Images), performs validation against configurable business rules, handles identity resolution, and generates client-specific invoices with minimal human intervention.

### Key Features

- **📥 Multi-Channel Ingestion**: Accept timesheets via PDF uploads, emails, images, and portal submissions
- **🔍 Intelligent Extraction**: Vision OCR and structured data extraction with confidence scores
- **⚙️ Flexible Validation**: Per-client business rules (OT caps, working day ranges, signature verification)
- **🎯 Smart Matching**: Resolve ambiguous employee identities using client context and confidence scoring
- **📊 Dashboard**: Real-time visibility into processing queue, KPIs, and exception handling
- **👥 Role-Based Access**: Separate views for Finance/FinOps and Client stakeholders
- **💬 Context-Aware Chat**: Ask TIA questions about cases, rules, and invoice status
- **📤 Dispatch Rules**: Per-client invoice delivery ordering and channel configuration

---

## 🏗️ Project Structure

```
invoicing_agent/
├── backend.py           # FastAPI backend with all API endpoints
├── TIA.html             # Standalone frontend (no build required)
├── run_server.py        # Server startup script
├── README.md            # This file
└── __pycache__/         # Python cache (auto-generated)
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      TIA.html (Frontend)                 │
│  • HTML5 + CSS3 + Vanilla JavaScript                     │
│  • Role switching (Finance ↔ Client View)                │
│  • Workbench: Inbox, Invoices, Dispatch, Config         │
│  • Chat interface with preset questions                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON
                         │ (fetch, CORS enabled)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   backend.py (FastAPI)                   │
│  • Serves TIA.html at root (/)                           │
│  • /api/bootstrap - Load initial data                    │
│  • /api/chat - Context-aware chat responses             │
│  • /api/actions/* - Match confirmation, field review    │
│  • /api/upload-timesheet - Timesheet upload handler     │
│  • Database: In-memory (Python dicts)                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **pip** (Python package manager)
- **Windows/Mac/Linux** with port 5000 available

### Installation

1. **Clone/Navigate to project**:
   ```bash
   cd c:\Users\KHUSHI\Downloads\MY_PROGRAMS\HackArena_Final\invoicing_agent
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

3. **Start the server**:
   ```bash
   python run_server.py
   ```

4. **Open in browser**:
   ```
   http://localhost:5000
   ```

### Expected Output

```
🚀 Starting TIA Backend Server...
📝 Frontend: TIA.html
📡 API: http://localhost:5000
📚 Docs: http://localhost:5000/docs

Press CTRL+C to stop the server

INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 📡 API Endpoints

### GET `/`
Returns the TIA.html frontend.

### GET `/api/bootstrap`
**Returns**: Initial data load (cases, invoices, clients, rules)
```json
{
  "cases": [...],
  "invoices": [...],
  "dispatchQueue": [...],
  "clientMaster": [...],
  "validationRules": [...],
  "dispatchRules": [...],
  "kpis": {
    "touchlessRate": "81%",
    "touchlessCount": "34 of 42",
    "avgTurnaround": "6 min",
    "needsReview": 3,
    "extractionAccuracy": "99.2%"
  }
}
```

### POST `/api/chat`
**Request**:
```json
{
  "question": "Why is TS-0143 flagged?",
  "role": "finance",
  "clientCode": null
}
```
**Response**:
```json
{
  "answer": "TS-0143 is held because the email gave a name but no Emp ID. 'Ravi Menon' matches 3 employees..."
}
```

### POST `/api/actions/confirm-match`
**Request**:
```json
{
  "caseId": "TS-0143",
  "employeeId": "EMP10136"
}
```
**Response**:
```json
{
  "status": "ok",
  "message": "Confirmed EMP10136 for TS-0143. Invoice regeneration has been queued."
}
```

### POST `/api/actions/review-field`
**Request**:
```json
{
  "caseId": "TS-0144",
  "field": "OT Hours",
  "value": "8"
}
```
**Response**:
```json
{
  "status": "ok",
  "message": "TS-0144 OT Hours set to 8. Validation and invoice regeneration have been queued."
}
```

### POST `/api/upload-timesheet`
**Response**:
```json
{
  "status": "ok",
  "message": "demo-timesheet.pdf received. TIA extraction and validation are queued."
}
```

---

## 🎮 Using the Frontend

### Dashboard Views

#### 📥 Inbox (Default)
- **Processing Queue**: All timesheets from receipt to dispatch
- **KPI Row**: Touchless rate, turnaround time, accuracy metrics
- **Case List**: Interactive rows with expandable details
  - Extract fields with confidence scores
  - Identity match candidates (if needed)
  - Field review actions (if needed)
  - Activity timeline

#### 🧾 Invoices
- **Generated Invoices**: Formatted per client requirements
- **Status**: Sent, Pending (awaiting field review or identity match)
- **Metadata**: Amount, sent date, format (full breakdown or summary)

#### 🚚 Dispatch
- **Dispatch Queue**: Invoices waiting to send (FinOps only)
- **Dispatch Rules**: Client-specific ordering (ascending pay, alphabetical, etc.)
- **Status**: Held (reason), Ready, Sent

#### 🏢 Clients (FinOps Only)
- **Master Data**: Client profiles, currencies, validation profiles
- **Format**: What invoice format each client expects
- **Profile**: Validation rules specific to the client

#### ⚙️ Validation Rules (FinOps Only)
- **Active Rules**: Working day range, OT cap, signature requirements
- **Scope**: Which clients each rule applies to
- **Action**: Flag or Hold on failure

#### 📤 Dispatch Rules (FinOps Only)
- **Ordering**: How invoices are sorted before delivery
- **Channel**: Email or Client portal
- **Per-client**: Different rules for different clients

#### 📊 Analytics
- **KPI Dashboard**: Touchless rate, turnaround, accuracy, exception count
- **Exception Breakdown**: By type (identity match, field confidence, rule violation)
- **Trends**: Month-to-date performance

#### 💬 Ask TIA
- **Context-Aware Chat**: Ask about the current timesheet, client, or invoice
- **Preset Questions**: "Why is TS-0143 flagged?", "Which clients have pending invoices?"
- **Natural Language**: Understands case IDs, employee names, client names, rule types

### Role Switching

**FinOps / Finance** (Default)
- Full access to all views
- Can manage client configuration
- Can set validation and dispatch rules
- Can review and confirm matches
- Can upload timesheets

**Client View**
- See only their own timesheets and invoices
- No access to configuration or other clients' data
- Cannot upload or manage rules
- Read-only dashboard and analytics

---

## 🔧 Configuration

### Client Master Data
Located in `backend.py`, defines per-client settings:
```python
{
  "code": "CL001",
  "name": "Emirates Steel Industries LLC",
  "currency": "AED",
  "profile": "Standard + OT cap 40h/wk",
  "fields": "Full breakdown"
}
```

### Validation Rules
Located in `backend.py`, defines business logic:
```python
{
  "rule": "OT hours over 40/week requires approval note",
  "appliesTo": "CL001, CL004",
  "onFail": "Flag",
  "active": True
}
```

### Dispatch Rules
Located in `backend.py`, defines invoice delivery:
```python
{
  "code": "CL001",
  "client": "Emirates Steel Industries LLC",
  "order": "Ascending by net pay",
  "channel": "Email"
}
```

---

## 📊 Sample Data

The system includes sample data with 5 test cases:

| Case | Employee | Status | Reason |
|------|----------|--------|--------|
| TS-0142 | Carlos Smith | Auto-approved ✅ | Exact ID match, all fields high-confidence |
| TS-0143 | Ravi Menon | Match review ⚠️ | Name matches 3 employees; client hints at one |
| TS-0144 | Fatima Khan | Field review ⚠️ | Handwritten OT field is ambiguous (54% confidence) |
| TS-0145 | Meera Al Rashid | Dispatched ✅ | Reimbursements and leave processed |
| TS-0146 | Aisha Al Zaabi | Auto-approved ✅ | Employee self-reported via email |

---

## 🔐 Security & Compliance

- **Role-Based Access Control**: Client data is filtered at both backend and frontend
- **CORS Enabled**: Allows cross-origin requests (production: configure origins)
- **Data Isolation**: Clients only see their own data, never leaked to DOM
- **Confidence Scoring**: All extracted fields have confidence indicators
- **Audit Trail**: Activity timeline on each case shows all processing steps

---

## 🛠️ Development & Troubleshooting

### Port Already in Use
If port 5000 is busy:
```bash
# Edit run_server.py, change:
# port=5000 → port=5001
# Then update browser: http://localhost:5001
```

### Backend Not Responding
Check if the server is running:
```bash
# In new terminal, check if port 5000 is listening
netstat -ano | find ":5000"
```

### CORS Issues
If browser shows CORS errors, verify `CORSMiddleware` in `backend.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific domains: ["http://localhost:5000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Shows "Using local fallback data"
The backend is not responding to API calls. Check:
1. Backend server is running (`http://localhost:5000` should load HTML)
2. No browser console errors (F12 → Console tab)
3. Network tab shows failed requests (F12 → Network tab)

---

## 🚀 Next Steps / Production Deployment

### TODO
- [ ] Connect to real database (PostgreSQL, MongoDB) instead of in-memory dicts
- [ ] Implement file upload and document OCR processing
- [ ] Add user authentication and audit logging
- [ ] Create admin panel for rule management
- [ ] Set up CI/CD pipeline
- [ ] Add email/portal delivery channels
- [ ] Implement batch processing for large volumes
- [ ] Add performance monitoring and alerting

### Deployment Options
- **Heroku**: `git push heroku main` with Procfile
- **AWS Lambda**: Serverless FastAPI with AWS API Gateway
- **Docker**: Container deployment with Docker Compose
- **Kubernetes**: Helm charts for scaling

---

## 📞 Support

For questions or issues:
1. Check the console (F12 → Console) for error messages
2. Review the API Docs: `http://localhost:5000/docs`
3. Check backend logs in terminal
4. Review this README for common issues

---

## 📄 License

Internal project for Hacker Arena 2.0

---

## 🎯 Key Metrics

**Current Status** (Demo Data):
- **Touchless Rate**: 81% (target: 80%+)
- **Avg Turnaround**: 6 minutes (target: minutes, not days)
- **Extraction Accuracy**: 99.2% (target: 99%+)
- **Cases Pending Review**: 3 (1 match, 2 field review)
- **Invoices Sent**: 42 in June

---

**Last Updated**: 2026-06-29  
**Version**: 1.0.0 (Demo)
