import sqlite3
import sys,os,logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings as config
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from agent.vector_store import VectorStoresService
from typing import List
from langchain_core.documents import Document # 导入 LangChain 标准文档对象（向量库返回的数据格式）
from langchain_core.tools import tool
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.agents import create_agent
from duckduckgo_search import DDGS
import requests
from langgraph.checkpoint.sqlite import SqliteSaver


'''
日志等级从低到高：
DEBUG：最详细的调试信息（程序开发阶段用）。
INFO：一般信息，程序运行状态、关键步骤。
WARNING：警告信息，程序还能运行但有潜在问题。
ERROR：错误信息，程序运行出现问题。
CRITICAL：严重错误，可能导致程序崩溃。
-----------------------------------------------------------
DEBUG（调试）最详细，给开发者看细节（如：连接数据库成功）
INFO（普通信息）程序正常运行的提示（如：启动成功、加载完成）
WARNING（警告）不影响运行，但需要注意（如：配置为空）
ERROR（错误）功能出错，但程序还能跑
CRITICAL（严重错误）程序直接崩掉
'''
# 配置日志记录器，生产环境排查故障的核心抓手
# logger 对象，后续可以调用 logger.info(), logger.error(), logger.debug() 等方法打印日志。
logger = logging.getLogger(__name__)  #获取一个日志记录器   (__name__ =当前文件tool.py)
# 设置日志级别：INFO以上的信息都会打印出来
logging.basicConfig(level=logging.INFO)  #配置全局日志输出，最低级别是 INFO。

# ======================向量库核心服务初始化======================
try:
    # 注入阿里通义千问嵌入模型
    embedding_model = DashScopeEmbeddings(model=config.embedding_model_name)

    # 初始化向量库连接
    vector_service = VectorStoresService(embedding=embedding_model)

    # 获取检索器（内部已封装为默认获取 top_k=3 相似文本）
    retriever = vector_service.get_retriever()
    logger.info("Successfully initialized VectorStoresService and retriever.")
except Exception as e:
    logger.critical(f"Failed to initialize Vector Stores Service: {e}")
    raise e


# ====================== 辅助工具函数：格式化文档 ======================

def format_document(docs: List[Document]) -> str:
    """
    将检索到的标准 Document 对象列表转换为适合大模型阅读的纯文本字符串。

    性能优化：使用列表推导式配合 "".join()，在处理并发、长文本时
    内存开销和速度比传统的 `formatted_str += ...` 循环拼接提升数倍。
    """
    if not docs:
        return "本地知识库中未找到任何与该问题相关的参考资料。"

    # 提取内容和元数据进行标准化格式拼接
    parts = [
        f"【本地知识库片段】: {doc.page_content}\n【知识元数据】: {doc.metadata}\n"
        for doc in docs
    ]

    # 用双换行分隔每个知识点，形成清晰的“小抄”
    return "\n\n".join(parts)



# 大模型智能 Agent 工具（Tool）注册
@tool
def rag_search(query: str) -> str:
    """
    当用户询问关于山东省（齐鲁大地）旅游、景点、门票、路线规划、当地美食
    或任何与山东本地相关的历史、文化特色知识时，调用此工具查询本地知识库。

    注意：请传入具体的实体关键词或短句（如：'泰山日出时间'、'大明湖门票价格'、'青岛三日游攻略'）。

    :param query: 提取出的具体查询关键词。
    :return: 格式化后的本地知识库相关参考资料文本。
    """
    # 边缘情况校验：防止大模型传入空字符串
    if not query or not query.strip():
        return "输入的查询关键词不能为空，请输入具体的山东旅游或文化相关词汇。"

    logger.info(f"Agent triggered 'rag_search' with query: {query}")

    try:
        # 1. 触发向量数据库进行相似度对齐捞取
        docs = retriever.invoke(query.strip())

        # 2. 转换为大模型直观可读的纯文本字符串并返回
        return format_document(docs)

    except Exception as e:
        # 稳健性防线：捕获可能由于网络、API过期或磁盘IO导致的异常
        # 保证外层的整个 Agent 链条不会因为单次检索失败而彻底崩溃
        logger.error(f"Error occurred during rag_search for query '{query}': {e}", exc_info=True)
        return "抱歉，系统在检索本地山东旅游知识库时遇到系统异常，请稍后再试或切换其他问题。"


