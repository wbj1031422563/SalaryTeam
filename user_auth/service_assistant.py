from openai import OpenAI
from typing import List, Dict
import json

class ServiceAssistant:
    def __init__(self):
        self.client = OpenAI(
            #api_key="sk-FSaV63sjv2Xcpl0pxrUcCcf5mLW2vkGRwnMJjSLlgVMahR60",
            api_key="sk-dc4287a8d0764fc5b32b62eb611543b3",
            #base_url="https://api.moonshot.cn/v1",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.conversation_history = []
        self.system_prompt = """
你是一个专业的金融服务助手，专门解答用户关于金融市场、投资理财、风险管理等方面的问题。
你需要：
1. 提供准确、专业的金融知识
2. 解释复杂的金融概念
3. 提供风险提示
4. 保持对话的连贯性
5. 在必要时建议用户咨询人工客服

你不能：
1. 提供具体的投资建议
2. 承诺投资回报
3. 泄露用户隐私信息
4. 处理账户资金操作
"""

    def get_response(self, user_message: str, user_context: Dict = None) -> str:
        # 构建消息历史
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 添加用户上下文（如果有）
        if user_context:
            context_prompt = f"用户信息：\n- 风险偏好：{user_context.get('risk_preference', '未知')}\n- 投资经验：{user_context.get('investment_experience', '未知')}"
            messages.append({"role": "system", "content": context_prompt})
        
        # 添加历史对话
        messages.extend(self.conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            completion = self.client.chat.completions.create(
                #model="moonshot-v1-8k",
                model="qwen-plus",
                messages=messages,
                temperature=0.7,
            )
            
            response = completion.choices[0].message.content
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # 保持对话历史在合理范围内
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
        except Exception as e:
            return f"抱歉，我现在无法回答您的问题。请稍后再试或联系人工客服。错误：{str(e)}"
    
    def get_quick_answers(self) -> List[Dict]:
        """获取常见问题的快速回答"""
        return [
            {
                "question": "如何开始投资？",
                "answer": "建议您先了解基本的投资知识，评估自己的风险承受能力，然后从低风险的理财产品开始尝试。"
            },
            {
                "question": "如何查看我的账户余额？",
                "answer": "您可以在'账号管理'页面查看您的账户详细信息，包括余额、持仓和交易记录。"
            },
            {
                "question": "忘记密码怎么办？",
                "answer": "您可以点击登录页面的'忘记密码'链接，通过验证手机号或邮箱来重置密码。"
            },
            {
                "question": "如何评估投资风险？",
                "answer": "我们提供专业的风险评估工具，您可以在'风险警报'页面进行风险评估测试。"
            }
        ]