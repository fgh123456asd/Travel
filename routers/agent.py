from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

from agent.tool import generate_travel_itinerary, get_messages, clear_messages, chat_with_agent
from config import auth
from schemas.agent import ItineraryRequest, ChatRequest

router=APIRouter(prefix= "/agent", tags=["智能体"])


@router.post("/generate")
def generate_itinerary_endpoint(
        request: ItineraryRequest,
        user_id: int = Depends(auth.auth_handler.auth_access_dependency),
):
    """
    纯同步路由：直接丢给 StreamingResponse
    """
    if not request.form_data.destination:
        raise HTTPException(status_code=400, detail="目的地不能为空")

    form_dict = request.form_data.model_dump()

    # 直接返回同步生成器，FastAPI 会自动在后台线程处理它，不会阻塞主程序
    return StreamingResponse(
        generate_travel_itinerary(form_dict, request.thread_id),
        media_type="text/plain"
    )


@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    流式追问接口：结合历史上下文，对已有行程进行调整或提问
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="提问内容不能为空")

    # 同样直接丢给 StreamingResponse，LangGraph 会通过 thread_id 自动关联历史
    return StreamingResponse(
        chat_with_agent(request.message, request.thread_id),
        media_type="text/plain"
    )



@router.get("/history/{thread_id}")
def get_history_endpoint(thread_id: str):
    return {"status": "success", "data": get_messages(thread_id)}


@router.delete("/history/{thread_id}")
def clear_history_endpoint(thread_id: str):
    clear_messages(thread_id)
    return {"status": "success", "message": "会话已清空"}