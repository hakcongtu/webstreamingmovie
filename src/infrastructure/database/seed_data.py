import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.database import AsyncSessionLocal
from src.infrastructure.database.models import User

async def seed_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT COUNT(*) FROM users")
        count = result.scalar()
        if count == 0:
            admin = User(email="admin@movieapi.com", username="admin", password_hash="admin123", role="admin")
            demo = User(email="demo@movieapi.com", username="demo", password_hash="demo123", role="user")
            session.add_all([admin, demo])
            await session.commit()
            print("Seeded admin and demo users.")
        else:
            print("Users already exist, skipping seed.")

if __name__ == "__main__":
    asyncio.run(seed_users()) 