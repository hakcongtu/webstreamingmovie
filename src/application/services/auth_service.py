"""
Authentication Service - Application Layer
Handles password hashing, JWT token generation and validation
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext

from domain.entities.user import User
from application.dtos.auth_schemas import TokenPayloadDto


class AuthService:
    """
    Authentication Service - Application Layer
    Handles authentication operations
    """
    
    def __init__(
        self,
        secret_key: str = "your-secret-key-change-in-production",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a plain password"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: User) -> tuple[str, datetime]:
        """Create JWT access token for user"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, expire

    def verify_token(self, token: str) -> Optional[TokenPayloadDto]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                return None
            
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            # Create token payload DTO
            token_payload = TokenPayloadDto(
                sub=payload.get("sub"),
                email=payload.get("email"),
                username=payload.get("username"),
                is_superuser=payload.get("is_superuser", False),
                exp=exp,
                iat=payload.get("iat")
            )
            
            return token_payload
            
        except JWTError:
            return None

    def generate_user_id(self) -> str:
        """Generate unique user ID"""
        return str(uuid.uuid4())

    def create_user_from_registration(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str
    ) -> User:
        """Create user entity from registration data"""
        user_id = self.generate_user_id()
        hashed_password = self.hash_password(password)
        
        return User(
            id=user_id,
            email=email.lower().strip(),
            username=username.strip(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def authenticate_user(self, user: User, password: str) -> bool:
        """Authenticate user with password"""
        if not user:
            return False
        
        if not user.can_login():
            return False
        
        return self.verify_password(password, user.hashed_password)

    def is_email_or_username(self, identifier: str) -> str:
        """Determine if identifier is email or username"""
        if "@" in identifier:
            return "email"
        return "username"

    def get_token_expire_time(self) -> int:
        """Get token expiration time in seconds"""
        return self.access_token_expire_minutes * 60

    def create_refresh_token(self, user: User) -> tuple[str, datetime]:
        """Create refresh token (longer expiration)"""
        expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
        
        payload = {
            "sub": user.id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, expire

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """Verify refresh token and return user ID"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                return None
            
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
            
            # Check if it's a refresh token
            if payload.get("type") != "refresh":
                return None
            
            return payload.get("sub")
            
        except JWTError:
            return None

    def validate_password_strength(self, password: str) -> tuple[bool, list[str]]:
        """Validate password strength and return errors if any"""
        errors = []
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        if len(password) > 100:
            errors.append("Password cannot exceed 100 characters")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        return len(errors) == 0, errors 