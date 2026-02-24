# backend/app/services/llm_service.py
"""
LLM 服务模块，用于与大语言模型进行交互。
支持 OpenRouter API。
"""
import logging
from typing import List, Optional, Dict, Any
import httpx
from ..config import settings
import json
from datetime import datetime
import statistics

# --- 终极调试：在模块加载时打印 ---
# 这行会在该模块第一次被导入时执行
logger = logging.getLogger(__name__)
key_status = "LOADED" if settings.OPENROUTER_API_KEY else "NOT LOADED"
key_preview = settings.OPENROUTER_API_KEY[:15] + "..." if len(settings.OPENROUTER_API_KEY) > 15 else "Too_Short/Empty"
logger.critical(f"[LLM Service Module Load] OPENROUTER_API_KEY Status: {key_status}, Preview: {key_preview}")
# --- 终极调试结束 ---

# logger = logging.getLogger(__name__)

# --- 1. 定义常量 ---
# OpenRouter API 基础 URL
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# 你可以选择任何在 OpenRouter 上可用的模型
# 如果Mistral不可用，可以尝试其他免费模型
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"
# 备用模型选项：
# "meta-llama/llama-3.1-8b-instruct:free"
# "deepseek/deepseek-chat-v3-0324:free"
# "google/gemma-2-9b-it:free"

# --- 2. 定义内部辅助函数 ---

async def _call_openrouter(prompt: str, model: str = DEFAULT_MODEL, system_message: str = "你是一个专业的问卷调查助手。") -> str:
    """
    调用 OpenRouter API。
    """
    if not settings.OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY 未在环境变量中设置。")
        # 返回一个默认的响应而不是抛出异常
        return f"由于API密钥未配置，无法调用LLM服务。以下是基于输入的分析：\n\n{prompt}\n\n请配置OPENROUTER_API_KEY环境变量以启用完整的AI功能。"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8000", # 可选，但推荐填写，有助于 OpenRouter 统计
        "X-Title": "Survey System", # 可选，应用名称
        "Content-Type": "application/json"
    }
    
    # --- 在发送请求前，再打印一次 headers 的关键部分 ---
    auth_header_preview = headers.get("Authorization", "")[:20] + "..." if len(headers.get("Authorization", "")) > 20 else "Missing/Too_Short"
    logger.debug(f"3. [LLM Service] Final Authorization header (preview): {auth_header_preview}")
    # --- 调试信息结束 ---

    # 构造消息列表
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    
    data = {
        "model": model,
        "messages": messages,
        # 你可以根据需要调整这些参数
        # "temperature": 0.7,
        # "max_tokens": 1000,
        # "top_p": 1,
        # "frequency_penalty": 0,
        # "presence_penalty": 0,
    }

    async with httpx.AsyncClient() as client:
        try:
            # 增加超时时间，Mistral模型可能需要更长时间
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=300.0) 
            response.raise_for_status()

            logger.debug(f"OpenRouter API 原始响应状态码: {response.status_code}")
            logger.debug(f"OpenRouter API 原始响应头: {response.headers}")
            logger.debug(f"OpenRouter API 原始响应内容 (前500字符): {response.text[:500]}")
            
            try:
                res_data = response.json()
            except json.JSONDecodeError as json_err:
                logger.error(f"无法解析OpenRouter API 的 JSON 响应。原始响应内容: {response.text[:500]}")
                raise RuntimeError(f"API 返回了无效的 JSON: {response.text[:500]}...") from json_err
            
            # 提取生成的文本
            if 'choices' in res_data and res_data['choices']:
                # OpenRouter 返回的是标准的 OpenAI 格式
                generated_text = res_data['choices'][0]['message']['content']
                return generated_text
            else:
                error_msg = f"OpenRouter API 返回格式异常: {res_data}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except httpx.HTTPStatusError as e:
            # 尝试解析错误信息
            try:
                error_detail = e.response.json().get('error', {}).get('message', '未知错误')
            except:
                error_detail = e.response.text[:500]
            error_msg = f"调用 OpenRouter API 失败 (HTTP {e.response.status_code}): {error_detail}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"调用 OpenRouter API 时发生网络错误: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"调用 OpenRouter API 时发生未知错误: {e}"
            logger.exception(error_msg)
            raise RuntimeError(error_msg) from e

