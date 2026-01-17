"""
Stripe Payment Router

Handles Stripe payment integration for premium subscriptions.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
import os
import stripe

router = APIRouter()

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
STRIPE_PRICE_ID_PREMIUM = os.getenv('STRIPE_PRICE_ID_PREMIUM')  # Premium subscription price ID

# Import auth dependencies
try:
    import asyncpg
    from ..auth_extended import get_current_user
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class CheckoutSession(BaseModel):
    success_url: str
    cancel_url: str


async def get_db_pool():
    """Get database connection pool."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise HTTPException(status_code=500, detail="Database not configured")

    return await asyncpg.create_pool(database_url)


@router.post("/payments/create-checkout-session")
async def create_checkout_session(
    session_data: CheckoutSession,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session for premium subscription.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    if not STRIPE_PRICE_ID_PREMIUM:
        raise HTTPException(status_code=500, detail="Premium price not configured")

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user['email'],
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRICE_ID_PREMIUM,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=session_data.success_url,
            cancel_url=session_data.cancel_url,
            metadata={
                'user_id': current_user['id'],
                'username': current_user['username'],
            }
        )

        return {
            'sessionId': checkout_session.id,
            'url': checkout_session.url
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        await handle_subscription_updated(subscription)

    return {'status': 'success'}


async def handle_successful_payment(session: Dict[str, Any]):
    """
    Handle successful payment - upgrade user to premium.
    """
    user_id = session['metadata'].get('user_id')
    if not user_id:
        return

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Upgrade user to premium
            await conn.execute(
                "UPDATE users SET role = 'premium' WHERE id = $1",
                user_id
            )

            # Update quota limits
            premium_daily = int(os.getenv('PREMIUM_DAILY_LIMIT', 1000))
            premium_monthly = int(os.getenv('PREMIUM_MONTHLY_LIMIT', 10000))

            await conn.execute("""
                UPDATE usage_quotas
                SET daily_limit = $1, monthly_limit = $2
                WHERE user_id = $3
            """, premium_daily, premium_monthly, user_id)

            # Store subscription info
            await conn.execute("""
                INSERT INTO subscriptions (user_id, stripe_subscription_id, status, created_at)
                VALUES ($1, $2, 'active', NOW())
                ON CONFLICT (user_id) DO UPDATE
                SET stripe_subscription_id = $2, status = 'active', updated_at = NOW()
            """, user_id, session.get('subscription'))

    finally:
        await pool.close()


async def handle_subscription_cancelled(subscription: Dict[str, Any]):
    """
    Handle subscription cancellation - downgrade user to demo.
    """
    customer_id = subscription['customer']

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Find user by Stripe customer ID
            user = await conn.fetchrow("""
                SELECT user_id FROM subscriptions
                WHERE stripe_subscription_id = $1
            """, subscription['id'])

            if not user:
                return

            user_id = user['user_id']

            # Downgrade to demo
            await conn.execute(
                "UPDATE users SET role = 'demo' WHERE id = $1",
                user_id
            )

            # Update quota limits
            demo_daily = int(os.getenv('DEMO_DAILY_LIMIT', 50))
            demo_monthly = int(os.getenv('DEMO_MONTHLY_LIMIT', 500))

            await conn.execute("""
                UPDATE usage_quotas
                SET daily_limit = $1, monthly_limit = $2
                WHERE user_id = $3
            """, demo_daily, demo_monthly, user_id)

            # Update subscription status
            await conn.execute("""
                UPDATE subscriptions
                SET status = 'cancelled', updated_at = NOW()
                WHERE user_id = $1
            """, user_id)

    finally:
        await pool.close()


async def handle_subscription_updated(subscription: Dict[str, Any]):
    """
    Handle subscription updates (renewal, etc.).
    """
    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE subscriptions
                SET status = $1, updated_at = NOW()
                WHERE stripe_subscription_id = $2
            """, subscription['status'], subscription['id'])

    finally:
        await pool.close()


@router.get("/payments/subscription-status")
async def get_subscription_status(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get current user's subscription status.
    """
    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            subscription = await conn.fetchrow("""
                SELECT stripe_subscription_id, status, created_at, updated_at
                FROM subscriptions
                WHERE user_id = $1
            """, current_user['id'])

            if not subscription:
                return {
                    'has_subscription': False,
                    'status': None
                }

            return {
                'has_subscription': True,
                'status': subscription['status'],
                'stripe_subscription_id': subscription['stripe_subscription_id'],
                'created_at': subscription['created_at'].isoformat() if subscription['created_at'] else None,
                'updated_at': subscription['updated_at'].isoformat() if subscription['updated_at'] else None,
            }

    finally:
        await pool.close()


@router.post("/payments/cancel-subscription")
async def cancel_subscription(
    current_user: Dict = Depends(get_current_user)
):
    """
    Cancel current user's subscription.
    """
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    if not HAS_POSTGRES:
        raise HTTPException(status_code=503, detail="Database not available")

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            subscription = await conn.fetchrow("""
                SELECT stripe_subscription_id
                FROM subscriptions
                WHERE user_id = $1 AND status = 'active'
            """, current_user['id'])

            if not subscription:
                raise HTTPException(status_code=404, detail="No active subscription found")

            # Cancel in Stripe
            try:
                stripe.Subscription.delete(subscription['stripe_subscription_id'])
            except stripe.error.StripeError as e:
                raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

            return {'message': 'Subscription cancelled successfully'}

    finally:
        await pool.close()
