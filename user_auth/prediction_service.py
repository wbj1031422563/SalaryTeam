from openai import OpenAI
import json
from datetime import datetime, timedelta
import random  # 用于生成模拟数据

class PredictionService:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-FSaV63sjv2Xcpl0pxrUcCcf5mLW2vkGRwnMJjSLlgVMahR60",
            base_url="https://api.moonshot.cn/v1",
        )
    
    def get_stock_prediction(self, stock_code, time_frame, prediction_type):
        # 构建提示词
        prompt = f"""请基于以下参数对股票进行预测分析：
        股票代码：{stock_code}
        时间范围：{time_frame}
        预测类型：{prediction_type}
        
        请提供：
        1. 预测价格区间
        2. 可信度评估
        3. 主要影响因素分析
        4. 风险提示
        5. 未来趋势预测数据点（按天）
        
        返回格式要求：JSON格式，包含以下字段：
        {{
            "prediction_price": {{
                "min": float,
                "max": float,
                "current": float
            }},
            "confidence_level": "high|medium|low",
            "factors": [string],
            "risks": [string],
            "trend_data": [
                {{
                    "date": "YYYY-MM-DD",
                    "predicted_price": float,
                    "upper_bound": float,
                    "lower_bound": float
                }}
            ]
        }}
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的金融分析AI助手，请基于历史数据和市场分析提供准确的股票预测。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        
        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None
    
    def get_market_prediction(self):
        """获取整体市场预测"""
        prompt = """请分析当前市场整体趋势，并提供：
        1. 主要指数预测
        2. 行业板块展望
        3. 市场情绪分析
        4. 关键风险因素
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的市场分析AI助手，请提供准确的市场预测。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None

    def get_technical_indicators(self, stock_code):
        """获取技术指标预测"""
        prompt = f"""请分析{stock_code}的主要技术指标，包括：
        1. MA (移动平均线)
        2. RSI (相对强弱指标)
        3. MACD (指数平滑移动平均线)
        4. KDJ (随机指标)
        
        并提供未来趋势预测。返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的技术分析AI助手，请提供准确的技术指标分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None

    def get_time_series_prediction(self, stock_code: str, historical_data: list, prediction_days: int = 30):
        """基于时间序列数据进行预测
        
        Args:
            stock_code: 股票代码
            historical_data: 历史数据列表，每个元素为 {date: str, price: float, volume: int}
            prediction_days: 预测天数
            
        Returns:
            预测结果，包含预测值和置信区间
        """
        prompt = f"""基于以下历史数据进行时间序列预测分析：
        股票代码：{stock_code}
        历史数据：{json.dumps(historical_data, ensure_ascii=False)}
        预测天数：{prediction_days}
        
        请提供：
        1. 时间序列预测值（未来{prediction_days}天）
        2. 预测置信区间（95%置信度）
        3. 时间序列特征分析（趋势、季节性、周期性）
        4. 关键转折点预测
        5. 预测可靠性评估
        
        返回格式：
        {{
            "predictions": [
                {{
                    "date": "YYYY-MM-DD",
                    "predicted_value": float,
                    "confidence_interval": {{
                        "lower": float,
                        "upper": float
                    }}
                }}
            ],
            "features": {{
                "trend": string,
                "seasonality": string,
                "cyclical": string
            }},
            "turning_points": [
                {{
                    "date": "YYYY-MM-DD",
                    "type": "上升|下降",
                    "confidence": float
                }}
            ],
            "reliability_score": float  # 0-1之间
        }}
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的时间序列分析AI助手，请基于历史数据提供准确的预测分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 降低随机性以提高预测准确度
        )
        
        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None