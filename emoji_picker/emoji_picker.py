import json
import os
import sys
from PySide6 import QtCore as qtc
from PySide6 import QtWidgets as qtw
from PySide6 import QtGui as qtg
from PySide6 import QtUiTools as qtu


with open("./emoji_picker/emojis.json", "r", encoding="utf-8") as file:
    data = json.load(file)

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
)


class EmojiPicker(QWidget):
    def __init__(self, emojis):
        super().__init__()
        self.setWindowTitle("Emoji Picker")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Add emoji groups
        for category, emoji_dict in emojis.items():
            group_box = QGroupBox(category)
            group_layout = QGridLayout()

            row, col = 0, 0
            for emoji, description in emoji_dict.items():
                label = QLabel(emoji)
                label.setToolTip(description)
                group_layout.addWidget(label, row, col)

                col += 1
                if col >= 8:  # Set max columns per row
                    col = 0
                    row += 1

            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)

        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


if __name__ == "__main__":

    app = QApplication([])
    window = EmojiPicker(data)
    window.show()
    app.exec()
