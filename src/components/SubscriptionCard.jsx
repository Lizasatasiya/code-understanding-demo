import React, { useState, useEffect, useMemo, useCallback } from 'react';

// Formats a currency amount into standard USD notation with defensive validation.
export function formatPlanPrice(amount, billingCycle = 'monthly') {
  if (typeof amount !== 'number' || isNaN(amount) || amount < 0) {
    return '$0.00';
  }
  const suffix = billingCycle === 'annual' ? '/yr' : '/mo';
  return `$${amount.toFixed(2)}${suffix}`;
}

// Computes discounted pricing for an annual commitment without mutating inputs.
export function calculateAnnualDiscount(monthlyPrice, discountRate = 0.15) {
  if (typeof monthlyPrice !== 'number' || monthlyPrice <= 0) {
    return { annualTotal: 0, savings: 0 };
  }
  const standardAnnual = monthlyPrice * 12;
  const discounted = standardAnnual * (1 - discountRate);
  return {
    annualTotal: Math.round(discounted * 100) / 100,
    savings: Math.round((standardAnnual - discounted) * 100) / 100,
  };
}

// Maps subscription tier status to label and styling class with defensive fallback.
export function getStatusBadgeInfo(status) {
  switch (status) {
    case 'active':
      return { label: 'Active', className: 'badge-active' };
    case 'past_due':
      return { label: 'Past Due', className: 'badge-warning' };
    case 'paused':
      return { label: 'Paused', className: 'badge-secondary' };
    case 'cancelled':
      return { label: 'Cancelled', className: 'badge-danger' };
    default:
      return { label: 'Inactive', className: 'badge-default' };
  }
}

/**
 * SubscriptionCard Component with full software engineering standards:
 * Immutable state, lifecycle cleanup, memoization without stale closures, and resilience.
 */
export function SubscriptionCard({
  plan = {
    id: 'pro-team',
    name: 'Professional Team',
    monthlyPrice: 29.99,
    description: 'Scalable infrastructure and automated compliance workflows.',
    features: [
      'Unlimited repository hooks',
      'Automated code comprehension audits',
      'Dedicated developer support',
      'SOC2 Type II certified reports',
    ],
    isPopular: true,
  },
  currentStatus = 'active',
  onSubscribe,
}) {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [activeMembers, setActiveMembers] = useState(12);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Clean lifecycle effect: interval with proper timer teardown cleanup
  useEffect(() => {
    const timerId = setInterval(() => {
      setActiveMembers((prevCount) => prevCount + 1);
    }, 30000);

    return () => {
      clearInterval(timerId);
    };
  }, []);

  // Derived calculation: pure memoization without side-effects
  const pricingSummary = useMemo(() => {
    if (billingCycle === 'annual') {
      return calculateAnnualDiscount(plan.monthlyPrice);
    }
    return { annualTotal: plan.monthlyPrice * 12, savings: 0 };
  }, [plan.monthlyPrice, billingCycle]);

  // Formatted price string for current view
  const displayPrice = useMemo(() => {
    if (billingCycle === 'annual') {
      return formatPlanPrice(pricingSummary.annualTotal / 12, 'monthly');
    }
    return formatPlanPrice(plan.monthlyPrice, 'monthly');
  }, [plan.monthlyPrice, pricingSummary.annualTotal, billingCycle]);

  const badgeInfo = useMemo(() => {
    return getStatusBadgeInfo(currentStatus);
  }, [currentStatus]);

  // Exhaustive dependencies: avoids stale closures
  const handlePlanSelection = useCallback(async () => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      if (onSubscribe) {
        await onSubscribe(plan.id, billingCycle);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Subscription checkout failed';
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  }, [plan.id, billingCycle, onSubscribe]);

  // Defensive input validation guardrail
  if (!plan || typeof plan !== 'object') {
    return null;
  }

  return (
    <div className={`subscription-card ${plan.isPopular ? 'popular-card' : ''}`}>
      <div className="card-header">
        <h3 className="plan-title">{plan.name}</h3>
        <span className={`status-badge ${badgeInfo.className}`}>
          {badgeInfo.label}
        </span>
      </div>

      <p className="plan-description">{plan.description}</p>

      <div className="billing-toggle" role="group" aria-label="Billing frequency">
        <button
          type="button"
          className={billingCycle === 'monthly' ? 'btn-active' : 'btn-inactive'}
          onClick={() => setBillingCycle('monthly')}
        >
          Monthly
        </button>
        <button
          type="button"
          className={billingCycle === 'annual' ? 'btn-active' : 'btn-inactive'}
          onClick={() => setBillingCycle('annual')}
        >
          Annual (Save 15%)
        </button>
      </div>

      <div className="pricing-section">
        <div className="price-tag">{displayPrice}</div>
        {billingCycle === 'annual' && pricingSummary.savings > 0 && (
          <span className="savings-badge">
            Billed annually: ${pricingSummary.annualTotal.toFixed(2)}/yr
          </span>
        )}
        <div className="active-counter">
          Active team members: {activeMembers}
        </div>
      </div>

      <ul className="features-list">
        {plan.features.map((feature) => (
          <li key={feature} className="feature-item">
            <span aria-hidden="true">✓</span> {feature}
          </li>
        ))}
      </ul>

      {errorMessage && (
        <div className="error-banner" role="alert">
          {errorMessage}
        </div>
      )}

      <div className="card-actions">
        <button
          type="button"
          disabled={isSubmitting}
          className="submit-button"
          onClick={handlePlanSelection}
        >
          {isSubmitting ? 'Processing...' : 'Select Plan'}
        </button>
      </div>
    </div>
  );
}

export default SubscriptionCard;
