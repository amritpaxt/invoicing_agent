from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import os
import json
from orchestrator import resolve_employee_and_payroll
from validate import validate_invoice
from typing import Optional
from invoice_store import create_invoice, list_invoices, get_invoice, approve_invoice, dispatch_all_approved
from chat_assistant import ask_assistant
from extract_batch import extract_client_list, extract_reimbursements
from orchestrator_main import process_any_input
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

class MatchPayload(BaseModel):
    caseId: str
    employeeId: str


class ReviewPayload(BaseModel):
    caseId: str
    field: str
    value: str


@app.get("/bootstrap")
async def bootstrap():
    invoices = list_invoices()
    cases = [_invoice_to_frontend_case(inv) for inv in invoices[-8:]]
    return {
        "cases": list(reversed(cases)) if cases else _demo_cases(),
        "invoices": [_invoice_to_frontend_invoice(inv) for inv in invoices[-8:]] or _demo_invoices(),
        "dispatchQueue": [
            {
                "client": inv.get("client_name") or "Client pending",
                "rule": "Held until review clears",
                "amount": _format_amount(inv.get("amount")),
                "status": "Needs review",
            }
            for inv in invoices
            if inv.get("status") == "needs_review"
        ],
        "clientMaster": [
            {"code": "CL001", "name": "TechCorp Dubai", "currency": "AED", "profile": "Standard", "fields": "Full breakdown"},
            {"code": "CL004", "name": "FinanceCo Dubai", "currency": "AED", "profile": "Standard + ambiguity review", "fields": "Full breakdown"},
            {"code": "CL005", "name": "HealthCo Dubai", "currency": "AED", "profile": "Reimbursement validation", "fields": "Full breakdown"},
            {"code": "CL007", "name": "LogisticsCo Dubai", "currency": "AED", "profile": "Standard", "fields": "Emp ID + total"},
        ],
        "validationRules": [
            {"rule": "Working days must be 20-26 for June 2026", "appliesTo": "All clients", "onFail": "Flag", "active": True},
            {"rule": "Employee must resolve to exactly one client roster record", "appliesTo": "All clients", "onFail": "Hold", "active": True},
            {"rule": "Overtime cannot exceed 50 hours/month", "appliesTo": "All clients", "onFail": "Hold", "active": True},
            {"rule": "Handwritten confidence below 85% routes to HITL", "appliesTo": "Portal images/PDF", "onFail": "Flag", "active": True},
            {"rule": "Reimbursements require reason and allowed type", "appliesTo": "All clients", "onFail": "Flag", "active": True},
        ],
        "dispatchRules": [
            {"code": "CL001", "client": "TechCorp Dubai", "order": "Ascending by net pay", "channel": "Email"},
            {"code": "CL004", "client": "FinanceCo Dubai", "order": "Descending by net pay", "channel": "Portal"},
            {"code": "CL005", "client": "HealthCo Dubai", "order": "As received", "channel": "Email"},
        ],
        "loggedInClientCode": "CL001",
        "loggedInClientName": "TechCorp Dubai",
    }


