import json
import os
import platform
import re
import socket
import threading
import sys
import time


from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from PySide6 import QtUiTools as qtu
import pyperclip
from assets.emoji.QCustomEmojiPicker import QCustomEmojiPicker
from assets.ui.chat_client_ui import Ui_ChatClient
from backend import sm
from backend import PROTO
from backend import CONSTS
from backend.encryption import EncryptionManager
from backend.managers import RateLimitedManager
from backend.managers import HeaderReceiver
from backend.managers.client_ft_manager import ClientFileTransferManager
from screens.confirm_file_screen import ConfirmFileScreen
from tools.toolkit import Tools as t
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import subprocess
import sys
import tempfile


mutex = qtc.QMutex()


class ChatClient(qtw.QWidget, Ui_ChatClient):
    # typing = qtc.Signal(str)
    # update_send_file_button_status = qtc.Signal()
    save_file = qtc.Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        t.qt.center_widget(self)

        try:
            ### This order must not be changed
            self.setupCredentials()
            self.updateUi()
            self.setup_font_system(self)
            self.setup_font_system(self.message_lineEdit)
            self.connect_to_server()
            self.connect_to_slots()
            ###
        except Exception as e:
            print(e)

        self.original_key_press_event = self.message_lineEdit.keyPressEvent
        self.message_lineEdit.keyPressEvent = self.my_key_press_event

        self.typing_lock = threading.Lock()
        self.typing_list = ObservableSet()
        self.typing_list.set_add_listener(self.typing_list_handler)
        self.typing_list.set_remove_listener(self.typing_list_handler)

        self.rate_manager = RateLimitedManager(0.9)

        self.connection_closed = False
        self.tfile_paths = []  # temp file paths

        self.setup_audio_system()

    def connect_to_slots(self):
        self.emoji_chooser_pushButton.clicked.connect(
            lambda: self.showEmojiPicker(self.message_lineEdit)
        )
        self.message_lineEdit.returnPressed.connect(self.send_client_message)
        self.send_message_pushButton.clicked.connect(self.send_client_message)
        self.message_lineEdit.textChanged.connect(self.handle_typing)
        self.clear_chat_pushButton.clicked.connect(self.clear_chat)
        self.choose_file_option.triggered.connect(self.choose_file)
        self.send_file_pushButton.clicked.connect(self.show_menu)
        sm.start_send_file.connect_method(self.send_file_handler)
        self.user_list_listWidget.itemClicked.connect(self.handle_on_user_click)
        self.save_file.connect(self.decrypt_and_save_file)

    def setup_audio_system(self):
        self.in_message = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.in_message.setAudioOutput(self.audio_output)
        self.in_message.setSource("assets/audio/in_message.wav")

    def setup_font_system(self, entity):
        text_font = qtg.QFont()
        text_font.setPixelSize(18)
        text_font.setLetterSpacing(qtg.QFont.PercentageSpacing, 110)
        emoji_font1 = qtg.QFont("Noto Color Emoji")
        emoji_font2 = qtg.QFont("Segoe UI Emoji")
        text_font.setFamilies(
            [text_font.family(), emoji_font1.family(), emoji_font2.family()]
        )

        entity.setFont(text_font)

    def setupCredentials(self):
        self.host = self._setup_credential(
            "Enter host to connect to:", "Host", text=CONSTS.HOST
        )
        self.port = int(self._setup_credential("Enter port:", "Port", text=CONSTS.PORT))
        self.username = self._setup_credential("Enter your username:", "Username")

        self.em = EncryptionManager()
        self.server_public_key = None

    def updateUi(self):
        self.setWindowTitle(f"Encrypted Chat Client v1.0 - [ {self.username} ]")
        self.emoji_font = qtg.QFont("Noto Color Emoji")
        self.setFont(self.emoji_font)
        self.message_lineEdit.setFont(self.emoji_font)
        self.message_box_listWidget.setFont(self.emoji_font)

        self.file_menu = qtw.QMenu(self)
        self.choose_file_option = self.file_menu.addAction("Send File")
        self.file_menu.setCursor(qtc.Qt.PointingHandCursor)

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

    def showEmojiPicker(self, target_widget):
        emoji_picker = QCustomEmojiPicker(
            target=target_widget, parent=self, itemsPerRow=16
        )

        emoji_picker.show()

        # Add shadow effect
        effect = emoji_picker.graphicsEffect()
        if effect is None:
            effect = qtw.QGraphicsDropShadowEffect(emoji_picker)
        effect.setColor(qtg.QColor(30, 30, 30, 200))
        effect.setBlurRadius(20)
        effect.setXOffset(0)
        effect.setYOffset(0)
        emoji_picker.setGraphicsEffect(effect)

    def show_menu(self):
        self.file_menu.exec(
            self.send_file_pushButton.mapToGlobal(
                self.send_file_pushButton.rect().bottomLeft()
            )
        )

    def choose_file(self):
        file_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Select a file to send", "", "All Files (*);;"
        )

        if file_path:
            sm.dropped_file_path.signal.emit(file_path)
            self.confirm_file_screen = ConfirmFileScreen(self)
            self.confirm_file_screen.show()

    def my_key_press_event(self, event):

        if event.key() == qtc.Qt.Key_Return or event.key() == qtc.Qt.Key_Enter:
            if event.modifiers() == qtc.Qt.ShiftModifier:
                # Insert a newline character when Shift + Enter is pressed
                current_text = self.message_lineEdit.text()
                self.message_lineEdit.setText(current_text + "\n")
                return

            self.original_key_press_event(event)
        self.original_key_press_event(event)

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.host, self.port))
            self.show_popup("Successfully connected to the server.")

        except Exception as e:
            self.show_popup(
                f"Unable to connect to server with host: {self.host} and port: {self.port}\n{e}",
                critical=True,
                duration=60000,
            )

        ### This order must not be changed!
        self.send_client_public_key()
        self.get_server_public_key()
        self.send_aes_key()
        self.send_username()
        self.start_listening()
        ###

    def send_client_public_key(self):
        public_key_bytes = self.em.serialize_public_key(self.em.public_key)
        public_key_length = len(public_key_bytes)
        payload = f"{PROTO.PUB_KEY.ljust(10)}{public_key_length:04}"
        self.client_socket.sendall(payload.encode() + public_key_bytes)

    def get_server_public_key(self):
        protocol = self.client_socket.recv(10).decode().strip()
        if protocol == PROTO.PUB_KEY:
            key_length = int(self.client_socket.recv(4).decode().strip())
            server_public_key_bytes = self.client_socket.recv(key_length)
            self.server_public_key = self.em.deserialize_public_key(
                server_public_key_bytes
            )

    def send_aes_key(self):
        encrypted_aes_key = self.em.encrypt_aes_key(
            self.em.aes_key, self.server_public_key
        )
        encrypted_aes_length = len(encrypted_aes_key)
        payload = f"{PROTO.AES_KEY.ljust(10)}{encrypted_aes_length:04}"
        self.client_socket.sendall(payload.encode() + encrypted_aes_key)

    def send_username(self):
        encrypted_username = self.em.encrypt_text(self.username, self.em.aes_key)
        username_length = len(encrypted_username)
        payload = f"{PROTO.USER_NAME.ljust(10)}{username_length:04}"
        self.client_socket.sendall(payload.encode() + encrypted_username)

    def start_listening(self):
        self.listen_thread = ListenThread(self.client_socket)
        self.listen_thread.client_message_received.connect(
            self.handle_received_client_message
        )
        self.listen_thread.service_message_received.connect(
            self.handle_received_service_message
        )
        self.listen_thread.pub_key_received.connect(self.handle_received_pub_key)
        self.listen_thread.free_space_error.connect(self.handle_free_space_error)
        self.listen_thread.file_received.connect(self.handle_received_file)
        self.listen_thread.add_tfile_to_rmlist.connect(self.handle_add_tfile_to_rmlist)
        self.listen_thread.start()

    def start_receive_file_thread(self, filename, filesize):
        self.receive_file_thread = ReceiveFileThread(
            self.client_socket, filename, filesize
        )
        self.receive_file_thread.start()

    def handle_on_user_click(self, item: qtw.QListWidgetItem):
        username = item.text()
        if username == self.username:
            return

        self.message_lineEdit.setText(self.message_lineEdit.text() + f"@{username} ")
        self.message_lineEdit.setFocus()

    def handle_add_tfile_to_rmlist(self, tfile_path):
        self.tfile_paths.append(tfile_path)

    def show_popup(self, message, duration=2000, critical=False):
        self.popup = PopupWindow(message, duration, critical)
        t.qt.center_widget(self.popup, parent=self)
        self.popup.show()

    def send_client_message(self):
        msg = self.message_lineEdit.text()
        msg = msg.strip()

        if msg == "":
            return

        if msg.startswith("@"):
            nickname = self.extract_nickname(msg)
            if nickname:
                self.send_private_message_to(nickname, msg)
                return

        protocol = PROTO.MSG.ljust(10)

        encrypted_message = self.em.encrypt_text(msg, self.em.aes_key)
        msg_length = len(encrypted_message)

        payload = protocol.encode() + f"{msg_length:04}".encode() + encrypted_message

        try:
            self.client_socket.sendall(payload)
        except Exception as e:
            self.show_popup(e, 5000, critical=True)
        finally:
            self.message_lineEdit.clear()

    def send_private_message_to(self, nickname: str, message: str):
        protocol = PROTO.PRIV_MSG.ljust(10)
        message = message.replace(nickname, "").strip()
        nickname = nickname[1:]
        encrypted_nickname = self.em.encrypt_text(nickname, self.em.aes_key)
        encrypted_message = self.em.encrypt_text(message, self.em.aes_key)
        nickname_length = len(encrypted_nickname)
        message_length = len(encrypted_message)
        payload = (
            protocol.encode()
            + f"{nickname_length:04}".encode()
            + encrypted_nickname
            + f"{message_length:04}".encode()
        )

        self.client_socket.sendall(payload)
        self.client_socket.sendall(encrypted_message)
        self.message_lineEdit.clear()

    def send_service_message(self, protocol: str, data: str):
        protocol = protocol.ljust(10)
        data_length = len(data.encode())
        payload = f"{protocol}{data_length:04}{data}"
        self.client_socket.sendall(payload.encode())

    def handle_received_pub_key(self, public_key_bytes: bytes):
        self.server_public_key = self.em.deserialize_public_key(public_key_bytes)

    def handle_received_client_message(self, username: bytes, message: bytes):
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

        decrypted_username = self.em.decrypt_text(username, self.em.aes_key)
        decrypted_message = self.em.decrypt_text(message, self.em.aes_key)

        label = self.format_message(decrypted_username, decrypted_message)
        item.setSizeHint(label.sizeHint())
        label.setTextInteractionFlags(qtc.Qt.TextSelectableByMouse)

        self.message_box_listWidget.addItem(item)
        self.message_box_listWidget.setItemWidget(item, label)
        self.message_box_listWidget.scrollToBottom()

    def extract_nickname(self, message):
        # Regex pattern to match nicknames starting with @
        pattern = r"@(\w+)"
        match = re.search(pattern, message)
        if match:
            return match.group(0)  # Return the full match (with "@")
        return None  # No nickname found

    def format_message(self, username: str, message: str, clickable=False):
        username_color = "#0887aa"
        message_color = "#0cb482"
        own_nickname_color = "#c13310"

        if username == "SERVER":
            username_color = "#df6c81"
            message_color = "#df6c81"

        if "@" in message:
            nickname = self.extract_nickname(message)
            if nickname:
                if nickname == "@" + self.username:
                    formatted_nickname = f'<span style="color:{own_nickname_color};"><strong>{nickname}</strong></span>'
                    message = message.replace(nickname, formatted_nickname)
                    # If current nickname was mentioned in the chat, play audio notification
                    self.in_message.play()

        text_decorator = ""

        if clickable:
            text_decorator = "text-decoration: underline; font-weight: bold;"
            message_color = "#9b44b3"

        label = ClickableLabel(
            f'<span style="color:{username_color}; font-weight:bold;">[{username}]</span>: '
            f'<span style="color:{message_color};{text_decorator}">{message}</span>',
            clickable=clickable,
        )
        self.setup_font_system(label)
        label.setStyleSheet("padding: 0 0 5px 0; margin-bottom: 0px;")
        label.setText(label.text().replace("\n", "<br>"))
        label.setWordWrap(True)  # Enable word wrapping
        label.setContentsMargins(0, 0, 0, 0)
        # label.adjustSize()
        # label.setAlignment(qtc.Qt.AlignLeft)

        label.setMinimumWidth(self.message_box_listWidget.width())

        return label

    def handle_received_service_message(self, protocol: str, data: bytes):
        if protocol == PROTO.UPD_ULIST:
            self.update_user_list(data)
        if protocol == PROTO.SRV_DOWN:
            self.handle_server_shutdown()
        if protocol == PROTO.TYPING:
            decrypted_user = self.em.decrypt_text(data, self.em.aes_key)
            self.typing_list.add(decrypted_user)
        if protocol == PROTO.NO_TYPING:
            decrypted_user = self.em.decrypt_text(data, self.em.aes_key)
            self.typing_list.discard(decrypted_user)

    def handle_received_file(
        self, temp_file_path: str, encrypted_filename: bytes, encrypted_username: bytes
    ):
        decrypted_filename = self.em.decrypt_text(encrypted_filename, self.em.aes_key)
        decrypted_username = self.em.decrypt_text(encrypted_username, self.em.aes_key)
        print("Finish line:")
        print("Temp file path:", temp_file_path)
        print("Filename:", decrypted_filename)
        print("Sender:", decrypted_username)

        self.add_file_link_to_chat(
            temp_file_path, decrypted_filename, decrypted_username
        )

    def handle_free_space_error(self):
        qtw.QMessageBox.critical(self, "Drive Error", "Free space is not enough!")

    def add_file_link_to_chat(self, temp_filepath: str, filename: str, username: str):

        item = qtw.QListWidgetItem()

        label = self.format_message(username, f"{filename}", clickable=True)
        label.clicked.connect(lambda: self.save_file.emit(temp_filepath, filename))
        item.setSizeHint(label.sizeHint())

        # label.setSizePolicy(item.sizeHint())

        # label.setFixedSize(item_size)
        # label.setMaximumHeight(item.sizeHint().height())
        self.message_box_listWidget.addItem(item)
        self.message_box_listWidget.setItemWidget(item, label)
        self.message_box_listWidget.scrollToBottom()

        # Example: Add this link to a QListWidget or UI element in your chat

    def handle_server_shutdown(self):
        self.show_popup(
            "Server was shut down. Connection closed.", 3600000, critical=True
        )
        self.client_socket.close()
        self.setEnabled(False)

    # def handle_receiving_file(self, filename, file_size):
    #     print(f"Receiving file: {filename} ({file_size} bytes)")
    #     file_data = bytearray()
    #     while True:
    #         chunk = self.client_socket.recv(4096)
    #         if not chunk:  # File transfer complete
    #             break
    #         file_data.extend(chunk)
    #     print(f"Received file: {filename}")

    def update_user_list(self, data: bytes):
        self.user_list_listWidget.clear()

        decrypted_json = self.em.decrypt_text(data, self.em.aes_key)
        active_users_list = json.loads(decrypted_json)

        for user in active_users_list:
            self.user_list_listWidget.addItem(user)

    def closeEvent(self, event):
        self.client_socket.close()
        self.listen_thread.terminate()
        self.listen_thread.wait()
        self.delete_tfiles()
        threading.Thread(target=ClipboardClearingThread(self).run, daemon=True).start()
        event.accept()

    def delete_tfiles(self):
        for path in self.tfile_paths:
            os.remove(path)

    def handle_typing(self):
        threading.Thread(target=self.send_typing_status).start()

    def send_typing_status(self):
        with self.rate_manager as released:
            if released:
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

    def send_file_handler(self, filepath):
        self.send_file_thread = SendFileThread(self.client_socket, filepath, self.em)
        self.send_file_thread.start()

    def clear_chat(self):
        self.message_box_listWidget.clear()

    def decrypt_and_save_file(self, filepath: str, filename: str):
        save_path, _ = qtw.QFileDialog.getSaveFileName(None, "Save File", filename)
        if save_path:
            with open(filepath, "rb") as temp_file, open(save_path, "wb") as final_file:
                try:
                    while chunk := temp_file.read(CONSTS.ENCRYPTED_CHUNK_SIZE):
                        decrypted_chunk = self.em.decrypt_file_chunk(
                            chunk, self.em.aes_key
                        )

                        if CONSTS.EOF_MARKER in decrypted_chunk:
                            decrypted_chunk = decrypted_chunk.rstrip(CONSTS.ZERO_BYTE)
                            decrypted_chunk = decrypted_chunk.replace(
                                CONSTS.EOF_MARKER, CONSTS.EMPTY_BYTE_VALUE
                            )

                        final_file.write(decrypted_chunk)
                except Exception as e:
                    print(e)


