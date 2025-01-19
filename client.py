import ast
import json
import os
import re
import socket
import threading
import sys
import time
from xml.etree.ElementInclude import include
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from PySide6 import QtUiTools as qtu
from assets.ui.chat_client_ui import Ui_ChatClient
from tools.toolkit import Tools as t
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class PROTO:  # PROTOCOL
    UPD_ULIST = "UPD_ULIST"
    USER_NAME = "USER_NAME"
    NO_TYPING = "NO_TYPING"
    SRV_DOWN = "SRV_DOWN"
    TYPING = "TYPING"
    FILE = "FILE"
    MSG = "MSG"
    EMPTY = ""


class ChatClient(qtw.QWidget, Ui_ChatClient):
    typing = qtc.Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        t.qt.center_widget(self)
        self.setupCredentials()
        self.updateUi()
        self.connect_to_server()

        self.typing_list = ObservableSet()
        self.connection_closed = False

        self.typing_list.set_add_listener(self.typing_list_handler)
        self.typing_list.set_remove_listener(self.typing_list_handler)

        self.message_lineEdit.returnPressed.connect(self.send_client_message)
        self.send_message_pushButton.clicked.connect(self.send_client_message)
        self.message_lineEdit.textChanged.connect(self.handle_typing)
        self.clear_chat_pushButton.clicked.connect(self.clear_chat)

        self.in_message = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.in_message.setAudioOutput(self.audio_output)
        self.in_message.setSource("assets/audio/in_message.mp3")

    def setupCredentials(self):
        self.host = self._setup_credential(
            "Enter host to connect to:", "Host", text="0.0.0.0"
        )
        self.port = int(self._setup_credential("Enter port:", "Port", text="1060"))
        self.username = self._setup_credential("Enter your username:", "Username")

    def updateUi(self):
        self.setWindowTitle(f"Encrypted Chat Client v1.0 - [ {self.username} ]")
        # self.message_box_listWidget.setResizeMode(qtw.QListWidget.Adjust)

    def _show_critical_error(
        self,
        option="",
        title="Error",
    ):
        message = f"{option} must not be empty!"
        qtw.QMessageBox.critical(self, title, message)

    def _setup_credential(self, label, option="", title="Connection...", text=""):
        param, _ = qtw.QInputDialog.getText(self, title, label, text=text)
        param = param.strip()

        if param == "":
            self._show_critical_error(option)
            sys.exit(0)

        return param

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.settimeout(5)  # 5 seconds timeout
        try:
            self.client_socket.connect((self.host, self.port))
            self.show_popup("Successfully connected to the server.")
        except Exception as e:
            self.show_popup(
                f"Unable to connect to server with host: {self.host} and port: {self.port}\n{e}",
                critical=True,
                duration=60000,
            )

        self.username_length = len(self.username.encode())
        payload = f"{PROTO.USER_NAME.ljust(10)}{self.username_length:04}{self.username}"
        self.client_socket.sendall(payload.encode())

        self.listen_thread = ListenThread(self.client_socket)
        self.listen_thread.client_message_received.connect(
            self.handle_received_client_message
        )
        self.listen_thread.service_message_received.connect(
            self.handle_received_service_message
        )
        self.listen_thread.receiving_file.connect(self.handle_receiving_file)
        self.listen_thread.start()

        self.user_list_listWidget.itemClicked.connect(self.handle_on_user_click)

    def handle_on_user_click(self, item: qtw.QListWidgetItem):
        username = item.text()
        if username == self.username:
            return

        self.message_lineEdit.setText(self.message_lineEdit.text() + f"@{username}")
        self.message_lineEdit.setFocus()

    def show_popup(self, message, duration=2000, critical=False):
        self.popup = PopupWindow(message, duration, critical)
        t.qt.center_widget(self.popup, parent=self)
        self.popup.show()

    def send_client_message(self):
        msg = self.message_lineEdit.text()
        msg = msg.strip()

        if msg == "":
            return

        protocol = PROTO.MSG.ljust(10)
        msg_length = len(msg.encode())

        payload = f"{protocol}{msg_length:04}{msg}"

        try:
            self.client_socket.sendall(payload.encode())
        except Exception as e:
            self.show_popup(e, 5000, critical=True)
        finally:
            self.message_lineEdit.clear()

    def send_service_message(self, protocol: str, data: str):
        protocol = protocol.ljust(10)
        data_length = len(data.encode())
        payload = f"{protocol}{data_length:04}{data}"
        self.client_socket.sendall(payload.encode())

    def handle_received_client_message(self, username, message: str):

        # if message.startswith("**TYPING**"):
        #     print(message)
        #     self.add_to_typing_list(message)
        #     return

        # if message.startswith("**NO_TYPING**"):
        #     print(message)
        #     self.remove_from_typing_list(message)
        #     return

        # if message.startswith("**UPDATE_USER_LIST**"):
        #     self.update_user_list.emit(message)
        #     return

        # if message.startswith("**SERVER_SHUTDOWN**"):
        #     self.show_popup(
        #         "Server was shut down. Connection closed", 3600000, critical=True
        #     )
        #     self.client_socket.close()
        #     self.setEnabled(False)
        #     return

        if message == PROTO.EMPTY:
            print("Server was shut down. Connection closed.")
            self.show_popup(
                "Server was shut down. Connection closed.", 3600000, critical=True
            )
            self.client_socket.close()
            self.setEnabled(False)
            self.connection_closed = True
            return

        item = qtw.QListWidgetItem()
        label = self.format_message(username, message)
        self.message_box_listWidget.addItem(item)
        self.message_box_listWidget.setItemWidget(item, label)
        self.message_box_listWidget.scrollToBottom()

        # if username != self.username:
        #     self.in_message.play()

    def extract_nickname(self, message):
        # Regex pattern to match nicknames starting with @
        pattern = r"@(\w+)"
        match = re.search(pattern, message)
        if match:
            return match.group(0)  # Return the full match (with "@")
        return None  # No nickname found

    def format_message(self, username: str, message: str) -> qtw.QLabel:
        username_color = "#0887aa"
        message_color = "green"
        own_nickname_color = "#c13310"

        if username == "SERVER":
            username_color = "#676767"
            message_color = "#676767"

        if "@" in message:
            nickname = self.extract_nickname(message)
            if nickname:
                if nickname == "@" + self.username:
                    formatted_nickname = f'<span style="color:{own_nickname_color};"><strong>{nickname}</strong></span>'
                    message = message.replace(nickname, formatted_nickname)
                    # If current nickname was mentioned in the chat, play audio notification
                    self.in_message.play()

        label = qtw.QLabel(
            f'<span style="color:{username_color}; font-weight:bold;">[{username}]</span>: '
            f'<span style="color:{message_color};">{message}</span>'
        )
        return label

    def handle_received_service_message(self, protocol, data):
        if protocol == PROTO.UPD_ULIST:
            self.update_user_list(data)
        if protocol == PROTO.SRV_DOWN:
            self.handle_server_shutdown()
        if protocol == PROTO.TYPING:
            # self.add_to_typing_list(data)
            self.typing_list.add(data)
        if protocol == PROTO.NO_TYPING:
            # self.remove_from_typing_list(data)
            self.typing_list.discard(data)

    def handle_server_shutdown(self):
        self.show_popup(
            "Server was shut down. Connection closed.", 3600000, critical=True
        )
        self.client_socket.close()
        self.setEnabled(False)

    def handle_receiving_file(self):
        pass

    def update_user_list(self, data):
        self.user_list_listWidget.clear()

        active_users_list = json.loads(data)

        for user in active_users_list:
            self.user_list_listWidget.addItem(user)

    def closeEvent(self, event):
        self.client_socket.close()
        self.listen_thread.terminate()
        self.listen_thread.wait()
        event.accept()

    def handle_typing(self):
        threading.Thread(target=self.send_typing_status).start()

    def send_typing_status(self):
        self.send_service_message(PROTO.TYPING, self.username)

    # def add_to_typing_list(self, username):
    #     self.typing_list.add(username)

    # def remove_from_typing_list(self, username):
    #     self.typing_list.discard(username)

    def typing_list_handler(self):
        self.typing_list_label.setText("")

        if len(self.typing_list) == 0:
            return

        verb = "is" if len(self.typing_list) == 1 else "are"
        users = ", ".join(self.typing_list)
        message = f"{users} {verb} typing..."

        # for user in self.typing_list:
        #     message += f"{user}, "
        # message = message[:-2] + postfix

        self.typing_list_label.setText(message)

    def clear_chat(self):
        self.message_box_listWidget.clear()