# --- 3. 定义对外服务函数 ---

async def generate_questions(topic: str, num_questions: int = 5, model: str = DEFAULT_MODEL) -> List[str]:
    """
    根据给定主题自动生成问卷问题。

    Args:
        topic (str): 问卷的主题。
        num_questions (int): 要生成的问题数量。
        model (str): 要使用的 LLM 模型名称。

    Returns:
        List[str]: 生成的问题列表。
    """
    prompt = f"""
请为以下主题生成 {num_questions} 个问卷问题。
主题: {topic}

要求:
1. 问题应清晰、具体，避免歧义。
2. 问题类型可以包括单选、多选和开放式问题。
3. 请直接列出问题，每行一个问题，不要添加编号或项目符号。
4. 请用中文回答。

问题列表:
"""
    try:
        raw_response = await _call_openrouter(prompt, model=model)
        
        # 简单的后处理：按行分割，并过滤掉空行
        questions = [q.strip() for q in raw_response.strip().split('\n') if q.strip()]
        logger.info(f"为 '{topic}' 生成了 {len(questions)} 个问题。")
        return questions
        
    except Exception as e:
        logger.exception(f"生成问题时失败: {e}")
        raise RuntimeError(f"生成问题失败: {e}") from e

async def summarize_answers(question_text: str, answers: List[str], model: str = DEFAULT_MODEL) -> str:
    """
    使用 LLM 对问卷问题的回答进行总结。

    Args:
        question_text (str): 问题的文本。
        answers (List[str]): 回答列表。
        model (str): 要使用的 LLM 模型名称。

    Returns:
        str: LLM 生成的总结文本。
    """
    if not answers:
        return "没有收集到任何回答。"

    # 数据预处理
    answers_text = "\n".join([f"- {answer}" for answer in answers if answer.strip()])
    
    if not answers_text.strip():
         return "所有回答均为空。"

    # 构造 Prompt
    prompt = f"""
你是一个专业的数据分析员。请根据以下信息，对用户的回答进行总结和分析。

问题：
{question_text}

用户的回答如下：
{answers_text}

请执行以下任务：
1.  **总结主要观点**: 概括用户回答中的核心内容和共同点。
2.  **识别趋势和模式**: 指出回答中出现的明显趋势或模式。
3.  **情感分析 (可选)**: 如果适用，简要分析回答的整体情感倾向（积极、消极、中立）。
4.  **输出格式**: 请使用清晰、简洁的中文，并分点列出你的发现。

你的总结：
"""

    try:
        summary = await _call_openrouter(prompt, model=model)
        logger.info(f"为问题 '{question_text[:20]}...' 生成了总结。")
        return summary
        
    except Exception as e:
        logger.exception(f"总结回答时失败: {e}")
        raise RuntimeError(f"总结回答失败: {e}") from e

