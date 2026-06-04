-- ========================================
-- 电商系统数据库初始化脚本
-- ========================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ecommerce
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ecommerce;

-- ----------------------------
-- 用户表（用于 auth_service）
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,   -- 明文存储，仅用于练习
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入测试用户
INSERT INTO users (username, password) VALUES
    ('admin', 'admin123'),
    ('test', 'test123')
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- ----------------------------
-- 商品表（用于 product_service）
-- ----------------------------
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    price       DECIMAL(10, 2) NOT NULL,
    stock       INT DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入测试商品数据
INSERT INTO products (name, price, stock) VALUES
    ('笔记本电脑', 5999.00, 10),
    ('无线鼠标', 99.00, 50),
    ('机械键盘', 299.00, 30),
    ('显示器', 1499.00, 15),
    ('耳机', 199.00, 25)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- ----------------------------
-- 订单表（用于 order_service）
-- ----------------------------
CREATE TABLE IF NOT EXISTS orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    product_id  INT NOT NULL,
    quantity    INT NOT NULL DEFAULT 1,
    total_price DECIMAL(10, 2) NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入测试订单数据
INSERT INTO orders (user_id, product_id, quantity, total_price, status) VALUES
    (1, 1, 1, 5999.00, 'completed'),
    (1, 2, 2, 198.00,  'pending'),
    (2, 3, 1, 299.00,  'shipped'),
    (2, 5, 1, 199.00,  'completed')
ON DUPLICATE KEY UPDATE user_id = VALUES(user_id);