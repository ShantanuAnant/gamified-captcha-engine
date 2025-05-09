# mouse_auth/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MouseMovementSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_training_data = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'mouse_auth'  # Explicitly set the app label
        ordering = ['-timestamp']

class MouseMovementSequence(models.Model):
    session = models.ForeignKey(MouseMovementSession, on_delete=models.CASCADE, related_name='sequences')
    sequence = models.JSONField()
    features = models.JSONField(null=True, blank=True)
    
    class Meta:
        app_label = 'mouse_auth'  # Explicitly set the app label
        ordering = ['session__timestamp']