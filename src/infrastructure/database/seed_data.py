import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.database import AsyncSessionLocal
from src.infrastructure.database.models import UserModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import hashlib

def hash_password(password: str) -> str:
    # Sử dụng SHA256 để băm mật khẩu (chỉ mô phỏng, không dùng cho sản phẩm thực tế)
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

async def seed_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count == 0:
            admin = UserModel(
                id="admin",  # hoặc có thể dùng uuid nếu muốn
                email="admin@movieapi.com",
                username="admin",
                hashed_password=hash_password("admin123"),
                full_name="Admin User",
                is_active=True,
                is_superuser=True
            )
            demo = UserModel(
                id="demo",
                email="demo@movieapi.com",
                username="demo",
                hashed_password=hash_password("demo123"),
                full_name="Demo User",
                is_active=True,
                is_superuser=False
            )
            session.add_all([admin, demo])
            try:
                await session.commit()
                print("Seeded admin and demo users.")
            except IntegrityError:
                await session.rollback()
                print("Integrity error: Users may already exist.")
        else:
            print("Users already exist, skipping seed.")

if __name__ == "__main__":
    asyncio.run(seed_users()) 