class ListenThread(qtc.QThread):
    client_message_received = qtc.Signal(bytes, bytes)
    service_message_received = qtc.Signal(str, bytes)
    file_received = qtc.Signal(str, bytes, bytes)
    free_space_error = qtc.Signal()
    add_tfile_to_rmlist = qtc.Signal(str)
    pub_key_received = qtc.Signal(bytes)

    def __init__(self, client_socket: socket.socket):
        super().__init__()
        self.client_socket = client_socket
        self.client_ft_socket = None
        # self.setTerminationEnabled(True)

    def run(self):
        while True:
            try:

                protocol = self.client_socket.recv(10).decode().strip()
                print("Protocol:", protocol)

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

                if protocol == PROTO.FT_REQUEST:
                    with ClientFileTransferManager(
                        self.client_socket, receive=True
                    ) as cftm:
                        (
                            client_ft_socket,
                            encrypted_username,
                            encrypted_filename,
                            file_size,
                        ) = cftm

                        free_disk_space = self.get_free_disk_space()

                        if free_disk_space <= file_size:
                            self.free_space_error.emit()
                            continue

                        if not client_ft_socket:
                            continue

                        self.client_ft_socket = client_ft_socket

                        temp_file_path = self.receive_file(file_size)
                        self.add_tfile_to_rmlist.emit(temp_file_path)
                        self.file_received.emit(
                            temp_file_path, encrypted_filename, encrypted_username
                        )

                # if protocol == PROTO.PUB_KEY:
                #     key_length = self.get_received_length()
                #     pub_key_bytes = self.client_socket.recv(key_length)
                #     self.pub_key_received.emit(pub_key_bytes)

            except Exception as e:
                print(e)
                break

    def get_received_length(self):
        return int(self.client_socket.recv(4).decode().strip())

    def get_received_data(self, length):
        return self.client_socket.recv(length)

    def receive_file(self, filesize: int):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            received_size = 0
            chunk_index = 0

            while received_size < filesize:
                try:
                    chunk = self.client_ft_socket.recv(CONSTS.ENCRYPTED_CHUNK_SIZE)
                    if not chunk:
                        print("No more data received, waiting...")
                        time.sleep(1)
                        continue

                    if len(chunk) != CONSTS.ENCRYPTED_CHUNK_SIZE:
                        print(
                            f"Incomplete chunk received (size: {len(chunk)}), retrying..."
                        )
                        continue

                    self.client_ft_socket.send(f"ACK{chunk_index:06}".encode())

                    received_size += CONSTS.ORIGINAL_CHUNK_SIZE
                    chunk_index += 1
                    temp_file.write(chunk)
                    print(f"Received chunk {chunk_index}/{filesize}")
                except Exception as e:
                    print(f"Error receiving chunk: {e}")
                    break

            print("Finished receiving file")
            print(f"Received: {received_size}")
            print(f"Original size: {filesize}")
        return temp_file.name

    def get_free_disk_space(path=None):
        if os.name == "nt":  # Windows
            path = "C:\\"
        else:
            path = "/"
        statvfs = os.statvfs(path)
        free_space = statvfs.f_bavail * statvfs.f_frsize  # Free blocks * block size
        return free_space  # Free space in bytes


