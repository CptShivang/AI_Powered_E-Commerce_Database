-- Create database
CREATE DATABASE IF NOT EXISTS ai_ecommerce;
USE ai_ecommerce;

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    stock_quantity INT NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    thumb_url VARCHAR(255)
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('customer', 'retailer')
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Product reviews table
CREATE TABLE IF NOT EXISTS product_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    user_id INT,
    rating INT NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample data (15 products)
INSERT INTO products (name, description, price, category, stock_quantity, image_url) VALUES
('Smartphone X', 'Latest smartphone with AI camera', 799.99, 'Electronics', 50, 'https://example.com/phone.jpg'),
('Wireless Earbuds', 'Noise cancelling wireless earbuds', 129.99, 'Electronics', 100, 'https://example.com/earbuds.jpg'),
('Smart Watch', 'Fitness tracking and notifications', 199.99, 'Electronics', 30, 'https://example.com/watch.jpg'),
('Laptop Pro', 'High performance laptop for professionals', 1299.99, 'Electronics', 20, 'https://example.com/laptop.jpg'),
('Bluetooth Speaker', 'Portable speaker with 20h battery', 79.99, 'Electronics', 75, 'https://example.com/speaker.jpg'),
('Coffee Maker', 'Automatic coffee maker with timer', 59.99, 'Home', 40, 'https://example.com/coffee.jpg'),
('Air Fryer', 'Healthy cooking with little oil', 89.99, 'Home', 35, 'https://example.com/airfryer.jpg'),
('Yoga Mat', 'Non-slip premium yoga mat', 29.99, 'Sports', 60, 'https://example.com/yogamat.jpg'),
('Running Shoes', 'Lightweight running shoes', 89.99, 'Sports', 45, 'https://example.com/shoes.jpg'),
('Backpack', 'Waterproof backpack with USB port', 49.99, 'Fashion', 55, 'https://example.com/backpack.jpg'),
('Desk Lamp', 'Adjustable LED desk lamp', 39.99, 'Home', 25, 'https://example.com/lamp.jpg'),
('Novel - The Alchemist', 'Bestselling novel by Paulo Coelho', 12.99, 'Books', 80, 'https://example.com/alchemist.jpg'),
('External SSD', '1TB portable SSD storage', 129.99, 'Electronics', 30, 'https://example.com/ssd.jpg'),
('Water Bottle', 'Insulated stainless steel bottle', 24.99, 'Home', 70, 'https://example.com/bottle.jpg'),
('Wireless Charger', 'Fast charging pad for smartphones', 34.99, 'Electronics', 90, 'https://example.com/charger.jpg');

-- Insert sample users
INSERT INTO users (username, email, password) VALUES
('john_doe', 'john@example.com', 'hashed_password_123'),
('jane_smith', 'jane@example.com', 'hashed_password_456');

-- Insert sample orders
INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 929.98, 'Completed'),
(2, 219.98, 'Processing');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 799.99),
(1, 5, 1, 129.99),
(2, 3, 1, 199.99),
(2, 9, 1, 19.99);

-- Insert sample reviews
INSERT INTO product_reviews (product_id, user_id, rating, comment) VALUES
(1, 1, 5, 'Excellent phone with great camera!'),
(3, 2, 4, 'Good watch but battery could be better');

show tables;
