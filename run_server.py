#!/usr/bin/env python
from __future__ import annotations

import sys

import uvicorn

if __name__ == "__main__":
    print("Starting TIA project server...")
    print("Frontend: tia-frontend/dist or Vite dev server")
    print("Backend: http://127.0.0.1:5000")
    print("API: http://127.0.0.1:5000/api")
    try:
        uvicorn.run(
            "backend:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
            log_level="info",
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
