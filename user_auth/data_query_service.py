from openai import OpenAI
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class DataQueryService:
    def __init__(self):
        # 初始化 Moonshot AI 客户端
        self.client = OpenAI(
            api_key="sk-FSaV63sjv2Xcpl0pxrUcCcf5mLW2vkGRwnMJjSLlgVMahR60",
            base_url="https://api.moonshot.cn/v1",
        )
    
    def search_market_data(self, query, data_type='stock'):
        """搜索市场数据
        
        参数:
            query (str): 搜索关键词（股票代码或名称）
            data_type (str): 数据类型（股票、基金、债券等）
            
        返回:
            dict: 搜索结果
        """
        prompt = f"""请搜索以下金融数据：
        关键词：{query}
        数据类型：{data_type}
        
        请提供：
        1. 基本信息（代码、名称、类型、市场）
        2. 最新行情数据
        3. 相关推荐
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的金融数据分析助手，专注于市场数据查询和分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None
    
    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        """获取历史数据
        
        参数:
            symbol (str): 股票代码
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
            interval (str): 数据间隔（1d=日线，1w=周线，1m=月线）
            
        返回:
            dict: 历史数据
        """
        prompt = f"""请提供以下历史数据：
        股票代码：{symbol}
        时间范围：{start_date} 至 {end_date}
        数据间隔：{interval}
        
        请提供：
        1. 日期
        2. 开盘价、最高价、最低价、收盘价
        3. 成交量
        4. 涨跌幅
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的金融数据分析助手，专注于历史数据查询和分析。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None
    
    def analyze_market_data(self, symbol, analysis_type):
        """分析市场数据
        
        参数:
            symbol (str): 股票代码
            analysis_type (str): 分析类型（技术分析、基本面分析等）
            
        返回:
            dict: 分析结果
        """
        prompt = f"""请对以下数据进行分析：
        股票代码：{symbol}
        分析类型：{analysis_type}
        
        请提供：
        1. 核心指标分析
        2. 市场表现评估
        3. 行业对比分析
        4. 投资建议
        
        返回JSON格式数据。
        """

        completion = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个专业的金融数据分析助手，专注于市场数据分析和投资建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        try:
            return json.loads(completion.choices[0].message.content)
        except:
            return None