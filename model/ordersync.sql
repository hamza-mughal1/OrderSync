USE ordersync;

CREATE TABLE categories (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    toggle TINYINT DEFAULT 1,
    PRIMARY KEY (id)
);

CREATE TABLE products (
    id INT NOT NULL AUTO_INCREMENT,
    category_id INT NOT NULL,
    name VARCHAR(200) NOT NULL UNIQUE,
    price INT NOT NULL,
    toggle TINYINT DEFAULT 1,
    image_path VARCHAR(300) DEFAULT "None",
    PRIMARY KEY (id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE role (
    id INT NOT NULL AUTO_INCREMENT,
    role VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    user_name VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(300) NOT NULL,
    user_role INT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(user_role) REFERENCES role(id)
);

CREATE TABLE sales (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    price INT NOT NULL,
    date DATETIME DEFAULT NOW(),
    discount_per INT DEFAULT 0,
    discount_price INT DEFAULT 0,
    discount_des VARCHAR(500) DEFAULT "None",
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE sale_details (
    id INT NOT NULL AUTO_INCREMENT,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price INT NOT NULL,
    discount_per INT DEFAULT 0,
    discount_price INT DEFAULT 0,
    discount_des VARCHAR(500) DEFAULT "None",
    PRIMARY KEY(id),
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id)
    REFERENCES products(id)
);

CREATE TABLE available_refresh_token (
    id INT NOT NULL AUTO_INCREMENT,
    token VARCHAR(300) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_id INT NOT NULL, 
    user_role INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    jwt_token VARCHAR(300) NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (user_role) REFERENCES roles(id)
);

CREATE TABLE blacklisted_token (
    id INT NOT NULL AUTO_INCREMENT,
    token VARCHAR(300) NOT NULL,
    user_id INT NOT NULL, 
    role INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role) REFERENCES roles(id)
);

CREATE TABLE endpoints (
    id INT NOT NULL AUTO_INCREMENT,
    endpoint VARCHAR(300),
    method SET("GET","POST","PUT","PATCH","DELETE") DEFAULT "GET",
    role JSON DEFAULT "[]",
    PRIMARY KEY(id)
);

SET GLOBAL event_scheduler = ON;

CREATE EVENT delete_old_acess_tokens
ON SCHEDULE EVERY 30 MINUTE
DO
DELETE FROM blacklisted_token
WHERE created_at < NOW() - INTERVAL 15 MINUTE;

CREATE EVENT delete_old_refresh_tokens
ON SCHEDULE EVERY 30 MINUTE
DO
DELETE FROM available_refresh_token
WHERE created_at < NOW() - INTERVAL 2 DAY;


