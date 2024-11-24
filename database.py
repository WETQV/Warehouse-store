# database.py
import sqlite3
import bcrypt

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('app.db')
        self.conn.row_factory = sqlite3.Row  # Enable named column access
        self.create_tables()

    def create_tables(self):
        with self.conn:
            cursor = self.conn.cursor()

            # Table for users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'client'))
                )
            ''')

            # Table for products
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL CHECK(price >= 0),
                    quantity INTEGER NOT NULL CHECK(quantity >= 0)
                )
            ''')

            # Table for orders
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity > 0),
                    total_price REAL NOT NULL CHECK(total_price >= 0),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )
            ''')

            # Add default admin user if not exists
            cursor.execute('SELECT * FROM users WHERE role = ?', ('admin',))
            if not cursor.fetchone():
                self.add_user('admin', 'admin', 'admin')

    # User management methods
    def add_user(self, username, password, role='client'):
        cursor = self.conn.cursor()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username, password, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return {'id': user['id'], 'username': user['username'], 'role': user['role']}
        else:
            return None

    # Product management methods
    def add_product(self, name, description, price, quantity):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price, quantity)
                VALUES (?, ?, ?, ?)
            ''', (name, description, price, quantity))

    def get_products(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products')
        return cursor.fetchall()

    def update_product(self, product_id, name, description, price, quantity):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE products
                SET name = ?, description = ?, price = ?, quantity = ?
                WHERE id = ?
            ''', (name, description, price, quantity, product_id))

    def delete_product(self, product_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))

    # Order management methods
    def place_order(self, user_id, product_id, quantity):
        with self.conn:
            cursor = self.conn.cursor()
            # Check product availability
            cursor.execute('SELECT price, quantity FROM products WHERE id = ?', (product_id,))
            product = cursor.fetchone()
            if product and product['quantity'] >= quantity:
                total_price = product['price'] * quantity
                # Insert order
                cursor.execute('''
                    INSERT INTO orders (user_id, product_id, quantity, total_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, product_id, quantity, total_price))
                # Update product quantity
                cursor.execute('''
                    UPDATE products SET quantity = quantity - ? WHERE id = ?
                ''', (quantity, product_id))
                return True
            else:
                return False

    def get_orders_by_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT orders.id, products.name, orders.quantity, orders.total_price
            FROM orders
            JOIN products ON orders.product_id = products.id
            WHERE orders.user_id = ?
        ''', (user_id,))
        return cursor.fetchall()

    def get_all_orders(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT orders.id, users.username, products.name, orders.quantity, orders.total_price
            FROM orders
            JOIN users ON orders.user_id = users.id
            JOIN products ON orders.product_id = products.id
        ''')
        return cursor.fetchall()

    def search_products(self, search_text):
        cursor = self.conn.cursor()
        query = '''
            SELECT * FROM products
            WHERE name LIKE ? OR description LIKE ?
        '''
        search_pattern = f'%{search_text}%'
        cursor.execute(query, (search_pattern, search_pattern))
        return cursor.fetchall()

    def cancel_order(self, order_id):
        with self.conn:
            cursor = self.conn.cursor()
            # Get order details
            cursor.execute('SELECT product_id, quantity FROM orders WHERE id = ?', (order_id,))
            order = cursor.fetchone()
            if order:
                product_id, quantity = order['product_id'], order['quantity']
                # Update product quantity
                cursor.execute('UPDATE products SET quantity = quantity + ? WHERE id = ?', (quantity, product_id))
                # Delete the order
                cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
                return True
            else:
                return False