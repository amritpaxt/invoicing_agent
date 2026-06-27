from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "TIA.html"

app = FastAPI(title="TIA - Touchless Invoice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CASES: list[dict[str, Any]] = [
    {
        "id": "TS-0142",
        "name": "Ahmed Nasser",
        "sub": "Case 1 - PDF timesheet, exact employee ID",
        "client": "Emirates Steel Industries LLC",
        "clientCode": "CL001",
        "amount": "AED 9,834.13",
        "status": "clear",
        "statusLabel": "Auto-approved",
        "channel": "PDF upload",
        "empId": "EMP10012",
        "fields": [
            {"k": "Emp ID", "v": "EMP10012", "c": 99},
            {"k": "Full Name", "v": "Ahmed Nasser", "c": 98},
            {"k": "Working Days", "v": "22", "c": 96},
            {"k": "OT Hours", "v": "14", "c": 94},
            {"k": "Net Pay", "v": "AED 9,834.13", "c": 99},
        ],
        "flagType": None,
        "timeline": [
            {"t": "09:08", "label": "Received via PDF upload", "live": False},
            {"t": "09:09", "label": "Matched EMP10012 - exact ID match", "live": False},
            {"t": "09:10", "label": "Validated - passed", "live": False},
            {"t": "09:15", "label": "Invoice generated and dispatched", "live": False},
        ],
    },
    {
        "id": "TS-0143",
        "name": "Ravi Menon",
        "sub": "Case 5 - Name collision, client hint",
        "client": "Dubai Cargo Village LLC",
        "clientCode": "CL007",
        "amount": "AED 7,120.00",
        "status": "match",
        "statusLabel": "Match review needed",
        "channel": "Email (unstructured)",
        "empId": "",
        "fields": [
            {"k": "Full Name", "v": "Ravi Menon", "c": 96},
            {"k": "Client (stated)", "v": "CL007 - Dubai Cargo Village", "c": 91},
            {"k": "Working Days", "v": "22", "c": 94},
            {"k": "Emp ID", "v": "- not provided -", "c": 0, "flagged": True},
        ],
        "flagType": "match",
        "candidates": [
            {"name": "Ravi Menon", "id": "EMP10070", "client": "CL004 - Sharjah Ports Authority"},
            {"name": "Ravi Menon", "id": "EMP10136", "client": "CL007 - Dubai Cargo Village"},
            {"name": "Ravi Menon", "id": "EMP10157", "client": "CL008 - Al Futtaim Group"},
        ],
        "timeline": [
            {"t": "09:31", "label": "Received via Email", "live": False},
            {"t": "09:32", "label": "3 employees named Ravi Menon found", "live": False},
            {"t": "09:32", "label": "Stated client narrows to EMP10136 - confidence 91%", "live": True},
        ],
    },
    {
        "id": "TS-0144",
        "name": "Fatima Khan",
        "sub": "Case 4 - Handwritten attendance sheet",
        "client": "Al Ghurair Centre LLC",
        "clientCode": "CL009",
        "amount": "AED 6,480.00",
        "status": "review",
        "statusLabel": "Field review needed",
        "channel": "Image (handwritten, scanned)",
        "empId": "EMP10083",
        "fields": [
            {"k": "Emp ID", "v": "EMP10083", "c": 88},
            {"k": "Full Name", "v": "Fatima Khan", "c": 95},
            {"k": "Working Days", "v": "23", "c": 92},
            {"k": "OT Hours", "v": "6 or 8?", "c": 54, "flagged": True},
            {"k": "Signature", "v": "Present, unverified", "c": 70},
        ],
        "flagType": "review",
        "note": "Handwritten OT figure is ambiguous between 6 and 8. Only this one field is held for review.",
        "timeline": [
            {"t": "08:55", "label": "Received via scanned image upload", "live": False},
            {"t": "08:56", "label": "Vision OCR extraction complete", "live": False},
            {"t": "08:56", "label": "OT hours field flagged - 54% confidence", "live": True},
        ],
    },
    {
        "id": "TS-0145",
        "name": "Meera Al Rashid",
        "sub": "Case 6 - Email, reimbursements + leave",
        "client": "Emirates Steel Industries LLC",
        "clientCode": "CL001",
        "amount": "AED 13,950.00",
        "status": "sent",
        "statusLabel": "Dispatched",
        "channel": "Email (structured)",
        "empId": "EMP10003",
        "fields": [
            {"k": "Emp ID", "v": "EMP10003", "c": 99},
            {"k": "Reimbursement", "v": "AED 240 - taxi, client site", "c": 97},
            {"k": "Reimbursement", "v": "AED 85 - printing", "c": 96},
            {"k": "Leave taken", "v": "1 day, annual", "c": 98},
        ],
        "flagType": None,
        "timeline": [
            {"t": "08:10", "label": "Received via Email", "live": False},
            {"t": "08:11", "label": "Matched EMP10003 - exact ID match", "live": False},
            {"t": "08:12", "label": "Validated - passed", "live": False},
            {"t": "08:13", "label": "Invoice dispatched per client order rule", "live": False},
        ],
    },
    {
        "id": "TS-0146",
        "name": "Aisha Al Zaabi",
        "sub": "Case 2 - Email from employee, no client stated",
        "client": "Dubai Airports FZE",
        "clientCode": "CL003",
        "amount": "AED 8,260.00",
        "status": "clear",
        "statusLabel": "Auto-approved",
        "channel": "Email (employee)",
        "empId": "EMP10058",
        "fields": [
            {"k": "Sender", "v": "emp10058@test.com", "c": 99},
            {"k": "Emp ID", "v": "EMP10058", "c": 99},
            {"k": "Working Days", "v": "21", "c": 96},
            {"k": "Client (looked up)", "v": "CL003 - Dubai Airports FZE", "c": 99},
        ],
        "flagType": None,
        "timeline": [
            {"t": "07:40", "label": "Received via Email (employee self-report)", "live": False},
            {"t": "07:41", "label": "Matched EMP10058 - exact ID match", "live": False},
            {"t": "07:41", "label": "Client resolved from employee master record", "live": False},
            {"t": "07:42", "label": "Invoice generated, dispatched to client", "live": False},
        ],
    },
]

