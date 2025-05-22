from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user_auth.views import UserViewSet, login_page, register_page
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
]