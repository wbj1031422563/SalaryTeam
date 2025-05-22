from openai import OpenAI
from typing import List, Dict
import json
from datetime import datetime

class RiskMonitor:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-FSaV63sjv2Xcpl0pxrUcCcf5mLW2vkGRwnMJjSLlgVMahR60",
            base_url="https://api.moonshot.cn/v1",
        )
    
    def analyze_portfolio_risk(self, portfolio: Dict) -> Dict:
        """分析投资组合的整体风险"""
        prompt = f"""请分析以下投资组合的风险情况：

        投资组合：
        {json.dumps(portfolio, ensure_ascii=False, indent=2)}

        请提供：
        1. 整体风险评级（低/中/高）
        2. 主要风险点
        3. 风险缓解建议
        4. 需要重点关注的指标

        返回JSON格式：
        {{
            "risk_level": string,
            "risk_score": float,  # 0-100
            "major_risks": [string],
            "mitigation_suggestions": [string],
            "key_indicators": [string]
        }}
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的风险分析AI助手，专注于金融市场风险评估和预警。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None

    def generate_market_alerts(self, market_data: Dict) -> List[Dict]:
        """生成市场风险警报"""
        prompt = f"""基于以下市场数据生成风险警报：

        市场数据：
        {json.dumps(market_data, ensure_ascii=False, indent=2)}

        请识别潜在的风险并生成警报，包括：
        1. 市场波动风险
        2. 行业风险
        3. 宏观经济风险
        4. 政策风险

        每个警报包含：
        - 风险等级（高/中/低）
        - 具体描述
        - 可能的影响
        - 建议措施

        返回JSON数组格式。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的市场风险分析AI助手，负责识别和预警潜在的市场风险。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return []

    def analyze_stock_risk(self, stock_code: str, stock_data: Dict) -> Dict:
        """分析单只股票的风险"""
        prompt = f"""请分析以下股票的风险情况：

        股票代码：{stock_code}
        股票数据：
        {json.dumps(stock_data, ensure_ascii=False, indent=2)}

        请提供：
        1. 技术面风险分析
        2. 基本面风险分析
        3. 市场情绪分析
        4. 具体风险点

        返回JSON格式。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的股票风险分析AI助手，专注于个股风险评估。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None