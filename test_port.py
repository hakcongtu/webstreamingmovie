#!/usr/bin/env python3
"""
Test port binding locally before deployment
"""

import os
import sys
import socket
from pathlib import Path

def test_port_binding():
    """Test if we can bind to the specified port"""
    port = int(os.environ.get("PORT", 8000))
    
    try:
        # Test socket binding
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        print(f"✅ Port {port} is available for binding")
        return True
    except Exception as e:
        print(f"❌ Cannot bind to port {port}: {e}")
        return False

def test_app_import():
    """Test if app can be imported"""
    try:
        # Setup paths
        current_dir = Path(__file__).parent
        src_path = current_dir / "src"
        sys.path.insert(0, str(src_path))
        
        # Set environment
        os.environ.setdefault("CSV_FILE_PATH", str(current_dir / "data" / "movies.csv"))
        
        # Import app
        from src.presentation.main import app
        print("✅ FastAPI app imported successfully")
        print(f"✅ App type: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_quick_server():
    """Start a quick test server"""
    try:
        import uvicorn
        from src.presentation.main import app
        
        port = int(os.environ.get("PORT", 8001))  # Use different port for test
        print(f"🧪 Starting test server on port {port}")
        print("🔗 Test URLs:")
        print(f"   - Health: http://localhost:{port}/health")
        print(f"   - Docs: http://localhost:{port}/docs")
        print("📝 Press Ctrl+C to stop")
        
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
        
    except KeyboardInterrupt:
        print("\n✅ Test server stopped successfully")
    except Exception as e:
        print(f"❌ Test server failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing port binding for Movie Streaming API")
    print("=" * 50)
    
    port_ok = test_port_binding()
    app_ok = test_app_import()
    
    if port_ok and app_ok:
        print("\n✅ All tests passed!")
        
        # Ask user if they want to start test server
        response = input("\n🚀 Start test server? (y/n): ").lower()
        if response in ['y', 'yes']:
            test_quick_server()
    else:
        print("\n❌ Tests failed. Fix issues before deployment.") 