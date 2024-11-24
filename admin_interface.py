# admin_interface.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QDialog, QFormLayout, QHeaderView
)
from PyQt6.QtCore import Qt
from database import Database

class AdminWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Ссылка на главное окно
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        # Приветственное сообщение
        self.label = QLabel('Добро пожаловать, Администратор!')

        # Таблица товаров
        self.products_table = QTableWidget()
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_products()

        # Кнопки действий
        self.add_product_button = QPushButton('Добавить товар')
        self.add_product_button.clicked.connect(self.add_product)

        self.edit_product_button = QPushButton('Редактировать товар')
        self.edit_product_button.clicked.connect(self.edit_product)

        self.delete_product_button = QPushButton('Удалить товар')
        self.delete_product_button.clicked.connect(self.delete_product)

        self.view_orders_button = QPushButton('Просмотреть заказы')
        self.view_orders_button.clicked.connect(self.view_orders)

        self.logout_button = QPushButton('Выйти')
        self.logout_button.clicked.connect(self.logout)

        # Макеты
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_product_button)
        buttons_layout.addWidget(self.edit_product_button)
        buttons_layout.addWidget(self.delete_product_button)
        buttons_layout.addWidget(self.view_orders_button)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.products_table)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.logout_button)

        # Устанавливаем растяжение для таблицы
        layout.setStretch(1, 1)

        self.setLayout(layout)

    def load_products(self):
        products = self.db.get_products()
        self.products_table.clearContents()
        self.products_table.setRowCount(len(products))
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(['ID', 'Название', 'Описание', 'Цена', 'Количество'])
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        for row_index, product in enumerate(products):
            for col_index, item in enumerate(product):
                self.products_table.setItem(row_index, col_index, QTableWidgetItem(str(item)))

    def disable_buttons(self):
        self.add_product_button.setEnabled(False)
        self.edit_product_button.setEnabled(False)
        self.delete_product_button.setEnabled(False)
        self.view_orders_button.setEnabled(False)

    def enable_buttons(self):
        self.add_product_button.setEnabled(True)
        self.edit_product_button.setEnabled(True)
        self.delete_product_button.setEnabled(True)
        self.view_orders_button.setEnabled(True)

    def add_product(self):
        self.disable_buttons()
        dialog = ProductDialog()
        if dialog.exec():
            name, description, price, quantity = dialog.get_data()
            self.db.add_product(name, description, price, quantity)
            self.load_products()
        self.enable_buttons()

    def edit_product(self):
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            self.disable_buttons()
            # Получаем данные из выбранной строки
            product_id_item = self.products_table.item(selected_row, 0)
            name_item = self.products_table.item(selected_row, 1)
            description_item = self.products_table.item(selected_row, 2)
            price_item = self.products_table.item(selected_row, 3)
            quantity_item = self.products_table.item(selected_row, 4)

            try:
                product_id = int(product_id_item.text())
                name = name_item.text()
                description = description_item.text()
                price = float(price_item.text())
                quantity = int(quantity_item.text())

                dialog = ProductDialog(product_id, name, description, price, quantity)
                if dialog.exec():
                    name, description, price, quantity = dialog.get_data()
                    self.db.update_product(product_id, name, description, price, quantity)
                    self.load_products()
            except ValueError:
                QMessageBox.warning(self, 'Ошибка', 'Некорректные данные товара.')
            self.enable_buttons()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите товар для редактирования.')

    def delete_product(self):
        selected_row = self.products_table.currentRow()
        if selected_row >= 0:
            self.disable_buttons()
            product_id_item = self.products_table.item(selected_row, 0)
            try:
                product_id = int(product_id_item.text())
                confirm = QMessageBox.question(
                    self, 'Подверждение', 'Вы уверены, что хотите удалить этот товар?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    self.db.delete_product(product_id)
                    self.load_products()
            except ValueError:
                QMessageBox.warning(self, 'Ошибка', 'Некорректный идентификатор товара.')
            self.enable_buttons()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите товар для удаления.')

    def view_orders(self):
        orders = self.db.get_all_orders()
        if orders:
            self.disable_buttons()
            # Создаём диалоговое окно для отображения заказов
            self.orders_dialog = QDialog(self)
            self.orders_dialog.setWindowTitle('Все заказы')
            self.orders_dialog.setFixedSize(600, 400)
            self.orders_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.orders_dialog.finished.connect(self.enable_buttons)

            orders_table = QTableWidget()
            orders_table.setRowCount(len(orders))
            orders_table.setColumnCount(5)
            orders_table.setHorizontalHeaderLabels(['ID заказа', 'Пользователь', 'Товар', 'Количество', 'Сумма'])
            orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            for row_index, order in enumerate(orders):
                for col_index, item in enumerate(order):
                    orders_table.setItem(row_index, col_index, QTableWidgetItem(str(item)))

            layout = QVBoxLayout()
            layout.addWidget(QLabel('Все заказы'))
            layout.addWidget(orders_table)

            self.orders_dialog.setLayout(layout)
            self.orders_dialog.exec()
        else:
            QMessageBox.information(self, 'Заказы', 'Заказов нет.')

    def logout(self):
        self.main_window.switch_to_auth()

class ProductDialog(QDialog):
    def __init__(self, product_id=None, name='', description='', price=0.0, quantity=0):
        super().__init__()
        self.product_id = product_id
        self.init_ui(name, description, price, quantity)

    def init_ui(self, name, description, price, quantity):
        self.setWindowTitle('Добавить товар' if self.product_id is None else 'Редактировать товар')

        self.name_input = QLineEdit(name)
        self.description_input = QLineEdit(description)
        self.price_input = QLineEdit(str(price))
        self.quantity_input = QLineEdit(str(quantity))

        form_layout = QFormLayout()
        form_layout.addRow('Название:', self.name_input)
        form_layout.addRow('Описание:', self.description_input)
        form_layout.addRow('Цена:', self.price_input)
        form_layout.addRow('Количество:', self.quantity_input)

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def accept(self):
        try:
            name = self.name_input.text()
            description = self.description_input.text()
            price = float(self.price_input.text())
            quantity = int(self.quantity_input.text())
            if not name or price < 0 or quantity < 0:
                raise ValueError
            super().accept()
        except ValueError:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите корректные данные.')

    def get_data(self):
        name = self.name_input.text()
        description = self.description_input.text()
        price = float(self.price_input.text())
        quantity = int(self.quantity_input.text())
        return name, description, price, quantity