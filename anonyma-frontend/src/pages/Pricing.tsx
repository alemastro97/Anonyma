import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface SubscriptionStatus {
  has_subscription: boolean;
  status: string | null;
  stripe_subscription_id?: string;
  created_at?: string;
}

const Pricing: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/payments/subscription-status`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSubscriptionStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch subscription status:', err);
    }
  };

  const handleUpgradeToPremium = async () => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/payments/create-checkout-session`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            success_url: `${window.location.origin}/pricing?success=true`,
            cancel_url: `${window.location.origin}/pricing?cancelled=true`,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const data = await response.json();

      // Redirect to Stripe Checkout
      window.location.href = data.url;
    } catch (err: any) {
      setError(err.message || 'Failed to start checkout');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription? You will be downgraded to Demo.')) {
      return;
    }

    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/payments/cancel-subscription`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to cancel subscription');
      }

      alert('Subscription cancelled successfully');
      window.location.reload();
    } catch (err: any) {
      setError(err.message || 'Failed to cancel subscription');
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      name: 'Demo',
      role: 'demo',
      price: '$0',
      period: 'forever',
      features: [
        '50 requests per day',
        '500 requests per month',
        'All anonymization modes',
        'All document formats',
        'Basic support',
      ],
      limitations: [
        'Limited daily usage',
        'Quota resets daily',
      ],
      current: user?.role === 'demo',
      actionButton: null,
    },
    {
      name: 'Premium',
      role: 'premium',
      price: '$29',
      period: 'per month',
      features: [
        '1,000 requests per day',
        '10,000 requests per month',
        'All anonymization modes',
        'All document formats',
        'Priority support',
        'API access',
        'Advanced analytics',
      ],
      limitations: [],
      current: user?.role === 'premium',
      recommended: true,
      actionButton: 'upgrade',
    },
    {
      name: 'Admin',
      role: 'admin',
      price: 'Custom',
      period: '',
      features: [
        'Unlimited requests',
        'All Premium features',
        'User management',
        'Advanced analytics',
        'Dedicated support',
        'Custom integrations',
      ],
      limitations: [],
      current: user?.role === 'admin',
      actionButton: null,
      customNote: 'Contact us for admin access',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900">Choose Your Plan</h2>
        <p className="mt-4 text-lg text-gray-600">
          Select the plan that best fits your needs
        </p>
      </div>

      {/* Success/Error Messages */}
      {new URLSearchParams(window.location.search).get('success') && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          Payment successful! Your account has been upgraded to Premium.
        </div>
      )}

      {new URLSearchParams(window.location.search).get('cancelled') && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-md">
          Payment cancelled. You can upgrade anytime.
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Current Status */}
      {user && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">Current Plan</p>
              <p className="text-2xl font-bold text-blue-700 mt-1">
                {user.role === 'admin' && '👑 Admin'}
                {user.role === 'premium' && '⭐ Premium'}
                {user.role === 'demo' && '🎯 Demo'}
              </p>
            </div>
            {subscriptionStatus?.has_subscription && subscriptionStatus.status === 'active' && (
              <button
                onClick={handleCancelSubscription}
                disabled={loading}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
              >
                Cancel Subscription
              </button>
            )}
          </div>
        </div>
      )}

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
        {plans.map((plan) => (
          <div
            key={plan.role}
            className={`relative bg-white rounded-lg shadow-sm border-2 p-8 ${
              plan.recommended
                ? 'border-blue-500'
                : plan.current
                ? 'border-green-500'
                : 'border-gray-200'
            }`}
          >
            {/* Recommended Badge */}
            {plan.recommended && (
              <div className="absolute top-0 right-0 -mt-4 -mr-4">
                <span className="inline-flex items-center px-4 py-1 rounded-full text-sm font-medium bg-blue-600 text-white">
                  Recommended
                </span>
              </div>
            )}

            {/* Current Plan Badge */}
            {plan.current && (
              <div className="absolute top-0 right-0 -mt-4 -mr-4">
                <span className="inline-flex items-center px-4 py-1 rounded-full text-sm font-medium bg-green-600 text-white">
                  Current Plan
                </span>
              </div>
            )}

            {/* Plan Header */}
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
              <div className="mt-4">
                <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                {plan.period && <span className="text-gray-600 ml-2">{plan.period}</span>}
              </div>
            </div>

            {/* Features */}
            <ul className="mt-8 space-y-4">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-start">
                  <svg
                    className="flex-shrink-0 h-6 w-6 text-green-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span className="ml-3 text-gray-700">{feature}</span>
                </li>
              ))}
            </ul>

            {/* Limitations */}
            {plan.limitations.length > 0 && (
              <ul className="mt-4 space-y-2">
                {plan.limitations.map((limitation, index) => (
                  <li key={index} className="flex items-start text-sm text-gray-500">
                    <span className="mr-2">⚠️</span>
                    <span>{limitation}</span>
                  </li>
                ))}
              </ul>
            )}

            {/* Action Button */}
            <div className="mt-8">
              {plan.actionButton === 'upgrade' && !plan.current && user?.role !== 'admin' && (
                <button
                  onClick={handleUpgradeToPremium}
                  disabled={loading}
                  className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Upgrade to Premium'}
                </button>
              )}

              {plan.current && (
                <button
                  disabled
                  className="w-full py-3 px-4 bg-green-100 text-green-800 font-medium rounded-md cursor-default"
                >
                  Current Plan
                </button>
              )}

              {plan.customNote && (
                <p className="text-center text-sm text-gray-500">{plan.customNote}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* FAQ */}
      <div className="mt-16 border-t border-gray-200 pt-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h3>
        <div className="space-y-6">
          <div>
            <h4 className="font-semibold text-gray-900">Can I change my plan anytime?</h4>
            <p className="mt-2 text-gray-600">
              Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">What happens when I reach my quota?</h4>
            <p className="mt-2 text-gray-600">
              Your quota resets daily and monthly. If you exceed your limit, you'll need to wait for the reset or upgrade your plan.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">How does billing work?</h4>
            <p className="mt-2 text-gray-600">
              Premium subscriptions are billed monthly via Stripe. You can cancel anytime with no long-term commitment.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">What payment methods do you accept?</h4>
            <p className="mt-2 text-gray-600">
              We accept all major credit cards via Stripe's secure payment processing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
