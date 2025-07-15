#!/usr/bin/env python3
"""
Render deployment starter
Simple script for Render deployment
"""

import os
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

# Set environment
os.environ.setdefault("CSV_FILE_PATH", str(current_dir / "data" / "movies.csv"))

# Import app
from presentation.main import app

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