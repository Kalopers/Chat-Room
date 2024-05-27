import PyQt6 as qt
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QTextEdit, QListWidget, QFileDialog, QInputDialog
from PyQt6.QtCore import QTimer, QDateTime
import tkinter as tk
import socket
import pyaudio
import threading
import os
import time
import requests

from ReceiveThread import ReceiveThread
from messgaebox import MessageboxThread
from VoiceCallThread import VoiceCallThread, VoiceCallWindow

class ChatWindow(QMainWindow):
    def __init__(self, _client):
        super().__init__()

        self.client = _client
        self.file_state = 0
        self.file_sent_size = 0
        self.voice_state = 0
        self.MyPeer = None
        self.P2P = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Chat Room - {self.client.username}") 
        self.setGeometry(300, 300, 600, 500)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(3000)

        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setGeometry(5, 5, 370, 390)

        self.list = QListWidget(self)
        self.list.setGeometry(380, 30, 200, 280)

        self.edit = QTextEdit(self)
        self.edit.setGeometry(5, 430, 370, 50)

        self.label1 = QLabel("Online Users:", self)
        self.label1.move(380, 5)

        self.label2 = QLabel("Input:", self)
        self.label2.move(5, 400)

        self.button1 = QPushButton("Private Chat", self)
        self.button1.move(380, 320)
        self.button1.clicked.connect(self.send_private_message)

        self.button2 = QPushButton("Group Chat", self)
        self.button2.move(480, 320)
        self.button2.clicked.connect(self.send_group_message)

        self.button3 = QPushButton("Send File", self)
        self.button3.move(380, 360)
        self.button3.clicked.connect(self.send_file)

        self.button4 = QPushButton("Voice Call", self)
        self.button4.move(480, 360)
        self.button4.clicked.connect(self.voice_call)

        self.button5 = QPushButton("NAT Traversal", self)
        self.button5.move(380, 400)
        self.button5.clicked.connect(self.nat_traversal)

        self.button6 = QPushButton("P2P Chat", self)
        self.button6.move(480, 400)
        self.button6.clicked.connect(self.P2P_chat)

        chunk_size = 1024                   
        audio_format = pyaudio.paInt16      
        channels = 1                        
        rate = 20000                        
        self.playing_stream = pyaudio.PyAudio().open(format=audio_format, channels=channels, rate=rate, output=True,
                                                     frames_per_buffer=chunk_size)
        self.recording_stream = pyaudio.PyAudio().open(format=audio_format, channels=channels, rate=rate, input=True,
                                                       frames_per_buffer=chunk_size)

        self.receive_messages()
        self.messagebox()

    def receive_messages(self):
        self.receive_thread = ReceiveThread(self.client, self)
        self.receive_thread.message_received.connect(self.handle_received_message)
        self.receive_thread.start()

    def messagebox(self):
        self.messagebox_thread = MessageboxThread(self)
        self.messagebox_thread.message_received.connect(self.show_messagebox)
        self.messagebox_thread.start()

    def show_messagebox(self, text, message, mode):
        # information
        if mode == 0:
            QMessageBox.information(None, text, message)
        # question
        elif mode == 1:
            reply = QMessageBox.question(None, text, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                return True
            else:
                return False
        
    # def send(self):
    #     message = self.message_input.text()
    #     self.client.send_message(f"MESSAGE|{self.client.username}|{message}")
    #     self.message_input.setText("")

    def check_connection(self):
        if self.client.close_window:
            QMessageBox.critical(None, "Error", "Connection to the server is lost.")
            self.close()
            raise SystemExit
        self.timer.start(3000)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                    "Are you sure to quit?", QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.client.socket.close()
            event.accept()
        else:
            event.ignore()

    def send_private_message(self):
        recipient_choice = self.list.currentItem()
        if recipient_choice:
            recipient = recipient_choice.text()
            message = self.edit.toPlainText()
            if message:
                send_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                self.text.append(f"{send_time} {self.client.username} to {recipient}: \n{message}")
                self.client.send_message(f"PRIVATE|{self.client.username}|{recipient}|{send_time}|{message}")
                self.edit.clear()
            else:
                QMessageBox.critical(None, "Error", "Message cannot be empty")
        else:
            QMessageBox.critical(None, "Error", "Please select a user")

    def send_group_message(self):
        message = self.edit.toPlainText()
        if message:
            send_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.text.append(f"{send_time} {self.client.username} to Public: \n{message}")
            self.client.send_message(f"GROUP|{self.client.username}|{send_time}|{message}")
            self.edit.clear()
        else:
            QMessageBox.critical(None, "Error", "Message cannot be empty")

    def send_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select File", ".")[0]
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            #recipient = self.list.currentItem().text()
            recipient, ok = QInputDialog.getText(self, 'Input Dialog','Enter file recipent\'s name:')
            if ok:
                print(f"file_state = {self.file_state}")
                self.client.send_message(f"FILE_HEADER|{self.client.username}|{recipient}|{file_name}|{file_size}")
                threading.Thread(target=self.send_file_thread, args=(recipient, file_path, file_size, )).start()
            else:
                QMessageBox.critical(None, "Error", "Please select a user")

    def send_file_thread(self, recipient, file_path, file_size):    
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

    def file_cancel(self):
        self.file_state = 0

    def update_online_users(self, message):
        user = message[4:]
        if message.startswith("ADD"):
            self.list.addItem(user)
        elif message.startswith("DEL"):
            for i in range(self.list.count()):
                if self.list.item(i).text() == user:
                    self.list.takeItem(i)
                    break

    def recv_private_message(self, message):
        parts = message.split("|", maxsplit=3)
        sender = parts[0]
        recipient = parts[1]
        send_time = parts[2]
        msg = parts[3]
        if recipient == self.client.username:
            self.text.append(f"{sender} -> {recipient} ({send_time}):\n{msg}\n")

    def recv_group_message(self, message):
        parts = message.split("|", maxsplit=2)
        sender = parts[0]
        send_time = parts[1]
        msg = parts[2]
        self.text.append(f"{sender} -> public ({send_time}):\n{msg}\n")

    def recv_file(self, message, data):
        if message.startswith("HEADER"):
            parts = message.split("|", maxsplit=3)
            sender = parts[1]
            file_name = parts[2]
            file_size = int(parts[3])
            reply = QMessageBox.question(None, "File Transfer", f"{sender} has send you a file\n{file_name}({file_size}Bytes)\nDo you want to accept it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                threading.Thread(target=self.recv_file_thread, args=(sender, file_name, file_size, 1)).start()
            else:
                self.client.send_message(f"FILE_REJECT|{self.client.username}|{sender}")
        elif message.startswith("OFFLINE_HEADER"):
            parts = message.split("|", maxsplit=3)
            sender = parts[1]
            file_name = parts[2]
            file_size = int(parts[3])
            reply = QMessageBox.question(None, "File Transfer111", f"{sender} has send you a offline file\n{file_name}({file_size}Bytes)\nDo you want to accept it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                threading.Thread(target=self.recv_file_thread, args=(sender, file_name, file_size, 2)).start()
            else:
                self.client.send_message(f"FILE_REJECT|{self.client.username}|{sender}")
        elif message.startswith("CONTENT"):
            parts = message.split("|", maxsplit=1)
            file_name = parts[1]
            with open(file_name+".tmp", "ab") as f:
                f.write(data)
        elif message.startswith("END"):
            parts = message.split("|", maxsplit=1)
            file_name = parts[1]
            os.rename(file_name + ".tmp", file_name)
            threading.Thread(target=self.recv_file_thread, args=("", file_name, "", 3)).start()
        elif message.startswith("CANCEL"):
            parts = message.split("|", maxsplit=1)
            file_name = parts[1]
            threading.Thread(target=self.recv_file_thread, args=("", file_name, "", 4)).start()
        elif message.startswith("USER_NO_EXIST"):
            self.file_state = 1
        elif message.startswith("REJECT"):
            self.file_state = 2
        elif message.startswith("ACCEPT"):
            self.file_sent_size = int(message[7:])
            self.file_state = 3
        elif message.startswith("OFFLINE_USER"):
            self.file_sent_size = int(message[13:])
            self.file_state = 4

    def recv_file_thread(self, sender, file_name, file_size, mode):
        if mode == 1:
            file_sent_size = 0
            if os.path.isfile(file_name+".tmp"):
                file_sent_size = os.path.getsize(file_name+".tmp")
            self.client.send_message(f"FILE_ACCEPT|{self.client.username}|{sender}|{file_sent_size}")
        elif mode == 2:
            self.messagebox_thread.send_message("File Tr111ansfer", f"{sender} has send you a offline file\n{file_name}({file_size}Bytes)", 0)
            file_sent_size = 0
            if os.path.isfile(file_name+".tmp"):
                file_sent_size = os.path.getsize(file_name+".tmp")
            self.client.send_message(f"FILE_ACCEPT|{self.client.username}|SERVER|{file_sent_size}")
        elif mode == 3:
            self.messagebox_thread.send_message("File Transfer", f"{file_name} Transfer Complete!", 0)
        elif mode == 4:
            self.messagebox_thread.send_message("File Transfer", f"{file_name} Transfer Cancel!", 0)

    def voice_call(self):
        recipient_choice = self.list.currentItem()
        if recipient_choice:
            recipient = recipient_choice.text()
            if self.voice_state == 2:
                self.voice_state = 0
                self.client.send_message(f"VOIC_END|{self.client.username}|{recipient}")
            else:
                self.client.send_message(f"VOIC_HEADER|{self.client.username}|{recipient}")
                threading.Thread(target=self.send_voice_thread, args=(recipient, )).start()
        else:
            self.messagebox_thread.send_message("Error", "Please select a user", 0)

    def send_voice_thread(self, recipient):
        while not self.voice_state:
            continue
        if self.voice_state == 1:
            self.messagebox_thread.send_message("Voice Call", "The other party refused to accept the call", 0)
            self.voice_state = 0
        elif self.voice_state == 2:
            message = f"VOIC_CONTENT|{self.client.username}|{recipient}"
            while self.voice_state == 2:
                data = self.recording_stream.read(1024)
                self.client.send_message(message, data)
            self.close_voice()
            self.client.send_message(f"VOIC_END|{self.client.username}|{recipient}")

    def close_voice(self):
        self.voice_state = 0

    def recv_voice(self, message, data):
        if message.startswith("HEADER"):
            parts = message.split("|", maxsplit=1)
            sender = parts[1]
            reply = QMessageBox.question(None, "Voice Call", f"{sender} request to establish a voice call", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.client.send_message(f"VOIC_ACCEPT|{self.client.username}|{sender}")
                threading.Thread(target=self.send_voice_thread, args=(sender,)).start()
                self.voice_state = 2
            else:
                self.client.send_message(f"VOIC_REJECT|{self.client.username}|{sender}")
        elif message.startswith("CONTENT"):
            self.playing_stream.write(data)
        elif message.startswith("END"):
            parts = message.split("|", maxsplit=1)
            sender = parts[1]
            self.voice_state = 0
            QMessageBox.information(None, "Voice Call", f"{sender} has closed the voice call")
        elif message.startswith("REJECT"):
            self.voice_state = 1
        elif message.startswith("ACCEPT"):
            self.voice_state = 2

    def recv_voice_thread(self, sender, mode):
        if mode == 1:
            reply = self.messagebox_thread.send_message("Voice Call", f"{sender} request to establish a voice call\nDo you want to accept it?", 1)
            if reply == True:
                self.client.send_message(f"VOIC_ACCEPT|{self.client.username}|{sender}")
                threading.Thread(target=self.send_voice_thread, args=(sender,)).start()
                self.voice_state = 2
            else:
                self.client.send_message(f"VOIC_REJECT|{self.client.username}|{sender}")
        elif mode == 2:
            self.messagebox_thread.send_message("Voice Call", f"{sender} has closed the voice call", 0)

    def nat_traversal(self):
        recipient_choice = self.list.currentItem()
        if recipient_choice:
            recipient = recipient_choice.text()
            self.client.send_message(f"NAT_REQUEST|{self.client.username}|{recipient}")
        else:
            QMessageBox.critical(None, "Error", "Please select a user")

    def nat_handle(self, message):
        if message.startswith("REQUEST"):
            parts = message.split("|", maxsplit=1)
            sender = parts[1]
            reply = QMessageBox.question(None, "NAT traversal", f"{sender} request to establish a connection\nDo you want to accept it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                threading.Thread(target=self.nat_thread, args=(sender, 1)).start()
            else:
                self.client.send_message(f"NAT_REJECT|{self.client.username}|{sender}")
        elif message.startswith("ACCEPT"):
            parts = message.split("|", maxsplit=1)
            sender = parts[1]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = self.get_public_ip()
            sock.sendto(f"NAT_SERVER|{sender}".encode("utf-8"), (ip, 6666))
            threading.Thread(target=self.nat_send, args=(sock, sender)).start()
            threading.Thread(target=self.nat_recv, args=(sock,)).start()
        elif message.startswith("REJECT"):
            threading.Thread(target=self.nat_thread, args=("", 2)).start()
        elif message.startswith("ADDRESS"):
            parts = message.split("|", maxsplit=1)
            self.MyPeer = eval(parts[1])

    def nat_thread(self, sender, mode):
        if mode == 1:
            self.client.send_message(f"NAT_ACCEPT|{self.client.username}|{sender}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            time.sleep(1)
            ip = self.get_public_ip()
            sock.sendto(f"NAT_SERVER|{sender}".encode("utf-8"), ("8.217.76.56", 6666))
            threading.Thread(target=self.nat_send, args=(sock, sender)).start()
            threading.Thread(target=self.nat_recv, args=(sock,)).start()
        elif mode == 2:
            self.messagebox_thread.send_message("NAT traversal", f"{sender} has refused to establish a connection", 0)

    def nat_send(self, sock, recipient):
        while not self.MyPeer:
            continue
        print(f"The other party\'s public IP address and port number:{self.MyPeer}")
        for i in range(5):
            sock.sendto("NAT_HELLO".encode("utf-8"), self.MyPeer)
            time.sleep(1)
        self.P2P = False
        while True:
            if self.P2P:
                message = self.input.get("1.0", tk.END)
                if message:
                    send_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
                    self.textbox.insert(tk.END, f"{self.client.username} -> {recipient} ({send_time}):\n{message}\n")
                    self.textbox.see(tk.END)
                    try:
                        sock.sendto(f"{self.client.username}|{recipient}|{send_time}|{message}".encode("utf-8"), self.MyPeer)
                    except socket.error as e:
                        print(e)
                        sock.close()
                        self.MyPeer = None
                        self.P2P = False
                        raise SystemExit
                else:
                    self.messagebox_thread.send_message("Error", "Message cannot be empty", 0)
                self.P2P = False

    def nat_recv(self, sock):
        while True:
            try:
                message = sock.recvfrom(1024)[0].decode("utf-8")
            except socket.error as e:
                print(e)
                sock.close()
                self.MyPeer = None
                self.P2P = False
                raise SystemExit
            else:
                if message.startswith("NAT_HELLO"):
                    print("connect!")
                    continue
                parts = message.split("|", maxsplit=3)
                sender = parts[0]
                recipient = parts[1]
                send_time = parts[2]
                msg = parts[3]
                if recipient == self.client.username:
                    self.textbox.insert(tk.END, f"(P2P){sender} -> {recipient} ({send_time}):\n{msg}\n")
                    self.textbox.see(tk.END)

    def P2P_chat(self):
        self.P2P = True
    
    def handle_received_message(self, message, data):
        print(f"Received message: {message}, Data: {data}")
        if message.startswith("UPDATE_USERS"):
            self.update_online_users(message[13:])
        elif message.startswith("PRIVATE"):
            self.recv_private_message(message[8:])
        elif message.startswith("GROUP"):
            self.recv_group_message(message[6:])
        elif message.startswith("FILE"):
            self.recv_file(message[5:], data)
        elif message.startswith("VOIC"):
            self.recv_voice(message[5:], data)
        elif message.startswith("NAT"):
            self.nat_handle(message[4:])

    def get_public_ip():
        try:
            response = requests.get('https://api.ipify.org')
            return response.text
        except requests.RequestException as e:
            print(f"Error retrieving public IP: {e}")
            return None