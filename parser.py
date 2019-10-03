# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 下午2:34

解析类

@author: mick.yi

"""
import db


def get_in_param(datatime, business_param=''):
    """
    获取输入参数
    :param datatime: 数据日期
    :param business_param: 自定义的业务参数 eg: a=15&b=abc&c=hello
    :return:
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
    :param in_param_dict:
    :return:
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
