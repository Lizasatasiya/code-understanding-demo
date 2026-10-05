from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid


class ReturnReason(Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    BUYERS_REMORSE = "buyers_remorse"
    SIZE_FIT = "size_fit"
    ARRIVED_LATE = "arrived_late"


class ReturnStatus(Enum):
    REQUESTED = "requested"
    LABEL_GENERATED = "label_generated"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    REJECTED = "rejected"


class ItemCondition(Enum):
    UNOPENED = "unopened"
    OPENED_LIKE_NEW = "opened_like_new"
    DAMAGED_BY_CUSTOMER = "damaged_by_customer"
    DEFECTIVE_ON_ARRIVAL = "defective_on_arrival"


class RefundChannel(Enum):
    ORIGINAL_PAYMENT = "original_payment"
    STORE_CREDIT = "store_credit"


@dataclass
class ReturnItem:
    item_id: str
    name: str
    price: float
    quantity: int
    reason: ReturnReason
    category: str = "general"
    condition: Optional[ItemCondition] = None


@dataclass
class ReturnRequest:
    rma_id: str
    order_id: str
    customer_id: str
    items: List[ReturnItem]
    status: ReturnStatus = ReturnStatus.REQUESTED
    refund_channel: RefundChannel = RefundChannel.ORIGINAL_PAYMENT
    created_at: datetime = field(default_factory=datetime.utcnow)
    return_shipping_fee: float = 6.99
    restocking_fee: float = 0.0
    final_refund_amount: float = 0.0
    rejection_reason: Optional[str] = None


class ReturnsManager:
    """Oversees product return authorizations, condition inspection, and refund processing."""

    CATEGORY_RETURN_WINDOWS = {
        "electronics": 14,
        "apparel": 30,
        "general": 30,
        "digital": 0,       # Non-returnable
        "perishable": 0     # Non-returnable
    }

    STORE_CREDIT_BONUS_PERCENTAGE = 10.0  # Incentivize keeping capital in store

    def __init__(self):
        self._returns: Dict[str, ReturnRequest] = {}

    def is_eligible_for_return(self, order_date: datetime, category: str) -> bool:
        """Verify if item is within its category-specific return window."""
        allowed_days = self.CATEGORY_RETURN_WINDOWS.get(category, 30)
        if allowed_days <= 0:
            return False
        return (datetime.utcnow() - order_date).days <= allowed_days

    def create_return_request(
        self,
        order_id: str,
        customer_id: str,
        order_date: datetime,
        items: List[ReturnItem],
        preferred_channel: RefundChannel = RefundChannel.ORIGINAL_PAYMENT
    ) -> ReturnRequest:
        if not items:
            raise ValueError("Return request must contain at least one item.")

        for item in items:
            if not self.is_eligible_for_return(order_date, item.category):
                raise ValueError(
                    f"Item '{item.name}' ({item.category}) has exceeded its return window or is non-returnable."
                )

        rma_id = f"RMA-{uuid.uuid4().hex[:8].upper()}"
        req = ReturnRequest(
            rma_id=rma_id,
            order_id=order_id,
            customer_id=customer_id,
            items=items,
            status=ReturnStatus.LABEL_GENERATED,
            refund_channel=preferred_channel
        )
        self._returns[rma_id] = req
        return req

    def inspect_and_assess_fees(
        self,
        rma_id: str,
        inspected_conditions: Dict[str, ItemCondition]
    ) -> ReturnStatus:
        """Inspect items upon warehouse receipt and calculate restocking deductions."""
        req = self._returns.get(rma_id)
        if not req:
            raise KeyError(f"Return request {rma_id} not found.")

        total_restocking_fee = 0.0
        all_rejected = True

        for item in req.items:
            condition = inspected_conditions.get(item.item_id, ItemCondition.OPENED_LIKE_NEW)
            item.condition = condition

            if condition == ItemCondition.DAMAGED_BY_CUSTOMER:
                continue  # Rejected, 0 refund for this item

            all_rejected = False
            item_total = item.price * item.quantity

            if condition == ItemCondition.OPENED_LIKE_NEW:
                # 15% restocking fee for opened box
                total_restocking_fee += round(item_total * 0.15, 2)

        if all_rejected:
            req.status = ReturnStatus.REJECTED
            req.rejection_reason = "All returned items were damaged by customer."
            return req.status

        req.restocking_fee = total_restocking_fee
        req.status = ReturnStatus.INSPECTED
        return req.status

    def calculate_final_refund(self, rma_id: str) -> float:
        """Calculate payable refund after restocking and shipping fees."""
        req = self._returns.get(rma_id)
        if not req or req.status != ReturnStatus.INSPECTED:
            raise ValueError("Return must be inspected before calculating refund.")

        eligible_items_subtotal = sum(
            item.price * item.quantity
            for item in req.items
            if item.condition != ItemCondition.DAMAGED_BY_CUSTOMER
        )

        base_amount = eligible_items_subtotal - req.restocking_fee

        # Deduct return shipping fee unless defective on arrival
        has_defect = any(
            item.condition == ItemCondition.DEFECTIVE_ON_ARRIVAL or item.reason == ReturnReason.DEFECTIVE
            for item in req.items
        )
        shipping_deduction = 0.0 if has_defect else req.return_shipping_fee

        net_refund = max(0.0, base_amount - shipping_deduction)

        if req.refund_channel == RefundChannel.STORE_CREDIT:
            bonus = round(net_refund * (self.STORE_CREDIT_BONUS_PERCENTAGE / 100.0), 2)
            net_refund += bonus

        req.final_refund_amount = round(net_refund, 2)
        return req.final_refund_amount

    def complete_refund(self, rma_id: str) -> Dict[str, any]:
        """Mark RMA refunded and generate audit payload."""
        req = self._returns.get(rma_id)
        if not req:
            raise KeyError(f"Return request {rma_id} not found.")

        req.status = ReturnStatus.REFUNDED
        return {
            "rma_id": req.rma_id,
            "order_id": req.order_id,
            "customer_id": req.customer_id,
            "refund_amount": req.final_refund_amount,
            "channel": req.refund_channel.value,
            "completed_at": datetime.utcnow().isoformat()
        }
