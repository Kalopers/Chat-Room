from PyQt6.QtCore import QThread, pyqtSignal, QVariant

class ReceiveThread(QThread):
    message_received = pyqtSignal(QVariant, QVariant)  # 创建一个自定义信号

    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client

    def run(self):
        while True:
            message, data = self.client.receive_message()
            self.message_received.emit(message, data)