class SendFileThread(qtc.QThread):
    def __init__(
        self, client_socket: socket.socket, filepath: str, em: EncryptionManager
    ):
        super().__init__()
        self.setTerminationEnabled(True)
        self.client_socket = client_socket
        self.filepath = filepath
        self.em = em

    def run(self):
        with ClientFileTransferManager(self.client_socket) as client_ft_socket:
            protocol = PROTO.FILE.ljust(10)
            filename: str = os.path.basename(self.filepath)
            encrypted_filename = self.em.encrypt_text(filename, self.em.aes_key)
            filename_length = f"{len(encrypted_filename):04}"
            file_size = os.path.getsize(self.filepath)
            file_size = f"{file_size:010}"

            file_payload = (
                protocol.encode()
                + filename_length.encode()
                + encrypted_filename
                + file_size.encode()
            )
            print("Send_file_payload:", file_payload)

            client_ft_socket.sendall(file_payload)

            with open(self.filepath, "rb") as file:
                chunk_index = 0

                while chunk := file.read(CONSTS.ORIGINAL_CHUNK_SIZE):
                    is_last_chunk = len(chunk) < CONSTS.ORIGINAL_CHUNK_SIZE

                    if is_last_chunk:
                        print("Size of last chunk:", len(chunk))
                        chunk += CONSTS.EOF_MARKER
                        chunk += CONSTS.ZERO_BYTE * (
                            CONSTS.ORIGINAL_CHUNK_SIZE - len(chunk)
                        )

                    encrypted_chunk = self.em.encrypt_file_chunk(chunk, self.em.aes_key)
                    chunk_sent = False
                    retries = 0
                    max_retries = 5

                    while not chunk_sent and retries < max_retries:
                        client_ft_socket.send(encrypted_chunk)
                        print("Size of sent encrypted chunk: ", len(encrypted_chunk))

                        try:
                            client_ft_socket.settimeout(5)
                            ack = client_ft_socket.recv(8)
                            if ack == f"ACK{chunk_index:06}".encode():
                                chunk_sent = True
                            else:
                                print(
                                    f"Invalid ACK for chunk {chunk_index} retrying..."
                                )
                                print("Received:", ack)
                        except socket.timeout:
                            print(
                                f"Timeout waiting for ACK for chunk {chunk_index}, retrying..."
                            )
                            retries += 1
                        finally:
                            client_ft_socket.settimeout(None)

                    if retries >= max_retries:
                        print(
                            f"Failed to send chunk {chunk_index} after {max_retries} retries. Aborting..."
                        )
                        return

                    chunk_index += 1

                print("Successfully sent...")


