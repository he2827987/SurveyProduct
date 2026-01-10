# backend/app/api/llm_api.py
"""
LLM 相关的 API 端点。
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

# 导入我们的服务
from ..services import llm_service

logger = logging.getLogger(__name__)

# --- 定义 Pydantic 模型 (Schemas) ---
class GenerateQuestionsRequest(BaseModel):
    topic: str
    num_questions: int = 5

class GenerateQuestionsResponse(BaseModel):
    questions: List[str]

class SummarizeAnswersRequest(BaseModel):
    question_text: str
    answers: List[str]

class SummarizeAnswersResponse(BaseModel):
    question_text: str
    summary: str

class SurveySummaryRequest(BaseModel):
    survey_data: Dict[str, Any]

class SurveySummaryResponse(BaseModel):
    survey_title: str
    total_answers: int
    generated_at: str
    summary: str
    key_metrics: Dict[str, Any]

class QuestionInsightsRequest(BaseModel):
    question_data: Dict[str, Any]

class QuestionInsightsResponse(BaseModel):
    question_id: str
    question_text: str
    total_responses: int
    insights: str
    response_distribution: Dict[str, Any]
    analysis_timestamp: str

# --- 创建路由器 ---
router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)

# --- 定义 API 端点 ---

@router.post("/generate_questions", response_model=GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest):
    """
    根据主题自动生成问卷问题。
    """
    logger.info(f"收到生成问题请求: 主题='{request.topic}', 数量={request.num_questions}")
    try:
        questions = await llm_service.generate_questions(request.topic, request.num_questions)
        return GenerateQuestionsResponse(questions=questions)
    except Exception as e:
        logger.error(f"生成问题失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/summarize_answers", response_model=SummarizeAnswersResponse)
async def summarize_answers(request: SummarizeAnswersRequest):
    """
    对问卷问题的回答进行 LLM 总结。
    """
    logger.info(f"收到总结回答请求: 问题='{request.question_text[:30]}...'")
    try:
        summary = await llm_service.summarize_answers(request.question_text, request.answers)
        return SummarizeAnswersResponse(question_text=request.question_text, summary=summary)
    except Exception as e:
        logger.error(f"总结回答失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate_survey_summary", response_model=SurveySummaryResponse)
async def generate_survey_summary(request: SurveySummaryRequest):
    """
    生成调研的智能总结报告。
    """
    logger.info(f"收到生成调研总结请求: 调研='{request.survey_data.get('survey_title', '未知')}'")
    try:
        summary_data = await llm_service.generate_survey_summary(request.survey_data)
        return SurveySummaryResponse(**summary_data)
    except Exception as e:
        logger.error(f"生成调研总结失败: {e}")
        # 返回一个默认的响应而不是抛出异常
        from datetime import datetime
        return SurveySummaryResponse(
            survey_title=request.survey_data.get('survey_title', '未知调研'),
            total_answers=request.survey_data.get('total_answers', 0),
            generated_at=datetime.now().isoformat(),
            summary=f"由于LLM服务暂时不可用，无法生成AI总结。错误信息：{str(e)}\n\n请检查LLM服务配置或稍后重试。",
            key_metrics={
                "total_questions": len(request.survey_data.get('question_analytics', [])),
                "total_participants": request.survey_data.get('participant_analysis', {}).get('total_participants', 0),
                "participation_rate": request.survey_data.get('participation_rate', 0)
            }
        )

@router.post("/generate_question_insights", response_model=QuestionInsightsResponse)
async def generate_question_insights(request: QuestionInsightsRequest):
    """
    生成单个问题的深度洞察分析。
    """
    logger.info(f"收到生成问题洞察请求: 问题='{request.question_data.get('question_text', '未知')[:30]}...'")
    try:
        insights_data = await llm_service.generate_question_insights(request.question_data)
        return QuestionInsightsResponse(**insights_data)
    except Exception as e:
        logger.error(f"生成问题洞察失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

