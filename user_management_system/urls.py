from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user_auth.views import UserViewSet, alert_page, login_page, register_page, account_page, get_user_info, \
    update_user_info, service_page, advice_page,query_page,predict_page,chat_with_assistant
from django.views.generic import RedirectView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),  # Redirect root to login
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),  # Handle favicon
    path('account/', account_page, name='account'),
    path('service/', service_page, name='service'), 
    path('alert',alert_page,name='alert'),
    path('advice',advice_page,name='advice'),
    path('query',query_page,name='query'),
    path('predict',predict_page,name='predict'),
    path('api/user/info/', get_user_info, name='get_user_info'),
    path('api/user/update/', update_user_info, name='update_user_info'),
    path('service/api/chat/message/', chat_with_assistant, name='chat_message'),
    
]