class ReceiveFileThread(qtc.QThread):
    def __init__(self, client_socket: socket.socket, filename, filesize):
        super().__init__()
        self.setTerminationEnabled(True)

        self.client_socket = client_socket
        self.filename = filename
        self.filesize = filesize

    def run(self):
        print("From ReceiveFileThread")

        file_data = bytearray()
        while True:
            chunk = self.client_socket.recv(4096)
            if not chunk:  # File transfer complete
                break
            file_data.extend(chunk)
        print(f"Received file: {self.filename}")


class ClipboardClearingThread:
    def __init__(self, client_instance: ChatClient):
        self.client_instance = client_instance

    def run(self):
        if platform.system() == "Linux":
            if self.is_xclip_available() is False:
                self.show_popup()
                return

        pyperclip.copy("")

    def is_xclip_available(self):
        try:
            subprocess.run(["xclip", "-version"], check=True, stdout=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def show_popup(self):
        self.client_instance.popup = PopupWindow(
            "xclip is not installed. please run: 'sudo apt install xclip' on your system.",
            3600000,
            critical=True,
        )
        self.client_instance.popup = t.qt.center_widget(self.client_instance.popup)
        self.client_instance.popup.show()

        self.client_instance.client_socket.close()
        self.client_instance.setEnabled(False)


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


class ClickableLabel(qtw.QLabel):
    clicked = qtc.Signal()

    def __init__(self, *args, clickable=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.clickable = clickable
        if self.clickable:
            self.setMouseTracking(True)
            self.setCursor(qtc.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if self.clickable:
            if event.button() == qtc.Qt.LeftButton:
                self.clicked.emit()
        else:
            event.accept()


def main():

    app = qtw.QApplication(sys.argv)
    window = ChatClient()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
