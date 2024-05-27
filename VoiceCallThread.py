from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont

class VoiceCallThread(QThread):
    voiceStateChanged = pyqtSignal(int)
    def __init__(self, client, recipient, _playing_stream, _recording_stream, parent=None):
        super(VoiceCallThread, self).__init__(parent)
        self.client = client
        self.recipient = None
        self.voice_state = 0
        self.recipient = recipient
        self.playing_stream = _playing_stream
        self.recording_stream = _recording_stream

    def run(self):
        # 等待应答
        while self.voice_state == 0:
            self.sleep(100)  # 避免CPU占用过高，稍作休息
        # 控制信息
        message = f"VOIC_CONTENT|{self.client.username}|{self.recipient}"
        # 发送语音数据
        while self.voice_state == 2:
            data = self.recording_stream.read(1024)
            self.client.send_message(message, data)
        # 语音通话结束
        self.client.send_message(f"VOIC_END|{self.client.username}|{self.recipient}")

    def start_call(self, recipient):
        self.recipient = recipient
        self.voice_state = 2
        self.start()

    def close_call(self):
        self.voice_state = 0

class VoiceCallWindow(QWidget):
    def __init__(self, client, parent=None):
        super(VoiceCallWindow, self).__init__(parent)
        self.client = client
        self.voice_thread = VoiceCallThread(client, self)
        self.voice_thread.voiceStateChanged.connect(self.update_call_state)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Voice Call")
        self.setGeometry(300, 300, 300, 200)

        self.calling_label = QLabel(f"Calling to {self.client.username}...", self)
        self.calling_label.setFont(QFont("Arial", 10))

        layout = QVBoxLayout()
        layout.addWidget(self.calling_label)
        self.setLayout(layout)

    def start_voice_call(self):
        self.voice_thread.start_call(self.client.username)

    def closeEvent(self, event):
        # 在关闭窗口前执行的操作
        reply = QMessageBox.question(self,
                                     "Confirm Exit",
                                     "Are you sure you want to close the voice call?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.Yes:
            self.voice_thread.close_call()
            event.accept()  # 接受关闭事件，继续关闭窗口
        else:
            event.ignore()  # 忽略关闭事件，不关闭窗口

    def update_call_state(self, state):
        if state == 1:
            self.calling_label.setText("The other party refused to accept the call")
        elif state == 2:
            self.calling_label.setText(f"Calling to {self.client.username}...")
