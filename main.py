# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QInputDialog, QMessageBox)
from PyQt5.QtCore import (QThread, pyqtSignal)
from Ui_mainWindow import Ui_wechat_tools


class MainWindow(QMainWindow, Ui_wechat_tools):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(800, 600)
        self.ui = Ui_wechat_tools()
        self.ui.setupUi(self)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())