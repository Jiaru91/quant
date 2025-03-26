from typing import List, Dict, Any, Optional
import openai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def analyze_text(self, text: str, system_prompt: str) -> str:
        """使用OpenAI API分析文本"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"文本分析失败: {str(e)}")
            return ""

    async def analyze_news(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析新闻内容，提取关键信息并生成摘要"""
        try:
            # 构建提示词
            prompt = """请分析以下新闻内容，重点关注：
1. 公司基本面变化
2. 市场情绪
3. 重大事件影响
4. 行业趋势
5. 风险因素

请提供：
1. 关键要点总结
2. 情感分析（积极/消极/中性）
3. 可能对股价的影响
4. 置信度评分（0-1）

新闻内容：
{news_content}
"""
            
            # 准备新闻内容
            news_content = "\n\n".join([
                f"标题：{news['title']}\n"
                f"日期：{news['published_date']}\n"
                f"来源：{news['source']}\n"
                f"内容：{news['content']}\n"
                for news in news_list
            ])
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的金融分析师，擅长分析新闻对股票市场的影响。"},
                    {"role": "user", "content": prompt.format(news_content=news_content)}
                ],
                temperature=0.3
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"新闻分析失败: {str(e)}")
            return {"error": str(e)}

    async def analyze_financial_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析财务报表，提取关键指标并进行评估"""
        try:
            # 构建提示词
            prompt = """请分析以下财务报表数据，重点关注：
1. 收入增长
2. 利润率变化
3. 现金流状况
4. 资产负债结构
5. 主要财务指标分析

请提供：
1. 关键财务指标分析
2. 同比环比变化
3. 财务健康评估
4. 风险提示
5. 建议关注点

财务数据：
{report_data}
"""
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的财务分析师，擅长解读财务报表并提供深入分析。"},
                    {"role": "user", "content": prompt.format(report_data=str(report_data))}
                ],
                temperature=0.2
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"财务报表分析失败: {str(e)}")
            return {"error": str(e)}

    async def predict_stock_price(
        self,
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        news_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """预测股票价格"""
        try:
            analysis_text = (
                f"技术面数据:\n{technical_data}\n\n"
                f"基本面数据:\n{fundamental_data}\n\n"
                f"新闻分析:\n{news_analysis}"
            )
            
            system_prompt = """
            你是一个专业的量化分析师。请基于提供的技术面、基本面和新闻数据，进行股票价格预测分析：
            1. 短期价格趋势预测
            2. 支撑和阻力位预测
            3. 预测置信度评估
            4. 风险提示
            请以JSON格式返回结果。
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_text}
                ],
                temperature=0.3
            )
            
            return {
                "prediction": response.choices[0].message.content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"股价预测失败: {str(e)}")
            return {"error": str(e)}

    async def resolve_conflicts(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """解决不同分析结果之间的冲突"""
        try:
            # 构建提示词
            prompt = """请分析以下多个分析结果中的冲突，并给出综合建议：

分析结果：
{analyses}

请提供：
1. 冲突点分析
2. 各观点的支持论据
3. 综合评估
4. 最终建议
5. 置信度评分（0-1）
"""
            
            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个资深的投资顾问，擅长分析不同观点并给出平衡的建议。"},
                    {"role": "user", "content": prompt.format(analyses=str(analyses))}
                ],
                temperature=0.3
            )
            
            return {
                "resolution": response.choices[0].message.content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"冲突解决失败: {str(e)}")
            return {"error": str(e)} 