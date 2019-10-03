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


def main(func_id, datatime, mode='normal', business_param=''):
    session = db.get_session(cfg.url)
    if mode in ['debug', 'redo']:
        # 先删除已存在的执行信息
        db.delete_exec_cmd(session, datatime, func_id, business_param)
        session.commit()
        # 然后重新生成
        cmd_cfg_list = db.get_cmd_cfg(session, func_id)
        cmd_info_list = parser.parse(cmd_cfg_list, session, datatime, business_param)
        session.add_all(cmd_info_list)
        session.commit()

    if mode in ['normal', 'redo']:
        cmd_todo_list = db.get_exec_cmd(session, datatime, func_id, business_param)
        cmd_todo_list = [cmd for cmd in cmd_todo_list if cmd.flag is None or cmd.flag != 0]
        run.run_list(session, cmd_todo_list)
    # 关闭session
    session.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
