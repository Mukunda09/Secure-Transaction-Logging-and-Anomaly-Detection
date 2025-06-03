CREATE TABLE transactions (
id SERIAL PRIMARY KEY,
transaction_id VARCHAR(255) UNIQUE NOT NULL,
user_id VARCHAR(50) NOT NULL,
ammount DECIMAL(15, 2) NOT NULL,
Transaction_time TIMESTAMP NOT NULL,
merchant_id VARCHAR(50) NOT NULL,
hash VARCHAR(64) NOT NULL
);
