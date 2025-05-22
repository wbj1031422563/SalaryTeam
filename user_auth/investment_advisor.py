from openai import OpenAI
import json
from datetime import datetime

class InvestmentAdvisor:
    def __init__(self):
        # 初始化 Moonshot AI 客户端
        self.client = OpenAI(
            api_key="sk-FSaV63sjv2Xcpl0pxrUcCcf5mLW2vkGRwnMJjSLlgVMahR60",
            base_url="https://api.moonshot.cn/v1",
        )
    
    def analyze_portfolio(self, portfolio, risk_preference):
        """分析投资组合并提供优化建议
        
        参数:
            portfolio (dict): 当前投资组合
            risk_preference (str): 风险偏好（保守、稳健、激进）
            
        返回:
            dict: 分析结果和建议
        """
        prompt = f"""请分析以下投资组合并提供优化建议：

        当前投资组合：
        {json.dumps(portfolio, ensure_ascii=False, indent=2)}
        
        风险偏好：{risk_preference}
        
        请提供：
        1. 当前组合分析
        2. 建议资产配置
        3. 调整建议
        4. 风险评估
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的投资顾问AI助手，专注于投资组合分析和建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None
    
    def get_stock_recommendations(self, criteria):
        """获取股票推荐
        
        参数:
            criteria (dict): 筛选条件（行业、市值、风险等级等）
            
        返回:
            list: 推荐股票列表
        """
        prompt = f"""请根据以下条件推荐股票：

        筛选条件：
        {json.dumps(criteria, ensure_ascii=False, indent=2)}
        
        请提供：
        1. 推荐股票列表（包含代码、名称、行业）
        2. 推荐理由
        3. 风险提示
        4. 目标价位
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的股票分析AI助手，专注于股票筛选和推荐。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None
    
    def get_investment_strategy(self, market_condition, time_horizon):
        """获取投资策略建议
        
        参数:
            market_condition (str): 市场状况
            time_horizon (str): 投资期限
            
        返回:
            dict: 投资策略建议
        """
        prompt = f"""请根据以下条件提供投资策略建议：

        市场状况：{market_condition}
        投资期限：{time_horizon}
        
        请提供：
        1. 市场分析
        2. 策略建议
        3. 行业配置
        4. 风险控制
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的投资策略AI助手，专注于市场分析和策略制定。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None