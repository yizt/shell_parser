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
    __tablename__ = 'tb_param_cfg'

    func_id = Column(String(20))
    param_type = Column(String(20))
    param_name = Column(String(40))
    param_desc = Column(String(200))
    param_format = Column(String(40))
    param_val_expr = Column(Text())
    enable = Column(String(1))
    replace_order = Column(BigInteger())

    __table_args__ = (
        PrimaryKeyConstraint('func_id', 'param_type', 'param_name'),
        {},
    )


def main():
    from config import cur_config as cfg
    sess = get_session(cfg.url)
    param_cfg = TbParamCfg(func_id='123', param_type='232', param_name='123')
    sess.add(param_cfg)
    sess.commit()


if __name__ == '__main__':
    main()
