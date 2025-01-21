#####################################
#                                   #
#  Custom enhanced Signal Manager   #
#                                   #
#####################################

from PySide6 import QtCore as qtc


class DataSignal(qtc.QObject):
    signal = qtc.Signal(object)

    def __init__(self):
        super().__init__()
        self.data = None
        self.signal.connect(self._connector)

    def connect_method(self, method):
        self.signal.connect(method)

    def disconnect_method(self, method):
        self.signal.disconnect(method)

    def _connector(self, data):
        if data:
            self.data = data


class DataSignalManager:
    dropped_file_path = DataSignal()


sm = DataSignalManager()