@app.get("/bootstrap.js")
async def bootstrap_js(callback: str = "__tiaBootstrap"):
    payload = await bootstrap()
    safe_callback = "".join(ch for ch in callback if ch.isalnum() or ch in "._$") or "__tiaBootstrap"
    return Response(
        content=f"{safe_callback}({json.dumps(payload)});",
        media_type="application/javascript",
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    path = await _save_upload(file)
    result, trace = process_any_input(file_path=path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    invoice = create_invoice(result["match_result"], result["validation"])
    result["invoice"] = invoice
    result["agent_trace"] = trace
    result["filename"] = file.filename
    result["path"] = path
    return result

@app.post("/test-match")
async def test_match(
    emp_id: Optional[str] = None,
    name: Optional[str] = None,
    client_name: Optional[str] = None
):
    extracted = {
        "emp_id": emp_id,
        "employee_name": name,
        "client_name": client_name
    }
    trace = []
    match_result, trace = resolve_employee_and_payroll(extracted, trace)
    validation = validate_invoice(match_result, extracted)

    return {
        "agent_trace": trace,
        "match_result": match_result,
        "validation": validation
    }
from typing import Optional

@app.post("/process")
async def process_input(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = None
):
    file_path = None
    if file:
        file_path = await _save_upload(file)

    result, trace = process_any_input(file_path=file_path, raw_text=raw_text)
    
    invoice = create_invoice(result["match_result"], result["validation"])
    result["invoice"] = invoice
    result["agent_trace"] = trace
    return result

@app.get("/invoices")
async def get_invoices():
    return {"invoices": list_invoices()}

@app.get("/invoices/{invoice_id}")
async def get_invoice_detail(invoice_id: str):
    invoice = get_invoice(invoice_id)
    if not invoice:
        return {"error": "not found"}
    return invoice

@app.post("/invoices/{invoice_id}/approve")
async def approve(invoice_id: str):
    result = approve_invoice(invoice_id)
    if not result:
        return {"error": "invoice not found"}
    return result

@app.post("/dispatch")
async def dispatch():
    dispatched = dispatch_all_approved()
    return {"dispatched_count": len(dispatched), "invoices": dispatched}

@app.post("/chat")
async def chat(request: Request, question: Optional[str] = None):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    asked = question or payload.get("question") or ""
    answer = ask_assistant(asked) if asked else "Ask me about a case, invoice, exception, or validation rule."
    return {"answer": answer}

CLIENTS_CONFIG = {}

@app.post("/clients/{client_code}/config")
async def set_client_config(client_code: str, currency: str = "AED", dispatch_order: str = "amount_asc"):
    CLIENTS_CONFIG[client_code] = {"currency": currency, "dispatch_order": dispatch_order}
    return CLIENTS_CONFIG[client_code]

@app.get("/clients/{client_code}/config")
async def get_client_config(client_code: str):
    return CLIENTS_CONFIG.get(client_code, {"currency": "AED", "dispatch_order": "amount_asc"})

@app.get("/analytics")
async def get_analytics():
    invoices = list_invoices()
    total = len(invoices)
    approved = len([i for i in invoices if i["status"] == "approved"])
    needs_review = len([i for i in invoices if i["status"] == "needs_review"])
    dispatched = len([i for i in invoices if i.get("dispatched")])
    total_amount = sum(i["amount"] for i in invoices if i.get("amount"))

    return {
        "total_invoices": total,
        "approved": approved,
        "needs_review": needs_review,
        "dispatched": dispatched,
        "touchless_rate": round((approved / total * 100), 1) if total else 0,
        "total_amount": total_amount
    }
from query_store import raise_query, list_queries, respond_to_query
from invoice_store import finalize_invoice, mark_sent_to_client

@app.post("/queries")
async def create_query(invoice_id: str, message: str):
    return raise_query(invoice_id, message)

@app.get("/queries")
async def get_queries():
    return {"queries": list_queries()}

@app.post("/queries/{query_id}/respond")
async def answer_query(query_id: str, response: str):
    result = respond_to_query(query_id, response)
    if not result:
        return {"error": "query not found"}
    return result

@app.post("/invoices/{invoice_id}/finalize")
async def finalize(invoice_id: str, decision: str):
    result = finalize_invoice(invoice_id, decision)
    if not result:
        return {"error": "not found"}
    return result

@app.post("/invoices/{invoice_id}/notify-client")
async def notify_client(invoice_id: str):
    result = mark_sent_to_client(invoice_id)
    if not result:
        return {"error": "invoice not dispatched yet"}
    return result
@app.post("/invoices/{invoice_id}/approve")
async def approve(invoice_id: str):
    if not invoice_id or len(invoice_id) < 4:
        raise HTTPException(status_code=400, detail="Invalid invoice ID")
    result = approve_invoice(invoice_id)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return result
@app.post("/process-batch-list")
async def process_batch_list(raw_text: str):
    extracted_list = extract_client_list(raw_text)
    results = []
    for item in extracted_list:
        trace = [f"Processing: {item['employee_name']}"]
        match_result, trace = resolve_employee_and_payroll(item, trace)
        validation = validate_invoice(match_result, item)
        invoice = create_invoice(match_result, validation)
        results.append({"extracted": item, "match_result": match_result, "validation": validation, "invoice": invoice, "agent_trace": trace})
    return {"processed_count": len(results), "results": results}

@app.post("/process-reimbursement")
async def process_reimbursement(raw_text: str):
    extracted = extract_reimbursements(raw_text)
    trace = [f"Extracted reimbursement data for {extracted['emp_id']}"]
    match_result, trace = resolve_employee_and_payroll(extracted, trace)

    validation = validate_invoice(match_result, extracted)

    invoice = create_invoice(match_result, validation)
    return {"extracted": extracted, "match_result": match_result, "validation": validation, "invoice": invoice}


@app.post("/actions/confirm-match")
async def confirm_match(payload: MatchPayload):
    return {
        "status": "queued",
        "message": f"{payload.caseId}: {payload.employeeId} confirmed. Invoice regeneration has been queued.",
    }


@app.post("/actions/review-field")
async def review_field(payload: ReviewPayload):
    return {
        "status": "queued",
        "message": f"{payload.caseId}: {payload.field} set to {payload.value}. Validation will rerun.",
    }


@app.post("/upload-timesheet")
async def upload_timesheet_compat():
    return {
        "status": "ready",
        "message": "Use the capture modal to upload Excel/PDF/image files or paste messy email text.",
    }


async def _save_upload(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing upload filename")
    safe_name = os.path.basename(file.filename)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    os.makedirs("uploads", exist_ok=True)
    path = os.path.join("uploads", safe_name)
    with open(path, "wb") as f:
        f.write(contents)
    return path


def _format_amount(amount):
    if amount is None:
        return "Pending"
    return f"AED {float(amount):,.2f}"


def _invoice_to_frontend_case(inv):
    status = "clear" if inv.get("status") == "approved" else "review"
    return {
        "id": f"INV-{inv['id']}",
        "name": inv.get("employee_name") or "Unmatched employee",
        "sub": "Processed by integrated backend",
        "client": inv.get("client_name") or "Client pending",
        "clientCode": "",
        "amount": _format_amount(inv.get("amount")),
        "status": status,
        "statusLabel": "Auto-approved" if status == "clear" else "Review needed",
        "channel": "Backend invoice store",
        "empId": None,
        "fields": [
            {"k": "Employee", "v": inv.get("employee_name") or "Unknown", "c": 90 if inv.get("employee_name") else 40},
            {"k": "Client", "v": inv.get("client_name") or "Pending", "c": 90 if inv.get("client_name") else 40},
            {"k": "Net Pay", "v": _format_amount(inv.get("amount")), "c": 99 if inv.get("amount") else 0},
            {"k": "Status", "v": inv.get("status"), "c": 99},
        ],
        "flagType": None if status == "clear" else "review",
        "note": ", ".join(inv.get("issues", [])),
        "timeline": [
            {"t": "now", "label": "Loaded from backend invoice store", "live": False},
            {"t": "now", "label": f"Status: {inv.get('status')}", "live": status != "clear"},
        ],
    }


def _invoice_to_frontend_invoice(inv):
    return {
        "num": inv["id"],
        "clientCode": "",
        "client": inv.get("client_name") or "Client pending",
        "format": "TIA full breakdown",
        "amount": _format_amount(inv.get("amount")),
        "status": "sent" if inv.get("dispatched") else ("pending" if inv.get("status") != "approved" else "generated"),
        "sent": "Sent" if inv.get("dispatched") else "Awaiting dispatch",
    }


def _demo_cases():
    return [
        {
            "id": "DEMO-01",
            "name": "Carlos Smith",
            "sub": "Excel happy path - upload case7_excel_complete.xlsx",
            "client": "TechCorp Dubai",
            "clientCode": "CL001",
            "amount": "AED 12,007.69",
            "status": "clear",
            "statusLabel": "Auto-approved",
            "channel": "Portal upload (.xlsx)",
            "empId": "EMP10001",
            "fields": [
                {"k": "Emp ID", "v": "EMP10001", "c": 99},
                {"k": "Full Name", "v": "Carlos Smith", "c": 99},
                {"k": "Working Days", "v": "24", "c": 99},
                {"k": "Net Pay", "v": "AED 12,007.69", "c": 99},
            ],
            "flagType": None,
            "timeline": [{"t": "demo", "label": "Use Capture timesheet to process live files", "live": False}],
        },
        {
            "id": "DEMO-02",
            "name": "Ravi Menon",
            "sub": "Handwritten/PDF fallback - low confidence routes to HITL",
            "client": "FinanceCo Dubai",
            "clientCode": "CL004",
            "amount": "Pending",
            "status": "review",
            "statusLabel": "Field review needed",
            "channel": "Image/PDF upload",
            "empId": None,
            "fields": [
                {"k": "Full Name", "v": "Ravi Menon", "c": 68, "flagged": True},
                {"k": "Client", "v": "FinanceCo CL004", "c": 86},
                {"k": "Days", "v": "21", "c": 64, "flagged": True},
            ],
            "flagType": "review",
            "note": "Handwritten fields are intentionally low confidence and require human review.",
            "timeline": [{"t": "demo", "label": "Upload an image/PDF to test capture", "live": True}],
        },
    ]


def _demo_invoices():
    return [
        {"num": "DEMO-INV-01", "clientCode": "CL001", "client": "TechCorp Dubai", "format": "TIA full breakdown", "amount": "AED 12,007.69", "status": "sent", "sent": "Demo"},
    ]
