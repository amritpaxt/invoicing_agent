from match_employee import match_employee
from get_payroll import get_payroll_for_employee

def resolve_employee_and_payroll(extracted: dict, trace: list):
    emp_id = extracted.get("emp_id")
    name = extracted.get("employee_name")
    client = extracted.get("client_name")

    matched, status, candidates = match_employee(emp_id=emp_id, name=name, client_name=client)

    if status == "matched":
        trace.append(f"Matched to {matched['Emp ID']} — {matched['Full Name']} ({matched['Client Name']})")
        payroll = get_payroll_for_employee(matched["Emp ID"])
        return {"employee": matched, "payroll": payroll, "match_status": "matched"}, trace

    elif status == "ambiguous":
        trace.append(f"Name '{name}' matches {len(candidates)} employees — ambiguous, needs human review")
        return {"employee": None, "candidates": candidates, "match_status": "ambiguous"}, trace

    else:
        trace.append(f"No match found for '{name or emp_id}' — needs human review")
        return {"employee": None, "match_status": "not_found"}, trace