INVOICES = [
    {"num": "INV-2026-0301", "clientCode": "CL001", "client": "Emirates Steel Industries LLC", "format": "Full breakdown", "amount": "AED 9,834.13", "status": "sent", "sent": "29 Jun, 09:15"},
    {"num": "INV-2026-0302", "clientCode": "CL001", "client": "Emirates Steel Industries LLC", "format": "Full breakdown", "amount": "AED 13,950.00", "status": "sent", "sent": "29 Jun, 08:13"},
    {"num": "INV-2026-0303", "clientCode": "CL003", "client": "Dubai Airports FZE", "format": "Emp ID + total only", "amount": "AED 8,260.00", "status": "sent", "sent": "29 Jun, 07:42"},
    {"num": "INV-2026-0304", "clientCode": "CL009", "client": "Al Ghurair Centre LLC", "format": "Full breakdown", "amount": "AED 6,480.00", "status": "pending", "sent": "- awaiting field review"},
    {"num": "INV-2026-0305", "clientCode": "CL007", "client": "Dubai Cargo Village LLC", "format": "Emp ID + total only", "amount": "AED 7,120.00", "status": "pending", "sent": "- awaiting identity match"},
]

DISPATCH_QUEUE = [
    {"client": "Al Ghurair Centre LLC", "rule": "Ascending by net pay", "amount": "AED 6,480.00", "status": "Held - field review"},
    {"client": "Dubai Cargo Village LLC", "rule": "Ascending by net pay", "amount": "AED 7,120.00", "status": "Held - identity match"},
]

CLIENT_MASTER = [
    {"code": "CL001", "name": "Emirates Steel Industries LLC", "currency": "AED", "profile": "Standard + OT cap 40h/wk", "fields": "Full breakdown"},
    {"code": "CL002", "name": "Emaar Properties PJSC", "currency": "AED", "profile": "Standard", "fields": "Full breakdown"},
    {"code": "CL003", "name": "Dubai Airports FZE", "currency": "AED", "profile": "Minimal", "fields": "Emp ID + total only"},
    {"code": "CL004", "name": "Sharjah Ports Authority", "currency": "AED", "profile": "Standard", "fields": "Full breakdown"},
    {"code": "CL007", "name": "Dubai Cargo Village LLC", "currency": "AED", "profile": "Minimal", "fields": "Emp ID + total only"},
    {"code": "CL009", "name": "Al Ghurair Centre LLC", "currency": "AED", "profile": "Standard + signature check", "fields": "Full breakdown"},
]

VALIDATION_RULES = [
    {"rule": "Working days must be 18-26 for the pay period", "appliesTo": "All clients", "onFail": "Flag", "active": True},
    {"rule": "OT hours over 40/week requires approval note", "appliesTo": "CL001, CL004", "onFail": "Flag", "active": True},
    {"rule": "Emp ID must resolve to exactly one employee", "appliesTo": "All clients", "onFail": "Hold", "active": True},
    {"rule": "Handwritten field confidence must be >= 85%", "appliesTo": "All clients", "onFail": "Flag", "active": True},
    {"rule": "Signature or stamp must be present", "appliesTo": "CL009", "onFail": "Hold", "active": True},
    {"rule": "Reimbursement lines must include a reason", "appliesTo": "All clients", "onFail": "Flag", "active": False},
]

DISPATCH_RULES = [
    {"code": "CL001", "client": "Emirates Steel Industries LLC", "order": "Ascending by net pay", "channel": "Email"},
    {"code": "CL002", "client": "Emaar Properties PJSC", "order": "Alphabetical by employee", "channel": "Client portal"},
    {"code": "CL003", "client": "Dubai Airports FZE", "order": "As received", "channel": "Email"},
    {"code": "CL007", "client": "Dubai Cargo Village LLC", "order": "Ascending by net pay", "channel": "Email"},
    {"code": "CL009", "client": "Al Ghurair Centre LLC", "order": "Descending by net pay", "channel": "Client portal"},
]


