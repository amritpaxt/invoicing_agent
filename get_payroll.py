from master_data import CANONICAL_EMPLOYEES_DF, PAYROLL_DF


def get_payroll_for_employee(emp_id: str):
    canonical = CANONICAL_EMPLOYEES_DF[
        CANONICAL_EMPLOYEES_DF["Emp ID"].astype(str).str.upper() == str(emp_id).upper()
    ]
    if len(canonical) == 1:
        employee = canonical.iloc[0].to_dict()
        gross = float(employee["Total CTC"])
        return {
            "Emp ID": employee["Emp ID"],
            "Employee Name": employee["Full Name"],
            "Client Code": employee["Client Code"],
            "Client Name": employee["Client Name"],
            "Pay Period": "June 2026",
            "Basic": float(employee["Basic"]),
            "Housing": float(employee["Housing"]),
            "Transport": float(employee["Transport"]),
            "Food": float(employee["Food"]),
            "Phone": float(employee["Phone"]),
            "Gross": gross,
            "OT Hours": 0.0,
            "OT Amount": 0.0,
            "Deductions": 0.0,
            "Net Pay": gross,
            "Currency": "AED",
            "Working Days": 26,
            "IBAN": employee.get("IBAN"),
            "Job Title": employee.get("Job Title"),
            "Department": employee.get("Department"),
        }

    match = PAYROLL_DF[PAYROLL_DF["Emp ID"] == emp_id]
    if len(match) == 1:
        return match.iloc[0].to_dict()
    return None
