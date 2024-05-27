# Chat Room

## Overview

This project is a chat program based on Socket network programming, which implements communication between the client and the server. The project is designed in a C/S model, using the TCP protocol for data transmission, and integrates various communication features, including private chat, group chat, file transfer, and voice call.

## Features

- **Registration and Login**: Users can register and log in with preset account passwords.
- **Private and Group Chat**: Supports private or group chatting in the chat room.
- **File Transfer**: Users can send files to online or offline users, with support for offline file transfer and file resumption.
- **Voice Call**: Real-time voice call functionality between users.
- **NAT Penetration**: Although not tested in a symmetric network environment, the project design considers NAT penetration to support P2P communication.

## Technology Stack

- **Backend**: Custom application layer protocol and Socket library for communication logic processing.
- **Frontend**: PyQt6 framework for client interface design, implementing multi-threading and asynchronous non-blocking communication.

## Environment

- Python 3.x
- PyQt6
- pyaudio (for voice functionality only)

## Installation Guide

1. Ensure the Python environment is installed.
2. Install the required libraries:
   ```bash
   pip install PyQt6 pyaudio
   ```
3. Clone or download this project locally.
4. Run the server and client programs.

## Usage

1. Start the server program.
2. Run the client program and register or log in.
3. Choose private chat, group chat, file transfer, or voice call features as needed.

---