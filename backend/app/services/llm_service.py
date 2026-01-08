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
        # 构造调研总结的Prompt
        prompt = f"""
你是一个专业的数据分析师和调研专家。请根据以下调研数据生成一份全面的智能总结报告。

调研基本信息：
- 调研标题：{survey_data.get('survey_title', '未知')}
- 总答案数：{survey_data.get('total_answers', 0)}
- 问题数量：{len(survey_data.get('question_analytics', []))}

问题分析数据：
"""
        
        # 添加每个问题的分析数据
        for i, question in enumerate(survey_data.get('question_analytics', []), 1):
            prompt += f"""
问题{i}：{question.get('question_text', '')}
- 问题类型：{question.get('question_type', '')}
- 回答数：{question.get('total_responses', 0)}
- 回答分布：{question.get('response_distribution', {})}
"""
        
        # 添加参与者分析数据
        participant_analysis = survey_data.get('participant_analysis', {})
        if participant_analysis:
            prompt += f"""
参与者分析：
- 总参与者：{participant_analysis.get('total_participants', 0)}
- 按部门分布：{participant_analysis.get('by_department', {})}
- 按职位分布：{participant_analysis.get('by_position', {})}
"""
        
        prompt += """
请生成一份专业的调研总结报告，包含以下部分：

1. **执行摘要**：简要概述调研的主要发现和关键结论
2. **参与情况分析**：分析参与者的分布和参与度
3. **问题分析**：对每个重要问题的回答进行深入分析
4. **关键发现**：总结最重要的发现和洞察
5. **建议和行动方案**：基于调研结果提出具体的改进建议
6. **数据质量评估**：评估数据的可靠性和代表性

请使用专业、客观的语言，确保报告结构清晰，内容准确。每个部分请用标题分隔，便于阅读。
"""

        # 调用LLM生成总结
        summary_text = await _call_openrouter(prompt, model=model)
        
        # 构造返回结果
        result = {
            "survey_title": survey_data.get('survey_title', ''),
            "total_answers": survey_data.get('total_answers', 0),
            "generated_at": "2025-08-19T10:00:00Z",  # 这里应该使用实际时间
            "summary": summary_text,
            "key_metrics": {
                "total_questions": len(survey_data.get('question_analytics', [])),
                "total_participants": participant_analysis.get('total_participants', 0),
                "participation_rate": survey_data.get('participation_rate', 0)
            }
        }
        
        logger.info(f"为调研 '{survey_data.get('survey_title', '')}' 生成了智能总结报告。")
        return result
        
    except Exception as e:
        logger.exception(f"生成调研总结时失败: {e}")
        raise RuntimeError(f"生成调研总结失败: {e}") from e

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
        prompt = f"""
你是一个专业的数据分析师。请对以下调研问题进行深度洞察分析。

问题信息：
- 问题文本：{question_data.get('question_text', '')}
- 问题类型：{question_data.get('question_type', '')}
- 总回答数：{question_data.get('total_responses', 0)}
- 回答分布：{question_data.get('response_distribution', {})}
- 选项列表：{question_data.get('options', [])}

请提供以下分析：

1. **回答模式分析**：分析回答的分布模式和特点
2. **关键洞察**：识别回答中的关键发现和趋势
3. **异常发现**：指出任何异常或值得注意的回答模式
4. **改进建议**：基于分析结果提出改进建议
5. **后续行动**：建议下一步的行动方案

请使用清晰、专业的中文进行分析，确保分析准确且有洞察力。
"""

        insights_text = await _call_openrouter(prompt, model=model)
        
        result = {
            "question_id": question_data.get('question_id', ''),
            "question_text": question_data.get('question_text', ''),
            "total_responses": question_data.get('total_responses', 0),
            "insights": insights_text,
            "response_distribution": question_data.get('response_distribution', {}),
            "analysis_timestamp": "2025-08-19T10:00:00Z"
        }
        
        logger.info(f"为问题 '{question_data.get('question_text', '')[:30]}...' 生成了深度洞察。")
        return result
        
    except Exception as e:
        logger.exception(f"生成问题洞察时失败: {e}")
        raise RuntimeError(f"生成问题洞察失败: {e}") from e

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

