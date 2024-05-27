from tkinter import messagebox
import tkinter as tk
import socket

class Client:
    def __init__(self, server_ip, server_port):
        self.username = ""
        self.Server_ip = server_ip
        self.Server_port = server_port
        self.is_connected = False
        self.close_window = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.window = tk.Tk()
        self.window.withdraw()
        self.window.title("Client")
        
        try:
            self.socket.connect((server_ip, server_port))
        except socket.error as e:
            self.socket.close()
            messagebox.showerror("Error", "Failed to connect to the server.")
            raise SystemExit
        else:
            self.is_connected = True

    def send_message(self, message, data=b""):
        if message.startswith("FILE_CONTENT") or message.startswith("VOIC_CONTENT"):
            parts = message.split("|", maxsplit=2)
            name = parts[1].encode("utf-8")    
            recipient = parts[2].encode("utf-8")
            sent_data = message[:12].encode("utf-8") + bytes([len(name), len(recipient)]) + name + recipient + data
        else:
            sent_data = message.encode('utf-8')
        length = len(sent_data)
        header = bytes([length // 256, length % 256])
        try:
            self.socket.sendall(header + sent_data)
        except socket.error as e:
            if self.is_connected:
                self.is_connected = False
                self.socket.close()
                messagebox.showerror("Error", "Connection to the server is lost.")
                self.close_window = True
            raise SystemExit
        
    def receive_message(self):
        try:
            message = b""
            header = self.socket.recv(2)
            length = header[0] * 256 + header[1]
            while length > len(message):
                message += self.socket.recv(length - len(message))
        except socket.error as e:
            if self.is_connected:
                self.is_connected = False
                self.socket.close()
                messagebox.showerror("Error", "Connection to the server is lost.")
                self.close_window = True
            raise SystemExit
        else:
            if message[:12].decode('utf-8') == "FILE_CONTENT" or message[:12].decode('utf-8') == "VOIC_CONTENT":
                name_len = message[12]
                name = message[13:13 + name_len].decode('utf-8')  
                return f"{message[:12].decode('utf-8')}|{name}", message[13 + name_len:]
            else:
                return message.decode('utf-8'), b""