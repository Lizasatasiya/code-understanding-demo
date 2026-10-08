/**
 * discountCalculator.ts
 * Utility module for validating and applying e-commerce discounts to orders.
 */

export interface DiscountRule {
    code: string;
    type: 'PERCENT' | 'FIXED';
    value: number;
    minOrderValue: number;
    maxDiscountAmount?: number;
    expiresAt?: string;
}

export interface DiscountCalculationResult {
    isValid: boolean;
    discountAmount: number;
    newTotal: number;
    message: string;
}

/**
 * Validates a discount rule against the current order total.
 */
export function validateDiscount(rule: DiscountRule, orderTotal: number): boolean {
    if (!rule || orderTotal <= 0) {
        return false;
    }
    if (orderTotal < rule.minOrderValue) {
        return false;
    }
    if (rule.expiresAt && new Date(rule.expiresAt).getTime() < Date.now()) {
        return false;
    }
    return true;
}

/**
 * Applies a discount rule to calculate final discounted total.
 */
export function applyDiscount(rule: DiscountRule, orderTotal: number): DiscountCalculationResult {
    if (!validateDiscount(rule, orderTotal)) {
        return {
            isValid: false,
            discountAmount: 0,
            newTotal: orderTotal,
            message: `Discount code '${rule?.code || 'UNKNOWN'}' is not eligible for this order total.`,
        };
    }

    let discount = 0;
    if (rule.type === 'PERCENT') {
        const percentage = Math.min(Math.max(rule.value, 0), 100);
        discount = (orderTotal * percentage) / 100;
    } else {
        discount = Math.min(rule.value, orderTotal);
    }

    if (rule.maxDiscountAmount && rule.maxDiscountAmount > 0) {
        discount = Math.min(discount, rule.maxDiscountAmount);
    }

    const roundedDiscount = parseFloat(discount.toFixed(2));
    const finalTotal = parseFloat(Math.max(0, orderTotal - roundedDiscount).toFixed(2));

    return {
        isValid: true,
        discountAmount: roundedDiscount,
        newTotal: finalTotal,
        message: `Applied discount: -$${roundedDiscount.toFixed(2)}`,
    };
}
