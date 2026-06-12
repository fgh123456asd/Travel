import string
import random
from typing import Annotated
from aiosmtplib import SMTPResponseException
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from config import auth
from config.auth import AuthHandler
from config.db_conf import get_db
from config.mail_conf import get_mail
from crud import user
from schemas.user import RegisterIn, LoginIn, LoginOut

router=APIRouter(prefix= "/user", tags=["用户"])

auth_handler = AuthHandler()
# 获取邮箱验证码
@router.get("/code")
async def get_email_code(
        email: Annotated[EmailStr,Query(...)],
        mail: FastMail = Depends(get_mail),
        db: AsyncSession = Depends(get_db)
    ):
    # 1.生成四位数字的验证码
    source = string.digits * 4     #string.digits = 固定字符串："0123456789"
    code = "".join(random.sample(source, 4))
    # 2.创建消息对象
    message = MessageSchema(
        subject="【途智行】注册验证",  # 邮件标题
        recipients=[email],        # 收件人邮箱
        body=f"您的验证码为：{code}，五分钟有效！",   # 邮件正文
        subtype=MessageType.plain       # 邮件类型：纯文本
    )
    try:
        print(f"验证码：{code}")
        await mail.send_message(message)
        await user.create_code(email, code)
    except SMTPResponseException as e:
        # 检查是否是 QQ 特有的二进制响应错误
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("⚠️ 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
            # 可选：记录日志，但不中断流程
        else:
            raise HTTPException(500, "邮件发送失败！")
    return {"message": "验证码已发送！"}


# 注册
@router.post('/register')
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    # 1. 检查邮箱是否已存在
    if await user.email_is_exist(db, data.email):
        raise HTTPException(400, "邮箱已存在！")
    #2.检查验证码是否正确
    if not await user.check_email_code(data.email, data.code):
        raise HTTPException(400, "验证码错误！")
    # 3. 创建用户
    user_info=await user.create_user(db, data.email, data.password, data.username)
    return {"message": "注册成功！", "data": user_info}



# 登录
@router.post('/login',response_model=LoginOut)
async def login(data: LoginIn,db: AsyncSession = Depends(get_db)):
    # 1. 根据邮箱查找用户
    user_info = await user.get_by_email(db, data.email)
    if not user_info:
        raise HTTPException(400, "用户不存在！")
    # 2. 验证密码
    if not user_info.check_password(data.password):
        raise HTTPException(400, detail="邮箱或密码错误！")
    #  3. 生成JWToken根据用户ID
    tokens = auth_handler.encode_login_token(user_info.id)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    return {
        "user": user_info,
        "access_token":access_token,
        "refresh_token":refresh_token
    }












