/**
 * orderValidator.ts
 * Validation utility functions for e-commerce checkout pipeline.
 * Ensures shipping address integrity, postal code formatting, and payment boundaries.
 */

export interface ShippingAddress {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export interface PaymentDetails {
  cardNumber: string;
  expiryMonth: number;
  expiryYear: number;
  cvv: string;
}

/**
 * Validates required shipping address fields and postal code formatting.
 */
export function validateShippingAddress(address: ShippingAddress): ValidationResult {
  const errors: Record<string, string> = {};

  if (!address || typeof address !== 'object') {
    return {
      isValid: false,
      errors: { address: 'Address information is required.' }
    };
  }

  if (!address.line1 || !address.line1.trim()) {
    errors.line1 = 'Street address line 1 is required.';
  }

  if (!address.city || !address.city.trim()) {
    errors.city = 'City is required.';
  }

  if (!address.state || !address.state.trim()) {
    errors.state = 'State or province is required.';
  }

  if (!address.country || !address.country.trim()) {
    errors.country = 'Country is required.';
  }

  const postalCode = (address.postalCode || '').trim();
  const postalCodeRegex = /^[A-Za-z0-9\s-]{3,10}$/;
  if (!postalCode) {
    errors.postalCode = 'Postal code is required.';
  } else if (!postalCodeRegex.test(postalCode)) {
    errors.postalCode = 'Invalid postal code format.';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}

/**
 * Validates credit card payment details and expiry dates.
 */
export function validatePaymentDetails(payment: PaymentDetails): ValidationResult {
  const errors: Record<string, string> = {};

  if (!payment || typeof payment !== 'object') {
    return {
      isValid: false,
      errors: { payment: 'Payment details are required.' }
    };
  }

  const sanitizedCard = (payment.cardNumber || '').replace(/\s+/g, '');
  if (!/^\d{15,16}$/.test(sanitizedCard)) {
    errors.cardNumber = 'Card number must be 15 or 16 digits.';
  }

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;

  if (
    typeof payment.expiryMonth !== 'number' ||
    payment.expiryMonth < 1 ||
    payment.expiryMonth > 12
  ) {
    errors.expiryMonth = 'Expiry month must be between 1 and 12.';
  }

  if (
    typeof payment.expiryYear !== 'number' ||
    payment.expiryYear < currentYear ||
    (payment.expiryYear === currentYear && payment.expiryMonth < currentMonth)
  ) {
    errors.expiryYear = 'Card has expired.';
  }

  const cvv = (payment.cvv || '').trim();
  if (!/^\d{3,4}$/.test(cvv)) {
    errors.cvv = 'CVV must be 3 or 4 digits.';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
