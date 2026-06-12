from fastapi_mail import FastMail,ConnectionConfig
from pydantic import SecretStr
import settings


def create_mail_instance() -> FastMail:
    """ 创建并返回一个 FastMail 邮件发送实例。
    每次调用都会生成新的实例，确保线程/协程环境下的安全隔离。
    """
    # 构建邮件连接配置对象
    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(mail_config)



async def get_mail() -> FastMail:
    return create_mail_instance()

