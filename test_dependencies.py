#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported
Run this before deployment to catch import errors early
"""

def test_imports():
    """Test importing all required dependencies"""
    try:
        print("Testing core dependencies...")
        
        # FastAPI core
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
        
        import uvicorn
        print(f"✅ Uvicorn {uvicorn.__version__}")
        
        # Pydantic
        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")
        
        # Data processing
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
        
        # Authentication
        import jose
        print("✅ Python-JOSE imported")
        
        import passlib
        print("✅ Passlib imported")
        
        # Other dependencies
        import aiofiles
        print("✅ Aiofiles imported")
        
        import email_validator
        print("✅ Email-validator imported")
        
        print("\n🎉 All dependencies imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_fastapi_app():
    """Test if the FastAPI app can be imported"""
    try:
        print("\nTesting FastAPI app import...")
        from src.presentation.main import app
        print("✅ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing dependencies for Movie Streaming API")
    print("=" * 50)
    
    deps_ok = test_imports()
    app_ok = test_fastapi_app()
    
    if deps_ok and app_ok:
        print("\n✅ All tests passed! Ready for deployment 🚀")
    else:
        print("\n❌ Some tests failed. Fix issues before deployment.") 