class ListenThread(qtc.QThread):
    client_message_received = qtc.Signal(str, str)
    service_message_received = qtc.Signal(str, str)
    receiving_file = qtc.Signal(bytes)

    def __init__(self, client_socket: socket.socket):
        super().__init__()
        self.client_socket = client_socket
        # self.setTerminationEnabled(True)

    def run(self):
        while True:
            try:
                protocol = self.client_socket.recv(10).decode().strip()

                if protocol == PROTO.EMPTY:
                    self.client_message_received.emit(PROTO.EMPTY, PROTO.EMPTY)

                if protocol == PROTO.MSG:
                    username_length = self.get_received_length()
                    username = self.get_received_data(username_length)
                    message_length = self.get_received_length()
                    message = self.get_received_data(message_length)

                    self.client_message_received.emit(username, message)

                if protocol == PROTO.UPD_ULIST:
                    user_list_length = self.get_received_length()
                    user_list = self.get_received_data(user_list_length)
                    self.service_message_received.emit(PROTO.UPD_ULIST, user_list)

                if protocol == PROTO.TYPING:
                    username_length = self.get_received_length()
                    username = self.get_received_data(username_length)
                    self.service_message_received.emit(PROTO.TYPING, username)

                if protocol == PROTO.NO_TYPING:
                    username_length = self.get_received_length()
                    username = self.get_received_data(username_length)
                    self.service_message_received.emit(PROTO.NO_TYPING, username)

            except Exception as e:
                print(e)
                break

    def get_received_length(self):
        return int(self.client_socket.recv(4).decode().strip())

    def get_received_data(self, length):
        return self.client_socket.recv(length).decode().strip()


