import os
import base64
import json
from dotenv import load_dotenv

try:
    import anthropic
except Exception:
    anthropic = None

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if anthropic and api_key else None

def extract_from_image(image_path: str):
    if not client:
        return {
            "emp_id": None,
            "employee_name": "Ravi Menon",
            "client_name": "FinanceCo Dubai",
            "working_days": 21,
            "overtime_hours": 4.0,
            "leave_days": 5,
            "pay_period": "June 2026",
            "input_channel": "Portal Upload",
            "document_type": "Handwritten scanned image",
            "vision_fields": [
                {"field": "Employee", "value": "Ravi Menon", "confidence": 68, "note": "unclear handwriting"},
                {"field": "ID Number", "value": "EMP1013G", "confidence": 45, "note": "6/G ambiguous"},
                {"field": "Client stamp", "value": "FinanceCo CL004", "confidence": 86, "note": "stamp is clearer"},
                {"field": "Days present", "value": "21", "confidence": 64, "note": "could be 21 or 27"},
                {"field": "Overtime", "value": "4 hrs", "confidence": 72, "note": "scribbled but readable"},
            ],
            "confidence": 0.62,
            "warning": "Vision API is not configured; used deterministic handwritten demo fallback",
        }

    try:
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = image_path.lower()
        media_type = "image/png" if ext.endswith(".png") else "image/jpeg"

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": """This is a timesheet, possibly handwritten. Extract:
{"emp_id": "", "employee_name": "", "client_name": "", "working_days": 0, "confidence": 0}
Return ONLY this JSON, nothing else."""}
                ]
            }]
        )
        text_response = response.content[0].text.replace("```json", "").replace("```", "").strip()
        return json.loads(text_response)
    except Exception as e:
        print("VISION EXTRACTION ERROR:", e)
        return {"emp_id": None, "employee_name": None, "client_name": None, "working_days": None, "confidence": 0.0, "error": str(e)}
