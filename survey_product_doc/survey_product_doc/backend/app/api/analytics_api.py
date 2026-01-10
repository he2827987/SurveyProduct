# backend/app/api/analytics_api.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from backend.app.database import get_db
from backend.app.models.survey import Survey
from backend.app.models.survey_question import SurveyQuestion
from backend.app.models.answer import SurveyAnswer
from backend.app.models.question import Question, QuestionType
from backend.app.models.participant import Participant
from backend.app.models.department import Department
from backend.app.models.organization import Organization
from backend.app.models.organization_member import OrganizationMember

from backend.app.services import llm_service

router = APIRouter()



@router.get("/organizations/{organization_id}/analytics/overview")
async def get_survey_overview(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """获取组织调研概览统计"""
    
    # 获取组织的所有调研
    surveys = db.query(Survey).filter(Survey.organization_id == organization_id).all()
    
    total_surveys = len(surveys)
    total_answers = 0
    total_participants = 0
    
    for survey in surveys:
        answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey.id).all()
        total_answers += len(answers)
        # 统计独立参与者
        participant_ids = set()
        for answer in answers:
            if answer.participant_id:
                participant_ids.add(answer.participant_id)
        total_participants += len(participant_ids)
    
    # 最近7天的参与趋势
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_answers = db.query(SurveyAnswer).join(Survey).filter(
        and_(
            Survey.organization_id == organization_id,
            SurveyAnswer.submitted_at >= seven_days_ago
        )
    ).all()
    
    daily_stats = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).date()
        daily_stats[date.strftime("%Y-%m-%d")] = 0
    
    for answer in recent_answers:
        date_str = answer.submitted_at.date().strftime("%Y-%m-%d")
        if date_str in daily_stats:
            daily_stats[date_str] += 1
    
    return {
        "total_surveys": total_surveys,
        "total_answers": total_answers,
        "total_participants": total_participants,
        "average_answers_per_survey": total_answers / total_surveys if total_surveys > 0 else 0,
        "daily_trend": daily_stats
    }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/analytics")
