from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """Tracks the lifecycle of an order through the system."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Supported payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    WALLET = "wallet"
    COD = "cash_on_delivery"


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

    def is_international(self) -> bool:
        """Check if this is an international address (non-US)."""
        return self.country != "US"

    def format_full(self) -> str:
        """Return a formatted single-line address string."""
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"


@dataclass
class Customer:
    id: str
    name: str
    email: str
    address: Optional[Address] = None
    is_premium: bool = False
    loyalty_points: int = 0
    payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD

    def earn_points(self, amount: float) -> int:
        """Calculate loyalty points earned. Premium members earn 2x."""
        multiplier = 2 if self.is_premium else 1
        points = int(amount * multiplier)
        self.loyalty_points += points
        return points

    def redeem_points(self, points: int) -> float:
        """Redeem loyalty points for a discount. 100 points = $1."""
        if points > self.loyalty_points:
            raise ValueError(f"Insufficient points. Have {self.loyalty_points}, requested {points}")
        self.loyalty_points -= points
        return points / 100.0


@dataclass
class CartItem:
    id: str
    name: str
    price: float
    quantity: int = 1
    weight_kg: float = 0.5
    is_digital: bool = False
    category: str = "general"

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    def is_heavy(self) -> bool:
        """Items over 10kg total weight incur surcharges."""
        return (self.weight_kg * self.quantity) > 10.0


@dataclass
class Discount:
    code: str
    percentage: float
    max_amount: Optional[float] = None
    min_order_value: float = 0.0
    valid_categories: Optional[List[str]] = None
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if this discount code has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def is_applicable(self, subtotal: float, categories: List[str] = None) -> bool:
        """Check if this discount can be applied to the current order."""
        if self.is_expired():
            return False
        if subtotal < self.min_order_value:
            return False
        if self.valid_categories and categories:
            if not any(c in self.valid_categories for c in categories):
                return False
        return True

    def calculate_discount(self, subtotal: float) -> float:
        """Calculate the actual discount amount, respecting max_amount cap."""
        raw_discount = subtotal * self.percentage
        if self.max_amount is not None:
            return min(raw_discount, self.max_amount)
        return raw_discount


@dataclass
class OrderItem:
    """Snapshot of a CartItem at the time of purchase (price is locked in)."""
    item_id: str
    name: str
    unit_price: float
    quantity: int
    line_total: float
    category: str = "general"


@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    subtotal: float
    discount_amount: float
    shipping_cost: float
    tax: float
    total: float
    status: OrderStatus
    payment_method: PaymentMethod
    shipping_address: Optional[Address] = None
    loyalty_points_earned: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def can_cancel(self) -> bool:
        """Orders can only be cancelled before they are shipped."""
        return self.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PROCESSING)

    def can_refund(self) -> bool:
        """Orders can be refunded after delivery or if cancelled."""
        return self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)

    def transition_to(self, new_status: OrderStatus) -> None:
        """Transition the order to a new status with validation."""
        valid_transitions: Dict[OrderStatus, List[OrderStatus]] = {
            OrderStatus.PENDING:    [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED:  [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED:    [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED:  [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED:  [OrderStatus.REFUNDED],
            OrderStatus.REFUNDED:   [],
        }
        allowed = valid_transitions.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from {self.status.value} to {new_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()


@dataclass
class ShippingRate:
    region: str
    base_rate: float
    per_kg_rate: float
    free_shipping_threshold: float = 100.0
    heavy_item_surcharge: float = 15.0

    def calculate_for_weight(self, weight_kg: float, has_heavy_items: bool = False) -> float:
        """Calculate shipping cost for a given weight."""
        cost = self.base_rate + (weight_kg * self.per_kg_rate)
        if has_heavy_items:
            cost += self.heavy_item_surcharge
        return round(cost, 2)
