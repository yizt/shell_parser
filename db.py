# -*- coding: utf-8 -*-
"""
Created on 2019/10/3 上午8:50

@author: mick.yi

"""

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