async def get_survey_analytics(
    organization_id: int,
    survey_id: int,
    db: Session = Depends(get_db)
):
    """获取特定调研的详细分析"""
    
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取调研的所有问题（通过SurveyQuestion关联表）
    survey_questions = db.query(SurveyQuestion).filter(SurveyQuestion.survey_id == survey_id).order_by(SurveyQuestion.order).all()
    questions = []
    for sq in survey_questions:
        question = db.query(Question).filter(Question.id == sq.question_id).first()
        if question:
            questions.append(question)
    
    # 获取所有回答
    answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id).all()
    
    # 分析每个问题的回答
    question_analytics = []
    for question in questions:
        question_data = {
            "question_id": question.id,
            "question_text": question.text,
            "question_type": question.type.value,
            "total_responses": 0,
            "response_distribution": {},
            "options": json.loads(question.options) if question.options else []
        }
        question_data["answers_examples"] = []
        
        # 统计每个问题的回答
        for answer in answers:
            try:
                answer_data = json.loads(answer.answers)
                if str(question.id) in answer_data:
                    question_data["total_responses"] += 1
                    response = answer_data[str(question.id)]
                    
                    if question.type == QuestionType.SINGLE_CHOICE:
                        if response in question_data["response_distribution"]:
                            question_data["response_distribution"][response] += 1
                        else:
                            question_data["response_distribution"][response] = 1
                    elif question.type == QuestionType.MULTI_CHOICE:
                        if isinstance(response, list):
                            for choice in response:
                                if choice in question_data["response_distribution"]:
                                    question_data["response_distribution"][choice] += 1
                                else:
                                    question_data["response_distribution"][choice] = 1
                        else:
                            # 处理字符串格式的多选答案
                            if response in question_data["response_distribution"]:
                                question_data["response_distribution"][response] += 1
                            else:
                                question_data["response_distribution"][response] = 1
                    elif question.type in [QuestionType.TEXT_INPUT, QuestionType.NUMBER_INPUT]:
                        # 对于文本和数字输入，统计非空回答
                        if response and str(response).strip():
                            question_data["response_distribution"]["有回答"] = question_data["response_distribution"].get("有回答", 0) + 1
                        else:
                            question_data["response_distribution"]["无回答"] = question_data["response_distribution"].get("无回答", 0) + 1
                    
                    # 收集示例回答文本
                    if response and isinstance(response, str) and response.strip():
                        if len(question_data["answers_examples"]) < 20:
                            question_data["answers_examples"].append(response.strip())
                    elif response and isinstance(response, list):
                        joined = ", ".join([str(r).strip() for r in response if str(r).strip()])
                        if joined and len(question_data["answers_examples"]) < 20:
                            question_data["answers_examples"].append(joined)
            except (json.JSONDecodeError, KeyError):
                continue
        
        question_analytics.append(question_data)
    
    # 参与者分析
    participant_analysis = {
        "by_department": {},
        "by_position": {},
        "total_participants": 0
    }
    
    participant_ids = set()
    for answer in answers:
        if answer.participant_id:
            participant_ids.add(answer.participant_id)
    
    for participant_id in participant_ids:
        participant = db.query(Participant).filter(Participant.id == participant_id).first()
        if participant:
            participant_analysis["total_participants"] += 1
            
            # 按部门统计
            if participant.department_id:
                department = db.query(Department).filter(Department.id == participant.department_id).first()
                if department:
                    dept_name = department.name
                    participant_analysis["by_department"][dept_name] = participant_analysis["by_department"].get(dept_name, 0) + 1
            
            # 按职位统计
            if participant.position:
                participant_analysis["by_position"][participant.position] = participant_analysis["by_position"].get(participant.position, 0) + 1
    
    return {
        "survey_id": survey_id,
        "survey_title": survey.title,
        "total_answers": len(answers),
        "question_analytics": question_analytics,
        "participant_analysis": participant_analysis
    }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/analytics/ai-summary")
async def get_survey_ai_summary(
    organization_id: int,
    survey_id: int,
    db: Session = Depends(get_db)
):
    """获取调研的AI智能总结报告"""
    
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取调研分析数据
    survey_data = await get_survey_analytics(organization_id, survey_id, db)
    
    try:
        # 添加调试信息
        logger.info(f"开始生成AI总结，调研ID: {survey_id}, 组织ID: {organization_id}")
        logger.info(f"调研数据: {survey_data}")
        
        # 调用LLM服务生成智能总结
        summary_data = await llm_service.generate_survey_summary(survey_data)
        
        # 添加参与率信息
        participants = db.query(Participant).filter(Participant.organization_id == organization_id).all()
        total_participants = len(participants)
        active_participants = survey_data["participant_analysis"]["total_participants"]
        participation_rate = (active_participants / total_participants * 100) if total_participants > 0 else 0
        
        summary_data["participation_rate"] = participation_rate
        summary_data["generated_at"] = datetime.now().isoformat()
        
        logger.info(f"AI总结生成成功: {summary_data.get('summary', '')[:100]}...")
        return summary_data
        
    except Exception as e:
        logger.error(f"生成AI总结失败: {e}")
        logger.exception("详细错误信息:")
        # 返回一个友好的错误响应而不是抛出异常
        return {
            "survey_title": survey.title,
            "total_answers": survey_data.get("total_answers", 0),
            "generated_at": datetime.now().isoformat(),
            "summary": f"由于LLM服务暂时不可用，无法生成AI总结。错误信息：{str(e)}\n\n请检查LLM服务配置或稍后重试。",
            "key_metrics": {
                "total_questions": len(survey_data.get("question_analytics", [])),
                "total_participants": survey_data.get("participant_analysis", {}).get("total_participants", 0),
                "participation_rate": 0
            },
            "participation_rate": 0
        }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/questions/{question_id}/ai-insights")
