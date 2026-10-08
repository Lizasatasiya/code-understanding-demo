-- =============================================================================
-- Migration: 0003_add_cart_and_discount_tables.sql
-- Description: Introduces persistent cart storage and a discount_codes table
--              to support the useCart hook backend and promotional pricing.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Table: carts
-- Persists an active shopping cart session per user.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carts (
    cart_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMPTZ GENERATED ALWAYS AS (created_at + INTERVAL '7 days') STORED
);

CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);

-- ---------------------------------------------------------------------------
-- Table: cart_items
-- Line-item entries linked to a cart.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
    item_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id     UUID NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id  VARCHAR(64) NOT NULL,
    unit_price  NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    quantity    INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (cart_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);

-- ---------------------------------------------------------------------------
-- Table: discount_codes
-- Promotional codes that can be applied to a cart at checkout.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS discount_codes (
    code            VARCHAR(32) PRIMARY KEY,
    discount_type   VARCHAR(16) NOT NULL CHECK (discount_type IN ('percent', 'fixed')),
    discount_value  NUMERIC(10, 2) NOT NULL CHECK (discount_value > 0),
    min_order_value NUMERIC(10, 2) NOT NULL DEFAULT 0,
    max_uses        INTEGER,
    uses_so_far     INTEGER NOT NULL DEFAULT 0,
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until     TIMESTAMPTZ,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------------
-- Trigger: auto-update carts.updated_at on cart_items change
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_cart_timestamp()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE carts SET updated_at = NOW() WHERE cart_id = NEW.cart_id;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_cart_items_update_cart ON cart_items;
CREATE TRIGGER trg_cart_items_update_cart
    AFTER INSERT OR UPDATE OR DELETE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_cart_timestamp();

COMMIT;
