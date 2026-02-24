# backend/app/api/llm_api.py
"""
LLM 相关的 API 端点。
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
from datetime import datetime

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
    analysis_metadata: Optional[Dict[str, Any]] = None
    highlights: Optional[Dict[str, Any]] = None

class QuestionInsightsRequest(BaseModel):
    question_data: Dict[str, Any]

class QuestionInsightsResponse(BaseModel):
    question_id: str
    question_text: str
    question_type: Optional[str] = None
    total_responses: int
    insights: str
    response_distribution: Dict[str, Any]
    analysis_timestamp: str
    analysis_metadata: Optional[Dict[str, Any]] = None
    key_findings: Optional[Dict[str, Any]] = None

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
    survey_title = request.survey_data.get('survey_title', '未知调研')
    logger.info(f"收到生成调研总结请求: 调研='{survey_title}'")
    
    # 验证请求数据
    if not request.survey_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="请求数据不能为空"
        )
    
    # 检查是否有足够的数据进行分析
    question_analytics = request.survey_data.get('question_analytics', [])
    if not question_analytics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="没有问题分析数据，无法生成总结报告"
        )
    
    try:
        summary_data = await llm_service.generate_survey_summary(request.survey_data)
        
        # 验证返回数据完整性
        if not summary_data or 'summary' not in summary_data:
            raise ValueError("LLM服务返回的数据不完整")
            
        # 添加处理状态信息
        summary_data['processing_status'] = {
            "success": True,
            "message": "总结生成成功",
            "processing_time": datetime.now().isoformat()
        }
        
        return SurveySummaryResponse(**summary_data)
        
    except Exception as e:
        logger.error(f"生成调研总结失败: {e}")
        logger.exception("详细错误信息:")
        
        # 尝试提供有意义的错误分析
        error_type = type(e).__name__
        error_msg = str(e)
        
        # 根据错误类型提供不同的错误信息
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            user_msg = "AI服务暂时连接超时，请稍后重试。"
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            user_msg = "AI服务配置错误，请联系系统管理员。"
        elif "rate limit" in error_msg.lower():
            user_msg = "AI服务使用频率过高，请稍后重试。"
        else:
            user_msg = f"生成总结时遇到技术问题：{error_type}"
        
        # 返回带有详细错误信息的响应
        error_response_data = {
            "survey_title": survey_title,
            "total_answers": request.survey_data.get('total_answers', 0),
            "generated_at": datetime.now().isoformat(),
            "summary": f"""# 报告生成失败

## 错误信息
{user_msg}

## 技术详情
- 错误类型: {error_type}
- 错误详情: {error_msg}

## 建议操作
1. 检查网络连接是否正常
2. 稍后重试操作
3. 如果问题持续存在，请联系技术支持

## 数据概览
- 问题数量: {len(question_analytics)}
- 参与者数量: {request.survey_data.get('participant_analysis', {}).get('total_participants', 0)}
""",
            "key_metrics": {
                "total_questions": len(question_analytics),
                "total_participants": request.survey_data.get('participant_analysis', {}).get('total_participants', 0),
                "participation_rate": request.survey_data.get('participation_rate', 0),
                "analysis_failed": True
            },
            "analysis_metadata": {
                "error_occurred": True,
                "error_type": error_type,
                "error_message": error_msg,
                "fallback_mode": True
            },
            "processing_status": {
                "success": False,
                "message": user_msg,
                "error_type": error_type,
                "processing_time": datetime.now().isoformat()
            }
        }
        
        return SurveySummaryResponse(**error_response_data)

@router.post("/generate_question_insights", response_model=QuestionInsightsResponse)
async def generate_question_insights(request: QuestionInsightsRequest):
    """
    生成单个问题的深度洞察分析。
    """
    question_text = request.question_data.get('question_text', '未知问题')
    question_id = request.question_data.get('question_id', '未知ID')
    logger.info(f"收到生成问题洞察请求: 问题ID={question_id}, 问题='{question_text[:30]}...'")
    
    # 验证请求数据
    if not request.question_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="请求数据不能为空"
        )
    
    if not question_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="问题文本不能为空"
        )
    
    # 检查回答分布数据
    response_dist = request.question_data.get('response_distribution', {})
    if not response_dist or not isinstance(response_dist, dict):
        logger.warning(f"问题 {question_id} 没有有效的回答分布数据")
    
    try:
        insights_data = await llm_service.generate_question_insights(request.question_data)
        
        # 验证返回数据完整性
        if not insights_data or 'insights' not in insights_data:
            raise ValueError("LLM服务返回的数据不完整")
            
        # 添加处理状态信息
        insights_data['processing_status'] = {
            "success": True,
            "message": "洞察分析生成成功",
            "processing_time": datetime.now().isoformat()
        }
        
        return QuestionInsightsResponse(**insights_data)
        
    except Exception as e:
        logger.error(f"生成问题洞察失败: {e}")
        logger.exception("详细错误信息:")
        
        # 尝试提供有意义的错误分析
        error_type = type(e).__name__
        error_msg = str(e)
        
        # 根据错误类型提供不同的错误信息
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            user_msg = "AI服务暂时连接超时，请稍后重试。"
        elif "api" in error_msg.lower() and "key" in error_msg.lower():
            user_msg = "AI服务配置错误，请联系系统管理员。"
        elif "rate limit" in error_msg.lower():
            user_msg = "AI服务使用频率过高，请稍后重试。"
        else:
            user_msg = f"生成洞察时遇到技术问题：{error_type}"
        
        # 返回带有详细错误信息的响应
        error_response_data = {
            "question_id": question_id,
            "question_text": question_text,
            "question_type": request.question_data.get('question_type', ''),
            "total_responses": request.question_data.get('total_responses', 0),
            "insights": f"""# 问题洞察分析失败

## 错误信息
{user_msg}

## 技术详情
- 错误类型: {error_type}
- 错误详情: {error_msg}

## 数据概览
- 回答总数: {request.question_data.get('total_responses', 0)}
- 回答分布: {response_dist}
- 问题类型: {request.question_data.get('question_type', '未知')}

## 基础分析
基于可用数据进行的简单分析：
""",
            "response_distribution": response_dist,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_metadata": {
                "error_occurred": True,
                "error_type": error_type,
                "error_message": error_msg,
                "fallback_mode": True,
                "basic_analysis": True
            },
            "processing_status": {
                "success": False,
                "message": user_msg,
                "error_type": error_type,
                "processing_time": datetime.now().isoformat()
            }
        }
        
        # 添加基础分析
        basic_analysis = []
        if response_dist and isinstance(response_dist, dict):
            total_count = sum(response_dist.values())
            if total_count > 0:
                # 找出最常见的回答
                most_common = max(response_dist.items(), key=lambda x: x[1]) if response_dist else None
                if most_common:
                    basic_analysis.append(f"最常见回答：'{most_common[0]}' ({most_common[1]}次, 占比{most_common[1]/total_count*100:.1f}%)")
                
                # 计算回答分布的集中度
                proportions = [count/total_count for count in response_dist.values()]
                concentration = sum(p**2 for p in proportions)
                if concentration > 0.5:
                    basic_analysis.append("回答分布较为集中，表明受访者观点相对一致")
                elif concentration < 0.3:
                    basic_analysis.append("回答分布较为分散，表明受访者观点多样化")
                else:
                    basic_analysis.append("回答分布适中，没有明显的一致性或分歧")
        
        error_response_data["insights"] += "\n".join(f"- {analysis}" for analysis in basic_analysis)
        
        return QuestionInsightsResponse(**error_response_data)

