from rest_framework import serializers
from .models import MouseMovementSession, MouseMovementSequence

class MouseMovementSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouseMovementSequence
        fields = ['sequence']

class MouseMovementSessionSerializer(serializers.ModelSerializer):
    sequences = MouseMovementSequenceSerializer(many=True)
    
    class Meta:
        model = MouseMovementSession
        fields = ['user', 'timestamp', 'is_training_data', 'sequences']