async def get_question_ai_insights(
    organization_id: int,
    survey_id: int,
    question_id: int,
    db: Session = Depends(get_db)
):
    """获取单个问题的AI深度洞察分析"""
    
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取问题
    question = db.query(Question).filter(
        and_(
            Question.id == question_id,
            Question.survey_id == survey_id
        )
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 获取问题分析数据
    survey_data = await get_survey_analytics(organization_id, survey_id, db)
    
    # 找到对应的问题数据
    question_data = None
    for q in survey_data["question_analytics"]:
        if q["question_id"] == question_id:
            question_data = q
            break
    
    if not question_data:
        raise HTTPException(status_code=404, detail="问题分析数据不存在")
    
    try:
        # 调用LLM服务生成问题洞察
        insights_data = await llm_service.generate_question_insights(question_data)
        insights_data["analysis_timestamp"] = datetime.now().isoformat()
        
        return insights_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成问题洞察失败: {str(e)}")

@router.get("/organizations/{organization_id}/analytics/participants")
async def get_participant_analytics(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """获取参与者分析"""
    
    # 获取组织的所有参与者
    participants = db.query(Participant).filter(Participant.organization_id == organization_id).all()
    
    # 按部门统计
    department_stats = {}
    position_stats = {}
    total_participants = len(participants)
    
    for participant in participants:
        # 按部门统计
        if participant.department_id:
            department = db.query(Department).filter(Department.id == participant.department_id).first()
            if department:
                dept_name = department.name
                if dept_name not in department_stats:
                    department_stats[dept_name] = {
                        "count": 0,
                        "participants": []
                    }
                department_stats[dept_name]["count"] += 1
                department_stats[dept_name]["participants"].append({
                    "id": participant.id,
                    "name": participant.name,
                    "position": participant.position
                })
        
        # 按职位统计
        if participant.position:
            if participant.position not in position_stats:
                position_stats[participant.position] = 0
            position_stats[participant.position] += 1
    
    # 参与度分析（参与调研的参与者比例）
    participant_ids = set(p.id for p in participants)
    active_participants = db.query(SurveyAnswer.participant_id).join(Survey).filter(
        and_(
            Survey.organization_id == organization_id,
            SurveyAnswer.participant_id.in_(participant_ids)
        )
    ).distinct().count()
    
    return {
        "total_participants": total_participants,
        "active_participants": active_participants,
        "participation_rate": (active_participants / total_participants * 100) if total_participants > 0 else 0,
        "by_department": department_stats,
        "by_position": position_stats
    }

@router.get("/organizations/{organization_id}/analytics/trends")
async def get_trend_analytics(
    organization_id: int,
    days: int = Query(30, description="分析天数，默认30天"),
    db: Session = Depends(get_db)
):
    """获取趋势分析"""
    
    # 计算开始日期
    start_date = datetime.now() - timedelta(days=days)
    
    # 获取时间范围内的回答
    answers = db.query(SurveyAnswer).join(Survey).filter(
        and_(
            Survey.organization_id == organization_id,
            SurveyAnswer.submitted_at >= start_date
        )
    ).order_by(SurveyAnswer.submitted_at).all()
    
    # 按日期统计
    daily_stats = {}
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).date()
        daily_stats[date.strftime("%Y-%m-%d")] = {
            "answers": 0,
            "participants": set(),
            "surveys": set()
        }
    
    for answer in answers:
        date_str = answer.submitted_at.date().strftime("%Y-%m-%d")
        if date_str in daily_stats:
            daily_stats[date_str]["answers"] += 1
            if answer.participant_id:
                daily_stats[date_str]["participants"].add(answer.participant_id)
            if answer.survey_id:
                daily_stats[date_str]["surveys"].add(answer.survey_id)
    
    # 转换为可序列化的格式
    trend_data = []
    for date_str, stats in daily_stats.items():
        trend_data.append({
            "date": date_str,
            "answers": stats["answers"],
            "unique_participants": len(stats["participants"]),
            "active_surveys": len(stats["surveys"])
        })
    
    # 按日期排序
    trend_data.sort(key=lambda x: x["date"])
    
    return {
        "period_days": days,
        "total_answers": len(answers),
        "trend_data": trend_data
    }

@router.get("/organizations/{organization_id}/analytics/cross-analysis")
async def get_cross_analysis(
    organization_id: int,
    survey_id: int,
    question1_id: int,
    question2_id: int,
    db: Session = Depends(get_db)
):
    """获取交叉分析 - 分析两个问题之间的关系"""
    
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取两个问题
    question1 = db.query(Question).filter(Question.id == question1_id).first()
    question2 = db.query(Question).filter(Question.id == question2_id).first()
    
    if not question1 or not question2:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 获取所有回答
    answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id).all()
    
    # 交叉分析
    cross_analysis = {}
    
    for answer in answers:
        try:
            answer_data = json.loads(answer.answers)
            if str(question1_id) in answer_data and str(question2_id) in answer_data:
                response1 = answer_data[str(question1_id)]
                response2 = answer_data[str(question2_id)]
                
                # 处理不同类型的回答
                if question1.type == QuestionType.MULTI_CHOICE and isinstance(response1, list):
                    response1 = ", ".join(response1)
                if question2.type == QuestionType.MULTI_CHOICE and isinstance(response2, list):
                    response2 = ", ".join(response2)
                
                if response1 not in cross_analysis:
                    cross_analysis[response1] = {}
                
                if response2 not in cross_analysis[response1]:
                    cross_analysis[response1][response2] = 0
                
                cross_analysis[response1][response2] += 1
        except (json.JSONDecodeError, KeyError):
            continue
    
    return {
        "survey_id": survey_id,
        "question1": {
            "id": question1.id,
            "text": question1.text,
            "type": question1.type.value
        },
        "question2": {
            "id": question2.id,
            "text": question2.text,
            "type": question2.type.value
        },
        "cross_analysis": cross_analysis
    }

