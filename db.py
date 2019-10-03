# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 上午8:50

@author: mick.yi

"""

from sqlalchemy import Column, String, Text, BigInteger, FLOAT, SMALLINT, \
    DateTime, Date, PrimaryKeyConstraint, create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_session(url):
    # 初始化数据库连接:
    engine = create_engine(url)

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
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

    datatime = Column(String(8))
    func_id = Column(String(40))
    seq = Column(BigInteger())
    memo = Column(String(100))
    exec_cmd = Column(Text())
    flag = Column(SMALLINT())
    start_time = Column(DateTime())
    end_time = Column(DateTime())
    exec_elapsed = Column(BigInteger())
    exec_date = Column(Date())
    business_param = Column(String(40))

    __table_args__ = (
        PrimaryKeyConstraint('datatime', 'seq', 'func_id', 'business_param'),
        {},
    )


def get_cmd_cfg(session, func_id):
    """
    获取指定func_id的cmd配置
    :param session:
    :param func_id: 功能id
    :return: list of TbCmdCfg
    """
    return session.query(TbCmdCfg).filter(
        and_(TbCmdCfg.enable == '1', TbCmdCfg.func_id == func_id)).order_by(TbCmdCfg.seq).all()


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
             TbExecCmd.business_param == business_param)).order_by(TbExecCmd.seq).all()


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


def main():
    from config import cur_config as cfg
    sess = get_session(cfg.url)
    # param_cfg = TbParamCfg(param_type='2332', param_name='123')
    # sess.add(param_cfg)
    # sess.commit()
    # cmd_cfg = TbCmdCfg(func_id='1243', seq=2.5)
    # exec_cmd = TbExecCmd(func_id='1', seq=1, datatime='201808', memo='abc')
    # sess.add(exec_cmd)

    # sess(exec_cmd)
    # sess.bulk_update_mappings(TbExecCmd, [{'func_id': '1',
    #                                        'seq': 1,
    #                                        'datatime': '201808',
    #                                        'business_param': '',
    #                                        'exec_cmd': 'efg'}])
    # x = sess.query(TbExecCmd).all()
    # print(x[0].func_id)
    xs = get_exec_cmd(sess, '201808', '1')
    for x in xs:
        print(x.func_id)
    delete_exec_cmd(sess, '201808', '1')
    sess.commit()


if __name__ == '__main__':
    main()
