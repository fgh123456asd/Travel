from typing import Annotated

from pydantic import Field, BaseModel, EmailStr, model_validator

UsernameStr = Annotated[str, Field(..., min_length=2, max_length=20, description="用户名")]
RawPasswordStr = Annotated[str, Field(min_length=6, max_length=20, description="密码")]


# 注册
class RegisterIn(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: RawPasswordStr
    confirm_password: RawPasswordStr
    code: Annotated[str, Field(..., min_length=4, max_length=4)]

#@model_validator模型后置验证器
    @model_validator(mode="after")
    def password_is_match(self) -> "RegisterIn":
        password = self.password
        confirm_password = self.confirm_password
        if password != confirm_password:
            raise ValueError("密码不一致！")
        return self



# 登录
class LoginIn(BaseModel):
    email: EmailStr
    password: RawPasswordStr

# 用户信息
class UserSchema(BaseModel):
    id: Annotated[int, Field(..., description="用户ID")]
    email: EmailStr
    username: UsernameStr

# 登录返回数据
class LoginOut(BaseModel):
    user: UserSchema
    access_token : str
    refresh_token : str