@router.get("/organizations/{organization_id}/analytics/comparison")
async def get_comparison_analysis(
    organization_id: int,
    survey1_id: int,
    survey2_id: int,
    db: Session = Depends(get_db)
):
    """获取调研对比分析"""
    
    # 验证两个调研都属于该组织
    survey1 = db.query(Survey).filter(
        and_(
            Survey.id == survey1_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    survey2 = db.query(Survey).filter(
        and_(
            Survey.id == survey2_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey1 or not survey2:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取两个调研的答案
    answers1 = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey1_id).all()
    answers2 = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey2_id).all()
    
    # 统计参与者
    participants1 = set()
    participants2 = set()
    
    for answer in answers1:
        if answer.participant_id:
            participants1.add(answer.participant_id)
    
    for answer in answers2:
        if answer.participant_id:
            participants2.add(answer.participant_id)
    
    # 计算重叠参与者
    common_participants = participants1.intersection(participants2)
    
    return {
        "survey1": {
            "id": survey1.id,
            "title": survey1.title,
            "total_answers": len(answers1),
            "unique_participants": len(participants1)
        },
        "survey2": {
            "id": survey2.id,
            "title": survey2.title,
            "total_answers": len(answers2),
            "unique_participants": len(participants2)
        },
        "comparison": {
            "common_participants": len(common_participants),
            "participation_overlap_rate": (len(common_participants) / len(participants1.union(participants2)) * 100) if participants1.union(participants2) else 0,
            "answer_ratio": len(answers1) / len(answers2) if len(answers2) > 0 else 0
        }
    }

@router.get("/organizations/{organization_id}/analytics/export")
async def export_analytics_data(
    organization_id: int,
    survey_id: Optional[int] = None,
    format: str = Query("json", description="导出格式：json 或 csv"),
    db: Session = Depends(get_db)
):
    """导出分析数据"""
    
    if survey_id:
        # 导出特定调研的数据
        survey = db.query(Survey).filter(
            and_(
                Survey.id == survey_id,
                Survey.organization_id == organization_id
            )
        ).first()
        
        if not survey:
            raise HTTPException(status_code=404, detail="调研不存在")
        
        answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id).all()
        questions = db.query(Question).filter(Question.survey_id == survey_id).all()
        
        # 构建导出数据
        export_data = []
        for answer in answers:
            row = {
                "answer_id": answer.id,
                "participant_id": answer.participant_id,
                "submitted_at": answer.submitted_at.isoformat() if answer.submitted_at else None
            }
            
            try:
                answer_data = json.loads(answer.answers)
                for question in questions:
                    question_key = str(question.id)
                    if question_key in answer_data:
                        response = answer_data[question_key]
                        if isinstance(response, list):
                            response = ", ".join(response)
                        row[f"q{question.id}_{question.text[:20]}"] = response
                    else:
                        row[f"q{question.id}_{question.text[:20]}"] = None
            except (json.JSONDecodeError, KeyError):
                pass
            
            export_data.append(row)
        
        return {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "total_records": len(export_data),
            "data": export_data
        }
    else:
        # 导出组织概览数据
        surveys = db.query(Survey).filter(Survey.organization_id == organization_id).all()
        participants = db.query(Participant).filter(Participant.organization_id == organization_id).all()
        
        return {
            "organization_id": organization_id,
            "total_surveys": len(surveys),
            "total_participants": len(participants),
            "surveys": [
                {
                    "id": survey.id,
                    "title": survey.title,
                    "created_at": survey.created_at.isoformat() if survey.created_at else None
                }
                for survey in surveys
            ],
            "participants": [
                {
                    "id": participant.id,
                    "name": participant.name,
                    "position": participant.position,
                    "department_id": participant.department_id
                }
                for participant in participants
            ]
        }

# 在企业间对比功能部分添加新的API端点

@router.get("/organizations/{organization_id}/analytics/enterprise-comparison")
async def get_enterprise_comparison(
    organization_id: int,
    survey_id: int,
    compare_organizations: str = Query(..., description="要对比的组织ID列表，用逗号分隔"),
    db: Session = Depends(get_db)
):
    """获取企业间对比分析"""
    
    # 验证调研是否存在且属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 解析要对比的组织ID列表
    try:
        compare_org_ids = [int(org_id.strip()) for org_id in compare_organizations.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="组织ID格式错误")
    
    # 获取对比组织的调研数据
    comparison_data = []
    
    for compare_org_id in compare_org_ids:
        # 获取对比组织的同名调研
        compare_survey = db.query(Survey).filter(
            and_(
                Survey.title == survey.title,  # 同名调研
                Survey.organization_id == compare_org_id
            )
        ).first()
        
        if compare_survey:
            # 获取该调研的答案
            compare_answers = db.query(SurveyAnswer).filter(
                SurveyAnswer.survey_id == compare_survey.id
            ).all()
            
            # 获取组织信息
            compare_org = db.query(Organization).filter(Organization.id == compare_org_id).first()
            
            # 统计参与者
            participant_ids = set()
            for answer in compare_answers:
                if answer.participant_id:
                    participant_ids.add(answer.participant_id)
            
            comparison_data.append({
                "organization_id": compare_org_id,
                "organization_name": compare_org.name if compare_org else f"组织{compare_org_id}",
                "survey_id": compare_survey.id,
                "total_answers": len(compare_answers),
                "unique_participants": len(participant_ids),
                "participation_rate": len(participant_ids) / 100 if len(participant_ids) > 0 else 0  # 假设总员工数为100
            })
    
    # 获取当前组织的数据作为基准
    current_answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id).all()
    current_participant_ids = set()
    for answer in current_answers:
        if answer.participant_id:
            current_participant_ids.add(answer.participant_id)
    
    current_org = db.query(Organization).filter(Organization.id == organization_id).first()
    
    baseline_data = {
        "organization_id": organization_id,
        "organization_name": current_org.name if current_org else f"组织{organization_id}",
        "survey_id": survey_id,
        "total_answers": len(current_answers),
        "unique_participants": len(current_participant_ids),
        "participation_rate": len(current_participant_ids) / 100 if len(current_participant_ids) > 0 else 0
    }
    
    return {
        "survey_title": survey.title,
        "baseline": baseline_data,
        "comparison": comparison_data,
        "total_organizations": len(comparison_data) + 1
    }

