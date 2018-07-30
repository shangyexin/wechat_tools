# -*- coding: utf-8 -*-
import sys,logging
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QInputDialog, QMessageBox)
from PyQt5.QtCore import (QThread, pyqtSignal, QObject, pyqtSlot)
from Ui_mainWindow import Ui_wechat_tools

from wechat import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

class run_wechat(QObject):
    # 结束信号
    finished = pyqtSignal()
    # 声明一个登录成功信号，参数为登录用户名
    login_signal = pyqtSignal(str)
    # 声明一个退出登录信号
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.single_id = single_wechat_id()

    # 登录成功回调
    @pyqtSlot()
    def on_login_success(self):
        logging.debug('login success')
        try:
            username = self.single_id.get_self_nickname()
        except Exception as e:
            logging.error(e)
        # 发送登录成功信号
        self.login_signal.emit(username)

    # 退出登录回调
    @pyqtSlot()
    def on_logout_success(self):
        logging.debug('logout success')
        # 发送账号退出信号
        self.logout_signal.emit()
        # 发送进程结束信号
        self.finished.emit()

    # 登录微信
    @pyqtSlot()
    def log_in(self):
        try:
            self.single_id.login(self.on_login_success, self.on_logout_success)
        except Exception as e:
            logging.error(e)

    # 开启微信防撤回
    def enable_message_withdraw(self):
        logging.debug('这是微信打开函数')
        self.single_id.enable_message_withdraw()

    # 关闭微信防撤回
    def disable_message_withdraw(self):
        self.single_id.disable_message_withdraw()


class MainWindow(QMainWindow, Ui_wechat_tools):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(800, 600)

        # 微信登录处理函数
        self.wechat_handle = run_wechat()
        # 多线程
        self.thread = QThread()
        # 连接登录状态信号和槽函数
        self.wechat_handle.login_signal.connect(self.login_ui_set)
        self.wechat_handle.logout_signal.connect(self.logout_ui_set)
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
        self.ui.button_withdraw.clicked.connect(self.button_withdraw_message)

        # 按钮全部置灰，登录后才可使用
        self.disable_function_buttons(True)


    # 输出log到GUI文本框
    def ui_show_info(self, str):
        self.ui.textBrowser.append(str)

    # 扫码登录按钮
    def button_loggin_cliked(self):
        logging.debug('loggin button is cliked!')
        # 置灰按钮，防止被多次按下
        self.ui.button_login.setDisabled(True)
        # 启动新线程
        self.thread.start()

    # 开启消息防撤回按钮
    def button_withdraw_message(self):
        logging.debug('withdraw message button is clicked! ')
        self.wechat_handle.enable_message_withdraw()
        # 改变按钮显示
        self.ui_show_info('消息防撤回开启成功！')
        self.ui.button_withdraw.setText('关闭消息防撤回')

    # 登录成功处理函数
    def login_ui_set(self, username):
        # 开启其它功能按钮
        self.disable_function_buttons(False)
        # 改变登录按钮显示
        self.ui.button_login.setText('退出登录')
        # 取消按钮置灰，恢复可用
        self.ui.button_login.setDisabled(False)
        # 显示登录成功信息
        self.ui_show_info('登录成功！')
        # 改变用户名标签
        self.ui.label.setText(username)

    # 退出登录处理函数
    def logout_ui_set(self):
        # 置灰其他功能按钮
        self.disable_function_buttons(True)
        # 改变登录按钮显示
        self.ui.button_login.setText('扫码登录')
        # 显示退出信息
        self.ui_show_info('账号已退出登录！')

    # 置灰功能按钮
    def disable_function_buttons(self, switch):
        self.ui.button_withdraw.setDisabled(switch)
        self.ui.button_analyze.setDisabled(switch)
        self.ui.button_delete_detection.setDisabled(switch)
        self.ui.button_robot.setDisabled(switch)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())