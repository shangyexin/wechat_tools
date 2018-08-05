# -*- coding: utf-8 -*-
import sys, logging, os, subprocess, webbrowser
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QMessageBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import (QThread, pyqtSignal, QObject, pyqtSlot)
from PyQt5.QtGui import QIcon, QPixmap

from Ui_mainWindow import Ui_wechat_tools

from wechat import single_wechat_id
from configure import configure

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    )

single_id = None

help_url = 'https://www.shangyexin.com/wechat_tools'


class analyze_friends(QObject):
    # 进程结束信号
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    # 好友分析
    def do_analyze(self):
        home_path = os.path.expandvars('%USERPROFILE%')
        out_put_floder = 'wechat_friends'
        out_put_path = os.path.join(home_path, out_put_floder)
        if not os.path.isdir(out_put_path):
            os.makedirs(out_put_path)
        single_id.analyze_friends(out_put_path)
        self.finished.emit()
        return


class run_wechat(QObject):
    # 进程结束信号
    finished = pyqtSignal()
    # 声明一个登录成功信号
    login_signal = pyqtSignal()
    # 声明一个获取用户名成功信号，参数为登录用户名
    get_username_signal = pyqtSignal(str)
    # 声明一个注销成功信号
    logout_signal = pyqtSignal()
    # 声明一个消息撤回信号
    msg_withdraw_signal = pyqtSignal(str)
    # 声明一个机器人回复消息信号
    robot_reply_signal = pyqtSignal(str)

    # 登录扫码图片
    qr_pic = None
    # 工作目录
    work_dir = None

    def __init__(self):
        super().__init__()
        global single_id
        # self.single_id = single_wechat_id()
        single_id = single_wechat_id()

    # 登录成功回调
    @pyqtSlot()
    def on_login_success(self):
        logging.debug('login success')
        # 删除qr图片
        os.remove(self.qr_pic)
        # 发送登录成功信号
        self.login_signal.emit()
        try:
            username = single_id.get_self_nickname()
            single_id.get_self_head_img(self.work_dir)  # 下载头像到本地
        except Exception as e:
            logging.error(e)
        logging.info(username)
        # 发送成功获取用户名信号
        self.get_username_signal.emit(username)

    # 退出登录回调
    @pyqtSlot()
    def on_logout_success(self):
        logging.debug('logout success')
        # 发送账号退出信号
        self.logout_signal.emit()
        # 发送进程结束信号
        self.finished.emit()
        return

    # 登录微信
    def log_in(self):
        home_path = os.path.expandvars('%USERPROFILE%')
        self.work_dir = os.path.join(home_path, 'wechat_tools')
        logging.debug('work_dir is ' + self.work_dir)
        self.qr_pic = os.path.join(self.work_dir, 'QR.png')
        logging.debug('qr pic path is ' + self.qr_pic)
        self.status_storage_file = os.path.join(self.work_dir, 'itchat.pkl')
        logging.debug('status storage path is ' + self.status_storage_file)
        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)
        try:
            single_id.login(self.status_storage_file, self.qr_pic, self.on_login_success, self.on_logout_success)
        except Exception as e:
            logging.error(e)
        return

    # 注销登录
    def loggout(self):
        single_id.logout()
        # 发送进程结束信号
        self.finished.emit()
        return

    # 微信消息撤回回调
    def msg_withdraw_cb(self, msg):
        logging.info('消息撤回回调')
        logging.info('msg is %s' % msg)
        self.msg_withdraw_signal.emit(msg)
        return

    # 开启微信防撤回
    def enable_message_withdraw(self, file_store_path):
        logging.info('开启消息防撤回')
        single_id.enable_message_withdraw(file_store_path, self.msg_withdraw_cb)
        return

    # 关闭微信防撤回
    def disable_message_withdraw(self):
        single_id.disable_message_withdraw()
        return

    # 机器人回复消息回调
    def enable_robot_cb(self, msg_show):
        self.robot_reply_signal.emit(msg_show)

    # 开启聊天机器人
    def enable_robot(self):
        single_id.enable_robot(self.enable_robot_cb)
        return

    # 关闭聊天机器人
    def disable_robot(self):
        single_id.disable_robot()
        return


