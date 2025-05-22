
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserLoginLog, UserOperationLog
from .serializers import UserSerializer
from django.shortcuts import render, redirect
import jwt
from datetime import datetime
import hashlib
from django.http import JsonResponse
from .prediction_service import PredictionService
from .investment_advisor import InvestmentAdvisor
from .service_assistant import ServiceAssistant
from .risk_monitor import RiskMonitor
from .data_query_service import DataQueryService
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request):
        try:
            # 获取用户提交的数据
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            phone = request.data.get('phone')

            # 验证用户名是否已存在
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': '用户名已存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': '邮箱已被注册'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 使用SHA-256加密密码
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # 创建新用户
            user = User.objects.create(
                username=username,
                email=email,
                password=hashed_password,
                phone=phone
            )

            # 记录操作日志
            UserOperationLog.objects.create(
                user=user,
                operation_type='REGISTER',
                operation_detail=f'New user registration: {username}',
                ip_address=self.get_client_ip(request)
            )

            # 检查是否是API请求
            if request.accepted_renderer.format == 'json':
                # API请求返回JSON响应
                return Response({
                    'message': '注册成功',
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'redirect_url': '/login/'
                }, status=status.HTTP_201_CREATED)
            else:
                # 网页请求直接重定向到登录页
                return redirect('login')

        except Exception as e:
            # 记录错误并返回错误响应
            return Response({
                'error': f'注册失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')  # 这里接收的已经是SHA-256加密后的密码
            
            try:
                # 直接查询用户和密码
                user = User.objects.get(username=username, password=password)
                
                if user.is_locked:
                    return Response({'error': '账户已被锁定'}, status=status.HTTP_403_FORBIDDEN)
                
                # 重置失败登录次数
                user.failed_login_attempts = 0
                user.save()
                
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                
                # 记录登录日志
                UserLoginLog.objects.create(
                    user=user,
                    login_ip=self.get_client_ip(request),
                    login_status=True,
                    device_info=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # 检查是否是API请求
                if request.accepted_renderer.format == 'json':
                    # API请求返回JSON响应
                    return Response({
                        'token': str(refresh.access_token),
                        'refresh': str(refresh),
                        'redirect_url': '/account/'
                    })
                else:
                    # 网页请求直接重定向到account页面
                    return redirect('account')
                
            except User.DoesNotExist:
                # 用户不存在或密码错误
                try:
                    user = User.objects.get(username=username)
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 5:
                        user.is_locked = True
                    user.save()
                    
                    UserLoginLog.objects.create(
                        user=user,
                        login_ip=self.get_client_ip(request),
                        login_status=False,
                        device_info=request.META.get('HTTP_USER_AGENT', '')
                    )
                except User.DoesNotExist:
                    pass
                
                return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error': f'登录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def login_page(request):
    return render(request, 'user_auth/login.html')

def register_page(request):
    return render(request, 'user_auth/register.html')

def account_page(request):
    return render(request, 'user_auth/account.html')

def service_page(request):
    return render(request, 'user_auth/service.html')

def alert_page(request):
    return render(request, 'user_auth/alert.html')

def advice_page(request):
    return render(request, 'user_auth/advice.html')

def query_page(request):
    return render(request, 'user_auth/query.html')

def predict_page(request):
    return render(request,'user_auth/predict.html')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    login_logs = UserLoginLog.objects.filter(user=user).order_by('-login_time')[:5]
    operation_logs = UserOperationLog.objects.filter(user=user).order_by('-operation_time')[:5]
    
    return JsonResponse({
        'user': {
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'last_login': user.last_login,
            'failed_login_attempts': user.failed_login_attempts,
            'is_locked': user.is_locked
        },
        'login_logs': [{
            'login_time': log.login_time.strftime('%Y-%m-%d %H:%M:%S'),
            'login_ip': log.login_ip,
            'login_status': log.login_status,
            'device_info': log.device_info
        } for log in login_logs],
        'operation_logs': [{
            'operation_time': log.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'operation_type': log.operation_type,
            'operation_detail': log.operation_detail,
            'ip_address': log.ip_address
        } for log in operation_logs]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    data = request.data
    
    try:
        if 'email' in data:
            # 验证新邮箱是否已被使用
            if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
                return JsonResponse({'error': '该邮箱已被使用'}, status=400)
            user.email = data['email']
            
        if 'phone' in data:
            user.phone = data['phone']
            
        if 'password' in data:
            # 验证旧密码
            old_password = hashlib.sha256(data['old_password'].encode()).hexdigest()
            if user.password != old_password:
                return JsonResponse({'error': '旧密码错误'}, status=400)
            # 设置新密码
            new_password = hashlib.sha256(data['password'].encode()).hexdigest()
            user.password = new_password
        
        user.save()
        
        # 记录操作日志
        UserOperationLog.objects.create(
            user=user,
            operation_type='UPDATE_PROFILE',
            operation_detail='用户信息更新',
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({'message': '更新成功'})
        
    except Exception as e:
        return JsonResponse({'error': f'更新失败: {str(e)}'}, status=500)

def stock_prediction(request):
    if request.method == 'POST':
        stock_code = request.POST.get('stock_code')
        time_frame = request.POST.get('time_frame')
        prediction_type = request.POST.get('prediction_type')
        
        prediction_service = PredictionService()
        prediction_result = prediction_service.get_stock_prediction(
            stock_code, time_frame, prediction_type
        )
        
        if prediction_result:
            return JsonResponse({
                'status': 'success',
                'data': prediction_result
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '预测分析生成失败'
            }, status=400)


def get_investment_advice(request):
    if request.method == 'POST':
        # 获取用户的投资组合数据
        current_portfolio = request.POST.get('current_portfolio')
        user_profile = request.POST.get('user_profile')
        
        try:
            current_portfolio = json.loads(current_portfolio)
            user_profile = json.loads(user_profile)
        except:
            return JsonResponse({
                'status': 'error',
                'message': '数据格式错误'
            }, status=400)
        
        advisor = InvestmentAdvisor()
        advice = advisor.get_portfolio_advice(user_profile, current_portfolio)
        
        if advice:
            return JsonResponse({
                'status': 'success',
                'data': advice
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '生成建议失败'
            }, status=400)

def get_stock_recommendations(request):
    sector = request.GET.get('sector')
    risk_level = request.GET.get('risk_level')
    
    advisor = InvestmentAdvisor()
    recommendations = advisor.get_stock_recommendations(sector, risk_level)
    
    return JsonResponse({
        'status': 'success',
        'data': recommendations
    })


@csrf_exempt
def chat_with_assistant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            user_context = data.get('user_context', {})
            
            if not message:
                return JsonResponse({
                    'status': 'error',
                    'message': '消息不能为空'
                }, status=400)
            
            assistant = ServiceAssistant()
            response = assistant.get_response(message, user_context)
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'message': response,
                    'timestamp': datetime.now().isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def get_quick_answers(request):
    assistant = ServiceAssistant()
    answers = assistant.get_quick_answers()
    return JsonResponse({
        'status': 'success',
        'data': answers
    })


@csrf_exempt
def analyze_portfolio(request):
    """分析投资组合接口"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            portfolio = data.get('portfolio')
            risk_preference = data.get('risk_preference')
            
            if not all([portfolio, risk_preference]):
                return JsonResponse({
                    'status': 'error',
                    'message': '缺少必要参数'
                }, status=400)
            
            advisor = InvestmentAdvisor()
            analysis = advisor.analyze_portfolio(portfolio, risk_preference)
            
            if analysis:
                return JsonResponse({
                    'status': 'success',
                    'data': analysis
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '投资组合分析失败'
                }, status=500)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def get_stock_recommendations(request):
    """获取股票推荐接口"""
    try:
        criteria = {
            'industry': request.GET.get('industry'),
            'market_cap': request.GET.get('market_cap'),
            'risk_level': request.GET.get('risk_level')
        }
        
        advisor = InvestmentAdvisor()
        recommendations = advisor.get_stock_recommendations(criteria)
        
        if recommendations:
            return JsonResponse({
                'status': 'success',
                'data': recommendations
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '获取股票推荐失败'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_investment_strategy(request):
    """获取投资策略接口"""
    try:
        market_condition = request.GET.get('market_condition')
        time_horizon = request.GET.get('time_horizon')
        
        if not all([market_condition, time_horizon]):
            return JsonResponse({
                'status': 'error',
                'message': '缺少必要参数'
            }, status=400)
        
        advisor = InvestmentAdvisor()
        strategy = advisor.get_investment_strategy(market_condition, time_horizon)
        
        if strategy:
            return JsonResponse({
                'status': 'success',
                'data': strategy
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '获取投资策略失败'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_market_alerts(request):
    try:
        market_data = {  # 这里应该从实际数据源获取市场数据
            'market_indices': {},
            'sector_performance': {},
            'economic_indicators': {}
        }
        
        monitor = RiskMonitor()
        alerts = monitor.generate_market_alerts(market_data)
        
        return JsonResponse({
            'status': 'success',
            'data': alerts
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def analyze_stock_risk(request):
    stock_code = request.GET.get('stock_code')
    if not stock_code:
        return JsonResponse({
            'status': 'error',
            'message': '股票代码不能为空'
        }, status=400)
    
    try:
        stock_data = {}  # 这里应该从实际数据源获取股票数据
        
        monitor = RiskMonitor()
        risk_analysis = monitor.analyze_stock_risk(stock_code, stock_data)
        
        return JsonResponse({
            'status': 'success',
            'data': risk_analysis
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def get_stock_prediction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stock_code = data.get('stock_code')
            time_frame = data.get('time_frame')
            prediction_type = data.get('prediction_type')
            
            if not all([stock_code, time_frame, prediction_type]):
                return JsonResponse({
                    'status': 'error',
                    'message': '缺少必要参数'
                }, status=400)
            
            service = PredictionService()
            prediction = service.get_stock_prediction(stock_code, time_frame, prediction_type)
            
            if prediction:
                return JsonResponse({
                    'status': 'success',
                    'data': prediction
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '预测生成失败'
                }, status=500)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def get_market_prediction(request):
    try:
        service = PredictionService()
        prediction = service.get_market_prediction()
        
        if prediction:
            return JsonResponse({
                'status': 'success',
                'data': prediction
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '市场预测生成失败'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_technical_indicators(request):
    stock_code = request.GET.get('stock_code')
    if not stock_code:
        return JsonResponse({
            'status': 'error',
            'message': '股票代码不能为空'
        }, status=400)
    
    try:
        service = PredictionService()
        indicators = service.get_technical_indicators(stock_code)
        
        if indicators:
            return JsonResponse({
                'status': 'success',
                'data': indicators
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '技术指标分析失败'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def search_market_data(request):
    """搜索市场数据接口"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            data_type = data.get('data_type', 'stock')
            
            if not query:
                return JsonResponse({
                    'status': 'error',
                    'message': '搜索关键词不能为空'
                }, status=400)
            
            service = DataQueryService()
            results = service.search_market_data(query, data_type)
            
            if results:
                return JsonResponse({
                    'status': 'success',
                    'data': results
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '数据搜索失败'
                }, status=500)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def get_historical_data(request):
    """获取历史数据接口"""
    try:
        symbol = request.GET.get('symbol')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        interval = request.GET.get('interval', '1d')
        
        if not all([symbol, start_date, end_date]):
            return JsonResponse({
                'status': 'error',
                'message': '缺少必要参数'
            }, status=400)
        
        service = DataQueryService()
        data = service.get_historical_data(symbol, start_date, end_date, interval)
        
        if data:
            return JsonResponse({
                'status': 'success',
                'data': data
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '获取历史数据失败'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
def analyze_market_data(request):
    """分析市场数据接口"""
    try:
        symbol = request.GET.get('symbol')
        analysis_type = request.GET.get('analysis_type')
        
        if not all([symbol, analysis_type]):
            return JsonResponse({
                'status': 'error',
                'message': '缺少必要参数'
            }, status=400)
        
        service = DataQueryService()
        analysis = service.analyze_market_data(symbol, analysis_type)
        
        if analysis is not None:  # 更明确的判断
            return JsonResponse({
                'status': 'success',
                'data': analysis
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '数据分析失败或无结果'
            }, status=500)

    except Exception as e:
        logger.error(f"处理市场数据分析时发生错误: {e}")
        return JsonResponse({
            'status': 'error',
            'message': '服务器内部错误'
        }, status=500)
# def analyze_market_data(request):
#     """分析市场数据接口"""
#     try:
#         symbol = request.GET.get('symbol')
#         analysis_type = request.GET.get('analysis_type')
        
#         if not all([symbol, analysis_type]):
#             return JsonResponse({
#                 'status': 'error',
#                 'message': '缺少必要参数'
#             }, status=400)
        
#         service = DataQueryService()
#         analysis = service.analyze_market_data(symbol, analysis_type)
        
#         if analysis:
#             return JsonResponse({
#                 'status': 'success',
#                 'data': analysis
#             })
#         else:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': '数据分析失败'
#             }, status=500)
