"""
Admin API Router

Admin-only endpoints for user management and system monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import os

router = APIRouter()

# Import database and auth dependencies
try:
    import asyncpg
    from ..auth_extended import get_current_user, require_admin
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class RoleUpdate(BaseModel):
    role: str


class ActiveUpdate(BaseModel):
    is_active: bool


async def get_db_pool():
    """Get database connection pool."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")

    return await asyncpg.create_pool(database_url)


@router.get("/admin/users")
async def get_all_users(
    current_user: Dict = Depends(require_admin)
):
    """
    Get all users with their quota information.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Get users with their quotas
            query = """
                SELECT
                    u.id, u.email, u.username, u.role, u.is_active, u.created_at,
                    uq.daily_used, uq.daily_limit, uq.monthly_used, uq.monthly_limit,
                    uq.last_reset_daily, uq.last_reset_monthly
                FROM users u
                LEFT JOIN usage_quotas uq ON u.id = uq.user_id
                ORDER BY u.created_at DESC
            """
            rows = await conn.fetch(query)

            users = []
            for row in rows:
                user_data = {
                    "id": str(row['id']),
                    "email": row['email'],
                    "username": row['username'],
                    "role": row['role'],
                    "is_active": row['is_active'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                }

                # Add quota if exists
                if row['daily_used'] is not None:
                    user_data["quota"] = {
                        "user_id": str(row['id']),
                        "daily_used": row['daily_used'],
                        "daily_limit": row['daily_limit'],
                        "monthly_used": row['monthly_used'],
                        "monthly_limit": row['monthly_limit'],
                        "last_reset_daily": row['last_reset_daily'].isoformat() if row['last_reset_daily'] else None,
                        "last_reset_monthly": row['last_reset_monthly'].isoformat() if row['last_reset_monthly'] else None,
                    }

                users.append(user_data)

            return users
    finally:
        await pool.close()


@router.get("/admin/stats")
async def get_system_stats(
    current_user: Dict = Depends(require_admin)
):
    """
    Get system statistics.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Total users
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")

            # Active users
            active_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active = true")

            # Users by role
            roles = await conn.fetch("SELECT role, COUNT(*) as count FROM users GROUP BY role")
            users_by_role = {row['role']: row['count'] for row in roles}

            # Requests today
            total_requests_today = await conn.fetchval("""
                SELECT COUNT(*) FROM usage_logs
                WHERE timestamp >= CURRENT_DATE
            """) or 0

            # Requests this month
            total_requests_month = await conn.fetchval("""
                SELECT COUNT(*) FROM usage_logs
                WHERE timestamp >= DATE_TRUNC('month', CURRENT_DATE)
            """) or 0

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_requests_today": total_requests_today,
                "total_requests_month": total_requests_month,
                "users_by_role": {
                    "admin": users_by_role.get('admin', 0),
                    "premium": users_by_role.get('premium', 0),
                    "demo": users_by_role.get('demo', 0),
                }
            }
    finally:
        await pool.close()


@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: RoleUpdate,
    current_user: Dict = Depends(require_admin)
):
    """
    Update user role.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    if role_update.role not in ['admin', 'premium', 'demo']:
        raise HTTPException(status_code=400, detail="Invalid role")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Update user role
            await conn.execute(
                "UPDATE users SET role = $1 WHERE id = $2",
                role_update.role, user_id
            )

            # Update quota limits based on role
            if role_update.role == 'admin':
                daily_limit = 999999
                monthly_limit = 999999
            elif role_update.role == 'premium':
                daily_limit = int(os.getenv('PREMIUM_DAILY_LIMIT', 1000))
                monthly_limit = int(os.getenv('PREMIUM_MONTHLY_LIMIT', 10000))
            else:  # demo
                daily_limit = int(os.getenv('DEMO_DAILY_LIMIT', 50))
                monthly_limit = int(os.getenv('DEMO_MONTHLY_LIMIT', 500))

            await conn.execute("""
                UPDATE usage_quotas
                SET daily_limit = $1, monthly_limit = $2
                WHERE user_id = $3
            """, daily_limit, monthly_limit, user_id)

            return {"message": "Role updated successfully", "new_role": role_update.role}
    finally:
        await pool.close()


@router.post("/admin/users/{user_id}/reset-quota")
async def reset_user_quota(
    user_id: str,
    current_user: Dict = Depends(require_admin)
):
    """
    Reset user's daily and monthly quota.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE usage_quotas
                SET daily_used = 0,
                    monthly_used = 0,
                    last_reset_daily = NOW(),
                    last_reset_monthly = NOW()
                WHERE user_id = $1
            """, user_id)

            return {"message": "Quota reset successfully"}
    finally:
        await pool.close()


@router.put("/admin/users/{user_id}/active")
async def update_user_active_status(
    user_id: str,
    active_update: ActiveUpdate,
    current_user: Dict = Depends(require_admin)
):
    """
    Activate or deactivate user.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_active = $1 WHERE id = $2",
                active_update.is_active, user_id
            )

            status = "activated" if active_update.is_active else "deactivated"
            return {"message": f"User {status} successfully"}
    finally:
        await pool.close()


@router.get("/admin/usage-logs")
async def get_usage_logs(
    limit: int = 100,
    offset: int = 0,
    current_user: Dict = Depends(require_admin)
):
    """
    Get recent usage logs.
    Admin only.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            query = """
                SELECT
                    ul.id, ul.user_id, ul.endpoint, ul.method,
                    ul.status_code, ul.response_time_ms, ul.timestamp,
                    u.username, u.role
                FROM usage_logs ul
                JOIN users u ON ul.user_id = u.id
                ORDER BY ul.timestamp DESC
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset)

            logs = []
            for row in rows:
                logs.append({
                    "id": str(row['id']),
                    "user_id": str(row['user_id']),
                    "username": row['username'],
                    "role": row['role'],
                    "endpoint": row['endpoint'],
                    "method": row['method'],
                    "status_code": row['status_code'],
                    "response_time_ms": row['response_time_ms'],
                    "timestamp": row['timestamp'].isoformat() if row['timestamp'] else None,
                })

            # Get total count
            total = await conn.fetchval("SELECT COUNT(*) FROM usage_logs")

            return {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    finally:
        await pool.close()
