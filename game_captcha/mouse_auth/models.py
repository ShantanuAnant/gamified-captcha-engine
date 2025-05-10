# mouse_auth/models.py
from django.db import models

class MouseMovementSession(models.Model):
    user_id = models.IntegerField()  # You changed from ForeignKey to IntegerField
    timestamp = models.DateTimeField(auto_now_add=True)
    is_training_data = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'mouse_auth'
        ordering = ['-timestamp']

class MouseMovementSequence(models.Model):
    session = models.ForeignKey(
        MouseMovementSession, 
        on_delete=models.CASCADE, 
        related_name='sequences',
        null=True,  # Make it nullable
        blank=True  # Allow blank in forms
    )
    sequence = models.JSONField()
    features = models.JSONField(null=True, blank=True)
    
    class Meta:
        app_label = 'mouse_auth'
        ordering = ['session__timestamp']