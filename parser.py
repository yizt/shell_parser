# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午2:34

解析类

@author: mick.yi

"""
import db
import copy


def get_in_param(datatime, business_param=''):
    """
    获取输入参数
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15&b=abc&c=hello
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
        result_dict['$curday'] = datatime

    # 业务参数
    if business_param is not None and len(business_param) > 0:
        kvs = business_param.split('&')  # key=val
        for kv in kvs:
            k, v = kv.split('=')
            result_dict[k] = v

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
        for k, v in in_param_dict:
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
        for k, v in in_param_dict:
            expr = expr.replace(k, v)

        # 根据表达式获取集合值
        result_dict[param_cfg.param_name] = db.get_list_values(session, expr)

    return result_dict


def get_params(session, datatime, business_param=''):
    """
    获取所有配置参数
    :param session:
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15&b=abc&c=hello
    :return in_params: dict{param_name: param_value}
    :return single_params: dict{param_name: param_value}
    :return set_params: dict{param_name: param_value}
    """
    in_params = get_in_param(datatime, business_param)
    single_params = get_single_param(session, in_params)
    set_params = get_set_param(session, in_params)
    return in_params, single_params, set_params


def deal_set_param(cmd_info_list, set_param_list):
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
                cur_cmd_info = copy.copy(cmd_info)
                cur_cmd_info.memo += ";{}={}".format(cur_param_name, cur_param_val)
                cur_cmd_info.exec_cmd = cur_cmd_info.exec_cmd.replace(cur_param_name, cur_param_val)
                cur_cmd_list.append(cur_cmd_info)
        else:
            cur_cmd_list.append(cmd_info)

        # 递归处理
        result_list.extend(deal_set_param(cur_cmd_list, set_param_list[1:]))

    return result_list