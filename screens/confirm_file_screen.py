from assets.ui.confirm_file_ui import Ui_ConfirmFile
import sys
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from PySide6 import QtUiTools as qtu
from backend import sm
from tools.toolkit import Tools as t


class ConfirmFileScreen(qtw.QWidget, Ui_ConfirmFile):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.paparent = self.parentrent = parent
        self.updateUi()

        self.cancel_pushButton.clicked.connect(self.close)

    def updateUi(self):
        self.setWindowFlags(qtc.Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | qtc.Qt.WindowStaysOnTopHint)
        t.qt.center_widget(self)
        self.dropped_file_path = sm.dropped_file_path.data

        if self.dropped_file_path:
            self.file_name_label.setText(
                t.all.shorten_file_name(filepath=self.dropped_file_path)
            )