class ChatRequest(BaseModel):
    question: str
    role: str = "finance"
    clientCode: str | None = None


class MatchRequest(BaseModel):
    caseId: str
    employeeId: str


class ReviewRequest(BaseModel):
    caseId: str
    field: str
    value: str


@app.get("/")
def index():
    return FileResponse(HTML_FILE)


@app.get("/tia.html")
def tia_html():
    return FileResponse(HTML_FILE)


@app.get("/health")
def health():
    return {"status": "ok", "frontend": "TIA.html"}


@app.get("/api/bootstrap")
def bootstrap():
    return {
        "cases": deepcopy(CASES),
        "invoices": deepcopy(INVOICES),
        "dispatchQueue": deepcopy(DISPATCH_QUEUE),
        "clientMaster": deepcopy(CLIENT_MASTER),
        "validationRules": deepcopy(VALIDATION_RULES),
        "dispatchRules": deepcopy(DISPATCH_RULES),
        "loggedInClientCode": "CL001",
        "loggedInClientName": "Emirates Steel Industries LLC",
        "kpis": {
            "touchlessRate": "81%",
            "touchlessCount": "34 of 42",
            "avgTurnaround": "6 min",
            "needsReview": 3,
            "extractionAccuracy": "99.2%",
        },
    }


def script_response(callback: str, payload: dict[str, Any]):
    safe_callback = "".join(ch for ch in callback if ch.isalnum() or ch in "._$") or "callback"
    body = f"{safe_callback}({json.dumps(payload)});"
    return Response(content=body, media_type="application/javascript")


@app.get("/api/bootstrap.js")
def bootstrap_js(callback: str = "__tiaJsonp"):
    return script_response(callback, bootstrap())


@app.post("/api/chat")
def chat(req: ChatRequest):
    q = req.question.lower()
    if "ts-0143" in q or "ravi" in q:
        answer = "TS-0143 is held because the email gave a name but no Emp ID. Ravi Menon matches 3 employees, and the stated client narrows it to EMP10136 at 91% confidence."
    elif "ts-0144" in q or "fatima" in q:
        answer = "TS-0144 is held because one handwritten field, OT hours, is ambiguous between 6 and 8. Every other extracted field is high-confidence."
    elif "pending" in q or "awaiting" in q:
        answer = "Two invoices are pending: Al Ghurair Centre for AED 6,480.00 and Dubai Cargo Village for AED 7,120.00."
    elif "ot cap" in q or "overtime" in q:
        answer = "The active rule caps OT hours at 40/week for CL001 and CL004. Anything above that needs an approval note."
    elif "touchless" in q or "rate" in q:
        answer = "Touchless rate this period is 81%, meaning 34 of 42 timesheets completed without human intervention."
    else:
        answer = "I can answer questions about the current client, invoice, or timesheet in view. Try a case ID, a client rule, or pending invoices."
    return {"answer": answer}


@app.get("/api/chat.js")
def chat_js(callback: str = "__tiaJsonp", question: str = "", role: str = "finance", clientCode: str | None = None):
    return script_response(callback, chat(ChatRequest(question=question, role=role, clientCode=clientCode)))


@app.post("/api/actions/confirm-match")
def confirm_match(req: MatchRequest):
    return {
        "status": "ok",
        "message": f"Confirmed {req.employeeId} for {req.caseId}. Invoice regeneration has been queued.",
    }


@app.get("/api/actions/confirm-match.js")
def confirm_match_js(callback: str = "__tiaJsonp", caseId: str = "", employeeId: str = ""):
    return script_response(callback, confirm_match(MatchRequest(caseId=caseId, employeeId=employeeId)))


@app.post("/api/actions/review-field")
def review_field(req: ReviewRequest):
    return {
        "status": "ok",
        "message": f"{req.caseId} {req.field} set to {req.value}. Validation and invoice regeneration have been queued.",
    }


@app.get("/api/actions/review-field.js")
def review_field_js(callback: str = "__tiaJsonp", caseId: str = "", field: str = "", value: str = ""):
    return script_response(callback, review_field(ReviewRequest(caseId=caseId, field=field, value=value)))


@app.post("/api/upload-timesheet")
async def upload_timesheet():
    filename = "demo-timesheet.pdf"
    return {
        "status": "ok",
        "message": f"{filename} received. TIA extraction and validation are queued.",
    }


@app.get("/api/upload-timesheet.js")
def upload_timesheet_js(callback: str = "__tiaJsonp"):
    return script_response(
        callback,
        {
            "status": "ok",
            "message": "demo-timesheet.pdf received. TIA extraction and validation are queued.",
        },
    )
