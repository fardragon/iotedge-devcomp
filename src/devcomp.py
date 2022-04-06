from PyQt5 import QtWidgets as qtw
import sys

from src.devcomp_main_window import MainWindow
from src.devcomp_model import AzureModel

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    window = MainWindow(AzureModel())
    window.show()

    sys.exit(app.exec_())
