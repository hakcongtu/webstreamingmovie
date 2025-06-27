"""
Setup Database and Create Admin User
"""
import asyncio
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import select

from src.infrastructure.database.database import database
from src.infrastructure.database.models import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup_database():
    """Setup database and create admin user"""
    print("Setting up database...")
    
    # Create tables
    await database.create_tables()
    print("Database tables created successfully!")
    
    # Create admin user
    await create_admin_user()
    
    # List all users
    await list_users()
    
    await database.close()

async def create_admin_user():
    """Create admin user if not exists"""
    print("\nCreating admin user...")
    
    try:
        async with database.session_factory() as session:
            # Check if admin exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == 'admin@movieapi.com')
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print(f"✅ Admin user already exists:")
                print(f"   Email: {existing_admin.email}")
                print(f"   Username: {existing_admin.username}")
                print(f"   Password: admin123")
                return
            
            # Create admin user
            admin_model = UserModel(
                id="admin-001",
                email="admin@movieapi.com",
                username="admin",
                hashed_password=pwd_context.hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(admin_model)
            await session.commit()
            print("✅ Admin user created successfully!")
            print("   Email: admin@movieapi.com")
            print("   Username: admin")
            print("   Password: admin123")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")

async def list_users():
    """List all users in database"""
    print("\n📋 All users in database:")
    try:
        async with database.session_factory() as session:
            result = await session.execute(select(UserModel))
            users = result.scalars().all()
            
            if not users:
                print("   No users found in database")
                return
            
            for user in users:
                status = "🟢 Active" if user.is_active else "🔴 Inactive"
                role = "👑 Admin" if user.is_superuser else "👤 User"
                print(f"   {user.email} ({user.username}) - {status} - {role}")
                
    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")

if __name__ == "__main__":
    asyncio.run(setup_database()) 