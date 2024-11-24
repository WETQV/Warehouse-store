# auth.py
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from database import Database

class AuthWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        # Создаем метки и поля ввода
        self.login_label = QLabel('Логин:')
        self.login_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-bottom: -15px; /* Опускаем метку ближе к полю */
            }
            """
        )
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #363636;
                border-radius: 8px;
                background-color: #242424;
                color: white;
                font-size: 12px;
            }
            """
        )

        self.password_label = QLabel('Пароль:')
        self.password_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-bottom: -15px;
            }
            """
        )
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #363636;
                border-radius: 8px;
                background-color: #242424;
                color: white;
                font-size: 12px;
            }
            """
        )

        # Создаем кнопки
        self.login_button = QPushButton('Войти')
        self.login_button.setStyleSheet(
            """
            QPushButton {
                background-color: #363636;
                color: white;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #242424;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            """
        )

        self.register_button = QPushButton('Регистрация')
        self.register_button.setStyleSheet(
            """
            QPushButton {
                background-color: #363636;
                color: white;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #242424;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            """
        )

        # Подключаем кнопки к методам
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.open_registration)

        # Компоновка кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        buttons_layout.setSpacing(10)

        # Основной макет
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)  # Уменьшено расстояние между элементами
        form_layout.addWidget(self.login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(buttons_layout)

        # Блок-контейнер для формы
        form_frame = QFrame()
        form_frame.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 15px; /* Уменьшен padding для компактности */
                max-width: 400px; /* Ограничиваем ширину блока */
            }
            """
        )
        form_frame.setLayout(form_layout)

        # Внешний слой: центрирование формы
        main_layout = QVBoxLayout()
        main_layout.addWidget(form_frame)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)


    def handle_login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите логин и пароль.')
            return

        user = self.db.authenticate_user(username, password)

        if user:
            role = user['role']
            if role == 'admin':
                self.main_window.switch_to_admin()
            elif role == 'client':
                self.main_window.switch_to_client(user_id=user['id'], username=user['username'])
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неизвестная роль пользователя.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неправильный логин или пароль.')

    def open_registration(self):
        self.registration_widget = RegistrationWidget(self.main_window)
        self.main_window.stack.addWidget(self.registration_widget)
        self.main_window.stack.setCurrentWidget(self.registration_widget)

class RegistrationWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        # Создаем поля ввода с метками над ними
        self.username_label = QLabel('Логин:')
        self.username_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-bottom: -15px; /* Опустить метку ближе к полю */
            }
            """
        )
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите ваш логин")
        self.username_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #363636;
                border-radius: 8px;
                background-color: #242424;
                color: white;
                font-size: 12px;
            }
            """
        )

        self.password_label = QLabel('Пароль:')
        self.password_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-bottom: -15px;
            }
            """
        )
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #363636;
                border-radius: 8px;
                background-color: #242424;
                color: white;
                font-size: 12px;
            }
            """
        )

        self.confirm_password_label = QLabel('Подтвердите пароль:')
        self.confirm_password_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: white;
                margin-bottom: -15px;
            }
            """
        )
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Введите пароль ещё раз")
        self.confirm_password_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #363636;
                border-radius: 8px;
                background-color: #242424;
                color: white;
                font-size: 12px;
            }
            """
        )

        # Создаем кнопки
        self.register_button = QPushButton('Зарегистрироваться')
        self.register_button.setStyleSheet(
            """
            QPushButton {
                background-color: #363636;
                color: white;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #242424;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            """
        )

        self.back_button = QPushButton('Назад')
        self.back_button.setStyleSheet(
            """
            QPushButton {
                background-color: #363636;
                color: white;
                font-size: 12px;
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #242424;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            """
        )

        # Подключаем кнопки к методам
        self.register_button.clicked.connect(self.handle_registration)
        self.back_button.clicked.connect(self.go_back)

        # Компоновка кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.setSpacing(10)

        # Основной макет
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)  # Уменьшено расстояние между элементами
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addLayout(buttons_layout)

        # Блок-контейнер для формы
        form_frame = QFrame()
        form_frame.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 15px; /* Уменьшен padding для компактности */
                max-width: 400px; /* Ограничиваем ширину блока */
            }
            """
        )
        form_frame.setLayout(form_layout)

        # Внешний слой: центрирование формы
        main_layout = QVBoxLayout()
        main_layout.addWidget(form_frame)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def handle_registration(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Input validation
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Логин и пароль не могут быть пустыми.')
            return

        if len(username) < 3:
            QMessageBox.warning(self, 'Ошибка', 'Логин должен быть не менее 3 символов.')
            return

        if len(password) < 6:
            QMessageBox.warning(self, 'Ошибка', 'Пароль должен быть не менее 6 символов.')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Ошибка', 'Пароли не совпадают.')
            return

        # Additional password strength checks can be added here
        # For example, checking for numbers, uppercase letters, etc.

        if self.db.add_user(username, password):
            QMessageBox.information(self, 'Успех', 'Вы успешно зарегистрировались!')
            self.go_back()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким логином уже существует.')

    def go_back(self):
        self.main_window.stack.setCurrentWidget(self.main_window.auth_widget)