class MainWindow(QMainWindow, Ui_wechat_tools):
    login_button_pressed = False
    msg_withdraw_button_pressed = False
    robot_button_pressed = False
    withdraw_file_store_path = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setFixedSize(800, 600)

        # 微信登录处理函数
        self.wechat_handle = run_wechat()
        # 多线程，微信运行线程
        self.thread = QThread()
        # 连接登录状态信号和槽函数
        self.wechat_handle.login_signal.connect(self.login_ui_set)
        self.wechat_handle.logout_signal.connect(self.logout_ui_set)
        self.wechat_handle.get_username_signal.connect(self.get_uername_success)
        self.wechat_handle.msg_withdraw_signal.connect(self.show_withdraw_msg)
        self.wechat_handle.robot_reply_signal.connect(self.show_robot_reply_msg)
        # 将处理函数与多线程绑定
        self.wechat_handle.moveToThread(self.thread)
        # 连接线程退出信号
        self.wechat_handle.finished.connect(self.thread.quit)
        # 连接线程启动函数
        self.thread.started.connect(self.wechat_handle.log_in)

        # 多线程，好友分析线程
        self.analyze = analyze_friends()
        self.analyze_thread = QThread()
        self.analyze.moveToThread(self.analyze_thread)
        self.analyze_thread.started.connect(self.analyze.do_analyze)
        self.analyze.finished.connect(self.analyze_friends_finished)
        self.analyze.finished.connect(self.thread.quit)

        self.ui = Ui_wechat_tools()
        self.ui.setupUi(self)

        # 托盘图标
        self.create_actions()
        self.create_tray_icon()
        self.trayIcon.activated.connect(self.icon_activated)

        # 菜单栏
        self.ui.file_quit.triggered.connect(self.close)
        self.ui.setting_file_storage_path.triggered.connect(self.setting_cliked)
        self.ui.help_about.triggered.connect(self.help_about_clicked)
        self.ui.help_guide.triggered.connect(self.help_guide_clicked)
        self.ui.help_contact.triggered.connect(self.help_contact_clicked)

        # 按钮
        self.ui.open_file_folder.clicked.connect(self.open_file_folder)
        self.ui.button_background.clicked.connect(self.run_in_background)
        self.ui.clear_display.clicked.connect(self.ui_show_clear)

        self.ui.button_login.clicked.connect(self.button_loggin_cliked)
        self.ui.button_analyze.clicked.connect(self.button_analyze_cliked)
        self.ui.button_delete_detection.clicked.connect(self.button_detection_cliked)
        self.ui.button_withdraw.clicked.connect(self.button_withdraw_message)
        self.ui.button_robot.clicked.connect(self.button_robot_cliked)



        # 按钮全部置灰，登录后才可使用
        self.disable_function_buttons(True)

        # 从配置文件中读取设置
        self.my_config = configure()
        self.read_config_file()

    # 创建托盘图标，可以让程序最小化到windows托盘中运行
    def create_tray_icon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icon/wechat.png"), QIcon.Normal, QIcon.Off)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(QIcon(icon))
        self.trayIcon.show()
        return

    # 为托盘图标添加功能
    def create_actions(self):
        self.restoreAction = QAction("恢复", self, triggered=self.showNormal)
        self.quitAction = QAction("退出", self, triggered=QApplication.instance().quit)

    # 激活托盘功能
    def icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.showNormal()

    # 后台运行
    def run_in_background(self):
        self.hide()

    # 输出log到GUI文本框
    def ui_show_info(self, str):
        self.ui.textBrowser.append(str)

    # 清除文本框显示
    def ui_show_clear(self):
        self.ui.textBrowser.clear()

    # 菜单栏-设置
    def setting_cliked(self):
        print('设置被点击')
        self.file_store_path_get = QFileDialog.getExistingDirectory(self, '选取文件夹', '/home')
        if self.file_store_path_get:
            self.withdraw_file_store_path = self.file_store_path_get
            # 将设置写入配置文件
            self.my_config.set_withdraw_msg_file_path(self.withdraw_file_store_path)
            self.ui_show_info('设置文件存储目录成功')
            try:
                # 写入配置文件
                None
            except Exception as e:
                logging.debug(e)
        else:
            self.ui_show_info('未设置文件存储目录')

    # 菜单栏-帮助-关于
    def help_about_clicked(self):
        QMessageBox.about(self, '关于',
                          'WechatTools'
                           '\n'
                          'Version：1.0'
                          '\n'
                          'Author: yasin')
        return

    # 菜单栏-帮助-使用说明
    def help_guide_clicked(self):
        webbrowser.open(help_url, new=0, autoraise=True)
        return

    # 菜单栏-帮助-联系我们
    def help_contact_clicked(self):
        QMessageBox.about(self, '联系我们',
                          'QQ :  835189922'
                          '\n' 
                          '\n'
                          '邮箱:  yexin.shang@gmail.com')
        return

    # 扫码登录按钮
    def button_loggin_cliked(self):
        logging.debug('loggin button is cliked!')
        if self.login_button_pressed is False:
            self.login_button_pressed = True
            # 置灰按钮，防止被多次按下
            self.ui.button_login.setDisabled(True)
            # 启动新线程
            self.thread.start()

        else:
            # 注销登录
            self.wechat_handle.loggout()
            self.login_button_pressed = False
        return

    # 好友分析按钮
    def button_analyze_cliked(self):
        logging.debug('analyze button is clicked!')
        self.ui_show_info('好友数据分析中，请稍后...')
        self.analyze_thread.start()
        return

    # 好友分析完成显示
    def analyze_friends_finished(self):
        self.ui_show_info('好友分析完成！')
        return

    # 好友删除检测按钮
    def button_detection_cliked(self):
        self.ui_show_info('邀请频率已被微信限制，该功能暂时无法使用！')
        return

    # 消息防撤回按钮
    def button_withdraw_message(self):
        logging.info('withdraw message button is clicked! ')
        try:
            if self.msg_withdraw_button_pressed is False:
                self.msg_withdraw_button_pressed = True
                logging.debug(self.withdraw_file_store_path)
                self.wechat_handle.enable_message_withdraw(self.withdraw_file_store_path)
                # 改变按钮显示
                self.ui_show_info('消息防撤回开启成功！')
                self.ui.button_withdraw.setText('关闭消息防撤回')
                self.ui.button_robot.setDisabled(True)
            else:
                self.msg_withdraw_button_pressed = False
                self.wechat_handle.disable_message_withdraw()
                self.ui_show_info('消息防撤回关闭成功！')
                self.ui.button_withdraw.setText('开启消息防撤回')
                self.ui.button_robot.setDisabled(False)
        except Exception as e:
            logging.error(e)
        return

    # 显示撤回的消息
    def show_withdraw_msg(self, msg):
        self.ui_show_info(msg)
        return

    # 点击聊天机器人按钮
    def button_robot_cliked(self):
        if self.robot_button_pressed is False:
            self.robot_button_pressed = True
            self.ui_show_info('开启聊天机器人成功！')
            self.ui.button_robot.setText('关闭自动回复机器人')
            self.ui.button_withdraw.setDisabled(True)
            self.wechat_handle.enable_robot()
        else:
            self.robot_button_pressed = False
            self.ui_show_info('关闭聊天机器人成功！')
            self.ui.button_robot.setText('开启自动回复机器人')
            self.ui.button_withdraw.setDisabled(False)
            self.wechat_handle.disable_robot()
        return

    # 显示机器人自动回复消息
    def show_robot_reply_msg(self, reply_msg):
        self.ui_show_info(reply_msg)
        return

    def open_file_folder(self):
        # 在资源管理器中打开
        abs_path = os.path.abspath(self.withdraw_file_store_path)
        open_dst_cmd = 'explorer.exe ' + abs_path
        print(open_dst_cmd)
        try:
            subprocess.Popen(open_dst_cmd)
            self.ui_show_info('打开撤回文件存放目录成功！')
        except Exception as e:
            logging.error(e)
        return

    # 登录成功处理函数
    def login_ui_set(self):
        # 改变登录按钮显示
        self.ui.button_login.setText('退出登录')
        # 取消按钮置灰，恢复可用
        self.ui.button_login.setDisabled(False)
        # 显示登录成功信息
        self.ui_show_info('登录成功！')
        self.ui_show_info('正在获取用户名及好友信息，请稍后...')
        return

    # 获取用户名成功
    def get_uername_success(self, username):
        # 改变用户名标签
        self.ui.login_name.setText(username)
        # 开启其它功能按钮
        self.disable_function_buttons(False)
        self.ui_show_info('获取用户名及好友信息成功！')
        return

    # 退出登录处理函数
    def logout_ui_set(self):
        # 置灰其他功能按钮
        self.disable_function_buttons(True)
        # 改变登录按钮显示
        self.ui.button_login.setText('扫码登录')
        # 清除文本框信息
        self.ui_show_clear()
        # 显示退出信息
        self.ui_show_info('账号已退出登录！')
        # 改变用户名标签
        self.ui.login_name.setText('Not Login')
        # 重置按钮状态
        self.msg_withdraw_button_pressed = False
        self.robot_button_pressed = False
        self.ui.button_withdraw.setText('开启消息防撤回')
        self.ui.button_robot.setText('开启自动回复机器人')
        return

    # 置灰功能按钮
    def disable_function_buttons(self, switch):
        self.ui.button_withdraw.setDisabled(switch)
        self.ui.button_analyze.setDisabled(switch)
        self.ui.button_delete_detection.setDisabled(switch)
        self.ui.button_robot.setDisabled(switch)
        return

    # 读取配置文件
    def read_config_file(self):
        # 读取撤回文件储存路径
        self.withdraw_file_store_path = self.my_config.get_withdraw_msg_file_path()
        # 文件夹不存在的话则创建
        if not os.path.isdir(self.withdraw_file_store_path):
            os.makedirs(self.withdraw_file_store_path)
        if (self.withdraw_file_store_path != None):
            logging.info(self.withdraw_file_store_path)
            self.ui_show_info('读取配置文件成功！')
        else:
            self.ui_show_info('读取配置文件失败！')
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
