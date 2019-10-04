# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午5:40

入口类

@author: mick.yi

"""
import sys
import db
from config import cur_config as cfg
import parser
import run


def generate_cmd_list(session, datatime, func_id, business_param):
    """
    生成待执行的命令信息
    :param session:
    :param datatime:
    :param func_id:
    :param business_param:
    :return None:
    """
    cmd_cfg_list = db.get_cmd_cfg(session, func_id)
    cmd_info_list = parser.parse(cmd_cfg_list, session, datatime, business_param)
    session.add_all(cmd_info_list)
    session.commit()


def main(func_id, datatime, mode='normal', business_param=''):
    session = db.get_session(cfg.url)
    # 命令生成
    if mode in ['debug', 'redo']:
        # 先删除已存在的执行信息
        db.delete_exec_cmd(session, datatime, func_id, business_param)
        session.commit()
        # 然后重新生成
        generate_cmd_list(session, datatime, func_id, business_param)

    if mode == 'normal':
        cmd_todo_list = db.get_exec_cmd(session, datatime, func_id, business_param)
        # 当前没有生成执行命令,则生成
        if cmd_todo_list is None or len(cmd_todo_list) == 0:
            generate_cmd_list(session, datatime, func_id, business_param)
            
    # 命令执行
    if mode in ['normal', 'redo']:
        cmd_todo_list = db.get_exec_cmd(session, datatime, func_id, business_param)
        cmd_todo_list = [cmd for cmd in cmd_todo_list if cmd.flag is None or cmd.flag != 0]
        run.run_list(session, cmd_todo_list)
    # 关闭session
    session.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
