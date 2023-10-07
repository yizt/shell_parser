# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午5:40

入口类

@author: mick.yi

"""
import sys
import time

import db
import parser
import run
from config import cur_config as cfg


def generate_cmd_list(session, datatime, func_id, business_param, runtime_dict=None):
    """
    生成待执行的命令信息
    :param session:
    :param datatime: 数据日期
    :param func_id:
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :param runtime_dict:
    :return None:
    """
    cmd_cfg_list = db.get_cmd_cfg(session, func_id)
    cmd_info_list = parser.parse(cmd_cfg_list, session, datatime, business_param, runtime_dict)
    session.add_all(cmd_info_list)
    session.commit()


def main(func_id, datatime, mode='normal', business_param=''):
    """
    主函数
    :param func_id: 功能id
    :param datatime: 数据日期
    :param mode: normal|debug|redo;
                normal:从上次出错的位置开始执行;如果没有执行过，则从头开始执行
                redo:删除之前已经执行过的命令，重新生成执行命令，并从头开始执行
                debug:删除之前已经执行过的命令，重新生成执行命令, 不执行命令
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :return None:
    """
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

    session.transaction = None
    # 关闭session
    session.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
