# -*- coding: utf-8 -*-
import sys,logging
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QInputDialog, QMessageBox)
from PyQt5.QtCore import (QThread, pyqtSignal)
from Ui_mainWindow import Ui_wechat_tools

from withdraw import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

class MainWindow(QMainWindow, Ui_wechat_tools):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(800, 600)
        self.ui = Ui_wechat_tools()
        self.ui.setupUi(self)

        # 菜单栏

        # 按钮
        self.ui.button_login.clicked.connect(self.button_loggin_cliked)

    # 输出log到GUI文本框
    def ui_show_log(self, str):
        self.ui.textBrowser.append(str)

    # 扫码登录按钮
    def button_loggin_cliked(self):
        logging.debug('enter button_loggin_cliked ')
        self.ui.button_login.setDisabled(True)
        # 新建对象，传入参数
        self.start_thread = run_wechat()
        try:
            self.start_thread.start()
        except Exception as e:
            logging.debug(e)

class run_wechat(QThread):
    # 构造函数里增加形参
    def __init__(self, parent=None):
        super(run_wechat, self).__init__(parent)

    def run(self):
        logging.debug('enter child thread')
        try:
            object = message_withdraw()
            object.login()
        except Exception as e:
            logging.error(e)

        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())