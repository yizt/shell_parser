# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 上午8:50

@author: mick.yi

"""
import os
import random
import time

from sqlalchemy import Column, String, Text, BigInteger, FLOAT, SMALLINT, \
    DateTime, Date, PrimaryKeyConstraint, create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from concurrent.futures import ThreadPoolExecutor

Base = declarative_base()


def dummy_func(session):
    """
    间隔一段时间查询数据库，保证session活动状态，不会被服务器断开；
    有些命令行执行非常久，比如llm微调
    :param session:
    :return:
    """
    print("dummy_func start")
    while session.transaction:
        get_constant_val(session, random.randint(1, 100))
        time.sleep(1)
    print("dummy_func end")


def get_session(url):
    # 初始化数据库连接:
    engine = create_engine(url)

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    # 保持session处于活动状态
    pool = ThreadPoolExecutor(max_workers=1)
    pool.submit(dummy_func, session)
    return session


class TbParamCfg(Base):
    """
    参数配置表
    """
    __tablename__ = 'tb_param_cfg'

    param_type = Column(String(20))
    param_name = Column(String(40))
    param_desc = Column(String(200))
    param_format = Column(String(40))
    param_val_expr = Column(Text())
    enable = Column(String(1))
    replace_order = Column(BigInteger())

    __table_args__ = (
        PrimaryKeyConstraint('param_type', 'param_name'),
        {},
    )


class TbCmdCfg(Base):
    """
    待执行命令配置表
    """
    __tablename__ = 'tb_cmd_cfg'

    seq = Column(FLOAT())
    func_id = Column(String(40))
    cfg_key = Column(String(40))
    memo = Column(String(100))
    exec_cmd = Column(Text())
    enable = Column(String(1))

    __table_args__ = (
        PrimaryKeyConstraint('seq', 'func_id'),
        {},
    )


class TbExecCmd(Base):
    """
    命令运行信息表
    """
    __tablename__ = 'tb_execcmd'

    datatime = Column(String(14))
    func_id = Column(String(40))
    seq = Column(BigInteger())
    memo = Column(String(400))
    exec_cmd = Column(Text())
    flag = Column(SMALLINT())
    err_msg = Column(Text())
    start_time = Column(DateTime())
    end_time = Column(DateTime())
    exec_elapsed = Column(BigInteger())
    exec_date = Column(Date())
    business_param = Column(String(400))

    __table_args__ = (
        PrimaryKeyConstraint('datatime', 'seq', 'func_id', 'business_param'),
        {},
    )


def get_param_cfg(session, param_type):
    """
    获取指定类型的参数配置信息
    :param session:
    :param param_type: 参数类别 in|single|set
    :return:
    """
    return session.query(TbParamCfg).filter(
        and_(TbParamCfg.enable == '1',
             TbParamCfg.param_type == param_type)).order_by(
        TbParamCfg.replace_order).all()


def get_cmd_cfg(session, func_id):
    """
    获取指定func_id的cmd配置
    :param session:
    :param func_id: 功能id
    :return: list of TbCmdCfg
    """
    return session.query(TbCmdCfg).filter(
        and_(TbCmdCfg.enable == '1',
             TbCmdCfg.func_id == func_id)).order_by(
        TbCmdCfg.seq).all()


def get_exec_cmd(session, datatime, func_id, business_param=''):
    """
    获取指定时间和func_id的待执行命令
    :param session:
    :param datatime: 数据日期
    :param func_id:
    :param business_param:业务参数
    :return:
    """
    return session.query(TbExecCmd).filter(
        and_(TbExecCmd.datatime == datatime,
             TbExecCmd.func_id == func_id,
             TbExecCmd.business_param == business_param)).order_by(
        TbExecCmd.seq).all()


def delete_exec_cmd(session, datatime, func_id, business_param=''):
    """
    删除定时间和func_id的待执行命令
    :param session:
    :param datatime: 数据日期
    :param func_id:
    :param business_param:
    :return: None
    """
    xs = get_exec_cmd(session, datatime, func_id, business_param)
    for x in xs:
        session.delete(x)
    session.commit()


def get_constant_val(session, expr):
    """
    获取常量值
    :param session:
    :param expr: eg: '201808' or date_format(now(),'%Y%m%d')
    :return:
    """
    xs = session.execute('select {}'.format(expr))
    return str(next(xs)[0])


def get_list_values(session, expr):
    """
    获取指定表达式的值列表
    :param session:
    :param expr: sql表达式
    :return: list of values
    """
    xs = session.execute(expr)
    xs = [x[0] for x in xs]
    return xs


def main():
    from config import cur_config as cfg
    engine = create_engine(cfg.url)
    Base.metadata.create_all(engine)  # 创建所有表结构


def test():
    from config import cur_config as cfg

    sess = get_session(cfg.url)

    param_cfg = TbParamCfg(param_type='2332', param_name='123')
    sess.add(param_cfg)
    sess.commit()
    # cmd_cfg = TbCmdCfg(func_id='1243', seq=2.5)
    # exec_cmd = TbExecCmd(func_id='1', seq=1, datatime='201808', memo='abc')
    # sess.add(exec_cmd)

    # sess(exec_cmd)
    # sess.bulk_update_mappings(TbExecCmd, [{'func_id': '1',
    #                                        'seq': 1,
    #                                        'datatime': '201808',
    #                                        'business_param': '',
    #                                        'exec_cmd': 'efg'}])
    # x = sess.query(TbCmdCfg).all()

    # print(x[0].func_id)
    # xs = get_exec_cmd(sess, '201808', '1')
    # for x in xs:
    #     print(x.func_id)
    # delete_exec_cmd(sess, '201808', '1')
    # get_param_cfg(sess, 'in')
    # x = sess.execute('select 2018')
    # print(y.func_id)
    # sess.commit()


if __name__ == '__main__':
    main()
