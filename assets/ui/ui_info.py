# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'infozMeqpZ.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(444, 79)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.frame = QFrame(Form)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.iconlabel = QLabel(self.frame)
        self.iconlabel.setObjectName("iconlabel")
        self.iconlabel.setMinimumSize(QSize(20, 20))
        self.iconlabel.setMaximumSize(QSize(20, 20))
        self.iconlabel.setScaledContents(True)

        self.horizontalLayout.addWidget(self.iconlabel, 0, Qt.AlignLeft)

        self.titlelabel = QLabel(self.frame)
        self.titlelabel.setObjectName("titlelabel")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titlelabel.sizePolicy().hasHeightForWidth())
        self.titlelabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setBold(True)
        self.titlelabel.setFont(font)
        self.titlelabel.setWordWrap(True)

        self.horizontalLayout.addWidget(self.titlelabel)

        self.closeButton = QPushButton(self.frame)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon = QIcon(QIcon.fromTheme("application-exit"))
        self.closeButton.setIcon(icon)

        self.horizontalLayout.addWidget(
            self.closeButton, 0, Qt.AlignRight | Qt.AlignTop
        )

        self.verticalLayout.addWidget(self.frame, 0, Qt.AlignTop)

        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName("frame_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy1)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.bodyLabel = QLabel(self.frame_2)
        self.bodyLabel.setObjectName("bodyLabel")
        self.bodyLabel.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.bodyLabel)

        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.iconlabel.setText("")
        self.titlelabel.setText(QCoreApplication.translate("Form", "Title", None))
        self.closeButton.setText("")
        self.bodyLabel.setText(QCoreApplication.translate("Form", "Body", None))

    # retranslateUi
