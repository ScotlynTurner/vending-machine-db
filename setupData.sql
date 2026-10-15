INSERT INTO owner (name) VALUES
('Apex Vending Services'),
('Metro Snack Co.'),
('University Refreshments');

-- Note: zip codes are passed as strings to maintain leading zeros
INSERT INTO vending_machine (owner_id, type, address, city, state, zip) VALUES
(1, 'freezer', '100 Main St', 'Austin', 'TX', '78701'),
(1, 'cooler', '450 University Ave', 'Austin', 'TX', '78705'),
(2, 'cooler', '88 Market St', 'San Francisco', 'CA', '94103'),
(2, 'room temp', '83 Market St', 'San Francisco', 'CA', '94103'),
(3, 'freezer', '1200 Campus Dr', 'Boston', 'MA', '02115');

INSERT INTO market_item (name, price) VALUES
('Coca-Cola 20oz', 2.00),
('Pepsi 20oz', 2.00),
('Lays Potato Chips', 1.50),
('Doritos Nacho Cheese', 1.75),
('Snickers Bar', 1.50),
('Bottled Water', 1.25),
('Monster Energy', 3.50);

-- Fill lanes
INSERT INTO lane (vend_id, lane_number, filled_slots, total_slots) VALUES
(1, 101, 8, 10),
(1, 102, 10, 10),
(1, 103, 5, 10),
(1, 104, 2, 10);

INSERT INTO lane (vend_id, lane_number, filled_slots, total_slots) VALUES
(2, 1, 12, 15),
(2, 2, 15, 15),
(2, 3, 4, 15);

INSERT INTO lane (vend_id, lane_number, filled_slots, total_slots) VALUES
(3, 10, 6, 8),
(3, 11, 7, 8);

INSERT INTO lane (vend_id, lane_number, filled_slots, total_slots) VALUES
(4, 201, 0, 10),
(4, 202, 0, 10),
(4, 203, 0, 10),
(4, 204, 0, 10);

-- Set items
INSERT INTO vending_item (vend_id, item_id, listed_price) VALUES
(1, 1, 2.50), -- Soda marked up to $2.50
(1, 3, 1.75), -- Chips marked up to $1.75
(1, 5, 1.50); -- Snickers at standard price

-- Machine 2 stock
INSERT INTO vending_item (vend_id, item_id, listed_price) VALUES
(2, 1, 2.25),
(2, 2, 2.25),
(2, 6, 1.50);

-- Machine 3 stock
INSERT INTO vending_item (vend_id, item_id, listed_price) VALUES
(3, 3, 2.00),
(3, 4, 2.00);

-- Machine 3 stock
INSERT INTO vending_item (vend_id, item_id, listed_price) VALUES
(4, 3, 2.00),
(4, 4, 2.00);

INSERT INTO sale (vend_id, lane_number, item_id, price_charged, sold_at) VALUES
-- Transactions for Machine 1
(1, 101, 1, 2.50, '2026-10-10 08:30:00'),
(1, 101, 1, 2.50, '2026-10-10 09:15:00'),
(1, 103, 3, 1.75, '2026-10-10 11:45:00'),
(1, 104, 5, 1.50, '2026-10-11 14:20:00'),

-- Transactions for Machine 2
(2, 1, 1, 2.25, '2026-10-11 10:05:00'),
(2, 3, 6, 1.50, '2026-10-12 12:00:00'),

-- Transactions for Machine 3
(3, 10, 3, 2.00, '2026-10-12 13:10:00');