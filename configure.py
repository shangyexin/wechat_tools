import os, configparser, logging

class configure():
    home_path = None
    withdraw_msg_file_path = None
    config_file_name = 'wechat_tools.ini'

    def __init__(self):
        self.home_path = os.path.expandvars('%USERPROFILE%')
        os.chdir(self.home_path)
        self.conf = configparser.ConfigParser()
        try:
            self.conf.read(self.config_file_name)
            self.read_all_configs()
            logging.info('read all configs success!')
        except Exception as e:
            logging.error(e)
            self.create_default_config_file()

    # 创建默认配置文件
    def create_default_config_file(self):
        default_folder_name = 'withdraw_files'
        default_folder_path = os.path.join(self.home_path, default_folder_name)
        print(default_folder_path)
        os.chdir(self.home_path)
        # add section / set option & key
        self.conf.add_section('folder_path')
        self.conf.set('folder_path', 'wihtdraw_files_store_path', default_folder_path)
        # write to file
        with open(self.config_file_name, "w+") as f_config:
            self.conf.write(f_config)

    # 获取撤回消息文件存储路径
    def get_withdraw_msg_file_path(self):
        return self.withdraw_msg_file_path

    # 在配置文件中更新设置
    def set_withdraw_msg_file_path(self, user_set_path):
        os.chdir(self.home_path)
        self.conf.set('folder_path', 'wihtdraw_files_store_path', user_set_path)
        with open(self.config_file_name, "w+") as f_config:
            self.conf.write(f_config)

    def read_all_configs(self):
        self.withdraw_msg_file_path = self.conf.get('folder_path', 'wihtdraw_files_store_path')
