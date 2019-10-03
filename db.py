# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 上午8:50

@author: mick.yi

"""

from sqlalchemy import Column, String, Text, BigInteger, PrimaryKeyConstraint, create_engine
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

    seq = Column(BigInteger())
    func_id = Column(String(40))
    cfg_key = Column(String(40))
    memo = Column(String(100))
    exec_cmd = Column(Text())
    enable = Column(String(1))
    __table_args__ = (
        PrimaryKeyConstraint('seq', 'func_id'),
        {},
    )


def main():
    from config import cur_config as cfg
    sess = get_session(cfg.url)
    # param_cfg = TbParamCfg(param_type='2332', param_name='123')
    # sess.add(param_cfg)
    # sess.commit()
    cmd_cfg = TbCmdCfg(func_id='123', seq=1.5)
    sess.add(cmd_cfg)
    sess.commit()


if __name__ == '__main__':
    main()
