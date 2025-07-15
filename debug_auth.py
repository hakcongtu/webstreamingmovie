"""
Debug Authentication Script
"""
import asyncio
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import select

from src.infrastructure.database.database import database
from src.infrastructure.database.models import UserModel
from src.application.services.auth_service import AuthService
from src.infrastructure.repositories.sql_user_repository import SqlUserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def debug_auth():
    """Debug authentication flow"""
    print("🔍 Debugging Authentication Flow...")
    
    # Create auth service
    auth_service = AuthService()
    
    try:
        async with database.session_factory() as session:
            # 1. Check if admin exists
            print("\n1. Checking admin user in database...")
            result = await session.execute(
                select(UserModel).where(UserModel.email == 'admin@movieapi.com')
            )
            admin_model = result.scalar_one_or_none()
            
            if not admin_model:
                print("❌ Admin user not found in database!")
                return
            
            print(f"✅ Admin found: {admin_model.email} ({admin_model.username})")
            print(f"   Active: {admin_model.is_active}")
            print(f"   Superuser: {admin_model.is_superuser}")
            
            # 2. Create repository and convert to domain entity
            print("\n2. Converting to domain entity...")
            repo = SqlUserRepository(session)
            admin_user = repo._to_domain(admin_model)
            print(f"✅ Domain entity created: {admin_user.email}")
            print(f"   Can login: {admin_user.can_login()}")
            
            # 3. Test password verification
            print("\n3. Testing password verification...")
            test_password = "admin123"
            is_valid = auth_service.verify_password(test_password, admin_user.hashed_password)
            print(f"✅ Password verification: {is_valid}")
            
            # 4. Test authentication
            print("\n4. Testing authentication...")
            is_authenticated = auth_service.authenticate_user(admin_user, test_password)
            print(f"✅ Authentication: {is_authenticated}")
            
            # 5. Test token creation
            print("\n5. Testing token creation...")
            access_token, expire_time = auth_service.create_access_token(admin_user)
            print(f"✅ Token created: {access_token[:50]}...")
            print(f"   Expires: {expire_time}")
            
            # 6. Test token verification
            print("\n6. Testing token verification...")
            token_payload = auth_service.verify_token(access_token)
            if token_payload:
                print(f"✅ Token verified: {token_payload.email}")
                print(f"   User ID: {token_payload.sub}")
                print(f"   Superuser: {token_payload.is_superuser}")
            else:
                print("❌ Token verification failed!")
            
            # 7. Test get_current_user flow
            print("\n7. Testing get_current_user flow...")
            user_response = await repo.find_by_id(token_payload.sub)
            if user_response:
                print(f"✅ User found by ID: {user_response.email}")
                print(f"   Can login: {user_response.can_login()}")
            else:
                print("❌ User not found by ID!")
                
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_auth()) 