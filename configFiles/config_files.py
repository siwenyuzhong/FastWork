import configparser
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conf_dir = os.path.join(BASE_DIR, "conf", "config.ini")

# 读取配置文件
config = configparser.ConfigParser()
config.read(conf_dir)


def get_key_value(keyLeft, keyRight):
    value = config.get(keyLeft, keyRight)
    return value
