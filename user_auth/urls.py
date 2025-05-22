from django.urls import path
from . import views

urlpatterns = [
    #定义了账户管理的API路由
    # 包含用户信息获取和更新的接口
    path('account/', views.account_page, name='account'),
    path('api/user/info/', views.get_user_info, name='get_user_info'),
    path('api/user/update/', views.update_user_info, name='update_user_info'),
    

    path('api/predict/stock/', views.get_stock_prediction, name='stock_prediction'),
    path('api/predict/market/', views.get_market_prediction, name='market_prediction'),
    path('api/predict/technical/', views.get_technical_indicators, name='technical_indicators'),
    path('api/investment/advice/', views.get_investment_advice, name='investment_advice'),
    path('api/advice/portfolio/', views.analyze_portfolio, name='portfolio_analysis'),
    path('api/advice/stocks/', views.get_stock_recommendations, name='stock_recommendations'),
    path('api/advice/strategy/', views.get_investment_strategy, name='investment_strategy'),
    path('api/chat/message/', views.chat_with_assistant, name='chat_message'),
    path('api/chat/quick-answers/', views.get_quick_answers, name='quick_answers'),
    path('api/risk/portfolio/', views.analyze_portfolio_risk, name='portfolio_risk'),
    path('api/risk/market/', views.get_market_alerts, name='market_alerts'),
    path('api/risk/stock/', views.analyze_stock_risk, name='stock_risk'),
    path('api/query/search/', views.search_market_data, name='market_data_search'),
    path('api/query/historical/', views.get_historical_data, name='historical_data'),
    path('api/query/analyze/', views.analyze_market_data, name='market_data_analysis'),
]