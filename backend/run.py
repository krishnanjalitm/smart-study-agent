"""
smart-study-agent/backend/run.py
Application entry point for development and production.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
