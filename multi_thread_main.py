# -*- coding: utf-8 -*-
"""
 @File    : multi_thread_main.py
 @Time    : 2023/3/17 下午4:28
 @Author  : yizuotian
 @Description    : 多线程(进程)并行执行
"""
import multiprocessing
import sys

import db
import run
from config import cur_config as cfg
from main import generate_cmd_list


def process_run(pno, cmd_todo_list):
    session = db.get_session(cfg.url)
    run.run_list(session, cmd_todo_list)
    session.close()


def multi_thread_run(num_processes, func_id, datatime, mode='normal', business_param=''):
    """
    主函数
    :param num_processes:线程数
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
    runtime_dict = {"$num_processes": num_processes}
    # 命令生成
    if mode in ['debug', 'redo']:
        # 先删除已存在的执行信息
        db.delete_exec_cmd(session, datatime, func_id, business_param)
        session.commit()
        # 然后重新生成
        generate_cmd_list(session, datatime, func_id, business_param, runtime_dict)

    if mode == 'normal':
        cmd_todo_list = db.get_exec_cmd(session, datatime, func_id, business_param)
        # 当前没有生成执行命令,则生成
        if cmd_todo_list is None or len(cmd_todo_list) == 0:
            generate_cmd_list(session, datatime, func_id, business_param, runtime_dict)

    # 命令执行
    if mode in ['normal', 'redo']:
        cmd_todo_list = db.get_exec_cmd(session, datatime, func_id, business_param)
        cmd_todo_list = [cmd for cmd in cmd_todo_list if cmd.flag is None or cmd.flag != 0]
        # 关闭session
        session.close()
        # run.run_list(session, cmd_todo_list)
        processes = []
        num_processes = int(num_processes)
        for i in range(num_processes):
            cur_cmd_list = [cmd for cmd in cmd_todo_list if cmd.seq % num_processes == i]
            p = multiprocessing.Process(target=process_run, args=(i, cur_cmd_list))
            p.start()
            processes.append(p)
        # 等待执行完成
        for p in processes:
            p.join()


if __name__ == '__main__':
    multi_thread_run(*sys.argv[1:])
