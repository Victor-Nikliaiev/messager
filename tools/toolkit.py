# This is custom code written for make it easier to use some features

from PySide6 import QtUiTools as qtu
from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
import logging
import sys
import os


class Tools:
    class all:
        @staticmethod
        def logging_config_file():
            """
            Configure the logging module to write log messages to a file
            named "my_app.log". The log level is set to INFO and the format
            is set to include the time, milliseconds, log level, logger name,
            and the log message itself.

            :return: The configured logging module
            :rtype: logging
            """

            logging.basicConfig(
                filename="my_app.log",
                level=logging.INFO,
                format="%(asctime)s.%(msecs)03d %(levelname)s: [ %(name)s ] :%(message)s",
                datefmt="%d.%m.%Y %H:%M:%S",
            )

            return logging

        @staticmethod
        def logging_config_screen():
            """
            Configure the logging module to print log messages to the console.
            The log level is set to INFO and the format is set to include the log
            level, logger name, and the log message itself.

            :return: The configured logging module
            :rtype: logging
            """

            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s: %(name)s: %(message)s ",
                style="%",
            )

            return logging

        @staticmethod
        def get_lorem():
            """
            Reads and returns the contents of the file "lorem.txt" located in
            the same directory as the module.

            :return: The contents of the file
            :rtype: str
            """

            file_path = os.path.join(os.path.dirname(__file__), "lorem.txt")
            with open(file_path, "r") as f:
                return f.read()

        @staticmethod
        def format_file_path(path):
            """
            Shortens the file path and file name if they exceed 30 characters each,
            by truncating and appending ellipses. Returns the formatted file path.

            :param path: The complete file path to be formatted
            :type path: str
            :return: The formatted file path with shortened file path and file name if necessary
            :rtype: str
            """

            file_path, file_name = os.path.split(path)

            if len(file_path) > 30:
                file_path = f"{file_path[:28]}..."

            if len(file_name) > 30:
                file_name = f"{file_name[:14]}...{file_name[-14:]}"

            return os.path.join(file_path, file_name)

        @staticmethod
        def shorten_file_name(
            file_name=None,
            filepath=None,
            max_length=20,
        ):
            """
            Shorten a file name to a maximum length by truncating and appending ellipses.

            Args:
                file_name: The file name to be shortened.
                filepath: The file path from which to extract the file name if it is not provided.
                max_length: The maximum length of the file name after shortening.

            Returns:
                The shortened file name.
            """
            if file_name is None and filepath is not None:
                file_name = os.path.basename(filepath)

            if file_name is None and filepath is None:
                raise ValueError("Either file_name or filepath must be provided.")

            if len(file_name) > max_length:
                file_extension = os.path.splitext(file_name)[1]
                file_name = f"{file_name[:17]}...{file_extension}"
                return file_name

            return file_name

    class qt:
        @staticmethod
        def run_qt_widget(WidgetClass: qtc.QObject, centered=False):
            """
            Launch a Qt widget, handling both class and instance inputs.

            This function accepts either a class derived from `QObject` or an instance of such a class.
            If an instance is provided, it will convert it to its corresponding class type and instantiate a new object.
            The resulting widget will be displayed as a standalone application.

            Parameters
            ----------
            WidgetClass : QObject
                The class or instance of the widget to be launched. Must be a subclass of `qtc.QObject`.
            centered : bool, optional
                Whether to center the widget on the screen before displaying it. Defaults to False.

            Returns
            -------
            None
                This function does not return any value. It starts the Qt event loop and exits when the application closes.

            Examples
            --------
            # Using a widget class
            >>> run_qt_widget(MyWidgetClass)

            # Using a widget instance
            >>> my_widget_instance = MyWidgetClass()
            >>> run_qt_widget(my_widget_instance, centered=True)

            Notes
            -----
            - If an instance of a widget is provided, it will instantiate a new object of the same type.
            - Ensure that the widget class is a proper subclass of `qtc.QObject`.
            - The function initializes a new `QApplication` and blocks execution until the app is closed.
            """
            app = qtw.QApplication(sys.argv)
            window: None

            if WidgetClass.__class__ != type:
                window = WidgetClass.__class__()

            window = WidgetClass()

            if centered:
                window = Tools.qt.center_widget(window)
            window.show()

            sys.exit(app.exec())

        @staticmethod
        def run_ui_file(ui_file_path, centered=False):
            """
            Load and display a UI file using PySide6.

            This function initializes a QApplication, loads a user interface from the specified
            `.ui` file, and displays it in a window. Optionally, the window can be centered
            on the screen before being shown.

            Parameters
            ----------
            ui_file_path : str
                The file path to the `.ui` file to be loaded.
            centered : bool, optional
                Whether to center the loaded window on the screen (default is False).

            Returns
            -------
            None
                This function does not return any value. The application runs until it exits.

            Example
            -------
            >>> from Tools.qt import run_ui_file
            >>> run_ui_file("path/to/your.ui", centered=True)

            Notes
            -----
            - This function uses the PySide6 `QUiLoader` class to dynamically load and display
            the UI file at runtime.
            - Ensure the `.ui` file exists at the specified path and is readable.
            - The QApplication instance must not already exist in the current Python process.
            """
            app = qtw.QApplication(sys.argv)

            ui_file = qtc.QFile(ui_file_path)
            ui_file.open(qtc.QFile.ReadOnly)
            loader = qtu.QUiLoader()
            window = loader.load(ui_file)

            if centered:
                window = Tools.qt.center_widget(window)
            window.show()

            sys.exit(app.exec())

        @staticmethod
        def center_widget(widget, parent=None, sticky=True) -> qtw.QWidget:
            """
            Centers the given widget on the screen or within the given parent widget.

            This function moves the given widget to the center of the screen if no parent widget is given.
            If a parent widget is given, the widget is centered within the parent.

            Parameters
            ----------
            widget : QWidget
                The widget to be centered.
            parent : QWidget, optional
                The parent widget within which the widget should be centered (default is None).

            Returns
            -------
            QWidget
                The centered widget.

            Examples
            --------
            >>> my_widget = QWidget()
            >>> my_widget.show()
            >>> center_widget(my_widget)

            >>> parent_widget = QWidget()
            >>> my_widget = QWidget(parent_widget)
            >>> my_widget.show()
            >>> center_widget(my_widget, parent_widget)

            Notes
            -----
            - If the parent widget is not given, the screen geometry is used to calculate the center.
            - If the parent widget is given, the parent's geometry is used to calculate the center.
            - The widget is not resized during the centering process.
            - The widget is not reparented unless the parent widget is given.
            """
            if parent:
                if sticky:
                    widget.setParent(parent)

                parent_geo = parent.frameGeometry()
                parent_center = parent_geo.center()

                geo = widget.frameGeometry()
                geo.moveCenter(parent_center)
                widget.move(geo.topLeft() - parent_geo.topLeft())

                return widget

            center = qtg.QScreen.availableGeometry(
                qtw.QApplication.primaryScreen()
            ).center()
            geo = widget.frameGeometry()
            geo.moveCenter(center)
            widget.move(geo.topLeft())

            return widget

        @staticmethod
        def get_qss_sheet(file_path):
            """
            Reads a QSS stylesheet from the given file path and returns it as a string.

            This method reads the contents of the file specified by the given path and
            returns the contents as a string. The method assumes that the file contains
            a valid QSS (Qt Style Sheet) stylesheet.

            Parameters:
            file_path (str): The path to the file containing the QSS stylesheet.

            Returns:
            str: The QSS stylesheet as a string.

            Example:
            >>> get_qss_sheet("path/to/style.qss")

            Note:
            - This method does not validate the QSS stylesheet. If the file contains
              invalid QSS, the method will still return the contents of the file.
            """
            with open(file_path, "r") as f:
                qss = f.read()
            return qss
