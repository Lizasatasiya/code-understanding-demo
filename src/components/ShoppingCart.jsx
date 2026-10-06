import React, { useState, useEffect, useMemo, useCallback } from 'react';

/**
 * Utility helper to format numbers as USD currency strings.
 */
export function formatCurrency(amount) {
  const numeric = typeof amount === 'number' ? amount : parseFloat(amount) || 0;
  return `$${numeric.toFixed(2)}`;
}

/**
 * Calculates line-item subtotal across all cart items.
 */
export function calculateSubtotal(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return 0;
  }
  return items.reduce((accumulator, item) => {
    const price = typeof item.price === 'number' ? item.price : 0;
    const qty = typeof item.quantity === 'number' ? item.quantity : 1;
    return accumulator + price * qty;
  }, 0);
}

/**
 * Evaluates promotional discount rules and percentage reductions.
 */
export function calculateDiscount(subtotal, promoCode) {
  if (!promoCode || subtotal <= 0) {
    return 0;
  }
  const normalized = promoCode.trim().toUpperCase();
  switch (normalized) {
    case 'SUMMER20':
      return subtotal * 0.20;
    case 'WELCOME10':
      return subtotal * 0.10;
    case 'VIP50':
      return Math.min(50, subtotal * 0.25);
    case 'FREESHIP':
      return 0;
    default:
      return 0;
  }
}

/**
 * Calculates delivery fees based on selected method and order value.
 */
export function calculateShipping(shippingMethod, subtotal) {
  if (subtotal >= 150 && shippingMethod === 'standard') {
    return 0;
  }
  switch (shippingMethod) {
    case 'express':
      return 14.99;
    case 'overnight':
      return 29.99;
    case 'standard':
    default:
      return 5.99;
  }
}

/**
 * Calculates tax on taxable balance after promotional discounts.
 */
export function calculateTax(taxableAmount, rate = 0.08) {
  if (taxableAmount <= 0) {
    return 0;
  }
  return taxableAmount * rate;
}

/**
 * Aggregates all pricing dimensions into final payable total.
 */
export function calculateGrandTotal(subtotal, discount, shipping, tax) {
  const rawTotal = subtotal - discount + shipping + tax;
  return Math.max(0, Math.round(rawTotal * 100) / 100);
}

/**
 * Validates promotional codes against active marketing campaigns.
 */
export function validateCouponCode(code) {
  if (!code) {
    return { valid: false, message: 'Please enter a promo code.' };
  }
  const cleanCode = code.trim().toUpperCase();
  const validCodes = ['SUMMER20', 'WELCOME10', 'VIP50', 'FREESHIP'];
  if (validCodes.includes(cleanCode)) {
    return { valid: true, code: cleanCode, message: 'Coupon applied successfully!' };
  }
  return { valid: false, message: 'Invalid or expired coupon code.' };
}

/**
 * Primary ShoppingCart Component
 *
 * Interacts with e-commerce cart inventory, pricing engine,
 * promo rules, and checkout lifecycle.
 */
