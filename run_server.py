#!/usr/bin/env python
import uvicorn
import sys

if __name__ == "__main__":
    print("🚀 Starting TIA Backend Server...")
    print("📝 Frontend: TIA.html")
    print("📡 API: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/docs")
    print("\nPress CTRL+C to stop the server\n")
    
    try:
        uvicorn.run(
            "backend:app",
            host="127.0.0.1",
            port=5000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