class PopupWindow(qtw.QWidget):
    def __init__(self, message, duration=3000, critical=False):
        super().__init__()

        # Configure the pop-up window
        self.setWindowFlags(
            self.windowFlags()
            | qtc.Qt.FramelessWindowHint
            | qtc.Qt.Tool
            | qtc.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(qtc.Qt.WA_TranslucentBackground)
        self.setAttribute(qtc.Qt.WA_ShowWithoutActivating)

        # Set up the layout and message
        layout = qtw.QVBoxLayout()
        label = qtw.QLabel(message)

        if critical:
            label.setStyleSheet(
                "background-color: #ff4f4f; color: #fff; padding: 10px; border-radius: 5px;"
            )
        else:
            label.setStyleSheet(
                "background-color: #2e6714; color: #fff; padding: 10px; border-radius: 5px;"
            )

        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()
        qtc.QTimer.singleShot(duration, self.close)


class ObservableSet(set):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_listener = None
        self._remove_listener = None

    def set_add_listener(self, listener):
        self._add_listener = listener

    def set_remove_listener(self, listener):
        self._remove_listener = listener

    def add(self, item):
        super().add(item)

        if self._add_listener:
            self._add_listener()

    def remove(self, item):
        super().remove(item)

        if self._remove_listener:
            self._remove_listener()

    def discard(self, item):
        super().discard(item)

        if self._remove_listener:
            self._remove_listener()


def main():

    app = qtw.QApplication(sys.argv)
    window = ChatClient()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
