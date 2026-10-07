import React, { useState, useCallback } from 'react';

/**
 * Formats a monetary number to USD currency.
 */
export function formatPrice(price) {
    if (typeof price !== 'number' || isNaN(price) || price < 0) {
        return '$0.00';
    }
    return `$${price.toFixed(2)}`;
}

/**
 * ProductCard Component
 * Displays product details with interactive quantity selection and add-to-cart action.
 */
export function ProductCard({
    product = { id: 'p-1', name: 'Standard Product', price: 0, stock: 0, rating: 5 },
    onAddToCart = () => { }
}) {
    const [quantity, setQuantity] = useState(1);
    const [isAdded, setIsAdded] = useState(false);

    const handleIncrement = useCallback(() => {
        setQuantity((prev) => (prev < product.stock ? prev + 1 : prev));
    }, [product.stock]);

    const handleDecrement = useCallback(() => {
        setQuantity((prev) => (prev > 1 ? prev - 1 : 1));
    }, []);

    const handleAdd = useCallback(() => {
        if (product.stock <= 0) return;
        onAddToCart({
            productId: product.id,
            quantity,
            unitPrice: product.price,
            totalPrice: product.price * quantity
        });
        setIsAdded(true);
        setTimeout(() => setIsAdded(false), 2000);
    }, [product, quantity, onAddToCart]);

    const isOutOfStock = (product.stock || 0) <= 0;

    return (
        <div className="product-card" data-product-id={product.id}>
            <div className="product-info">
                <h3 className="product-title">{product.name}</h3>
                <p className="product-price">{formatPrice(product.price)}</p>
                <span className={`stock-status ${isOutOfStock ? 'out-of-stock' : 'in-stock'}`}>
                    {isOutOfStock ? 'Out of Stock' : `${product.stock} in stock`}
                </span>
            </div>

            <div className="quantity-controls">
                <button
                    type="button"
                    onClick={handleDecrement}
                    disabled={quantity <= 1 || isOutOfStock}
                    aria-label="Decrease quantity"
                >
                    -
                </button>
                <span className="quantity-display">{quantity}</span>
                <button
                    type="button"
                    onClick={handleIncrement}
                    disabled={quantity >= product.stock || isOutOfStock}
                    aria-label="Increase quantity"
                >
                    +
                </button>
            </div>

            <button
                type="button"
                className="add-to-cart-button"
                onClick={handleAdd}
                disabled={isOutOfStock}
            >
                {isAdded ? 'Added to Cart ✓' : 'Add to Cart'}
            </button>
        </div>
    );
}
