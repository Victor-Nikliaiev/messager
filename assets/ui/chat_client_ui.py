# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'chat_client.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
import assets.icons_rc


class Ui_ChatClient(object):
    def setupUi(self, ChatClient):
        if not ChatClient.objectName():
            ChatClient.setObjectName("ChatClient")
        ChatClient.resize(662, 474)
        icon = QIcon()
        icon.addFile(
            ":/favicon/icons/chat.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        ChatClient.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(ChatClient)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.encypted_icon_label = QLabel(ChatClient)
        self.encypted_icon_label.setObjectName("encypted_icon_label")
        self.encypted_icon_label.setMaximumSize(QSize(10, 10))
        self.encypted_icon_label.setPixmap(QPixmap(":/widget/icons/padlock.png"))
        self.encypted_icon_label.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.encypted_icon_label)

        self.label_2 = QLabel(ChatClient)
        self.label_2.setObjectName("label_2")
        font = QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.message_box_listWidget = QListWidget(ChatClient)
        self.message_box_listWidget.setObjectName("message_box_listWidget")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.message_box_listWidget.sizePolicy().hasHeightForWidth()
        )
        self.message_box_listWidget.setSizePolicy(sizePolicy)
        self.message_box_listWidget.setFrameShape(QFrame.Shape.Box)
        self.message_box_listWidget.setFrameShadow(QFrame.Shadow.Raised)
        self.message_box_listWidget.setLineWidth(1)
        self.message_box_listWidget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.message_box_listWidget.setAutoScroll(True)
        self.message_box_listWidget.setAlternatingRowColors(True)
        self.message_box_listWidget.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.message_box_listWidget.setViewMode(QListView.ViewMode.ListMode)
        self.message_box_listWidget.setSortingEnabled(False)

        self.verticalLayout_3.addWidget(self.message_box_listWidget)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, -1, 0)
        self.typing_list_label = QLabel(ChatClient)
        self.typing_list_label.setObjectName("typing_list_label")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.typing_list_label.sizePolicy().hasHeightForWidth()
        )
        self.typing_list_label.setSizePolicy(sizePolicy1)
        self.typing_list_label.setStyleSheet("padding: 5px;")
        self.typing_list_label.setWordWrap(True)

        self.horizontalLayout_4.addWidget(self.typing_list_label)

        self.clear_chat_pushButton = QPushButton(ChatClient)
        self.clear_chat_pushButton.setObjectName("clear_chat_pushButton")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.clear_chat_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.clear_chat_pushButton.setSizePolicy(sizePolicy2)
        self.clear_chat_pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(
            ":/widget/icons/cleaning.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.clear_chat_pushButton.setIcon(icon1)
        self.clear_chat_pushButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_4.addWidget(self.clear_chat_pushButton)

        self.horizontalLayout_4.setStretch(0, 9)
        self.horizontalLayout_4.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.verticalLayout_3.setStretch(0, 9)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.groupBox = QGroupBox(ChatClient)
        self.groupBox.setObjectName("groupBox")
        sizePolicy1.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy1)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.user_list_listWidget = QListWidget(self.groupBox)
        self.user_list_listWidget.setObjectName("user_list_listWidget")
        sizePolicy.setHeightForWidth(
            self.user_list_listWidget.sizePolicy().hasHeightForWidth()
        )
        self.user_list_listWidget.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.user_list_listWidget)

        self.horizontalLayout.addWidget(self.groupBox)

        self.horizontalLayout.setStretch(0, 7)
        self.horizontalLayout.setStretch(1, 3)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.message_lineEdit = QLineEdit(ChatClient)
        self.message_lineEdit.setObjectName("message_lineEdit")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy3.setHorizontalStretch(7)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.message_lineEdit.sizePolicy().hasHeightForWidth()
        )
        self.message_lineEdit.setSizePolicy(sizePolicy3)
        self.message_lineEdit.setMinimumSize(QSize(0, 40))
        self.message_lineEdit.setStyleSheet("padding-left: 10px;\n" "color: auto;")
        self.message_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.message_lineEdit.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.message_lineEdit.setClearButtonEnabled(True)

        self.horizontalLayout_2.addWidget(self.message_lineEdit)

        self.send_message_pushButton = QPushButton(ChatClient)
        self.send_message_pushButton.setObjectName("send_message_pushButton")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy4.setHorizontalStretch(2)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(
            self.send_message_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.send_message_pushButton.setSizePolicy(sizePolicy4)
        self.send_message_pushButton.setMinimumSize(QSize(0, 40))
        font1 = QFont()
        font1.setPointSize(16)
        self.send_message_pushButton.setFont(font1)
        self.send_message_pushButton.setCursor(
            QCursor(Qt.CursorShape.PointingHandCursor)
        )
        icon2 = QIcon()
        icon2.addFile(
            ":/buttons/icons/send-message.png",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.send_message_pushButton.setIcon(icon2)
        self.send_message_pushButton.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.send_message_pushButton)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ChatClient)

        QMetaObject.connectSlotsByName(ChatClient)

    # setupUi

    def retranslateUi(self, ChatClient):
        ChatClient.setWindowTitle(
            QCoreApplication.translate("ChatClient", "Encrypted Chat Client v1.0", None)
        )
        self.encypted_icon_label.setText("")
        self.label_2.setText(
            QCoreApplication.translate(
                "ChatClient",
                "This chat is secured with RSA and AES encryption for your messages and data.",
                None,
            )
        )
        self.typing_list_label.setText("")
        # if QT_CONFIG(tooltip)
        self.clear_chat_pushButton.setToolTip(
            QCoreApplication.translate("ChatClient", "Clear chat", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.clear_chat_pushButton.setText("")
        self.groupBox.setTitle(
            QCoreApplication.translate("ChatClient", "Connected users:", None)
        )
        self.message_lineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "ChatClient",
                "Enter your message here and press Enter or Send button...",
                None,
            )
        )
        self.send_message_pushButton.setText(
            QCoreApplication.translate("ChatClient", " Send", None)
        )

    # retranslateUi
