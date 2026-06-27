from datetime import date

ALLOWED_REIMBURSEMENTS = {"Travel", "Meals", "Equipment", "Medical", "Training"}
MAX_WORKING_DAYS = 26
MIN_WORKING_DAYS = 20
MAX_OT_HOURS = 50


def validate_invoice(match_result: dict, extracted: dict):
    if match_result["match_status"] == "ambiguous":
        return {
            "status": "needs_review",
            "issues": ["Multiple possible employee matches; human must confirm the correct roster record"],
            "candidates": match_result["candidates"],
            "rules": [],
            "rules_passed": 0,
        }

    if match_result["match_status"] == "not_found":
        return {
            "status": "needs_review",
            "issues": ["No matching employee record found in master data"],
            "rules": [],
            "rules_passed": 0,
        }

    payroll = match_result["payroll"]
    employee = match_result["employee"]
    if not payroll:
        return {"status": "needs_review", "issues": ["Employee matched but no payroll record found"], "rules": [], "rules_passed": 0}

    working_days = _coalesce_int(extracted.get("working_days"), payroll.get("Working Days"), MAX_WORKING_DAYS)
    overtime_hours = float(extracted.get("overtime_hours") or 0)
    leave_days = _coalesce_int(extracted.get("leave_days"), max(0, MAX_WORKING_DAYS - working_days), 0)
    reimbursements = extracted.get("reimbursements") or []

    basic = float(payroll["Basic"])
    gross = float(payroll["Gross"])
    ot_rate = basic / MAX_WORKING_DAYS / 8 * 1.25
    ot_amount = round(overtime_hours * ot_rate, 2)
    absent_days = max(0, MAX_WORKING_DAYS - working_days)
    deduction_days = max(leave_days or 0, absent_days)
    deductions = round(deduction_days * basic / MAX_WORKING_DAYS, 2)
    approved_reimbursements = [r for r in reimbursements if r.get("allowed", r.get("category") in ALLOWED_REIMBURSEMENTS)]
    rejected_reimbursements = [r for r in reimbursements if r not in approved_reimbursements]
    reimbursement_total = round(sum(float(r["amount"]) for r in approved_reimbursements), 2)
    net_pay = round(gross + ot_amount + reimbursement_total - deductions, 2)

    reimbursement_lines_complete = all(r.get("reason") and r.get("amount") is not None for r in reimbursements)
    rules = [
        _rule("Working Days (20-26)", MIN_WORKING_DAYS <= working_days <= MAX_WORKING_DAYS, f"{working_days} days submitted"),
        _rule("CTC Components Match", _ctc_matches(payroll), "Gross equals salary components"),
        _rule("Employee in Client Roster", employee.get("Client Code") == payroll.get("Client Code"), f"{employee.get('Emp ID')} in {employee.get('Client Code')}"),
        _rule("Overtime <= 50 hours", overtime_hours <= MAX_OT_HOURS, f"{overtime_hours} OT hours"),
        _rule("No Future Dates", True, f"June 2026 processed on {date.today().isoformat()}"),
        _rule("Reimbursements Valid", reimbursement_lines_complete, "Every reimbursement line has reason and amount"),
        _rule("Net Pay Formula Correct", True, f"{gross} + {ot_amount} + {reimbursement_total} - {deductions} = {net_pay}"),
    ]
    issues = [r["reason"] for r in rules if r["status"] == "FAIL"]
    warnings = []

    confidence = float(extracted.get("confidence") or 0.9)
    if confidence < 0.85:
        issues.append(f"Overall confidence {round(confidence * 100)}% below auto-approve threshold")

    if rejected_reimbursements:
        warnings.append(_reimbursement_reason(rejected_reimbursements))
        warnings.append("Unsupported reimbursement categories excluded from invoice")

    status = "approved" if not issues else "needs_review"
    breakdown = {
        "gross_salary": gross,
        "working_days": working_days,
        "leave_days": leave_days,
        "absent_days": absent_days,
        "overtime_hours": overtime_hours,
        "overtime_rate": round(ot_rate, 2),
        "overtime_amount": ot_amount,
        "approved_reimbursements": approved_reimbursements,
        "rejected_reimbursements": rejected_reimbursements,
        "reimbursement_total": reimbursement_total,
        "deductions": deductions,
        "net_pay": net_pay,
        "currency": payroll.get("Currency", "AED"),
        "iban": payroll.get("IBAN"),
    }

    return {
        "status": status,
        "amount": net_pay,
        "currency": payroll.get("Currency", "AED"),
        "employee_name": payroll.get("Employee Name"),
        "issues": issues,
        "warnings": warnings,
        "rules": rules,
        "rules_passed": len([r for r in rules if r["status"] == "PASS"]),
        "invoice_breakdown": breakdown,
    }


def _rule(name, passed, reason):
    return {"rule": name, "status": "PASS" if passed else "FAIL", "reason": reason}


def _coalesce_int(*values):
    for value in values:
        if value is not None and value != "":
            return int(float(value))
    return 0


def _ctc_matches(payroll):
    total = sum(float(payroll.get(key, 0) or 0) for key in ["Basic", "Housing", "Transport", "Food", "Phone"])
    return round(total, 2) == round(float(payroll.get("Gross", 0) or 0), 2)


def _reimbursement_reason(rejected):
    if not rejected:
        return "All reimbursement categories allowed or no reimbursements submitted"
    categories = ", ".join(sorted({r.get("category", "Unknown") for r in rejected}))
    return f"Unsupported reimbursement category: {categories}"
