import bcrypt # type: ignore

# salt = bcrypt.gensalt()
salt = '$2b$12$Lx276RIKOupaQLN0Y0Yd1.'.encode('utf-8')

def password_gen(salt ,password):
    # Hash the password with the generated salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Convert the hashed password to a string for storage
    hashed_password_str = hashed_password.decode('utf-8')
    return hashed_password_str



print(password_gen("password123"))
print(password_gen('securepassword'))
print(password_gen('hamzamughal'))

"""
$2b$12$Lx276RIKOupaQLN0Y0Yd1.05H5bfGG7ZJV/Xmx86ueXLTJrW6E7Ai
$2b$12$Lx276RIKOupaQLN0Y0Yd1.ojafi9au4Oxwza7qEEaQJW3MsNgQIwS
$2b$12$Lx276RIKOupaQLN0Y0Yd1.oe26hMsYaMOhdOX3ROd2svdpY7n0SmG
"""

"""

INSERT INTO users (user_name, password) VALUES
('john_doe', '$2b$12$Lx276RIKOupaQLN0Y0Yd1.05H5bfGG7ZJV/Xmx86ueXLTJrW6E7Ai'),
('jane_smith', '$2b$12$Lx276RIKOupaQLN0Y0Yd1.ojafi9au4Oxwza7qEEaQJW3MsNgQIwS'),
('hamza', '$2b$12$Lx276RIKOupaQLN0Y0Yd1.oe26hMsYaMOhdOX3ROd2svdpY7n0SmG');

-- Insert demo data into the 'categorys' table
INSERT INTO categorys (name) VALUES
('Beverages'),
('Ice Cream'),
('Snacks');

-- Insert demo data into the 'products' table
INSERT INTO products (category_id, name, price) VALUES
(1, 'Coffee', 100),
(1, 'Tea', 50),
(1, 'Lemonade', 70),
(2, 'Vanilla Ice Cream', 150),
(2, 'Chocolate Ice Cream', 180),
(2, 'Strawberry Ice Cream', 170),
(3, 'Chips', 30),
(3, 'Cookies', 50),
(3, 'Sandwich', 120);

-- Insert demo data into the 'sales' table
INSERT INTO sales (user_id, price, discount_per, discount_price, discount_des) VALUES
(1, 350, 10, 35, 'Summer Sale'),
(2, 270, 0, 0, 'None'),
(3, 150, 5, 7.5, 'Loyalty Discount');

-- Insert demo data into the 'sale_details' table
INSERT INTO sale_details (sale_id, product_id, quantity, price, discount_per, discount_price, discount_des) VALUES
(1, 1, 2, 200, 10, 20, 'Summer Sale'),
(1, 4, 1, 150, 10, 15, 'Summer Sale'),
(2, 6, 2, 360, 0, 0, 'None'),
(2, 7, 3, 90, 0, 0, 'None'),
(3, 9, 1, 150, 5, 7.5, 'Loyalty Discount');


"""