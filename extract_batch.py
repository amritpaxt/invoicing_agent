import re

from extract_llm import extract_from_text, extract_reimbursement_lines


def extract_client_list(raw_text: str):
    client_name = _extract_client(raw_text)
    client_code = _extract_client_code(raw_text)
    results = []
    pattern = re.compile(
        r"^\s*(?:[-*]|\d+\.)\s*(?:\[Unknown Name\]\s*)?(?P<name>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s*(?:--|-|:)\s*(?P<days>\d{1,2})\s*days?(?:,\s*(?P<ot>\d+(?:\.\d+)?)\s*(?:hrs?|hours?)\s*OT)?",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    for match in pattern.finditer(raw_text or ""):
        results.append(
            {
                "employee_name": match.group("name").strip(),
                "client_name": client_name or client_code,
                "client_code": client_code,
                "working_days": int(match.group("days")),
                "overtime_hours": float(match.group("ot") or 0),
                "pay_period": "June 2026",
                "input_channel": "Mailbox",
                "document_type": "Client batch list",
                "confidence": 0.9 if client_name or client_code else 0.75,
                "reimbursements": [],
            }
        )
    return results


def extract_reimbursements(raw_text: str):
    extracted = extract_from_text(raw_text)
    extracted["reimbursements"] = extract_reimbursement_lines(raw_text)
    if extracted.get("working_days") is None:
        extracted["working_days"] = 24
    extracted["document_type"] = "Email with reimbursements"
    return extracted


def _extract_client(raw_text):
    match = re.search(r"Client\s*:\s*([A-Z][A-Za-z0-9\s]+)", raw_text or "", flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    for client in ["FinanceCo", "TechCorp", "RetailCo", "HealthCo"]:
        if client.lower() in (raw_text or "").lower():
            return client
    return None


def _extract_client_code(raw_text):
    match = re.search(r"\b(CL\d{3})\b", raw_text or "", flags=re.IGNORECASE)
    return match.group(1).upper() if match else None
