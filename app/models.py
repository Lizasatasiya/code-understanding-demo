from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

@dataclass
class Customer:
    id: str
    name: str
    email: str
    address: Optional[Address] = None
    is_premium: bool = False

@dataclass
class CartItem:
    id: str
    name: str
    price: float
    quantity: int = 1
    weight_kg: float = 0.5
    is_digital: bool = False

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

@dataclass
class Discount:
    code: str
    percentage: float
    max_amount: Optional[float] = None

@dataclass
class Order:
    id: str
    customer_id: str
    items: List[CartItem]
    subtotal: float
    shipping_cost: float
    tax: float
    total: float
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ShippingRate:
    region: str
    base_rate: float
    per_kg_rate: float
    free_shipping_threshold: float = 100.0

