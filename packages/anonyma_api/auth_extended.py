"""
Extended Authentication System with User Management and JWT.

Supports:
- User registration and login
- JWT token-based authentication
- Role-based access control (admin, premium, demo)
- Usage quota tracking
- Demo mode with limited requests
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://anonyma:anonyma_secure_password@localhost:5432/anonyma")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class DatabaseManager:
    """Database connection manager"""

    def __init__(self):
        self.connection_string = DATABASE_URL

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)

    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_results: bool = True):
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, params or ())

            result = None
            if fetch_results:
                if fetch_one:
                    result = cur.fetchone()
                else:
                    result = cur.fetchall()

            conn.commit()
            cur.close()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise


db_manager = DatabaseManager()


class AuthManager:
    """Authentication and user management"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user by username and password"""
        query = """
            SELECT id, email, username, password_hash, full_name, role, is_active
            FROM users
            WHERE (username = %s OR email = %s) AND is_active = true
        """
        user = db_manager.execute_query(query, (username, username), fetch_one=True)

        if not user:
            return None

        if not self.verify_password(password, user["password_hash"]):
            return None

        # Update last login
        update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
        db_manager.execute_query(update_query, (user["id"],), fetch_results=False)

        return dict(user)

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "demo"
    ) -> Dict:
        """Create a new user"""
        password_hash = self.get_password_hash(password)

        query = """
            INSERT INTO users (email, username, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, email, username, full_name, role, created_at
        """

        user = db_manager.execute_query(
            query,
            (email, username, password_hash, full_name, role),
            fetch_one=True
        )

        # Initialize usage quota
        quota_query = """
            INSERT INTO usage_quotas (user_id, daily_limit, monthly_limit)
            VALUES (%s, %s, %s)
        """
        daily_limit = 999999 if role == "admin" else (1000 if role == "premium" else 50)
        monthly_limit = 999999 if role == "admin" else (10000 if role == "premium" else 500)
        db_manager.execute_query(quota_query, (user["id"], daily_limit, monthly_limit), fetch_results=False)

        return dict(user)

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        query = """
            SELECT id, email, username, full_name, role, is_active, created_at, last_login
            FROM users
            WHERE id = %s AND is_active = true
        """
        user = db_manager.execute_query(query, (user_id,), fetch_one=True)
        return dict(user) if user else None


class UsageManager:
    """Manage user usage quotas and tracking"""

    @staticmethod
    def check_quota(user_id: str) -> bool:
        """Check if user has available quota"""
        # Reset quotas if needed
        db_manager.execute_query("SELECT reset_daily_quotas()", fetch_results=False)
        db_manager.execute_query("SELECT reset_monthly_quotas()", fetch_results=False)

        query = """
            SELECT daily_used, daily_limit, monthly_used, monthly_limit
            FROM usage_quotas
            WHERE user_id = %s
        """
        quota = db_manager.execute_query(query, (user_id,), fetch_one=True)

        if not quota:
            return False

        # Check both daily and monthly limits
        return (quota["daily_used"] < quota["daily_limit"] and
                quota["monthly_used"] < quota["monthly_limit"])

    @staticmethod
    def increment_usage(user_id: str) -> None:
        """Increment user usage counters"""
        query = """
            UPDATE usage_quotas
            SET daily_used = daily_used + 1,
                monthly_used = monthly_used + 1
            WHERE user_id = %s
        """
        db_manager.execute_query(query, (user_id,), fetch_results=False)

    @staticmethod
    def log_usage(
        user_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        processing_time: float = None,
        text_length: int = None,
        detections_count: int = None,
        mode: str = None
    ) -> None:
        """Log API usage for analytics"""
        query = """
            INSERT INTO usage_logs
            (user_id, endpoint, method, status_code, processing_time, text_length, detections_count, mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db_manager.execute_query(
            query,
            (user_id, endpoint, method, status_code, processing_time, text_length, detections_count, mode),
            fetch_results=False
        )

    @staticmethod
    def get_user_stats(user_id: str) -> Dict:
        """Get user usage statistics"""
        query = """
            SELECT
                uq.daily_used,
                uq.daily_limit,
                uq.monthly_used,
                uq.monthly_limit,
                COUNT(ul.id) as total_requests,
                AVG(ul.processing_time) as avg_processing_time
            FROM usage_quotas uq
            LEFT JOIN usage_logs ul ON uq.user_id = ul.user_id
            WHERE uq.user_id = %s
            GROUP BY uq.user_id, uq.daily_used, uq.daily_limit, uq.monthly_used, uq.monthly_limit
        """
        stats = db_manager.execute_query(query, (user_id,), fetch_one=True)
        return dict(stats) if stats else {}


# Dependency functions
auth_manager = AuthManager()
usage_manager = UsageManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = auth_manager.decode_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = auth_manager.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def check_user_quota(user: Dict = Depends(get_current_user)) -> Dict:
    """Check if user has available quota"""
    if user["role"] == "admin":
        return user  # Admin has unlimited access

    if not usage_manager.check_quota(user["id"]):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Usage quota exceeded. Please upgrade your plan or try again tomorrow."
        )

    # Increment usage
    usage_manager.increment_usage(user["id"])

    return user


async def require_admin(user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role"""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
