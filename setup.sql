CREATE TABLE owner (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL
);

CREATE TABLE vending_machine (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    type VARCHAR(30),
    address VARCHAR(60),
    city VARCHAR(60),
    state CHAR(2),
    zip VARCHAR(10),
    FOREIGN KEY (owner_id) REFERENCES owner(id) ON DELETE CASCADE
);

CREATE TABLE market_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    price DECIMAL(6,2) NOT NULL
);

CREATE TABLE lane (
    vend_id BIGINT NOT NULL,
    lane_number INT NOT NULL,
    filled_slots INT NOT NULL,
    total_slots INT NOT NULL,
    PRIMARY KEY (vend_id, lane_number),
    FOREIGN KEY (vend_id) REFERENCES vending_machine(id) ON DELETE CASCADE
);

CREATE TABLE vending_item (
    vend_id BIGINT NOT NULL,
    item_id BIGINT NOT NULL,
    listed_price DECIMAL(6,2) NOT NULL,
    PRIMARY KEY (vend_id, item_id),
    FOREIGN KEY (vend_id) REFERENCES vending_machine(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES market_item(id) ON DELETE CASCADE
);

CREATE TABLE sale (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vend_id BIGINT NOT NULL,
    lane_number INT NOT NULL,
    item_id BIGINT NOT NULL,
    price_charged DECIMAL(6,2) NOT NULL,
    sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vend_id, lane_number) REFERENCES lane(vend_id, lane_number),
    FOREIGN KEY (vend_id, item_id) REFERENCES vending_item(vend_id, item_id)
);