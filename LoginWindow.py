from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer

from ChatWindow import ChatWindow

class LoginWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login Page")
        self.setGeometry(300, 300, 450, 300)
        self.username_label = QLabel("Username  :", self)
        self.username_label.move(60, 50)

        self.username_input = QLineEdit(self)
        self.username_input.setFixedSize(200, 30)
        self.username_input.setPlaceholderText("3~9 characters")
        self.username_input.move(150, 50)

        self.password_label = QLabel("Password   :", self)
        self.password_label.move(60, 100)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("6~9 characters")
        self.password_input.setFixedSize(200, 30)
        self.password_input.move(150, 100)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Login", self)
        self.login_button.move(150, 180)
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Register", self)
        self.register_button.move(250, 180)
        self.register_button.clicked.connect(self.register)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(3000)

        self.show()

    def check_connection(self):
        if self.client.close_window:
            self.close()
            raise SystemExit
        self.timer.start(3000)

    # def closeEvent(self, event):
    #     reply = QMessageBox.question(self, 'Message',
    #                 "Are you sure to quit?", QMessageBox.StandardButton.Yes |
    #                 QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

    #     if reply == QMessageBox.StandardButton.Yes:
    #         self.client.socket.close()
    #         event.accept()
    #     else:
    #         event.ignore()

    def login(self):
        self.client.username = self.username_input.text()
        if self.client.username.isalnum() and 2 < len(self.client.username) < 10:
            password = self.password_input.text()
            if password.isalnum() and 5 < len(password) < 10:
                self.client.send_message(f"LOGIN|{self.client.username}|{password}")
                message, _ = self.client.receive_message()
                if message.startswith("LOGIN_SUCCEED"):
                    QMessageBox.information(None, "Success", "Login successfully")
                    self.close()
                    chat_window = ChatWindow(self.client)  
                    chat_window.show()  
                    self.main_window = chat_window  
                elif message.startswith("LOGIN_FAIL"):
                    QMessageBox.critical(None, "Error", "Invalid username or password")
            else:
                QMessageBox.critical(None, "Error", "Password can only contain numbers or letters and length 6~9")
        else:
            QMessageBox.critical(None, "Error", "Username can only contain numbers or letters and length 3~9")

    def register(self):
        self.client.username = self.username_input.text()
        if self.client.username.isalnum() and 2 < len(self.client.username) < 10:
            password = self.password_input.text()
            if password.isalnum() and 5 < len(password) < 10:
                self.client.send_message(f"REGISTER|{self.client.username}|{password}")
                message, data = self.client.receive_message()
                if message.startswith("REGISTER_SUCCEED"):
                    QMessageBox.information(None, "Success", "Register successfully")
                    self.close()
                    chat_window = ChatWindow(self.client)  
                    chat_window.show()  
                    self.main_window = chat_window  
                elif message.startswith("REGISTER_FAIL"):
                    QMessageBox.critical(None, "Error", "Username already exists")
            else:
                QMessageBox.critical(None, "Error", "Password can only contain numbers or letters and length 6~9")
        else:
            QMessageBox.critical(None, "Error", "Username can only contain numbers or letters and length 3~9")