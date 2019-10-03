# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午8:18
命令行执行
@author: mick.yi

"""
import os
import time
import datetime
import traceback
from db import TbExecCmd


def run_cmd(session, cmd_info):
    """
    执行cmd命令，并记录耗时和运行状态信息
    :param session:
    :param cmd_info: TbExecCmd
    :return flag: 0-代表成功，其它失败
    """
    start_time = time.time()
    try:
        flag = os.system(cmd_info.exec_cmd)
        err_msg = ''
    except BaseException as e:
        print('=======e:{}'.format(e))
        err_msg = traceback.format_exc()

    end_time = time.time()
    time_elapsed = end_time - start_time

    session.bulk_update_mappings(TbExecCmd, [{'func_id': cmd_info.func_id,
                                              'seq': cmd_info.seq,
                                              'datatime': cmd_info.datatime,
                                              'business_param': cmd_info.business_param,
                                              'flag': flag,
                                              'err_msg': err_msg,
                                              'start_time': datetime.datetime.fromtimestamp(start_time),
                                              'end_time': datetime.datetime.fromtimestamp(end_time),
                                              'exec_date': datetime.date.fromtimestamp(start_time),
                                              'exec_elapsed': time_elapsed}])
    session.commit()
    return flag


def run_list(session, cmd_todo_list):
    """
    执行todo 命令列表
    :param session:
    :param cmd_todo_list: list of TbExecCmd
    :return None:
    """
    for cmd_info in cmd_todo_list:
        flag = run_cmd(session, cmd_info)
        # 如果执行失败，后续命令不再执行
        if flag != 0:
            return