@router.get("/analytics/global-enterprise-comparison")
async def get_global_enterprise_comparison(
    survey_title: str = Query(..., description="调研标题"),
    db: Session = Depends(get_db)
):
    """获取全局企业间对比分析（基于调研标题）"""
    # 获取所有同名调研
    surveys = db.query(Survey).filter(Survey.title == survey_title).all()
    
    if not surveys:
        raise HTTPException(status_code=404, detail="未找到相关调研")
    
    comparison_data = []
    
    for survey in surveys:
        # 获取调研答案
        answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey.id).all()
        
        # 获取组织信息
        org = db.query(Organization).filter(Organization.id == survey.organization_id).first()
        
        # 统计参与者
        participant_ids = set()
        for answer in answers:
            if answer.participant_id:
                participant_ids.add(answer.participant_id)
        
        # 计算平均满意度（如果有满意度相关问题）
        avg_satisfaction = 0
        satisfaction_count = 0
        
        for answer in answers:
            try:
                answer_data = json.loads(answer.answers)
                for question_id, response in answer_data.items():
                    # 假设满意度问题包含"满意"关键词
                    if isinstance(response, str) and "满意" in response:
                        if "非常满意" in response:
                            avg_satisfaction += 5
                        elif "满意" in response:
                            avg_satisfaction += 4
                        elif "一般" in response:
                            avg_satisfaction += 3
                        elif "不满意" in response:
                            avg_satisfaction += 2
                        elif "非常不满意" in response:
                            avg_satisfaction += 1
                        satisfaction_count += 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        if satisfaction_count > 0:
            avg_satisfaction = avg_satisfaction / satisfaction_count
        
        comparison_data.append({
            "organization_id": survey.organization_id,
            "organization_name": org.name if org else f"组织{survey.organization_id}",
            "survey_id": survey.id,
            "total_answers": len(answers),
            "unique_participants": len(participant_ids),
            "participation_rate": len(participant_ids) / 100 if len(participant_ids) > 0 else 0,
            "avg_satisfaction": round(avg_satisfaction, 2)
        })
    
    # 按平均满意度排序
    comparison_data.sort(key=lambda x: x["avg_satisfaction"], reverse=True)
    
    return {
        "survey_title": survey_title,
        "total_organizations": len(comparison_data),
        "comparison_data": comparison_data,
        "industry_average": {
            "avg_satisfaction": round(sum(x["avg_satisfaction"] for x in comparison_data) / len(comparison_data), 2) if comparison_data else 0,
            "avg_participation_rate": round(sum(x["participation_rate"] for x in comparison_data) / len(comparison_data), 2) if comparison_data else 0
        }
    }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/questions/{question_id}/analytics")
