from orchestrator_main import process_any_input
from extract_batch import extract_client_list
from orchestrator import resolve_employee_and_payroll
from validate import validate_invoice


CASE_1 = """From: aisha.alzaabi@test.com
Subject: June 2026 Timesheet
Name: Aisha Al Zaabi
Client: FinanceCo
Total days worked: 24
No overtime this month.
"""

CASE_2 = """From: emp10070@test.com
Employee ID: EMP10070
Days worked this month: 23
Overtime: 6 hours
Please process for June 2026.
"""

CASE_3 = """Client: FinanceCo
Client Code: CL004
Period: June 2026

Employee Attendance:
1. Aisha Al Zaabi -- 22 days
2. Ravi Menon -- 24 days, 4hrs OT
3. [Unknown Name] James Cooper -- 20 days
4. Sara Ahmed -- 26 days
"""

CASE_6 = """Employee ID: EMP10083
Month: June 2026
Working Days: 24
Overtime: 0

Reimbursement Claims:
1. Client site travel -- Uber receipts -- AED 340
2. Team lunch -- client meeting 15 Jun -- AED 185
3. Medical -- clinic visit 20 Jun -- AED 420
4. Mobile data top-up -- field work -- AED 99
5. Parking -- DIFC office -- AED 750

Total reimbursements claimed: AED 1,794
Fatima Khan
EMP10083
"""


def assert_close(actual, expected):
    assert abs(actual - expected) < 0.01, f"expected {expected}, got {actual}"


def test_case_1_ambiguity():
    result, _ = process_any_input(raw_text=CASE_1)
    assert result["match_result"]["match_status"] == "ambiguous"
    assert result["validation"]["status"] == "needs_review"
    assert len(result["match_result"]["candidates"]) == 2


def test_case_2_empid_invoice():
    result, _ = process_any_input(raw_text=CASE_2)
    assert result["match_result"]["match_status"] == "matched"
    assert result["match_result"]["employee"]["Emp ID"] == "EMP10070"
    assert result["validation"]["status"] == "approved"
    assert_close(result["validation"]["amount"], 10775.72)


def test_case_3_batch_matching():
    extracted = extract_client_list(CASE_3)
    statuses = []
    for item in extracted:
        match_result, trace = resolve_employee_and_payroll(item, [])
        validation = validate_invoice(match_result, item)
        statuses.append((item["employee_name"], match_result["match_status"], validation["status"]))
    assert statuses == [
        ("Aisha Al Zaabi", "ambiguous", "needs_review"),
        ("Ravi Menon", "matched", "approved"),
        ("James Cooper", "not_found", "needs_review"),
        ("Sara Ahmed", "not_found", "needs_review"),
    ]


def test_case_6_reimbursements_touchless_with_warnings():
    result, _ = process_any_input(raw_text=CASE_6)
    assert result["match_result"]["employee"]["Emp ID"] == "EMP10083"
    assert result["validation"]["status"] == "approved"
    assert_close(result["validation"]["invoice_breakdown"]["reimbursement_total"], 945.0)
    assert result["validation"]["warnings"]
    assert_close(result["validation"]["amount"], 11279.62)


if __name__ == "__main__":
    test_case_1_ambiguity()
    test_case_2_empid_invoice()
    test_case_3_batch_matching()
    test_case_6_reimbursements_touchless_with_warnings()
    print("All demo regression checks passed.")
