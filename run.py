#!/usr/bin/env python3
"""
Movie Streaming API - Development Runner
Quick start script for development environment
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def main():
    """Run the FastAPI application"""
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(current_dir))
    os.environ.setdefault("CSV_FILE_PATH", "data/movies.csv")
    
    print("🎬 Starting Movie Streaming API...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🔄 Alternative documentation at: http://localhost:8000/redoc")
    print("💓 Health check at: http://localhost:8000/health")
    print("=" * 60)
    
    # Check if CSV file exists
    csv_file = Path("data/movies.csv")
    if not csv_file.exists():
        print("❌ ERROR: CSV file not found at data/movies.csv")
        print("Please ensure the CSV file exists before starting the API.")
        sys.exit(1)
    
    # Run the application
    uvicorn.run(
        "presentation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 