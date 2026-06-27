import uuid
from datetime import datetime

QUERIES = {}

def raise_query(invoice_id: str, message: str):
    query_id = str(uuid.uuid4())[:8]
    QUERIES[query_id] = {
        "id": query_id,
        "invoice_id": invoice_id,
        "message": message,
        "status": "open",
        "response": None,
        "created_at": datetime.now().isoformat()
    }
    return QUERIES[query_id]

def list_queries():
    return list(QUERIES.values())

def respond_to_query(query_id: str, response: str):
    if query_id in QUERIES:
        QUERIES[query_id]["response"] = response
        QUERIES[query_id]["status"] = "resolved"
        return QUERIES[query_id]
    return None