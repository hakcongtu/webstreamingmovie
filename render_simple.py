#!/usr/bin/env python3
"""
Simple startup script for Render deployment - fallback option
Minimal configuration that should work with Render's auto-detection
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add src directory to Python path  
src_dir = current_dir / "src"
if src_dir.exists():
    sys.path.insert(0, str(src_dir))

# Set basic environment variables
os.environ.setdefault("CSV_FILE_PATH", str(current_dir / "data" / "movies.csv"))

print(f"📁 Working directory: {current_dir}")
print(f"🐍 Python path: {sys.path[:3]}")
print(f"📊 CSV file: {os.environ.get('CSV_FILE_PATH')}")

# Check if CSV file exists
csv_file = Path(os.environ.get('CSV_FILE_PATH'))
if csv_file.exists():
    print(f"✅ CSV file found: {csv_file}")
else:
    print(f"⚠️ CSV file not found: {csv_file}")

# Import and run
try:
    import uvicorn
    print("✅ uvicorn imported successfully")
    
    # Try to import the app
    from src.presentation.main import app
    print("✅ FastAPI app imported successfully")
    
    # Get port
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting on port {port}")
    
    # Run the app with explicit port binding
    print(f"🌐 Binding to ALL interfaces (0.0.0.0) on port {port}")
    print(f"🔗 Health check URL: http://0.0.0.0:{port}/health")
    
    uvicorn.run(
        app,  # Use the imported app directly
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        timeout_keep_alive=5,
        backlog=2048  # Increase connection backlog
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    raise 