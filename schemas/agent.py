from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional


# --- 1. 定义前端传参的结构体 (Pydantic 验证) ---
class FormData(BaseModel):
    departure: Optional[str] = "未填写"
    destination: str  # 目的地是必填项（带红色 * 号）
    start_date: Optional[str] = "未计划"
    days: Optional[str] = "未确定"
    travelers: Optional[str] = "未确定"
    budget: Optional[str] = "未填写"
    preferences: Optional[List[str]] = []

class ItineraryRequest(BaseModel):
    thread_id: str
    form_data: FormData


class ChatRequest(BaseModel):
    thread_id: str
    message: str  # 用户的追加提问，例如："第二天的泰山爬山路线能改成坐索道吗？"