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