async def get_question_analytics(
    organization_id: int,
    survey_id: int,
    question_id: int,
    db: Session = Depends(get_db)
):
    """获取问题分析数据"""
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取问题信息
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 获取问题的答案
    answers = db.query(SurveyAnswer).filter(
        and_(
            SurveyAnswer.survey_id == survey_id,
            SurveyAnswer.answers.contains(f'"{question_id}"')
        )
    ).all()
    
    # 分析答案分布
    response_distribution = {}
    total_responses = 0
    total_score = 0
    
    for answer in answers:
        try:
            answer_data = json.loads(answer.answers)
            if str(question_id) in answer_data:
                response = answer_data[str(question_id)]
                total_responses += 1
                
                # 统计回答分布
                if response in response_distribution:
                    response_distribution[response] += 1
                else:
                    response_distribution[response] = 1
                
                # 计算分数（如果是满意度问题）
                if isinstance(response, str):
                    if "非常满意" in response:
                        total_score += 5
                    elif "满意" in response:
                        total_score += 4
                    elif "一般" in response:
                        total_score += 3
                    elif "不满意" in response:
                        total_score += 2
                    elif "非常不满意" in response:
                        total_score += 1
        except (json.JSONDecodeError, KeyError):
            continue
    
    # 计算平均分数
    average_score = total_score / total_responses if total_responses > 0 else 0
    
    return {
        "question_id": question_id,
        "question_text": question.text,
        "question_type": question.type.value,
        "total_responses": total_responses,
        "response_distribution": response_distribution,
        "average_score": round(average_score, 2),
        "options": json.loads(question.options) if question.options else []
    }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/analytics/category/{category_id}")
