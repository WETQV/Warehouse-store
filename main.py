# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from auth import AuthWidget
from admin_interface import AdminWidget
from client_interface import ClientWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Магазин')
        self.setFixedSize(800, 600)

        # Создаем центральный виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Создаем стек для переключения между экранами
        self.stack = QStackedWidget(self)
        central_layout = QHBoxLayout(central_widget)
        central_layout.addWidget(self.stack)

        # Меню
        self.menu_layout = QVBoxLayout()
        self.create_menu()

        # Добавляем виджеты
        self.auth_widget = AuthWidget(self)
        self.stack.addWidget(self.auth_widget)
        self.stack.setCurrentWidget(self.auth_widget)

    def create_menu(self):
        """Создание бокового меню."""
        self.auth_button = QPushButton("Авторизация", self)
        self.auth_button.clicked.connect(self.switch_to_auth)

        self.admin_button = QPushButton("Админ", self)
        self.admin_button.clicked.connect(self.switch_to_admin)

        self.client_button = QPushButton("Клиент", self)
        self.client_button.clicked.connect(self.switch_to_client)

        # Добавляем кнопки в меню
        self.menu_layout.addWidget(self.auth_button)
        self.menu_layout.addWidget(self.admin_button)
        self.menu_layout.addWidget(self.client_button)

        # Добавляем меню в основной layout
        self.menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stack.addWidget(self.create_side_menu())

    def create_side_menu(self):
        """Создание боковой панели меню."""
        side_menu = QWidget(self)
        side_menu.setLayout(self.menu_layout)
        return side_menu

    def switch_to_admin(self):
        self.admin_widget = AdminWidget(self)
        self.stack.addWidget(self.admin_widget)
        self.stack.setCurrentWidget(self.admin_widget)

    def switch_to_client(self, user_id, username):
        self.client_widget = ClientWidget(self, user_id, username)
        self.stack.addWidget(self.client_widget)
        self.stack.setCurrentWidget(self.client_widget)

    def switch_to_auth(self):
        self.stack.setCurrentWidget(self.auth_widget)

    def closeEvent(self, event):
        """Закрытие всех дочерних окон при выходе."""
        for widget in self.findChildren(QWidget):
            if widget is not self:
                widget.close()
        event.accept()

def main():
    app = QApplication(sys.argv)

    # Применение стилей
    try:
        with open('styles.qss', 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass  # Если файл стилей не найден, продолжаем без него

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()