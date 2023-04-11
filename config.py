# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 上午8:44

配置文件

@author: mick.yi

"""


class Config(object):
    url = "mysql+mysqlconnector://yizt:12345678@127.0.0.1:3306/cmd_db?auth_plugin=mysql_native_password"


class PGConfig(Config):
    url = "postgresql+psycopg2://postgres:123456@10.71.4.32:5432/cmd_db"


cur_config = PGConfig()
