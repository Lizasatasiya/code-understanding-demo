from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid


class BillingCycle(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class SubscriptionPlan:
    plan_id: str
    name: str
    price: float
    billing_cycle: BillingCycle
    discount_percentage: float = 0.0
    trial_days: int = 0
    features: List[str] = field(default_factory=list)

    def calculate_period_price(self) -> float:
        """Calculate base price minus plan-level recurring discount."""
        discount = self.price * (self.discount_percentage / 100.0)
        return round(self.price - discount, 2)


@dataclass
class Subscription:
    subscription_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    payment_method: str
    retry_count: int = 0
    cancellation_reason: Optional[str] = None
    paused_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_in_grace_period(self, max_days: int = 7) -> bool:
        """Check if past-due subscription is within dunning grace period."""
        if self.status != SubscriptionStatus.PAST_DUE:
            return False
        grace_deadline = self.current_period_end + timedelta(days=max_days)
        return datetime.utcnow() <= grace_deadline


class SubscriptionManager:
    """Manages recurring billing cycles, dunning retries, and plan migrations."""

    MAX_PAYMENT_RETRIES = 3
    DUNNING_GRACE_DAYS = 7

    def __init__(self):
        self._plans: Dict[str, SubscriptionPlan] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        self._seed_default_plans()

    def _seed_default_plans(self):
        self._plans = {
            "coffee_monthly": SubscriptionPlan(
                plan_id="coffee_monthly",
                name="Artisan Coffee Roasters Club",
                price=24.99,
                billing_cycle=BillingCycle.MONTHLY,
                discount_percentage=10.0,
                features=["2x 12oz whole bean bags", "Free priority delivery"]
            ),
            "snack_weekly": SubscriptionPlan(
                plan_id="snack_weekly",
                name="Healthy Snack Fuel Box",
                price=14.50,
                billing_cycle=BillingCycle.WEEKLY,
                discount_percentage=5.0,
                trial_days=7,
                features=["5 curated organic snacks"]
            ),
            "vip_annual": SubscriptionPlan(
                plan_id="vip_annual",
                name="Storewide VIP Pass",
                price=99.00,
                billing_cycle=BillingCycle.ANNUAL,
                discount_percentage=20.0,
                features=["Unlimited 2-day shipping", "Early access to drops"]
            ),
        }

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method: str = "credit_card"
    ) -> Subscription:
        if plan_id not in self._plans:
            raise ValueError(f"Plan '{plan_id}' does not exist.")

        plan = self._plans[plan_id]
        now = datetime.utcnow()

        if plan.trial_days > 0:
            start_date = now
            end_date = now + timedelta(days=plan.trial_days)
        else:
            start_date = now
            end_date = self._calculate_next_billing_date(start_date, plan.billing_cycle)

        sub_id = f"sub_{uuid.uuid4().hex[:10]}"
        subscription = Subscription(
            subscription_id=sub_id,
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=start_date,
            current_period_end=end_date,
            payment_method=payment_method
        )
        self._subscriptions[sub_id] = subscription
        return subscription

    def _calculate_next_billing_date(self, from_date: datetime, cycle: BillingCycle) -> datetime:
        if cycle == BillingCycle.WEEKLY:
            return from_date + timedelta(days=7)
        elif cycle == BillingCycle.MONTHLY:
            return from_date + timedelta(days=30)
        elif cycle == BillingCycle.QUARTERLY:
            return from_date + timedelta(days=90)
        elif cycle == BillingCycle.ANNUAL:
            return from_date + timedelta(days=365)
        return from_date + timedelta(days=30)

    def process_renewal(self, subscription_id: str, payment_successful: bool) -> bool:
        """Handle recurring renewal attempt."""
        sub = self._subscriptions.get(subscription_id)
        if not sub:
            raise KeyError(f"Subscription {subscription_id} not found.")

        if sub.status not in (SubscriptionStatus.ACTIVE, SubscriptionStatus.PAST_DUE):
            return False

        if payment_successful:
            plan = self._plans[sub.plan_id]
            sub.current_period_start = sub.current_period_end
            sub.current_period_end = self._calculate_next_billing_date(
                sub.current_period_start, plan.billing_cycle
            )
            sub.status = SubscriptionStatus.ACTIVE
            sub.retry_count = 0
            return True
        else:
            sub.retry_count += 1
            if sub.retry_count >= self.MAX_PAYMENT_RETRIES:
                sub.status = SubscriptionStatus.CANCELLED
                sub.cancellation_reason = "Max payment retries exceeded (dunning failed)"
            else:
                sub.status = SubscriptionStatus.PAST_DUE
            return False

    def pause_subscription(self, subscription_id: str, pause_days: int = 30) -> Subscription:
        sub = self._subscriptions.get(subscription_id)
        if not sub or sub.status != SubscriptionStatus.ACTIVE:
            raise ValueError("Only active subscriptions can be paused.")

        sub.status = SubscriptionStatus.PAUSED
        sub.paused_until = datetime.utcnow() + timedelta(days=pause_days)
        return sub

    def resume_subscription(self, subscription_id: str) -> Subscription:
        sub = self._subscriptions.get(subscription_id)
        if not sub or sub.status != SubscriptionStatus.PAUSED:
            raise ValueError("Only paused subscriptions can be resumed.")

        sub.status = SubscriptionStatus.ACTIVE
        sub.paused_until = None
        return sub

    def calculate_proration_credit(self, subscription_id: str, new_plan_id: str) -> float:
        """Compute prorated balance when switching plans mid-cycle."""
        sub = self._subscriptions.get(subscription_id)
        if not sub or sub.plan_id not in self._plans or new_plan_id not in self._plans:
            raise ValueError("Invalid subscription or target plan.")

        old_plan = self._plans[sub.plan_id]
        total_period_seconds = (sub.current_period_end - sub.current_period_start).total_seconds()
        remaining_seconds = max(0.0, (sub.current_period_end - datetime.utcnow()).total_seconds())

        if total_period_seconds <= 0:
            return 0.0

        fraction_remaining = remaining_seconds / total_period_seconds
        unused_credit = round(old_plan.calculate_period_price() * fraction_remaining, 2)
        return unused_credit
