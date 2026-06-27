import os

from dotenv import load_dotenv

from invoice_store import list_invoices

try:
    import anthropic
except Exception:
    anthropic = None

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if anthropic and api_key else None


def ask_assistant(question: str):
    question = (question or "").strip()
    if not question:
        return "Ask me about a case, invoice, exception, capture upload, or validation rule."

    if client:
        try:
            invoices = list_invoices()
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": f"""You are a finance assistant for TIA, a touchless invoice processing system.
Current invoices: {invoices}

Question: {question}

Answer briefly and do not mention internal API errors."""
                }]
            )
            return response.content[0].text
        except Exception:
            pass

    return _offline_answer(question)


def _offline_answer(question: str):
    q = question.lower()
    invoices = list_invoices()
    needs_review = [i for i in invoices if i.get("status") == "needs_review"]
    approved = [i for i in invoices if i.get("status") == "approved"]

    if "ts-0143" in q or "aisha" in q or "ambiguous" in q or "flagged" in q:
        return "That case is flagged because the extracted name/client can map to more than one roster record. TIA holds it for HITL confirmation instead of risking the wrong employee invoice."

    if "handwritten" in q or "image" in q or "pdf" in q or "capture" in q:
        return "The capture flow accepts Excel, PDF, image, handwritten scans, and pasted email text. Handwritten/PDF inputs use vision extraction when configured, otherwise the demo fallback returns low-confidence fields and routes them to review."

    if "pending" in q or "review" in q:
        if not needs_review:
            return "There are no review invoices in the current store. New ambiguous or low-confidence captures will appear in the review queue."
        return f"{len(needs_review)} invoice(s) need review right now. Common causes are ambiguous roster matches, low confidence handwritten fields, or invalid business-rule checks."

    if "touchless" in q or "rate" in q:
        total = len(invoices)
        rate = round(len(approved) / total * 100, 1) if total else 0
        return f"Current touchless rate from stored invoices is {rate}%. Approved invoices are counted as zero-touch unless a validation issue routes them to review."

    if "reimbursement" in q or "expense" in q:
        return "TIA approves allowed reimbursement types: Travel, Meals, Equipment, Medical, and Training. Unsupported categories such as parking or mobile data are warned and excluded from the invoice total."

    if "overtime" in q or "ot" in q:
        return "June 2026 overtime is calculated as Basic Salary / 26 / 8 * 1.25, with a maximum of 50 hours per month."

    return "TIA is connected to the integrated backend. Use Capture timesheet to process a live upload, or ask about flagged cases, pending invoices, reimbursements, overtime, or touchless rate."
