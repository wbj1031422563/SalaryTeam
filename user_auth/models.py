from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    
class UserLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    login_ip = models.GenericIPAddressField()
    login_status = models.BooleanField(default=True)
    device_info = models.CharField(max_length=255)
    
class UserOperationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_time = models.DateTimeField(auto_now_add=True)
    operation_type = models.CharField(max_length=50)
    operation_detail = models.TextField()
    ip_address = models.GenericIPAddressField()