async def generate_survey_summary(survey_data: Dict[str, Any], model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    生成调研的智能总结报告。

    Args:
        survey_data (Dict[str, Any]): 调研数据，包含问题、答案、统计等信息。
        model (str): 要使用的 LLM 模型名称。

    Returns:
        Dict[str, Any]: 包含总结报告的字典。
    """
    try:
        # 提取关键数据
        survey_title = survey_data.get('survey_title', '未知调研')
        total_answers = survey_data.get('total_answers', 0)
        question_analytics = survey_data.get('question_analytics', [])
        participant_analysis = survey_data.get('participant_analysis', {})
        participation_rate = survey_data.get('participation_rate', 0)
        
        # 数据预处理和分析
        question_types = {}
        response_rates = []
        satisfaction_scores = []
        key_insights = []
        
        for question in question_analytics:
            q_type = question.get('question_type', '')
            question_types[q_type] = question_types.get(q_type, 0) + 1
            
            # 计算响应率
            total_responses = question.get('total_responses', 0)
            response_rates.append(total_responses)
            
            # 分析回答分布，提取关键洞察
            response_dist = question.get('response_distribution', {})
            if response_dist and isinstance(response_dist, dict):
                # 识别最高频回答
                max_answer = max(response_dist.items(), key=lambda x: x[1]) if response_dist else None
                if max_answer:
                    key_insights.append({
                        "question": question.get('question_text', ''),
                        "most_common": max_answer[0],
                        "count": max_answer[1]
                    })
        
        # 构造更智能的提示词
        prompt = f"""
你是一个资深的数据分析师和调研专家，拥有丰富的行业经验和洞察力。请基于以下调研数据，生成一份深度分析报告。

## 调研背景信息
- 调研主题：{survey_title}
- 收集答案总数：{total_answers}
- 问题总数：{len(question_analytics)}
- 问题类型分布：{question_types}
- 参与率：{participation_rate:.2f}%

## 深度分析数据

### 问题详细数据：
"""
        
        # 添加每个问题的详细分析数据
        for i, question in enumerate(question_analytics, 1):
            question_text = question.get('question_text', '')
            question_type = question.get('question_type', '')
            total_responses = question.get('total_responses', 0)
            response_distribution = question.get('response_distribution', {})
            options = question.get('options', [])
            
            prompt += f"""
#### 问题{i}: {question_text}
- **类型**: {question_type}
- **回答总数**: {total_responses}
- **回答分布**: {response_distribution}
- **选项列表**: {options}
"""
            
            # 如果是评分题，添加分数分析
            if question_type in ['rating', 'scale'] and response_distribution:
                try:
                    # 尝试提取数字评分
                    scores = []
                    for key, value in response_distribution.items():
                        if key.replace('.', '').isdigit():
                            scores.extend([float(key)] * int(value))
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        prompt += f"- **平均分**: {avg_score:.2f}\n"
                        satisfaction_scores.append(avg_score)
                except Exception:
                    pass
        
        # 添加参与者分析数据
        if participant_analysis:
            participant_breakdown = []
            
            # 部门分析
            by_dept = participant_analysis.get('by_department', {})
            if by_dept:
                dept_analysis = []
                for dept, count in by_dept.items():
                    dept_analysis.append(f"{dept} ({count}人)")
                participant_breakdown.append(f"按部门: {', '.join(dept_analysis)}")
            
            # 职位分析
            by_position = participant_analysis.get('by_position', {})
            if by_position:
                pos_analysis = []
                for pos, count in by_position.items():
                    pos_analysis.append(f"{pos} ({count}人)")
                participant_breakdown.append(f"按职位: {', '.join(pos_analysis)}")
            
            if participant_breakdown:
                prompt += f"""
### 参与者结构分析
- 总参与人数：{participant_analysis.get('total_participants', 0)}
- 参与者分布：{"; ".join(participant_breakdown)}
"""
        
        # 添加关键洞察预分析
        if key_insights:
            prompt += "\n### 初步关键发现\n"
            for insight in key_insights:
                prompt += f"- **{insight['question']}**: 最常见回答是 '{insight['most_common']}' ({insight['count']}次)\n"
        
        # 添加整体满意度分析（如果有评分数据）
        if satisfaction_scores:
            overall_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            prompt += f"\n### 整体满意度评分: {overall_satisfaction:.2f}\n"
        
        prompt += """

## 分析要求
请基于以上数据，生成一份结构化、深入的分析报告，必须包含以下部分：

### 1. 执行摘要
- 用3-5个要点总结最重要的发现和结论
- 突出关键趋势和异常情况

### 2. 参与情况深度分析
- 评估样本代表性和数据质量
- 分析参与度影响因素
- 识别潜在的参与偏差

### 3. 问题专项分析
- 按问题类型分组分析
- 识别回答模式和异常
- 对比分析不同问题的相关性

### 4. 关键发现与洞察
- 列出5-7个最重要的发现
- 每个发现都要有数据支撑
- 识别潜在的根本原因

### 5. 情感与态度分析
- 基于回答内容分析整体情感倾向
- 识别热点问题和敏感话题
- 评估受访者的整体态度

### 6. 改进建议与行动计划
- 提供具体、可操作的改进建议
- 按优先级排序（高/中/低）
- 包含短期和长期行动计划

### 7. 风险评估与机遇
- 识别潜在风险点
- 发现改进机遇
- 提供风险缓解策略

请确保分析：
- 基于数据，避免主观臆测
- 结构清晰，逻辑严密
- 语言专业但不晦涩
- 每个结论都有数据支撑
- 建议具体且可执行

输出格式要求使用Markdown格式，标题层级清晰，便于阅读和理解。
"""

        # 调用LLM生成总结
        logger.info(f"开始生成调研 '{survey_title}' 的智能总结报告...")
        summary_text = await _call_openrouter(prompt, model=model)
        
        # 构造结构化的返回结果
        current_time = datetime.now().isoformat()
        
        # 计算附加指标
        total_questions = len(question_analytics)
        avg_responses_per_question = sum(response_rates) / total_questions if total_questions > 0 else 0
        
        result = {
            "survey_title": survey_title,
            "total_answers": total_answers,
            "generated_at": current_time,
            "summary": summary_text,
            "analysis_metadata": {
                "total_questions": total_questions,
                "total_participants": participant_analysis.get('total_participants', 0),
                "participation_rate": round(participation_rate, 2),
                "question_types": question_types,
                "avg_responses_per_question": round(avg_responses_per_question, 2),
                "data_quality_score": min(100, participation_rate * 2),  # 简单的数据质量评分
                "analysis_version": "2.0"  # 版本标识
            },
            "key_metrics": {
                "total_questions": total_questions,
                "total_participants": participant_analysis.get('total_participants', 0),
                "participation_rate": round(participation_rate, 2),
                "overall_satisfaction": round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else None
            },
            "highlights": {
                "top_insights": key_insights[:3],  # 前3个关键洞察
                "question_response_summary": {qt: count for qt, count in question_types.items()},
                "data_completeness": f"{(total_answers / (total_questions * participant_analysis.get('total_participants', 1))) * 100:.1f}%" if participant_analysis.get('total_participants', 0) > 0 else "N/A"
            }
        }
        
        logger.info(f"成功生成调研 '{survey_title}' 的智能总结报告，总长度: {len(summary_text)} 字符")
        return result
        
    except Exception as e:
        logger.exception(f"生成调研总结时失败: {e}")
        # 提供更详细的错误信息
        error_details = f"错误类型: {type(e).__name__}, 错误信息: {str(e)}"
        raise RuntimeError(f"生成调研总结失败: {error_details}") from e

async def generate_question_insights(question_data: Dict[str, Any], model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    生成单个问题的深度洞察分析。

    Args:
        question_data (Dict[str, Any]): 问题数据，包含问题文本、回答分布等。
        model (str): 要使用的 LLM 模型名称。

    Returns:
        Dict[str, Any]: 包含问题洞察的字典。
    """
    try:
        # 提取并预处理数据
        question_text = question_data.get('question_text', '')
        question_type = question_data.get('question_type', '')
        total_responses = question_data.get('total_responses', 0)
        response_distribution = question_data.get('response_distribution', {})
        options = question_data.get('options', [])
        
        # 数据分析预处理
        analysis_metadata = {}
        
        # 分析回答分布
        if response_distribution and isinstance(response_distribution, dict):
            total_count = sum(response_distribution.values())
            most_common = max(response_distribution.items(), key=lambda x: x[1]) if response_distribution else None
            least_common = min(response_distribution.items(), key=lambda x: x[1]) if response_distribution else None
            
            # 计算分布的集中度（基尼系数的简化版本）
            if total_count > 0:
                proportions = [count/total_count for count in response_distribution.values()]
                concentration = sum(p**2 for p in proportions)  # 集中度指数，越高表示分布越集中
                analysis_metadata['concentration'] = round(concentration, 3)
                
                # 识别异常值（占比显著高于/低于平均的回答）
                avg_proportion = 1/len(response_distribution) if len(response_distribution) > 0 else 0
                outliers = []
                for answer, count in response_distribution.items():
                    proportion = count/total_count
                    if proportion > avg_proportion * 2:  # 显著高于平均
                        outliers.append({"answer": answer, "proportion": round(proportion, 3), "type": "high"})
                    elif proportion < avg_proportion * 0.5:  # 显著低于平均
                        outliers.append({"answer": answer, "proportion": round(proportion, 3), "type": "low"})
                analysis_metadata['outliers'] = outliers
            
            analysis_metadata['most_common'] = {"answer": most_common[0], "count": most_common[1]} if most_common else None
            analysis_metadata['least_common'] = {"answer": least_common[0], "count": least_common[1]} if least_common else None
            analysis_metadata['total_responses'] = total_count
        
        # 如果是评分题，计算分数统计
        score_analysis = {}
        if question_type in ['rating', 'scale'] and response_distribution:
            try:
                scores = []
                for key, value in response_distribution.items():
                    if key.replace('.', '').replace('-', '').isdigit():
                        scores.extend([float(key)] * int(value))
                
                if scores:
                    score_analysis = {
                        "mean": round(statistics.mean(scores), 2),
                        "median": round(statistics.median(scores), 2),
                        "mode": round(statistics.mode(scores), 2) if len(set(scores)) < len(scores) else None,
                        "stdev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
                        "min_score": min(scores),
                        "max_score": max(scores),
                        "score_range": max(scores) - min(scores)
                    }
                    analysis_metadata['score_analysis'] = score_analysis
            except Exception as e:
                logger.warning(f"分数分析失败: {e}")
        
        # 构造更智能的提示词
        prompt = f"""
你是一位资深的数据分析专家和行为心理学研究员，擅长从调研数据中发现深层含义和行为模式。请对以下问题进行全方位的深度分析。

## 问题基本信息
- **问题文本**: {question_text}
- **问题类型**: {question_type}
- **总回答数**: {total_responses}

## 回答数据分析
- **回答分布**: {response_distribution}
- **选项列表**: {options}

## 预分析数据
"""
        
        # 添加预分析结果
        if analysis_metadata:
            prompt += "### 关键统计指标\n"
            for key, value in analysis_metadata.items():
                if key != 'outliers':  # 异常值单独处理
                    prompt += f"- **{key}**: {value}\n"
            
            # 处理异常值
            if 'outliers' in analysis_metadata and analysis_metadata['outliers']:
                prompt += "\n### 异常回答模式\n"
                for outlier in analysis_metadata['outliers']:
                    outlier_type = "显著高于平均" if outlier['type'] == 'high' else "显著低于平均"
                    prompt += f"- **{outlier['answer']}**: 占比 {outlier['proportion']*100:.1f}% ({outlier_type})\n"
        
        # 添加分数分析
        if score_analysis:
            prompt += "\n### 分数统计\n"
            for key, value in score_analysis.items():
                prompt += f"- **{key}**: {value}\n"
        
        prompt += """

## 分析要求
请提供以下六个维度的深度分析，每个分析都要基于数据、有洞察力、具有实用价值：

### 1. 回答模式与分布特征
- 分析回答分布的形状和特点（集中/分散/偏态等）
- 识别主流观点和少数派意见
- 分析不同选项之间的关联性

### 2. 行为与心理洞察
- 基于回答分析受访者的心理状态和行为动机
- 识别潜在的情绪倾向和态度模式
- 分析回答背后的深层原因

### 3. 异常值与特殊发现
- 深入分析异常回答的原因和含义
- 识别数据中的"惊喜"或意外发现
- 分析极端回答代表的意义

### 4. 业务影响与风险评估
- 评估这个问题反映的业务状况
- 识别潜在的风险点和机会
- 分析对业务决策的影响

### 5. 改进建议与行动方案
- 提供具体、可操作的改进建议
- 建议后续的跟进措施
- 提出优化问题的建议

### 6. 关键洞察总结
- 用3-5个要点总结最重要的发现
- 每个洞察都要有数据支撑
- 提供决策建议的优先级

## 输出要求
- 使用Markdown格式，结构清晰
- 每个部分都有数据支撑，避免主观臆测
- 语言专业但不晦涩，便于业务理解
- 突出实用性和可操作性
- 使用表情符号和格式化增强可读性

请开始你的分析：
"""

        # 调用LLM生成洞察
        logger.info(f"开始生成问题 '{question_text[:50]}...' 的深度洞察分析...")
        insights_text = await _call_openrouter(prompt, model=model)
        
        # 构造结构化的返回结果
        current_time = datetime.now().isoformat()
        
        result = {
            "question_id": question_data.get('question_id', ''),
            "question_text": question_text,
            "question_type": question_type,
            "total_responses": total_responses,
            "insights": insights_text,
            "response_distribution": response_distribution,
            "analysis_timestamp": current_time,
            "analysis_metadata": analysis_metadata,
            "key_findings": {
                "most_popular_answer": analysis_metadata.get('most_common'),
                "least_popular_answer": analysis_metadata.get('least_common'),
                "concentration_index": analysis_metadata.get('concentration'),
                "outlier_patterns": analysis_metadata.get('outliers', []),
                "score_metrics": score_analysis if score_analysis else None
            },
            "analysis_version": "2.0"  # 版本标识
        }
        
        logger.info(f"成功生成问题 '{question_text[:30]}...' 的深度洞察，分析长度: {len(insights_text)} 字符")
        return result
        
    except Exception as e:
        logger.exception(f"生成问题洞察时失败: {e}")
        error_details = f"错误类型: {type(e).__name__}, 错误信息: {str(e)}"
        raise RuntimeError(f"生成问题洞察失败: {error_details}") from e

async def generate_enterprise_comparison_analysis(comparison_data: Dict[str, Any], model: str = DEFAULT_MODEL) -> str:
    """
    生成企业对比的AI分析。

    Args:
        comparison_data (Dict[str, Any]): 企业对比数据，包含企业信息、对比维度、数据等。
        model (str): 要使用的 LLM 模型名称。

    Returns:
        str: 企业对比分析文本。
    """
    try:
        # 提取对比数据
        dimension = comparison_data.get('dimension', '')
        companies = comparison_data.get('companies', [])
        comparison_data_list = comparison_data.get('comparison_data', [])
        
        prompt = f"""
你是一个专业的企业对比分析专家。请根据以下企业对比数据生成专业的分析报告。

对比维度：{dimension}
参与企业数量：{len(companies)}个

企业信息：
"""
        
        # 添加企业信息
        for company in companies:
            prompt += f"- {company.get('name', '未知企业')} (ID: {company.get('id', 'N/A')})\n"
        
        prompt += f"""
对比数据：
"""
        
        # 添加对比数据
        for i, data in enumerate(comparison_data_list, 1):
            prompt += f"""
企业{i}：{data.get('organization_name', '未知企业')}
- 平均分数：{data.get('average_score', 0)}
- 参与率：{data.get('participation_rate', 0)}%
- 满意度：{data.get('average_satisfaction', 0)}
"""
        
        prompt += """
请生成一份专业的企业对比分析报告，包含以下部分：

1. **对比概览**：简要概述各企业的整体表现
2. **表现分析**：分析各企业在不同指标上的表现差异
3. **优势识别**：识别表现优秀企业的关键优势
4. **改进建议**：为表现相对较差的企业提供改进建议
5. **最佳实践**：总结可推广的最佳实践
6. **发展趋势**：分析企业间的发展趋势和竞争态势

请使用专业、客观的语言，确保分析准确且有洞察力。每个部分请用标题分隔，便于阅读。
"""

        # 调用LLM生成分析
        analysis_text = await _call_openrouter(prompt, model=model)
        
        logger.info(f"生成了企业对比AI分析，维度：{dimension}，企业数量：{len(companies)}")
        return analysis_text
        
    except Exception as e:
        logger.exception(f"生成企业对比分析时失败: {e}")
        raise RuntimeError(f"生成企业对比分析失败: {e}") from e

