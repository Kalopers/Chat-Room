from LoginWindow import LoginWindow
from client import Client
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

def main():
    Server_ip = "127.0.0.1"   
    Server_port = 8888
    Icon_Path = "" 
    app = QApplication([])
    app.setWindowIcon(QIcon(Icon_Path))
    client = Client(Server_ip, Server_port)
    login_window = LoginWindow(client)
    app.exec()

if __name__ == "__main__": 
    main()