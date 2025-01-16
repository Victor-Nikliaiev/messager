import ast
import socket
import threading
import sys
import time
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from PySide6 import QtUiTools as qtu
from assets.ui.chat_client_ui import Ui_ChatClient
from tools.toolkit import Tools as t


class ChatClient(qtw.QWidget, Ui_ChatClient):
    update_user_list = qtc.Signal(str)
    typing = qtc.Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        t.qt.center_widget(self)
        self.setupCredentials()
        self.updateUi()
        self.connect_to_server()

        self.typing_list = ObservableSet()
        self.typing_list.set_add_listener(self.typing_list_handler)
        self.typing_list.set_remove_listener(self.typing_list_handler)

        self.message_lineEdit.returnPressed.connect(self.send_message)
        self.send_message_pushButton.clicked.connect(self.send_message)
        self.update_user_list.connect(self.update_user_list_handler)
        self.message_lineEdit.textChanged.connect(self.handle_typing)
        self.clear_chat_pushButton.clicked.connect(self.clear_chat)

    def setupCredentials(self):
        self.host = self._setup_credential(
            "Enter host to connect to:", "Host", text="0.0.0.0"
        )
        self.port = int(self._setup_credential("Enter port:", "Port", text="1060"))
        self.username = self._setup_credential("Enter your username:", "Username")

    def updateUi(self):
        self.setWindowTitle(f"Encrypted Chat Client v1.0 - [ {self.username} ]")

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

        self.client_socket.sendall(self.username.encode())

        self.listen_thread = ListenThread(self.client_socket)
        self.listen_thread.message_received.connect(self.handle_received_message)
        self.listen_thread.start()

    def show_popup(self, message, duration=2000, critical=False):
        self.popup = PopupWindow(message, duration, critical)
        self.popup.show()

    def send_message(self):
        message = self.message_lineEdit.text()
        message = message.strip()

        if message == "":
            return

        try:
            self.client_socket.sendall(message.encode())
        except Exception as e:
            self.show_popup(e, 5000, critical=True)

        self.message_lineEdit.clear()

    def handle_received_message(self, message_bytes: bytes):
        message = message_bytes.decode()

        if message.startswith("**TYPING**"):
            print(message)
            self.add_to_typing_list(message)
            return

        if message.startswith("**NO_TYPING**"):
            print(message)
            self.remove_from_typing_list(message)
            return

        if message.startswith("**UPDATE_USER_LIST**"):
            self.update_user_list.emit(message)
            return

        if message.startswith("**SERVER_SHUTDOWN**"):
            self.show_popup(
                "Server was shut down. Connection closed", 3600000, critical=True
            )
            self.client_socket.close()
            self.setEnabled(False)
            return

        if message != "":
            username, content = message.split("~")
            item = qtw.QListWidgetItem(f"[ {username} ]: {content}")
            self.message_box_listWidget.addItem(item)
            self.message_box_listWidget.scrollToBottom()

        else:
            print("Server has closed the connection")
            self.show_popup("Server has closed the connection", 3600000, critical=True)
            self.client_socket.close()
            self.setEnabled(False)

    def update_user_list_handler(self, message):
        username_list = ast.literal_eval(message.split("**UPDATE_USER_LIST**")[1])

        self.user_list_listWidget.clear()

        for user in username_list:
            self.user_list_listWidget.addItem(user)

    def closeEvent(self, event):
        self.client_socket.close()
        self.listen_thread.terminate()
        self.listen_thread.wait()
        event.accept()

    def handle_typing(self):
        threading.Thread(target=self.send_typing_status).start()

    def send_typing_status(self):
        time.sleep(0.1)
        self.client_socket.sendall("**TYPING**".encode())

    def add_to_typing_list(self, message: str):
        username = message.split("**TYPING**")[1]
        self.typing_list.add(username)

    def remove_from_typing_list(self, message: str):
        username = message.split("**NO_TYPING**")[1]
        self.typing_list.discard(username)

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
    message_received = qtc.Signal(bytes)

    def __init__(self, client_socket: socket.socket):
        super().__init__()
        self.client_socket = client_socket
        # self.setTerminationEnabled(True)

    def run(self):
        while True:
            try:
                message = self.client_socket.recv(2048)
                if message != b"":
                    self.message_received.emit(message)
            except Exception as e:
                print(e)
                break


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
        t.qt.center_widget(self)

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
