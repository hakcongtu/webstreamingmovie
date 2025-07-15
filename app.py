#!/usr/bin/env python3
"""
Simple app.py for Render auto-detection
This file exposes the FastAPI app directly for deployment
"""

import os
import sys
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Set CSV file path
os.environ.setdefault("CSV_FILE_PATH", str(current_dir / "data" / "movies.csv"))

# Import and expose the app
from presentation.main import app

# This allows Render to auto-detect the FastAPI app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Movie API on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=port,
        log_level="info"
    ) 