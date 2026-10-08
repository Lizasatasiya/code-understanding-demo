import React, { useMemo } from 'react';

/**
 * CheckoutSummary Component
 * Displays order items, applied shipping rate, and computed order grand total.
 */
export function CheckoutSummary({ items = [], shippingCost = 0, discountAmount = 0 }) {
  const subtotal = useMemo(() => {
    return items.reduce((acc, item) => acc + (item.unitPrice || 0) * (item.quantity || 1), 0);
  }, [items]);

  const tax = useMemo(() => {
    const taxableAmount = Math.max(0, subtotal - discountAmount);
    return Math.round(taxableAmount * 0.08 * 100) / 100;
  }, [subtotal, discountAmount]);

  const grandTotal = useMemo(() => {
    return Math.max(0, subtotal - discountAmount) + shippingCost + tax;
  }, [subtotal, discountAmount, shippingCost, tax]);

  if (!items || items.length === 0) {
    return (
      <div className="checkout-summary empty-summary">
        <p>No items in checkout order.</p>
      </div>
    );
  }

  return (
    <div className="checkout-summary-card">
      <h3 className="summary-title">Order Summary</h3>

      <div className="summary-items-list">
        {items.map((item) => (
          <div key={item.productId || item.name} className="summary-item-row">
            <span className="item-name">
              {item.name} × {item.quantity || 1}
            </span>
            <span className="item-total">
              ${(((item.unitPrice || 0) * (item.quantity || 1))).toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      <hr className="summary-divider" />

      <div className="summary-line">
        <span>Subtotal</span>
        <span>${subtotal.toFixed(2)}</span>
      </div>

      {discountAmount > 0 && (
        <div className="summary-line discount-line">
          <span>Discount</span>
          <span>-${discountAmount.toFixed(2)}</span>
        </div>
      )}

      <div className="summary-line">
        <span>Estimated Tax (8%)</span>
        <span>${tax.toFixed(2)}</span>
      </div>

      <div className="summary-line">
        <span>Shipping</span>
        <span>{shippingCost === 0 ? 'Free' : `$${shippingCost.toFixed(2)}`}</span>
      </div>

      <div className="summary-line total-line">
        <strong>Total</strong>
        <strong>${grandTotal.toFixed(2)}</strong>
      </div>
    </div>
  );
}

export default CheckoutSummary;
