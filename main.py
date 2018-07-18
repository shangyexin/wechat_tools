# -*- coding: utf-8 -*-
import sys,logging
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QInputDialog, QMessageBox)
from PyQt5.QtCore import (QThread, pyqtSignal)
from Ui_mainWindow import Ui_wechat_tools

from wechat import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )


class MainWindow(QMainWindow, Ui_wechat_tools):
    logged_in = False

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

        # 账号未登录
        if not self.logged_in:
            # 创建新线程登录微信
            self.start_thread = run_wechat()
            try:
                self.start_thread.start()
            except Exception as e:
                logging.debug(e)

            self.logged_in = True
            self.ui.button_login.setText('退出登录')
            self.ui_show_log('登录成功！')

        # 账号已登录
        else:
            self.logged_in = False
            self.ui.button_login.setText('扫码登录')
            self.ui_show_log('账号已退出登录！')

class run_wechat(QThread):
    # 构造函数里增加形参
    def __init__(self, parent=None):
        super(run_wechat, self).__init__(parent)

    def run(self):
        logging.debug('enter child thread')
        try:
            new_id = single_wechat_id()
            new_id.login()
        except Exception as e:
            logging.error(e)

        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())