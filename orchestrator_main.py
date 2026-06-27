from extract_excel import extract_excel_timesheet
from extract_llm import extract_from_text
from extract_vision import extract_from_image
from orchestrator import resolve_employee_and_payroll
from validate import validate_invoice


def detect_file_type(filename: str):
    filename = (filename or "").lower()
    if filename.endswith((".xlsx", ".xls")):
        return "excel"
    if filename.endswith((".png", ".jpg", ".jpeg")):
        return "image"
    if filename.endswith(".pdf"):
        return "pdf"
    if filename.endswith((".txt", ".eml")):
        return "text"
    return "unknown"


def process_any_input(file_path: str = None, raw_text: str = None):
    trace = []

    if raw_text:
        trace.append("CAPTURE: raw text/email input received")
        extracted = extract_from_text(raw_text)
        trace.append(f"EXTRACT: deterministic text parser confidence {extracted.get('confidence')}")
    elif file_path:
        file_type = detect_file_type(file_path)
        trace.append(f"CAPTURE: {file_type} file uploaded")

        if file_type == "excel":
            extracted = extract_excel_timesheet(file_path)
            trace.append(f"EXTRACT: structured Excel parser confidence {extracted.get('confidence')}")
        elif file_type == "text":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
                extracted = extract_from_text(handle.read())
            trace.append(f"EXTRACT: uploaded text parser confidence {extracted.get('confidence')}")
        elif file_type in {"image", "pdf"}:
            extracted = extract_from_image(file_path)
            extracted.setdefault("input_channel", "Portal Upload")
            extracted.setdefault("document_type", "Handwritten/PDF upload")
            trace.append(f"EXTRACT: vision parser confidence {extracted.get('confidence', 'unknown')}")
        else:
            return {"error": "unsupported file type"}, trace
    else:
        return {"error": "no input provided"}, trace

    if extracted.get("confidence", 1.0) < 0.7:
        trace.append("SCORE: low confidence, HITL review required")

    match_result, trace = resolve_employee_and_payroll(extracted, trace)
    validation = validate_invoice(match_result, extracted)
    trace.append(f"VALIDATE: {validation['status']} with {validation.get('rules_passed', 0)}/7 rules passed")

    return {
        "extracted": extracted,
        "match_result": match_result,
        "validation": validation,
        "processing_report": build_processing_report(extracted, match_result, validation),
    }, trace


def build_processing_report(extracted, match_result, validation):
    employee = match_result.get("employee") or {}
    return {
        "title": "TIA PROCESSING REPORT",
        "capture": {
            "input_channel": extracted.get("input_channel", "Portal Upload"),
            "document_type": extracted.get("document_type", "Timesheet"),
            "pay_period": extracted.get("pay_period", "June 2026"),
        },
        "extraction": {
            "employee_name": extracted.get("employee_name"),
            "emp_id": extracted.get("emp_id"),
            "client_name": extracted.get("client_name"),
            "working_days": extracted.get("working_days"),
            "overtime_hours": extracted.get("overtime_hours", 0),
            "leave_days": extracted.get("leave_days"),
            "reimbursements": extracted.get("reimbursements", []),
            "confidence": extracted.get("confidence"),
        },
        "match": {
            "status": match_result.get("match_status"),
            "emp_id": employee.get("Emp ID"),
            "name": employee.get("Full Name"),
            "client": employee.get("Client Name"),
            "candidates": match_result.get("candidates", []),
        },
        "validation": {
            "status": validation.get("status"),
            "issues": validation.get("issues", []),
            "rules": validation.get("rules", []),
            "rules_passed": validation.get("rules_passed"),
        },
        "invoice": validation.get("invoice_breakdown", {}),
    }
