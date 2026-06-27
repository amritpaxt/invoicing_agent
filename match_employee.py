from master_data import CANONICAL_EMPLOYEES_DF, EMPLOYEES_DF


def match_employee(emp_id=None, name=None, client_name=None):
    """
    Match extracted input against canonical HackArena data first, then the
    spreadsheet fallback. Returns (row_or_none, status, candidates).
    """
    emp_id = str(emp_id).strip().upper() if emp_id else None
    name = str(name).strip() if name else None
    client_name = str(client_name).strip() if client_name else None

    result = _match_in_df(CANONICAL_EMPLOYEES_DF, emp_id, name, client_name)
    if result[1] != "not_found":
        return result

    return _match_in_df(EMPLOYEES_DF, emp_id, name, client_name)


def _match_in_df(df, emp_id=None, name=None, client_name=None):
    if emp_id:
        match = df[df["Emp ID"].astype(str).str.upper() == emp_id]
        if len(match) == 1:
            return match.iloc[0].to_dict(), "matched", []
        if len(match) > 1:
            return None, "ambiguous", match.to_dict(orient="records")
        return None, "not_found", []

    if name and client_name:
        client = client_name.lower()
        first_token = client.split()[0] if client.split() else client
        match = df[
            (df["Full Name"].astype(str).str.lower() == name.lower())
            & (
                df["Client Name"].astype(str).str.lower().str.contains(client, na=False)
                | df["Client Code"].astype(str).str.lower().str.contains(client, na=False)
                | df["Client Name"].astype(str).str.lower().str.contains(first_token, na=False)
            )
        ]
        if len(match) == 1:
            return match.iloc[0].to_dict(), "matched", []
        if len(match) > 1:
            return None, "ambiguous", match.to_dict(orient="records")
        return None, "not_found", []

    if name:
        match = df[df["Full Name"].astype(str).str.lower() == name.lower()]
        if len(match) == 1:
            return match.iloc[0].to_dict(), "matched", []
        if len(match) > 1:
            return None, "ambiguous", match.to_dict(orient="records")

    return None, "not_found", []
