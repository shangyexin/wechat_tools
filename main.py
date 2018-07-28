# -*- coding: utf-8 -*-
import sys,logging
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QInputDialog, QMessageBox)
from PyQt5.QtCore import (QThread, pyqtSignal,QObject,pyqtSlot)
from Ui_mainWindow import Ui_wechat_tools

from wechat import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

logged_in = False

class run_wechat(QObject):
    # 结束信号
    finished = pyqtSignal()
    # 声明一个登录状态信号，返回str类型登录结果
    log_status_signal = pyqtSignal(str)

    # 登录成功回调
    @pyqtSlot()
    def on_login_success(self):
        logging.debug('login success')
        status = 'online'
        # 发送登录成功信号
        self.log_status_signal.emit(status)

    # 退出登录回调
    @pyqtSlot()
    def on_logout_success(self):
        logging.debug('logout success')
        status = 'offline'
        # 发送登录成功信号
        self.log_status_signal.emit(status)

    # 登录微信
    @pyqtSlot()
    def log_in(self):
        # 全局登录状态标志位
        global logged_in
        try:
            new_id = single_wechat_id()
            new_id.login(self.on_login_success, self.on_logout_success)
        except Exception as e:
            logging.error(e)

        return


class MainWindow(QMainWindow, Ui_wechat_tools):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(800, 600)

        # 微信登录处理函数
        self.wechat_handle = run_wechat()
        # 多线程
        self.thread = QThread()
        # 连接登录状态信号和槽函数
        self.wechat_handle.log_status_signal.connect(self.log_status_change)
        # 将处理函数与多线程绑定
        self.wechat_handle.moveToThread(self.thread)
        # 连接线程退出信号
        self.wechat_handle.finished.connect(self.thread.quit)
        # 连接线程启动函数
        self.thread.started.connect(self.wechat_handle.log_in)

        self.ui = Ui_wechat_tools()
        self.ui.setupUi(self)

        # 按钮
        self.ui.button_login.clicked.connect(self.button_loggin_cliked)

    # 输出log到GUI文本框
    def ui_show_info(self, str):
        self.ui.textBrowser.append(str)

    # 扫码登录按钮
    def button_loggin_cliked(self):
        logging.debug('enter button_loggin_cliked ')
        # 置灰按钮，防止被多次按下
        self.ui.button_login.setDisabled(True)
        # 启动新线程
        self.thread.start()

    # 登录状态改变处理函数
    def log_status_change(self, status):
        # 全局登录状态标志位
        global logged_in
        self.ui.button_login.setDisabled(False)
        if status == 'online':
            logged_in = True
            # 改变登录按钮显示
            self.ui.button_login.setText('退出登录')
            # 显示登录成功信息
            self.ui_show_info('登录成功！')
        else:
            logged_in = False
            # 改变登录按钮显示
            self.ui.button_login.setText('扫码登录')
            # 显示登录成功信息
            self.ui_show_info('账号已退出登录！')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())