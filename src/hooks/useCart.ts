/**
 * useCart.ts
 * Custom React hook that manages shopping-cart state with TypeScript strict types.
 * Provides add, remove, update-quantity, and clear operations with derived totals.
 */

export interface CartItem {
    productId: string;
    name: string;
    unitPrice: number;
    quantity: number;
}

export interface CartSummary {
    itemCount: number;
    subtotal: number;
    tax: number;
    total: number;
}

export interface UseCartReturn {
    items: CartItem[];
    summary: CartSummary;
    addItem: (item: Omit<CartItem, 'quantity'> & { quantity?: number }) => void;
    removeItem: (productId: string) => void;
    updateQuantity: (productId: string, quantity: number) => void;
    clearCart: () => void;
    hasItem: (productId: string) => boolean;
}

const TAX_RATE = 0.08; // 8 %

function computeSummary(items: CartItem[]): CartSummary {
    const itemCount = items.reduce((acc, i) => acc + i.quantity, 0);
    const subtotal = items.reduce((acc, i) => acc + i.unitPrice * i.quantity, 0);
    const tax = parseFloat((subtotal * TAX_RATE).toFixed(2));
    const total = parseFloat((subtotal + tax).toFixed(2));
    return { itemCount, subtotal, tax, total };
}

// ---------------------------------------------------------------------------
// Hook implementation (plain function — attach to React.useState in consumer)
// ---------------------------------------------------------------------------

/**
 * useCart — manages a list of CartItem entries.
 *
 * Usage:
 *   import { useState } from 'react';
 *   import { createCartActions } from './hooks/useCart';
 *
 *   const [items, setItems] = useState<CartItem[]>([]);
 *   const cart = createCartActions(items, setItems);
 */
export function createCartActions(
    items: CartItem[],
    setItems: React.Dispatch<React.SetStateAction<CartItem[]>>
): UseCartReturn {
    const summary = computeSummary(items);

    function addItem(incoming: Omit<CartItem, 'quantity'> & { quantity?: number }): void {
        const qty = incoming.quantity ?? 1;
        setItems((prev) => {
            const existing = prev.find((i) => i.productId === incoming.productId);
            if (existing) {
                return prev.map((i) =>
                    i.productId === incoming.productId
                        ? { ...i, quantity: i.quantity + qty }
                        : i
                );
            }
            return [...prev, { ...incoming, quantity: qty }];
        });
    }

    function removeItem(productId: string): void {
        setItems((prev) => prev.filter((i) => i.productId !== productId));
    }

    function updateQuantity(productId: string, quantity: number): void {
        if (quantity <= 0) {
            removeItem(productId);
            return;
        }
        setItems((prev) =>
            prev.map((i) => (i.productId === productId ? { ...i, quantity } : i))
        );
    }

    function clearCart(): void {
        setItems([]);
    }

    function hasItem(productId: string): boolean {
        return items.some((i) => i.productId === productId);
    }

    return { items, summary, addItem, removeItem, updateQuantity, clearCart, hasItem };
}
