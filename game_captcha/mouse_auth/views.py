# mouse_auth/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MouseMovementSession, MouseMovementSequence
from .serializers import MouseMovementSessionSerializer
from .utils import extract_features, train_model, verify_user_identity
import json

# from django.contrib.auth.models import User

# mouse_auth/views.py
class CollectTrainingDataView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')  # Get the integer user_id
            movement_sequences = data.get('sequences', [])
            
            if not user_id or not movement_sequences:
                return Response(
                    {'error': 'user_id and sequences are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create session with user_id (not user)
            session = MouseMovementSession.objects.create(
                user_id=user_id,  # Changed from user=user to user_id=user_id
                is_training_data=True
            )
            
            # Save sequences
            for seq in movement_sequences:
                features = extract_features(seq)
                MouseMovementSequence.objects.create(
                    session=session,
                    sequence=seq,
                    features=features
                )
            
            return Response(
                {'status': 'success', 'session_id': session.id},
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class TrainModelView(APIView):
    def post(self, request):
        try:
            test_accuracy = train_model()
            return Response(
                {
                    'status': 'success',
                    'test_accuracy': test_accuracy
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyUserIdentityView(APIView):
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            movement_sequence = data.get('sequence')
            
            if not user_id or not movement_sequence:
                return Response(
                    {'error': 'user_id and sequence are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = verify_user_identity(user_id, movement_sequence)
            
            # Log verification attempt
            session = MouseMovementSession.objects.create(
                user_id=user_id,
                is_training_data=False
            )
            MouseMovementSequence.objects.create(
                session=session,
                sequence=movement_sequence,
                features=extract_features(movement_sequence)
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )