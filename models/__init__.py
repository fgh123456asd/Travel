# 定义命名约定的Base类
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        # ix: index，索引。
        "ix": 'ix_%(column_0_label)s',
        # un: unique，唯一约束
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        # ck: Check，检查约束
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        # fk: Foreign Key，外键约束
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        # pk: Primary Key，主键约束
        "pk": "pk_%(table_name)s"
    })

'''
把 user 模型（表结构） 导入到 Base 所在的文件中，
让 SQLAlchemy 能扫描、识别到这个表，否则 alembic 数据库迁移（生成表）会找不到表，根本不生成！
'''

from . import food ,culture, user, user,scenery,advice