export default function ShoppingCart({
  initialItems = [
    { id: 'prod-101', name: 'Ergonomic Mechanical Keyboard', price: 129.99, quantity: 1, stock: 12 },
    { id: 'prod-102', name: 'Noise-Canceling Wireless Headphones', price: 249.50, quantity: 1, stock: 8 },
    { id: 'prod-103', name: 'Braided USB-C Fast Charging Cable', price: 19.99, quantity: 2, stock: 25 },
  ],
  taxRate = 0.08,
  onCheckoutComplete = null,
}) {
  const [items, setItems] = useState(initialItems);
  const [promoInput, setPromoInput] = useState('');
  const [appliedPromo, setAppliedPromo] = useState(null);
  const [promoFeedback, setPromoFeedback] = useState(null);
  const [shippingMethod, setShippingMethod] = useState('standard');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [checkoutNotification, setCheckoutNotification] = useState(null);

  const subtotal = useMemo(() => calculateSubtotal(items), [items]);
  const discount = useMemo(() => calculateDiscount(subtotal, appliedPromo), [subtotal, appliedPromo]);
  const shipping = useMemo(() => calculateShipping(shippingMethod, subtotal), [shippingMethod, subtotal]);
  const tax = useMemo(() => calculateTax(subtotal - discount, taxRate), [subtotal, discount, taxRate]);
  const total = useMemo(() => calculateGrandTotal(subtotal, discount, shipping, tax), [subtotal, discount, shipping, tax]);

  const handleQuantityChange = (itemId, delta) => {
    setItems((previousItems) =>
      previousItems
        .map((item) => {
          if (item.id === itemId) {
            const updatedQty = item.quantity + delta;
            if (updatedQty <= 0) {
              return null;
            }
            if (updatedQty > item.stock) {
              alert(`Maximum stock available for ${item.name} is ${item.stock}.`);
              return item;
            }
            return { ...item, quantity: updatedQty };
          }
          return item;
        })
        .filter(Boolean)
    );
  };

  const handleRemoveItem = (itemId) => {
    setItems((previousItems) => previousItems.filter((item) => item.id !== itemId));
  };

  const handleClearCart = () => {
    setItems([]);
    setAppliedPromo(null);
    setPromoInput('');
    setPromoFeedback(null);
  };

  const handleApplyPromo = (event) => {
    event.preventDefault();
    const result = validateCouponCode(promoInput);
    if (result.valid) {
      setAppliedPromo(result.code);
      setPromoFeedback({ success: true, message: result.message });
    } else {
      setAppliedPromo(null);
      setPromoFeedback({ success: false, message: result.message });
    }
  };

  const handleShippingChange = (event) => {
    setShippingMethod(event.target.value);
  };

  const handleCheckoutSubmit = async (event) => {
    if (event && event.preventDefault) {
      event.preventDefault();
    }
    if (items.length === 0) {
      setCheckoutNotification({ error: true, text: 'Cart is empty. Add items before checking out.' });
      return;
    }

    setIsSubmitting(true);
    setCheckoutNotification(null);

    try {
      const orderSummary = {
        orderId: `ORD-${Date.now()}`,
        items,
        pricing: { subtotal, discount, shipping, tax, total },
        shippingMethod,
        appliedPromo,
      };

      // Simulating backend checkout service call
      await new Promise((resolve) => setTimeout(resolve, 600));

      setCheckoutNotification({
        error: false,
        text: `Order ${orderSummary.orderId} processed successfully!`,
      });

      if (typeof onCheckoutComplete === 'function') {
        onCheckoutComplete(orderSummary);
      }
    } catch (err) {
      setCheckoutNotification({
        error: true,
        text: 'Failed to process checkout. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="cart-container" style={{ maxWidth: '900px', margin: '32px auto', fontFamily: 'sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', margin: 0 }}>Shopping Cart ({items.length} items)</h1>
        {items.length > 0 && (
          <button
            type="button"
            onClick={handleClearCart}
            style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer' }}
          >
            Clear Cart
          </button>
        )}
      </header>

      {items.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '48px 16px', background: '#f9fafb', borderRadius: '8px' }}>
          <p style={{ fontSize: '18px', color: '#6b7280' }}>Your cart is empty.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
          <div>
            {items.map((item) => (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '16px 0',
                  borderBottom: '1px solid #e5e7eb',
                }}
              >
                <div>
                  <h3 style={{ margin: '0 0 6px 0', fontSize: '16px' }}>{item.name}</h3>
                  <div style={{ color: '#6b7280', fontSize: '14px' }}>
                    {formatCurrency(item.price)} each • {item.stock} in stock
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', border: '1px solid #d1d5db', borderRadius: '4px' }}>
                    <button
                      type="button"
                      onClick={() => handleQuantityChange(item.id, -1)}
                      style={{ padding: '4px 8px', border: 'none', background: 'transparent', cursor: 'pointer' }}
                    >
                      -
                    </button>
                    <span style={{ padding: '0 8px', fontWeight: 'bold' }}>{item.quantity}</span>
                    <button
                      type="button"
                      onClick={() => handleQuantityChange(item.id, 1)}
                      disabled={item.quantity >= item.stock}
                      style={{ padding: '4px 8px', border: 'none', background: 'transparent', cursor: 'pointer' }}
                    >
                      +
                    </button>
                  </div>

                  <span style={{ minWidth: '70px', textAlign: 'right', fontWeight: 'bold' }}>
                    {formatCurrency(item.price * item.quantity)}
                  </span>

                  <button
                    type="button"
                    onClick={() => handleRemoveItem(item.id)}
                    style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: '16px' }}
                    aria-label={`Remove ${item.name}`}
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>

          <aside style={{ background: '#f9fafb', padding: '24px', borderRadius: '8px', alignSelf: 'start' }}>
            <h2 style={{ fontSize: '18px', marginTop: 0, marginBottom: '16px' }}>Order Summary</h2>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Subtotal</span>
              <span>{formatCurrency(subtotal)}</span>
            </div>

            {discount > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#16a34a' }}>
                <span>Discount ({appliedPromo})</span>
                <span>-{formatCurrency(discount)}</span>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Shipping</span>
              <span>{shipping === 0 ? 'FREE' : formatCurrency(shipping)}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span>Tax (8%)</span>
              <span>{formatCurrency(tax)}</span>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '12px',
                borderTop: '2px solid #e5e7eb',
                fontSize: '18px',
                fontWeight: 'bold',
                marginBottom: '20px',
              }}
            >
              <span>Total</span>
              <span>{formatCurrency(total)}</span>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label htmlFor="shipping-select" style={{ display: 'block', fontSize: '13px', fontWeight: '600', marginBottom: '4px' }}>
                Shipping Speed
              </label>
              <select
                id="shipping-select"
                value={shippingMethod}
                onChange={handleShippingChange}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db' }}
              >
                <option value="standard">Standard (Free over $150 / $5.99)</option>
                <option value="express">Express 2-Day ($14.99)</option>
                <option value="overnight">Overnight Next-Day ($29.99)</option>
              </select>
            </div>

            <form onSubmit={handleApplyPromo} style={{ marginBottom: '16px' }}>
              <label htmlFor="promo-code" style={{ display: 'block', fontSize: '13px', fontWeight: '600', marginBottom: '4px' }}>
                Promo Code
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  id="promo-code"
                  type="text"
                  value={promoInput}
                  onChange={(e) => setPromoInput(e.target.value)}
                  placeholder="e.g. SUMMER20"
                  style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #d1d5db' }}
                />
                <button
                  type="submit"
                  style={{ padding: '8px 14px', background: '#374151', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Apply
                </button>
              </div>
              {promoFeedback && (
                <p style={{ margin: '6px 0 0', fontSize: '12px', color: promoFeedback.success ? '#16a34a' : '#ef4444' }}>
                  {promoFeedback.message}
                </p>
              )}
            </form>

            <button
              type="button"
              onClick={handleCheckoutSubmit}
              disabled={isSubmitting || items.length === 0}
              style={{
                width: '100%',
                padding: '12px',
                background: '#2563eb',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
              }}
            >
              {isSubmitting ? 'Processing...' : `Checkout (${formatCurrency(total)})`}
            </button>

            {checkoutNotification && (
              <div
                style={{
                  marginTop: '12px',
                  padding: '8px 12px',
                  borderRadius: '4px',
                  fontSize: '13px',
                  background: checkoutNotification.error ? '#fee2e2' : '#dcfce7',
                  color: checkoutNotification.error ? '#b91c1c' : '#15803d',
                }}
              >
                {checkoutNotification.text}
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}
