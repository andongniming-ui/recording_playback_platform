-- Rental System Database Setup
-- Uses the shared MySQL at localhost:3307

CREATE DATABASE IF NOT EXISTS rental_db
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

USE rental_db;

-- =============================================
-- Table: rental_user
-- =============================================
CREATE TABLE IF NOT EXISTS rental_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    real_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    id_card VARCHAR(18),
    driver_license VARCHAR(20),
    membership_level VARCHAR(20) DEFAULT 'SILVER',
    balance DECIMAL(12,2) DEFAULT 0.00,
    status TINYINT DEFAULT 1 COMMENT '1=active 0=inactive',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Table: rental_store
-- =============================================
CREATE TABLE IF NOT EXISTS rental_store (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20),
    business_hours VARCHAR(100) DEFAULT '09:00-21:00',
    status TINYINT DEFAULT 1 COMMENT '1=active 0=inactive',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Table: rental_vehicle
-- =============================================
CREATE TABLE IF NOT EXISTS rental_vehicle (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    color VARCHAR(20),
    year INT,
    seats INT DEFAULT 5,
    displacement VARCHAR(20),
    price_per_day DECIMAL(10,2) DEFAULT 300.00,
    store_id BIGINT,
    status TINYINT DEFAULT 1 COMMENT '1=available 2=rented 3=maintenance',
    mileage INT DEFAULT 0,
    insurance_expire DATETIME,
    maintenance_status VARCHAR(30) DEFAULT 'NORMAL',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_store (store_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Table: rental_order
-- =============================================
CREATE TABLE IF NOT EXISTS rental_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    vehicle_id BIGINT NOT NULL,
    store_id BIGINT NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    estimated_fee DECIMAL(10,2) DEFAULT 0.00,
    deposit DECIMAL(10,2) DEFAULT 0.00,
    actual_fee DECIMAL(10,2) DEFAULT 0.00,
    status TINYINT DEFAULT 1 COMMENT '1=active 2=completed 3=cancelled',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Table: rental_payment
-- =============================================
CREATE TABLE IF NOT EXISTS rental_payment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payment_no VARCHAR(32) NOT NULL UNIQUE,
    order_no VARCHAR(32) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    channel VARCHAR(10),
    payment_method VARCHAR(20),
    status TINYINT DEFAULT 1 COMMENT '1=pending 2=success 3=failed 4=refunded',
    pay_time DATETIME,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Table: transaction_log (for serial_no lookup)
-- =============================================
CREATE TABLE IF NOT EXISTS transaction_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    serial_no VARCHAR(18) NOT NULL,
    service_name VARCHAR(50),
    method_name VARCHAR(200),
    request_body MEDIUMTEXT,
    response_body MEDIUMTEXT,
    sub_calls MEDIUMTEXT COMMENT 'JSON array of sub-call records',
    db_calls MEDIUMTEXT COMMENT 'JSON array of DB call records',
    elapsed_ms BIGINT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_serial_no (serial_no),
    INDEX idx_service_method (service_name, method_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- =============================================
-- Seed Data
-- =============================================
-- Reset demo data so this script is safe to run repeatedly during tests.
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transaction_log;
TRUNCATE TABLE rental_payment;
TRUNCATE TABLE rental_order;
TRUNCATE TABLE rental_vehicle;
TRUNCATE TABLE rental_store;
TRUNCATE TABLE rental_user;
SET FOREIGN_KEY_CHECKS = 1;

-- Sample Users
INSERT INTO rental_user (username, password, real_name, phone, email, id_card, driver_license, membership_level, balance) VALUES
('zhangsan', 'pass123', 'Zhang San', '13800001001', 'zhangsan@email.com', '110101199001011234', 'DL20240001', 'GOLD', 5000.00),
('lisi', 'pass123', 'Li Si', '13800001002', 'lisi@email.com', '110101199102021235', 'DL20240002', 'SILVER', 3000.00),
('wangwu', 'pass123', 'Wang Wu', '13800001003', 'wangwu@email.com', '110101199203031236', 'DL20240003', 'PLATINUM', 10000.00),
('zhaoliu', 'pass123', 'Zhao Liu', '13800001004', 'zhaoliu@email.com', '110101199304041237', 'DL20240004', 'SILVER', 2000.00),
('sunqi', 'pass123', 'Sun Qi', '13800001005', 'sunqi@email.com', '110101199405051238', 'DL20240005', 'GOLD', 8000.00);

-- Sample Stores
INSERT INTO rental_store (store_name, address, phone, business_hours) VALUES
('Shanghai Pudong Airport Store', 'Pudong Airport T1, Shanghai', '021-58000001', '06:00-24:00'),
('Shanghai Hongqiao Store', 'Hongqiao Hub, Shanghai', '021-58000002', '07:00-23:00'),
('Beijing Chaoyang Store', 'Chaoyang District, Beijing', '010-68000001', '08:00-22:00'),
('Guangzhou Baiyun Airport Store', 'Baiyun Airport, Guangzhou', '020-38000001', '06:00-24:00'),
('Shenzhen Nanshan Store', 'Nanshan District, Shenzhen', '0755-28000001', '08:00-22:00');

-- Sample Vehicles
INSERT INTO rental_vehicle (plate_number, brand, model, color, year, seats, displacement, price_per_day, store_id, status, mileage, insurance_expire) VALUES
('HU-A00001', 'Toyota', 'Camry', 'Black', 2024, 5, '2.0L', 350.00, 1, 1, 15000, '2027-06-30'),
('HU-A00002', 'Honda', 'Accord', 'White', 2024, 5, '1.5T', 320.00, 1, 1, 12000, '2027-05-15'),
('HU-A00003', 'BMW', '320Li', 'Blue', 2024, 5, '2.0T', 580.00, 2, 1, 8000, '2027-08-20'),
('HU-A00004', 'Audi', 'A4L', 'Silver', 2023, 5, '2.0T', 520.00, 2, 1, 25000, '2026-12-31'),
('HU-A00005', 'Mercedes-Benz', 'C260L', 'Black', 2024, 5, '1.5T', 620.00, 3, 1, 5000, '2027-09-01'),
('HU-A00006', 'Volkswagen', 'Passat', 'Gray', 2023, 5, '2.0T', 280.00, 3, 1, 30000, '2026-11-15'),
('HU-A00007', 'Buick', 'GL8', 'White', 2024, 7, '2.0T', 450.00, 1, 1, 18000, '2027-07-01'),
('HU-A00008', 'Nissan', 'Teana', 'Black', 2023, 5, '2.0L', 260.00, 4, 1, 35000, '2027-04-20'),
('HU-A00009', 'BYD', 'Han EV', 'Red', 2024, 5, 'Electric', 400.00, 4, 1, 10000, '2027-10-01'),
('HU-A00010', 'Tesla', 'Model 3', 'White', 2024, 5, 'Electric', 420.00, 5, 1, 8000, '2027-11-30'),
('HU-A00011', 'Cadillac', 'CT5', 'Blue', 2024, 5, '2.0T', 480.00, 5, 1, 6000, '2027-06-15'),
('HU-A00012', 'Lexus', 'ES200', 'Silver', 2024, 5, '2.0L', 550.00, 2, 1, 9000, '2027-08-01');
