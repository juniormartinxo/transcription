#!/usr/bin/env python3
"""
Script de desenvolvimento com hot reload para a API de transcrição.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src/", "./"],
        reload_excludes=["*.pyc", "__pycache__", "*.log", "venv/", ".env"],
        log_level="info"
    )