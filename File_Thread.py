from PyQt6.QtCore import QThread, pyqtSignal, QVariant
from PyQt6.QtCore import QDateTime
import time
import os

class ReceiveThread(QThread):
    file_sig = pyqtSignal(int)
    state = pyqtSignal(int)

    def __init__(self, client, file_size, file_path, msgbox_thread, file_sent_size, parent=None):
        super().__init__(parent)
        self.client = client
        self.file_size = file_size
        self.file_path = file_path
        self.messagebox_thread = msgbox_thread
        self.file_sent_size = file_sent_size
        self.file_state = 0

    def run(self):
        self.state.connect(self.handle_state)
        file_size = self.file_size
        file_path = self.file_path
        while not self.file_state:
            send_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            print(f"[{send_time}] file_state = {self.file_state}")
            time.sleep(1)
            continue
        if self.file_state == 1:
            self.messagebox_thread.send_message("Wrong", "Recipient does not exist", 0)
            self.file_state = 0
        elif self.file_state == 2:
            self.messagebox_thread.send_message("Wrong", "Recipient refused to receive the file", 0)
            self.file_state = 0
        elif self.file_state == 3 or self.file_state == 4:
            file_name = os.path.basename(file_path)
            target = recipient
            if self.file_state == 4:
                recipient = "SERVER"   

            message = f"FILE_CONTENT|{file_name}|{recipient}"
            with open(file_path, "rb") as f:
                f.seek(self.file_sent_size)
                total_sent = self.file_sent_size
                while self.file_state != 0 and total_sent < file_size:
                    data = f.read(2**15)
                    total_sent += len(data)
                    self.client.send_message(message, data)

            self.file_sent_size = 0
            if self.file_state != 0:
                self.client.send_message(f"FILE_END|{self.client.username}|{recipient}|{file_name}|{file_size}|{target}")
                self.messagebox_thread.send_message("File Transfer", f"{file_name} Transfer Complete!", 0)
                self.file_state = 0
                print(f"[{send_time}] File Transfer Complete!")
            else:
                self.client.send_message(f"FILE_CANCEL|{recipient}|{file_name}")
                
    def handle_state(self, state):
        self.file_state = state