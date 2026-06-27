import uuid
from datetime import datetime
from db import SessionLocal, Invoice

def invoice_to_dict(inv):
    return {
        "id": inv.id,
        "employee_name": inv.employee_name,
        "client_name": inv.client_name,
        "amount": inv.amount,
        "currency": inv.currency,
        "status": inv.status,
        "issues": inv.issues.split(", ") if inv.issues else [],
        "dispatched": inv.dispatched,
        "client_notified": inv.client_notified,
        "finalized": inv.finalized,
        "created_at": inv.created_at.isoformat() if inv.created_at else None
    }

def create_invoice(match_result: dict, validation: dict):
    db = SessionLocal()
    invoice_id = str(uuid.uuid4())[:8]
    employee = match_result.get("employee") or {}
    invoice = Invoice(
        id=invoice_id,
        employee_name=validation.get("employee_name"),
        client_name=employee.get("Client Name"),
        amount=validation.get("amount"),
        currency=validation.get("currency"),
        status=validation.get("status"),
        issues=", ".join(validation.get("issues", [])) if validation.get("issues") else None,
        dispatched=False
    )
    db.add(invoice)
    db.commit()
    result = invoice_to_dict(invoice)
    db.close()
    return result

def list_invoices():
    db = SessionLocal()
    invoices = db.query(Invoice).all()
    result = [invoice_to_dict(i) for i in invoices]
    db.close()
    return result

def get_invoice(invoice_id: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    result = invoice_to_dict(inv) if inv else None
    db.close()
    return result

def approve_invoice(invoice_id: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if inv:
        inv.status = "approved"
        db.commit()
        result = invoice_to_dict(inv)
    else:
        result = None
    db.close()
    return result

def finalize_invoice(invoice_id: str, decision: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if inv:
        inv.status = "approved" if decision == "keep" else "discarded"
        inv.finalized = True
        db.commit()
        result = invoice_to_dict(inv)
    else:
        result = None
    db.close()
    return result

def dispatch_all_approved():
    db = SessionLocal()
    invoices = db.query(Invoice).filter(Invoice.status == "approved", Invoice.dispatched == False).all()
    invoices.sort(key=lambda x: x.amount or 0)
    dispatched = []
    for inv in invoices:
        inv.dispatched = True
        inv.dispatched_at = datetime.now()
        dispatched.append(invoice_to_dict(inv))
    db.commit()
    db.close()
    return dispatched

def mark_sent_to_client(invoice_id: str):
    db = SessionLocal()
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if inv and inv.dispatched:
        inv.client_notified = True
        db.commit()
        result = invoice_to_dict(inv)
    else:
        result = None
    db.close()
    return result