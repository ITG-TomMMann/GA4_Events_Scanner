CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    product VARCHAR(100),
    quantity INT,
    order_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
