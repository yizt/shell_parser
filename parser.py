# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午2:34

解析类

@author: mick.yi

"""
import copy
import subprocess

import db
from db import TbExecCmd


def get_in_param(datatime, business_param=''):
    """
    获取输入参数
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :return: dict{param_name: param_value}
    """
    result_dict = dict()
    # 日期
    result_dict['$datatime'] = datatime
    if len(datatime) == 6:
        result_dict['$curmon'] = datatime
        result_dict['$curday'] = datatime + '01'
    else:
        result_dict['$curmon'] = datatime[:6]
        result_dict['$curday'] = datatime[:8]

    # 业务参数
    if business_param is not None and len(business_param) > 0:
        kvs = business_param.split(',')  # key=val
        for kv in kvs:
            k, v = kv.split('=')
            result_dict["${}".format(k)] = v
    return result_dict


def get_single_param(session, in_param_dict):
    """
    获取单值参数
    :param session:
    :param in_param_dict: dict{param_name: param_value}
    :return: dict{param_name: param_value}
    """
    single_params = db.get_param_cfg(session, 'single')  # list of TbParamCfg
    result_dict = {}

    for param_cfg in single_params:
        expr = param_cfg.param_val_expr
        # 逐个替换输入参数
        for k, v in in_param_dict.items():
            expr = expr.replace(k, v)

        # 根据表达式获取常量值
        result_dict[param_cfg.param_name] = db.get_constant_val(session, expr)

    return result_dict


def get_set_param(session, in_param_dict):
    """
    获取集合参数
    :param session:
    :param in_param_dict: dict{param_name: param_value}
    :return: dict{param_name: param_value}
    """
    set_params = db.get_param_cfg(session, 'set')  # list of TbParamCfg

    result_dict = {}
    for param_cfg in set_params:
        expr = param_cfg.param_val_expr
        # 逐个替换输入参数
        for k, v in in_param_dict.items():
            expr = expr.replace(k, v)

        # 根据表达式获取集合值
        result_dict[param_cfg.param_name] = db.get_list_values(session, expr)

    return result_dict


def get_cmd_set_param(session, in_param_dict):
    """
    获取命令行的集合参数
    :param session:
    :param in_param_dict: dict{param_name: param_value}
    :return: dict{param_name: param_value}
    """
    set_params = db.get_param_cfg(session, 'cmdset')  # list of TbParamCfg

    result_dict = {}
    for param_cfg in set_params:
        expr = param_cfg.param_val_expr
        # 逐个替换输入参数
        for k, v in in_param_dict.items():
            expr = expr.replace(k, v)

        # 根据命令行获取集合值
        # print("param_name:{}\nexpr:{}\n".format(param_cfg.param_name, expr))
        _, val_str = subprocess.getstatusoutput(expr)
        # print("param_name:{}\nexpr:{}\nval:{}".format(param_cfg.param_name, expr, val_str))
        result_dict[param_cfg.param_name] = val_str.splitlines()

    return result_dict


def get_params(session, datatime, business_param=''):
    """
    获取所有配置参数
    :param session:
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :return in_params: dict{param_name: param_value}
    :return single_params: dict{param_name: param_value}
    :return set_params: dict{param_name: param_value}
    """
    in_params = get_in_param(datatime, business_param)
    single_params = get_single_param(session, in_params)
    set_params = get_set_param(session, in_params)
    cmd_set_params = get_cmd_set_param(session, in_params)
    set_params.update(cmd_set_params)  # 合并数据库和cmd的集合参数
    return in_params, single_params, set_params


def deal_set_param_bak(cmd_info_list, set_param_list):
    """
    处理集合参数
    :param cmd_info_list: list of TbExecCmd
    :param set_param_list: list of tuple(param_name,param_values)
    :return result_list: list of TbExecCmd
    """
    if len(set_param_list) == 0:
        return cmd_info_list
    cur_param_name, cur_param_values = set_param_list[0]  # 当前的参数键值对
    result_list = []  # 最终结果
    # 遍历所有元素
    for cmd_info in cmd_info_list:
        cur_cmd_list = []
        if cur_param_name in cmd_info.exec_cmd:  # 命令包含当前set参数
            for cur_param_val in cur_param_values:
                cur_cmd_info = copy.deepcopy(cmd_info)
                cur_cmd_info.memo += ";{}={}".format(cur_param_name, cur_param_val)
                cur_cmd_info.exec_cmd = cur_cmd_info.exec_cmd.replace(cur_param_name, str(cur_param_val))
                cur_cmd_list.append(cur_cmd_info)
        else:
            cur_cmd_list.append(cmd_info)

        # 递归处理
        result_list.extend(deal_set_param(cur_cmd_list, set_param_list[1:]))

    return result_list


def get_cur_dependency_param(dependency_param_list, cur_set_param_name):
    """
    根据集合参数名获取对应的依赖参数
    :param dependency_param_list: list of TbParamCfg
    :param cur_set_param_name: 集合参数名
    :return dependency_param_name_list:
    :return dependency_param_expr_list:
    """
    dependency_param_name_list, dependency_param_expr_list = [], []
    for param_cfg in dependency_param_list:
        if cur_set_param_name in param_cfg.param_val_expr:
            dependency_param_name_list.append(param_cfg.param_name)
            dependency_param_expr_list.append(param_cfg.param_val_expr)
    return dependency_param_name_list, dependency_param_expr_list


def deal_set_param(session, cmd_info_list, set_param_list, dependency_param_list):
    """
    处理集合参数
    :param session:
    :param cmd_info_list: list of TbExecCmd
    :param set_param_list: list of tuple(param_name,param_values)
    :param dependency_param_list: 依赖参数 list of TbParamCfg
    :return result_list: list of TbExecCmd
    """
    if len(set_param_list) == 0:
        return cmd_info_list
    cur_param_name, cur_param_values = set_param_list[0]  # 当前的参数键值对
    dependency_param_name_list, dependency_param_expr_list = get_cur_dependency_param(dependency_param_list,
                                                                                      cur_param_name)
    result_list = []  # 最终结果
    # 遍历所有元素
    for cmd_info in cmd_info_list:
        cur_cmd_list = []
        if cur_param_name in cmd_info.exec_cmd:  # 命令包含当前set参数
            for cur_param_val in cur_param_values:
                cur_cmd_info = copy.deepcopy(cmd_info)
                cur_cmd_info.memo += ";{}={}".format(cur_param_name, cur_param_val)
                cur_cmd_info.exec_cmd = cur_cmd_info.exec_cmd.replace(cur_param_name, str(cur_param_val))
                # 处理依赖参数
                for dependency_param_name, dependency_param_expr in zip(dependency_param_name_list,
                                                                        dependency_param_expr_list):
                    dependency_param_val = db.get_constant_val(session,
                                                               dependency_param_expr.replace(cur_param_name,
                                                                                             str(cur_param_val)))

                    cur_cmd_info.exec_cmd = cur_cmd_info.exec_cmd.replace(dependency_param_name, dependency_param_val)
                cur_cmd_list.append(cur_cmd_info)
        else:
            cur_cmd_list.append(cmd_info)

        # 递归处理
        result_list.extend(deal_set_param(session, cur_cmd_list, set_param_list[1:], dependency_param_list))

    return result_list


def deal_in_param(cmd_cfg_list, in_param_dict, datatime, business_param=''):
    """
    处理输入参数
    :param cmd_cfg_list: list of TbCmdCfg
    :param in_param_dict: dict{param_name: param_value}
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :return result_list: list of TbExecCmd
    """
    result_list = []
    for cmd_cfg in cmd_cfg_list:
        cmd_info = TbExecCmd(datatime=datatime,
                             func_id=cmd_cfg.func_id,
                             memo=cmd_cfg.memo,
                             exec_cmd=cmd_cfg.exec_cmd,
                             business_param=business_param)
        # 替换所有输入参数
        for param_name, param_val in in_param_dict.items():
            cmd_info.exec_cmd = cmd_info.exec_cmd.replace(param_name, param_val)

        result_list.append(cmd_info)

    return result_list


def deal_single_param(cmd_info_list, single_param_dict):
    """
    处理单值参数,逐个替换参数名为参数值即可
    :param cmd_info_list: list of TbExecCmd
    :param single_param_dict: dict{param_name: param_value}
    :return result_list: list of TbExecCmd
    """
    result_list = []
    for cmd_info in cmd_info_list:
        for param_name, param_val in single_param_dict.items():
            cmd_info.exec_cmd = cmd_info.exec_cmd.replace(param_name, param_val)

        result_list.append(cmd_info)

    return result_list


def deal_runtime_param(session, cmd_info_list, runtime_dict):
    """
    处理runtime参数
    :param session:
    :param cmd_info_list:
    :param runtime_dict: 运行时替换的k-v对
    :return: dict{param_name: param_value}
    """
    runtime_params = db.get_param_cfg(session, 'runtime')  # list of TbParamCfg
    result_list = []
    for cmd_info in cmd_info_list:
        for param_cfg in runtime_params:
            expr = param_cfg.param_val_expr
            # 替换seq no
            expr = expr.replace("$seq_no", str(cmd_info.seq))
            # 逐个替换输入参数
            for k, v in runtime_dict.items():
                expr = expr.replace(k, v)
            # 根据表达式获取常量值
            param_val = db.get_constant_val(session, expr)
            cmd_info.exec_cmd = cmd_info.exec_cmd.replace(param_cfg.param_name, param_val)
        result_list.append(cmd_info)

    return result_list


def parse(cmd_cfg_list, session, datatime, business_param='', runtime_dict: dict = None):
    """
    将命令配置对象TbCmdCfg解析为命令运行对象TbExecCmd
    :param cmd_cfg_list: list of TbCmdCfg
    :param session:
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15,b=abc,c=hello
    :param runtime_dict:
    :return cmd_info_list: list of TbExecCmd
    """
    in_param_dict, single_param_dict, set_param_dict = get_params(session, datatime, business_param)
    # 替换输出参数
    cmd_info_list = deal_in_param(cmd_cfg_list, in_param_dict, datatime, business_param)
    # 替换单值参数
    cmd_info_list = deal_single_param(cmd_info_list, single_param_dict)
    # # 替换集合参数
    # cmd_info_list = deal_set_param(cmd_info_list, list(set_param_dict.items()))
    # 替换集合参数
    dependency_param_list = db.get_param_cfg(session, 'dependency')  # 获取依赖参数
    cmd_info_list = deal_set_param(session, cmd_info_list, list(set_param_dict.items()), dependency_param_list)

    # seq字段赋值
    for i, cmd_info in enumerate(cmd_info_list):
        cmd_info.seq = i + 1
    # 多线程runtime参数
    if runtime_dict is not None:
        cmd_info_list = deal_runtime_param(session, cmd_info_list, runtime_dict)

    return cmd_info_list
