from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from models import Base
from pwdlib import PasswordHash

password_hash=PasswordHash.recommended()

class User(Base):
    __tablename__ = "user"
    '''
         Mapped：给字段标注类型（告诉 Python 这是什么类型）
         mapped_column：给字段设置数据库规则（主键、唯一、长度、约束等）
    '''
    id:Mapped[ int] = mapped_column(Integer,primary_key=True,autoincrement= True)
    username:Mapped[ str] = mapped_column(String(100),unique=True)
    email:Mapped[ str] = mapped_column(String(100),unique=True)
    # 命名为 _password：表示私有属性，外部不直接访问
    _password: Mapped[str] = mapped_column(String(200))
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now(),
                                                 comment="更新时间")

    # 3. 初始化方法：创建对象时触发
    def __init__(self,*args,**kwargs):
        password=kwargs.pop('password')
        super().__init__(*args,**kwargs)
        if password:
            self.password=password

    @property     #@property 密码只读属性  ---@property 把一个方法变成属性
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = password_hash.hash(raw_password)

    def check_password(self, raw_password):
        return password_hash.verify(raw_password, self.password)


