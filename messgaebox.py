from PyQt6.QtCore import QThread, pyqtSignal, QVariant

class MessageboxThread(QThread):
    message_received = pyqtSignal(str, str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages_queue = []

    def run(self):
        # 循环检测是否有消息需要处理
        while True:
            QThread.sleep(1)  # 适当的休眠以避免过度占用CPU
            if self.messages_queue:
                text, message, mode = self.messages_queue.pop(0)
                self.message_received.emit(text, message, mode)

    def send_message(self, text, message, mode):
        # 从其他线程安全地向消息队列中添加消息
        self.messages_queue.append((text, message, mode))