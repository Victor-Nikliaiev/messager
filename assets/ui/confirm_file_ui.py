# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'confirm_file.ui'
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
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
import assets.icons_rc


class Ui_ConfirmFile(object):
    def setupUi(self, ConfirmFile):
        if not ConfirmFile.objectName():
            ConfirmFile.setObjectName("ConfirmFile")
        ConfirmFile.resize(400, 250)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConfirmFile.sizePolicy().hasHeightForWidth())
        ConfirmFile.setSizePolicy(sizePolicy)
        ConfirmFile.setMinimumSize(QSize(400, 250))
        ConfirmFile.setMaximumSize(QSize(400, 250))
        icon = QIcon()
        icon.addFile(
            ":/favicon/icons/chat.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        ConfirmFile.setWindowIcon(icon)
        ConfirmFile.setStyleSheet(
            "QWidget {color: #33979c;\n"
            "background-color: #263238;\n"
            "}\n"
            "\n"
            "QPushButton {\n"
            "	border: 1px solid #33979c;\n"
            "	padding: 10px;\n"
            "	background-color: #202c39;\n"
            "}\n"
            "\n"
            "#ConfirmFile {\n"
            "	border: 1px solid #33979c; \n"
            "}"
        )
        self.verticalLayout = QVBoxLayout(ConfirmFile)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.verticalLayout.addItem(self.verticalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(ConfirmFile)
        self.label.setObjectName("label")
        self.label.setMaximumSize(QSize(60, 60))
        self.label.setPixmap(QPixmap(":/widget/icons/google-docs.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.file_name_label = QLabel(ConfirmFile)
        self.file_name_label.setObjectName("file_name_label")
        self.file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.file_name_label)

        self.verticalSpacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(30)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.cancel_pushButton = QPushButton(ConfirmFile)
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.cancel_pushButton.setMinimumSize(QSize(0, 40))
        self.cancel_pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(
            ":/widget/icons/multiply.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.cancel_pushButton.setIcon(icon1)
        self.cancel_pushButton.setIconSize(QSize(18, 18))

        self.horizontalLayout_2.addWidget(self.cancel_pushButton)

        self.send_pushButton = QPushButton(ConfirmFile)
        self.send_pushButton.setObjectName("send_pushButton")
        self.send_pushButton.setMinimumSize(QSize(0, 40))
        self.send_pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(
            ":/buttons/icons/document.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.send_pushButton.setIcon(icon2)
        self.send_pushButton.setIconSize(QSize(18, 18))

        self.horizontalLayout_2.addWidget(self.send_pushButton)

        self.horizontalSpacer_2 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_3 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.retranslateUi(ConfirmFile)

        QMetaObject.connectSlotsByName(ConfirmFile)

    # setupUi

    def retranslateUi(self, ConfirmFile):
        ConfirmFile.setWindowTitle(
            QCoreApplication.translate("ConfirmFile", "Sending File", None)
        )
        self.label.setText("")
        self.file_name_label.setText(
            QCoreApplication.translate("ConfirmFile", "[ Placeholder ]", None)
        )
        self.cancel_pushButton.setText(
            QCoreApplication.translate("ConfirmFile", " Cancel", None)
        )
        self.send_pushButton.setText(
            QCoreApplication.translate("ConfirmFile", " Send", None)
        )

    # retranslateUi
