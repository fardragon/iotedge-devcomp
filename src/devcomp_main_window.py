from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from src.ui.generated.main_window import Ui_DevCompMainWindow
from src.devcomp_model import AbstractModel

from typing import Optional


class MainWindow(qtw.QMainWindow):
    def __init__(self, model: AbstractModel):
        super(MainWindow, self).__init__()

        self.model = model
        self.ui = Ui_DevCompMainWindow()
        self.ui.setupUi(self)

        self.timer = qtc.QTimer(parent=self)
        self.timer.singleShot(0, self.load_data)

        self.ui.subscription_box.currentIndexChanged.connect(self.subscription_changed)
        self.ui.resource_group_box.currentIndexChanged.connect(self.resource_group_changed)
        self.ui.iothub_box.currentIndexChanged.connect(self.iothub_changed)

    def showEvent(self, a0: qtg.QShowEvent) -> None:
        super(MainWindow, self).showEvent(a0)

    def load_data(self):
        d = qtw.QDialog(parent=self)
        layout = qtw.QVBoxLayout(d)
        l1 = qtw.QLabel("")
        l2 = qtw.QLabel("")
        b1 = qtw.QPushButton("Continue")
        layout.addWidget(l1)
        layout.addWidget(l2)
        layout.addWidget(b1)

        d.move(self.pos())

        def clicked():
            d.accept()

        b1.clicked.connect(clicked)
        d.setWindowTitle("Dialog")
        d.setWindowModality(qtc.Qt.ApplicationModal)

        def callback(uri, code, expiration_date):
            print(uri)
            l1.setText('<a href=\"{}\">{}</a>'.format(uri, uri))
            l1.setOpenExternalLinks(True)
            l1.setTextInteractionFlags(qtc.Qt.TextBrowserInteraction)

            l2.setText(code)
            l2.setTextInteractionFlags(qtc.Qt.TextSelectableByMouse)

            d.exec_()
            print("...")

        self.model.authorize(callback)
        print("authorized")
        self.__load_subscriptions()

    def __load_subscriptions(self):
        for sub in self.model.get_all_subscriptions():
            self.ui.subscription_box.addItem(sub.name, sub)
        self.ui.subscription_box.setEnabled(True)

    def __get_subscription(self) -> str:
        return self.ui.subscription_box.itemData(self.ui.subscription_box.currentIndex()).id

    def __load_resource_groups(self, subscription: str):
        # self.ui.resource_group_box.setCurrentIndex(0)
        self.ui.resource_group_box.clear()
        self.ui.resource_group_box.addItems(self.model.get_all_resource_groups(subscription))
        self.ui.resource_group_box.setEnabled(True)

    def __get_resource_group(self) -> Optional[str]:
        index = self.ui.resource_group_box.currentIndex()
        return self.ui.resource_group_box.itemText(index) if index != -1 else None

    def __load_iothubs(self):
        self.ui.iothub_box.clear()
        iothubs = self.model.get_all_iothubs()
        if len(iothubs) > 0:
            self.ui.iothub_box.addItems(iothubs)
            self.ui.iothub_box.setEnabled(True)
        else:
            self.ui.iothub_box.setEnabled(False)

    def __clear_iothubs(self):
        self.ui.iothub_box.clear()
        self.ui.iothub_box.setEnabled(False)

    def __load_devices(self):
        self.ui.device_box.clear()
        devices = self.model.get_iothub_edge_devices()
        if len(devices) > 0:
            self.ui.device_box.addItems(devices)
            self.ui.device_box.setEnabled(True)
        else:
            self.ui.device_box.setEnabled(False)

    def __clear_devices(self):
        self.ui.device_box.clear()
        self.ui.device_box.setEnabled(False)

    def __get_iothub(self) -> Optional[str]:
        index = self.ui.iothub_box.currentIndex()
        return self.ui.iothub_box.itemText(index) if index != -1 else None

    def subscription_changed(self, _: int):
        sub_id = self.__get_subscription()
        self.model.set_subscription(sub_id)
        self.__load_resource_groups(sub_id)

    def resource_group_changed(self, _: int):
        resource_group = self.__get_resource_group()
        if resource_group is None:
            self.__clear_iothubs()
        else:
            self.model.set_resource_group(resource_group)
            self.__load_iothubs()

    def iothub_changed(self, _: int):
        iothub = self.__get_iothub()
        if iothub is None:
            self.__clear_devices()
        else:
            self.model.set_iothub(iothub)
            self.__load_devices()