@tool  # 工具装饰器：标记当前函数为一个可被外部调用的工具方法
def duckduckgo_search(query: str, max_results: int = 5, region: str = "cn-en") -> list:
    """
    【函数功能】基于DuckDuckGo搜索引擎执行网络搜索，返回结构化的搜索结果
    【核心依赖】需要提前安装库：pip install duckduckgo-search

    参数（类型标注）:
        query: 必传参数，字符串类型，搜索的关键词/问题
        max_results: 可选参数，整数类型，指定返回的最大搜索结果数，默认5条
        region: 可选参数，字符串类型，搜索区域/语言设置
               - cn-en：返回英文结果（默认）
               - cn-zh：返回中文结果

    返回值:
        列表类型，列表中每个元素是一个字典，包含3个搜索结果字段：
        title：搜索结果标题 | link：结果网页链接 | body：结果摘要/正文
    """
    # 初始化空列表，用于存储最终格式化后的搜索结果
    results = []

    try:
        # 上下文管理器创建DDGS实例（自动管理网络连接/资源释放，无需手动关闭）
        with DDGS() as ddgs:
            # 调用DDGS的text方法：执行【文本搜索】，传入关键词、区域、最大结果数参数
            # 遍历搜索返回的原始结果迭代器
            for r in ddgs.text(query, region=region, max_results=max_results):
                # 将原始结果格式化，提取需要的字段，追加到结果列表
                # 使用dict.get()方法：键不存在时返回空字符串，避免程序报错
                results.append({
                    "title": r.get("title", ""),  # 提取结果标题
                    "link": r.get("href", ""),  # 提取结果链接（原始字段名是href）
                    "body": r.get("body", "")  # 提取结果摘要正文
                })

    # 捕获所有异常（网络错误、搜索超时、参数错误等），防止程序崩溃
    except Exception as e:
        # 打印错误信息，方便调试
        print(f"搜索出错: {e}")

    # 返回最终的搜索结果列表（无结果/出错时返回空列表）
    return results



@ tool
def get_current_weather(location: str, unit: str = "celsius"):
    """
    【函数功能】调用第三方天气API（OpenWeatherMap），获取指定城市的**实时天气信息**
    【使用前提】1. 安装依赖：pip install requests  2. 拥有有效的OpenWeatherMap API密钥

    参数说明 (类型标注)：
        location: 字符串，必填参数 -> 城市名称（推荐英文/拼音：Beijing、Guangzhou）
        unit: 字符串，可选参数 -> 温度单位，默认摄氏度(celsius)，可选华氏度(fahrenheit)

    返回值：
        dict 字典类型：成功则返回结构化天气数据，失败则返回包含错误提示的字典
    """
    # OpenWeatherMap 平台的API密钥（用户个人身份凭证，用于鉴权调用API）
    api_key = "b6d0093c249877d66c19e0e0376282b7"
    # 天气API的固定请求基础地址（官方接口URL，不可修改）
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    # 构造API请求参数（按照OpenWeatherMap官方要求组装）
    params = {
        "q": location,  # q：API规定的城市参数名，传入用户指定的城市
        "appid": api_key,  # appid：API密钥，必填，用于验证用户权限
        # units：温度单位设置，metric=摄氏度，imperial=华氏度
        "units": "metric" if unit == "celsius" else "imperial",
        "lang": "zh_cn"  # lang：设置返回的天气描述为**中文**（默认英文）
    }

    try:
        # 【核心步骤1】发送HTTP GET请求到天气API
        # timeout=10：设置10秒超时，避免程序一直等待无响应
        response = requests.get(base_url, params=params, timeout=10)

        # 【核心步骤2】将API返回的JSON格式数据，转换为Python字典，方便读取
        data = response.json()

        # 【核心步骤3】校验API业务状态码（OpenWeatherMap规定：cod=200 代表查询成功）
        if data.get("cod") != 200:
            # 状态码非200：查询失败（城市错误/密钥过期/权限不足），返回错误信息
            return {"error": f"查询失败：{data.get('message', '城市不存在/API密钥错误')}"}

        # 【核心步骤4】解析成功返回的数据，组装成友好的天气信息字典
        # 使用字典取值，提取API返回的核心天气数据
        weather_info = {
            "location": location,  # 查询的城市名称
            "temperature": f"{data['main']['temp']}°C",  # 当前温度
            "description": data['weather'][0]['description'],  # 天气描述（多云/晴天等）
            "humidity": f"{data['main']['humidity']}%",  # 空气湿度
            "体感温度": f"{data['main']['feels_like']}°C"  # 体感温度（实用扩展字段）
        }
        # 返回最终整理好的天气数据
        return weather_info

    # 【异常处理1】请求超时：超过10秒API没有响应
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请检查网络"}
    # 【异常处理2】连接失败：无网络/无法连接API服务器
    except requests.exceptions.ConnectionError:
        return {"error": "网络连接失败"}
    # 【异常处理3】数据解析错误：API返回的数据缺少必填字段（格式异常）
    except KeyError as e:
        return {"error": f"数据解析失败，缺失字段：{str(e)}"}
    # 【异常处理4】兜底：捕获所有其他未知错误，保证程序不崩溃
    except Exception as e:
        return {"error": f"未知错误：{str(e)}"}



# 4.初始化checkpointer
# 连接sqlite
#check_same_thread检查是否是同一个线程   ,sqlite3 默认不允许多个线程同时用同一个数据库连接。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/personal_chief.db")