async def get_category_analytics(
    organization_id: int,
    survey_id: int,
    category_id: int,
    db: Session = Depends(get_db)
):
    """获取分类分析数据"""
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 获取该分类下的所有问题
    questions = db.query(Question).filter(Question.category_id == category_id).all()
    
    if not questions:
        return {
            "category_id": category_id,
            "total_questions": 0,
            "total_responses": 0,
            "average_score": 0
        }
    
    # 获取所有答案
    answers = db.query(SurveyAnswer).filter(SurveyAnswer.survey_id == survey_id).all()
    
    total_responses = 0
    total_score = 0
    
    for question in questions:
        for answer in answers:
            try:
                answer_data = json.loads(answer.answers)
                if str(question.id) in answer_data:
                    total_responses += 1
                    response = answer_data[str(question.id)]
                    
                    # 计算分数
                    if isinstance(response, str):
                        if "非常满意" in response:
                            total_score += 5
                        elif "满意" in response:
                            total_score += 4
                        elif "一般" in response:
                            total_score += 3
                        elif "不满意" in response:
                            total_score += 2
                        elif "非常不满意" in response:
                            total_score += 1
            except (json.JSONDecodeError, KeyError):
                continue
    
    average_score = total_score / total_responses if total_responses > 0 else 0
    
    return {
        "category_id": category_id,
        "total_questions": len(questions),
        "total_responses": total_responses,
        "average_score": round(average_score, 2)
    }

@router.get("/organizations/{organization_id}/surveys/{survey_id}/analytics/tag/{tag_id}")
async def get_tag_analytics(
    organization_id: int,
    survey_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """获取标签分析数据"""
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    # 这里需要根据实际的标签系统实现
    # 暂时返回模拟数据
    return {
        "tag_id": tag_id,
        "total_questions": 5,
        "total_responses": 50,
        "average_score": 75.5
    }

@router.post("/organizations/{organization_id}/surveys/{survey_id}/analytics/enterprise-comparison-ai")
async def generate_enterprise_comparison_ai(
    organization_id: int,
    survey_id: int,
    comparison_data: dict,
    db: Session = Depends(get_db)
):
    """生成企业对比AI分析"""
    
    # 验证调研属于该组织
    survey = db.query(Survey).filter(
        and_(
            Survey.id == survey_id,
            Survey.organization_id == organization_id
        )
    ).first()
    
    if not survey:
        raise HTTPException(status_code=404, detail="调研不存在")
    
    try:
        # 调用LLM服务生成企业对比分析
        ai_analysis = await llm_service.generate_enterprise_comparison_analysis(comparison_data)
        
        return {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "generated_at": datetime.now().isoformat(),
            "comparison_analysis": ai_analysis
        }
        
    except Exception as e:
        logger.error(f"生成企业对比AI分析失败: {e}")
        logger.exception("详细错误信息:")
        # 返回友好的错误响应
        return {
            "survey_id": survey_id,
            "survey_title": survey.title,
            "generated_at": datetime.now().isoformat(),
            "comparison_analysis": f"由于LLM服务暂时不可用，无法生成企业对比AI分析。错误信息：{str(e)}\n\n请检查LLM服务配置或稍后重试。"
        }
