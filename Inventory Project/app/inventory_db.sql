-- -------------------------------------------------------------------
-- PROJECT INVENTORY SYSTEM
-- DATABASE INIT SCRIPT
-- -------------------------------------------------------------------

-- 1. CLEAN RESET
DROP DATABASE IF EXISTS inventory_db;
CREATE DATABASE inventory_db;
USE inventory_db;

-- -------------------------------------------------------------------
-- 2. TABLE DEFINITIONS
-- -------------------------------------------------------------------

-- Users (Login system)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','cashier') NOT NULL
);

-- Categories
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Suppliers
CREATE TABLE suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(255)
);

-- Products
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category_id INT,
    supplier_id INT,
    price DECIMAL(10,2) NOT NULL,
    quantity INT DEFAULT 0,
    
    -- VARIABLE LOW STOCK ALERT
    -- Backend can set this to specific numbers (e.g., 5 for Laptops, 50 for Soda)
    alert_quantity INT DEFAULT 5,  

    image_path VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Transactions (Stock History: IN/OUT)
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,      
    
    -- Added product_name to preserve history if product is deleted
    product_name VARCHAR(100),    
    
    type ENUM('IN','OUT') NOT NULL,
    quantity INT NOT NULL,
    user_id INT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
    -- NOTE: No Foreign Key to products(id) to allow product deletion
);

-- Sales (Invoices)
CREATE TABLE sales (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cashier_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cashier_id) REFERENCES users(id)
);

-- Sale Items (Details of what was sold)
CREATE TABLE sale_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,       
    
    -- Added product_name to preserve receipt history if product is deleted
    product_name VARCHAR(100) NOT NULL, 
    
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id)
    -- NOTE: No Foreign Key to products(id) to allow product deletion
);

-- -------------------------------------------------------------------
-- 3. ESSENTIAL DATA (Defaults)
-- -------------------------------------------------------------------

INSERT INTO categories (name) VALUES ('General');
INSERT INTO suppliers (name, contact_info) VALUES ('Default Supplier','N/A');

-- Default Admin User (Password: admin123) - Change hash as needed
INSERT INTO users (username, password, role) 
VALUES ('admin', SHA2('admin123', 256), 'admin');

-- -------------------------------------------------------------------
-- 4. TRIGGERS (Automation)
-- -------------------------------------------------------------------

DELIMITER //

-- Trigger: Decrease Stock when a Sale is made
CREATE TRIGGER after_sale_item_insert
AFTER INSERT ON sale_items
FOR EACH ROW
BEGIN
    -- Check if product exists before updating to prevent errors on deleted items
    IF EXISTS (SELECT 1 FROM products WHERE id = NEW.product_id) THEN
        UPDATE products
        SET quantity = quantity - NEW.quantity
        WHERE id = NEW.product_id;
    END IF;
END;
//

-- Trigger: Update Stock when a Transaction (Restock/Damaged) is recorded
CREATE TRIGGER after_transaction_insert
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM products WHERE id = NEW.product_id) THEN
        IF NEW.type = 'IN' THEN
            UPDATE products
            SET quantity = quantity + NEW.quantity
            WHERE id = NEW.product_id;
        ELSEIF NEW.type = 'OUT' THEN
            UPDATE products
            SET quantity = quantity - NEW.quantity
            WHERE id = NEW.product_id;
        END IF;
    END IF;
END;
//

DELIMITER ;