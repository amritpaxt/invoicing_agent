import re

def extract_from_text_regex(raw_text: str):
    """Fallback extractor using regex patterns - works without any API calls."""
    text = raw_text.strip()
    
    result = {
        "emp_id": None,
        "employee_name": None,
        "client_name": None,
        "working_days": None,
        "confidence": 0.0
    }
    
    emp_match = re.search(r'\bEMP\d{4,6}\b', text, re.IGNORECASE)
    if emp_match:
        result["emp_id"] = emp_match.group().upper()
        result["confidence"] += 0.4

    days_match = re.search(r'(\d{1,2})\s*days', text, re.IGNORECASE)
    if days_match:
        result["working_days"] = int(days_match.group(1))
        result["confidence"] += 0.2

    name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)\b', text)
    if name_match:
        candidate = name_match.group(1)
        if candidate.lower() not in ["emp id", "this month"]:
            result["employee_name"] = candidate
            result["confidence"] += 0.3

    client_match = re.search(r'(?:at|for|client)\s+([A-Z][\w\s]+?(?:LLC|Ltd|Inc|Industries|Group|Corp))', text, re.IGNORECASE)
    if client_match:
        result["client_name"] = client_match.group(1).strip()
        result["confidence"] += 0.1

    result["confidence"] = min(result["confidence"], 1.0)
    return result