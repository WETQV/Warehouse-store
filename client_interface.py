# client_interface.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout,
    QMessageBox, QInputDialog, QLineEdit, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt
from database import Database

class ClientWidget(QWidget):
    def __init__(self, main_window, user_id, username):
        super().__init__()
        self.main_window = main_window  # Reference to the main window
        self.db = Database()
        self.user_id = user_id
        self.username = username
        self.init_ui()

    def init_ui(self):
        # Welcome message
        self.label = QLabel(f'Добро пожаловать, {self.username}!')

        # Search input for products
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Поиск товаров...')
        self.search_input.textChanged.connect(self.load_products)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Action buttons
        self.order_button = QPushButton('Сделать заказ')
        self.order_button.clicked.connect(self.place_order)

        self.view_orders_button = QPushButton('Мои заказы')
        self.view_orders_button.clicked.connect(self.view_orders)

        self.logout_button = QPushButton('Выйти')
        self.logout_button.clicked.connect(self.logout)

        # Layouts
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.view_orders_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.products_table)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.logout_button)

        # Set stretch factor for the products table to fill available space
        layout.setStretch(2, 1)

        self.setLayout(layout)

        # Load products after setting up the interface
        self.load_products()

    def load_products(self):
        search_text = self.search_input.text()
        products = self.db.search_products(search_text)
        self.products_table.clearContents()
        self.products_table.setRowCount(len(products))
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(['ID', 'Название', 'Описание', 'Цена', 'Количество'])
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        for row_index, product in enumerate(products):
            for col_index, item in enumerate(product):
                self.products_table.setItem(row_index, col_index, QTableWidgetItem(str(item)))

    def disable_buttons(self):
        self.order_button.setEnabled(False)
        self.view_orders_button.setEnabled(False)

    def enable_buttons(self):
        self.order_button.setEnabled(True)
        self.view_orders_button.setEnabled(True)

    def place_order(self):
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            self.disable_buttons()
            product_id_item = self.products_table.item(selected_row, 0)
            if product_id_item:
                try:
                    product_id = int(product_id_item.text())
                    quantity, ok = QInputDialog.getInt(self, 'Количество', 'Введите количество:', min=1)
                    if ok:
                        success = self.db.place_order(self.user_id, product_id, quantity)
                        if success:
                            QMessageBox.information(self, 'Успех', 'Заказ успешно оформлен!')
                            self.load_products()  # Refresh product list
                        else:
                            QMessageBox.warning(self, 'Ошибка', 'Недостаточное количество товара на складе.')
                except ValueError:
                    QMessageBox.warning(self, 'Ошибка', 'Неверный идентификатор товара.')
            self.enable_buttons()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите товар для заказа.')

    def view_orders(self):
        orders = self.db.get_orders_by_user(self.user_id)
        if orders:
            self.disable_buttons()
            # Create a dialog window to display orders
            self.orders_dialog = QDialog(self)
            self.orders_dialog.setWindowTitle('Мои заказы')
            self.orders_dialog.setFixedSize(600, 400)
            self.orders_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.orders_dialog.finished.connect(self.enable_buttons)

            self.orders_table = QTableWidget()
            self.orders_table.setRowCount(len(orders))
            self.orders_table.setColumnCount(5)
            self.orders_table.setHorizontalHeaderLabels(['ID заказа', 'Товар', 'Количество', 'Сумма', 'Отменить'])
            self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            for row_index, order in enumerate(orders):
                for col_index, item in enumerate(order):
                    self.orders_table.setItem(row_index, col_index, QTableWidgetItem(str(item)))
                cancel_button = QPushButton('Отменить')
                cancel_button.clicked.connect(lambda checked, order_id=order['id']: self.cancel_order(order_id))
                self.orders_table.setCellWidget(row_index, 4, cancel_button)

            layout = QVBoxLayout()
            layout.addWidget(QLabel('Мои заказы'))
            layout.addWidget(self.orders_table)

            self.orders_dialog.setLayout(layout)
            self.orders_dialog.exec()
        else:
            QMessageBox.information(self, 'Мои заказы', 'У вас пока нет заказов.')

    def cancel_order(self, order_id):
        confirm = QMessageBox.question(
            self, 'Подтверждение', 'Вы уверены, что хотите отменить этот заказ?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db.cancel_order(order_id):
                QMessageBox.information(self, 'Успех', 'Заказ успешно отменён.')
                # Refresh the products table to show updated quantities
                self.load_products()
                # Check if there are any orders left
                remaining_orders = self.db.get_orders_by_user(self.user_id)
                if remaining_orders:
                    # Refresh the orders table
                    self.refresh_orders_table(remaining_orders)
                else:
                    # Close the orders dialog if no orders are left
                    self.orders_dialog.close()
                    QMessageBox.information(self, 'Мои заказы', 'У вас пока нет заказов.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось отменить заказ.')

    def refresh_orders_table(self, orders):
        # Clear the orders table and reload it with updated data
        self.orders_table.clearContents()
        self.orders_table.setRowCount(len(orders))

        for row_index, order in enumerate(orders):
            for col_index, item in enumerate(order):
                self.orders_table.setItem(row_index, col_index, QTableWidgetItem(str(item)))
            cancel_button = QPushButton('Отменить')
            cancel_button.clicked.connect(lambda checked, order_id=order['id']: self.cancel_order(order_id))
            self.orders_table.setCellWidget(row_index, 4, cancel_button)

    def logout(self):
        self.main_window.switch_to_auth()