# 自动创建 db 文件夹（防止文件夹不存在）
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 建立数据库连接
connection = sqlite3.connect(DB_PATH, check_same_thread=False)
# 初始化checkpointer
checkpointer = SqliteSaver(connection)
# 自动建表
checkpointer.setup()




system_prompt = '''
你是一位专业的旅游规划师，请根据用户提供的信息和收集到的数据，生成一份详细、实用、个性化的旅行行程方案。
只回答山东旅游相关的问题，其余的问题不用回答
优先调用工具之后才能自己发挥。
'''


model = init_chat_model(
    api_key="sk-1b810b26af4f479dbca4369a612c809c",
    model="qwen3.5-plus-2026-02-15",  # 模型名称，这里选择qwen3.5-plus，这是一个多模态模型，支持图片、文本、音频、视频
    model_provider="openai",  # 阿里云百炼兼容了openai的API
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

agent=create_agent(
    model=model,
    tools=[rag_search,get_current_weather,duckduckgo_search],
    checkpointer=checkpointer,
    system_prompt=system_prompt,
)

logger = logging.getLogger(__name__)


def generate_travel_itinerary(form_data: dict, thread_id: str):
    """
    纯同步函数：调用 agent 搜索并流式返回行程
    """
    departure = form_data.get("departure", "未填写")
    destination = form_data.get("destination", "未填写")
    start_date = form_data.get("start_date", "未计划")
    days = form_data.get("days", "未确定")
    travelers = form_data.get("travelers", "未确定")
    budget = form_data.get("budget", "未填写")
    preferences = form_data.get("preferences", [])
    preferences_str = "、".join(preferences) if preferences else "无特定偏好"

    prompt = (
        f"请为我定制一份专属旅行行程，以下是我的需求：\n"
        f"- 出发地：{departure}\n"
        f"- 目的地：{destination}\n"
        f"- 出行日期：{start_date}\n"
        f"- 旅行天数：{days} 天\n"
        f"- 同行人数：{travelers}\n"
        f"- 预算范围：{budget}\n"
        f"- 兴趣偏好：{preferences_str}\n"
    )

    logger.info(f"[用户发起行程规划]: {destination}, thread_id: {thread_id}")

    try:
        message = HumanMessage(content=[{"type": "text", "text": prompt}])

        # 💡 核心修改：使用纯同步的 agent.stream
        # 记得要把 config 放在第二个参数
        for chunk, metadata in agent.stream(
                {"messages": [message]},
                config={"configurable": {"thread_id": thread_id}},
                stream_mode="messages"
        ):
            # 兼容处理：有些版本的 chunk 直接是消息对象，有些是字典
            #变量 = 条件成立时的值 if 条件 else 条件不成立时的值
            msg = chunk if not isinstance(chunk, dict) else chunk.get("messages", [None])[-1]

            if (isinstance(msg, AIMessageChunk) or isinstance(msg, AIMessage)) and msg.content:
                yield str(msg.content)

    except Exception as e:
        logger.error(f"同步 Agent 运行报错: {str(e)}", exc_info=True)
        yield "行程生成失败，请稍后重试"


def get_messages(thread_id: str) -> list[dict[str, str]]:
    """纯同步获取历史记录"""
    logger.info(f"获取历史消息，thread_id: {thread_id}")
    checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})
    if not checkpoint:
        return []

    channel_values = checkpoint.get("channel_values", {})
    messages = channel_values.get("messages", channel_values.get("values", []))
    if not messages:
        return []

    result = []
    for msg in messages:
        if not msg.content:
            continue
        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": str(msg.content)})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": str(msg.content)})
    return result


def clear_messages(thread_id: str):
    """纯同步清空会话"""
    logger.info(f"清空历史消息，thread_id: {thread_id}")
    checkpointer.delete_thread(thread_id)



def chat_with_agent(user_message: str, thread_id: str):
    """
    基于现有 thread_id 的历史上下文进行流式对话追问
    """
    logger.info(f"[用户追加提问], thread_id: {thread_id}, 内容: {user_message}")

    try:
        # 将用户的纯文本问题转化为 LangChain 的 HumanMessage
        message = HumanMessage(content=[{"type": "text", "text": user_message}])

        # 💡 关键点：传入相同的 thread_id，LangGraph 会自动把本次 message 追加到历史记录后面
        for chunk, metadata in agent.stream(
                {"messages": [message]},
                config={"configurable": {"thread_id": thread_id}},
                stream_mode="messages"
        ):
            # 兼容处理消息块
            msg = chunk if not isinstance(chunk, dict) else chunk.get("messages", [None])[-1]

            if (isinstance(msg, AIMessageChunk) or isinstance(msg, AIMessage)) and msg.content:
                yield str(msg.content)

    except Exception as e:
        logger.error(f"同步 Agent 追问运行报错: {str(e)}", exc_info=True)
        yield "对话处理失败，请稍后重试"