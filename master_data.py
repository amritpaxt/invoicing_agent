import pandas as pd

CANONICAL_EMPLOYEES = [
    {
        "Emp ID": "EMP10001",
        "Full Name": "Carlos Smith",
        "Email": "carlos.smith@test.com",
        "Client Code": "CL001",
        "Client Name": "TechCorp Dubai",
        "Job Title": "Senior Developer",
        "Department": "Technology",
        "IBAN": "AE070331234567890123456",
        "Basic": 9000,
        "Housing": 2500,
        "Transport": 600,
        "Food": 400,
        "Phone": 200,
        "Total CTC": 12700,
    },
    {
        "Emp ID": "EMP10058",
        "Full Name": "Aisha Al Zaabi",
        "Email": "aisha.alzaabi@test.com",
        "Client Code": "CL003",
        "Client Name": "RetailCo Sharjah",
        "Job Title": "Store Supervisor",
        "Department": "Retail Operations",
        "IBAN": "AE070331234567890100058",
        "Basic": 7500,
        "Housing": 2000,
        "Transport": 500,
        "Food": 300,
        "Phone": 150,
        "Total CTC": 10450,
    },
    {
        "Emp ID": "EMP10072",
        "Full Name": "Aisha Al Zaabi",
        "Email": "aisha.alzaabi.finance@test.com",
        "Client Code": "CL004",
        "Client Name": "FinanceCo Dubai",
        "Job Title": "Finance Analyst",
        "Department": "Finance",
        "IBAN": "AE070331234567890100072",
        "Basic": 8200,
        "Housing": 2200,
        "Transport": 550,
        "Food": 350,
        "Phone": 150,
        "Total CTC": 11450,
    },
    {
        "Emp ID": "EMP10077",
        "Full Name": "Aisha Al Zaabi",
        "Email": "aisha.alzaabi.ops@test.com",
        "Client Code": "CL004",
        "Client Name": "FinanceCo Dubai",
        "Job Title": "Accounts Associate",
        "Department": "Finance",
        "IBAN": "AE070331234567890100077",
        "Basic": 7800,
        "Housing": 2000,
        "Transport": 500,
        "Food": 300,
        "Phone": 150,
        "Total CTC": 10750,
    },
    {
        "Emp ID": "EMP10070",
        "Full Name": "Ravi Menon",
        "Email": "emp10070@test.com",
        "Client Code": "CL004",
        "Client Name": "FinanceCo Dubai",
        "Job Title": "Senior Accountant",
        "Department": "Finance",
        "IBAN": "AE070331234567890100070",
        "Basic": 8500,
        "Housing": 2000,
        "Transport": 500,
        "Food": 300,
        "Phone": 150,
        "Total CTC": 11450,
    },
    {
        "Emp ID": "EMP10136",
        "Full Name": "Ravi Menon",
        "Email": "ravi.logistics@test.com",
        "Client Code": "CL007",
        "Client Name": "LogisticsCo Dubai",
        "Job Title": "Logistics Coordinator",
        "Department": "Operations",
        "IBAN": "AE070331234567890101136",
        "Basic": 7200,
        "Housing": 1800,
        "Transport": 450,
        "Food": 300,
        "Phone": 150,
        "Total CTC": 9900,
    },
    {
        "Emp ID": "EMP10157",
        "Full Name": "Ravi Menon",
        "Email": "ravi.auto@test.com",
        "Client Code": "CL008",
        "Client Name": "AutoCorp Sharjah",
        "Job Title": "Plant Supervisor",
        "Department": "Manufacturing",
        "IBAN": "AE070331234567890101157",
        "Basic": 9500,
        "Housing": 2500,
        "Transport": 600,
        "Food": 400,
        "Phone": 200,
        "Total CTC": 13200,
    },
    {
        "Emp ID": "EMP10083",
        "Full Name": "Fatima Khan",
        "Email": "emp10083@test.com",
        "Client Code": "CL005",
        "Client Name": "HealthCo Dubai",
        "Job Title": "Clinic Coordinator",
        "Department": "Healthcare",
        "IBAN": "AE070331234567890100083",
        "Basic": 8000,
        "Housing": 2000,
        "Transport": 500,
        "Food": 300,
        "Phone": 150,
        "Total CTC": 10950,
    },
    {
        "Emp ID": "EMP10093",
        "Full Name": "Fatima Khan",
        "Email": "fatima.health@test.com",
        "Client Code": "CL005",
        "Client Name": "HealthCo Dubai",
        "Job Title": "Medical Admin",
        "Department": "Healthcare",
        "IBAN": "AE070331234567890100093",
        "Basic": 7500,
        "Housing": 1800,
        "Transport": 450,
        "Food": 250,
        "Phone": 150,
        "Total CTC": 10150,
    },
]

CANONICAL_EMPLOYEES_DF = pd.DataFrame(CANONICAL_EMPLOYEES)

def load_master_data(path="TASC_Sample_Database_vF.xlsx"):
    employees = pd.read_excel(path, sheet_name="Employees")
    payroll = pd.read_excel(path, sheet_name="Payroll_June2026")
    return employees, payroll

EMPLOYEES_DF, PAYROLL_DF = load_master_data()


def get_canonical_employee(emp_id: str | None = None, name: str | None = None, client_name: str | None = None):
    df = CANONICAL_EMPLOYEES_DF
    match = df
    if emp_id:
        return df[df["Emp ID"].str.upper() == str(emp_id).upper()]
    if name:
        match = match[match["Full Name"].str.lower() == str(name).lower()]
    if client_name and len(match) > 0:
        client = str(client_name).lower()
        match = match[
            match["Client Name"].str.lower().str.contains(client, na=False)
            | match["Client Code"].str.lower().str.contains(client, na=False)
            | match["Client Name"].str.lower().str.split().str[0].str.contains(client.split()[0], na=False)
        ]
    return match
