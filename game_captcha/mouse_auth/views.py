from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import MouseMovementSession, MouseMovementSequence
from .serializers import MouseMovementSessionSerializer
from .utils import extract_features, train_model, verify_user_identity
import json

User = get_user_model()

class CollectTrainingDataView(APIView):
    def post(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            data = request.data
            movement_sequences = data.get('sequences', [])
            
            if not movement_sequences:
                return Response(
                    {'error': 'No movement sequences provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create session
            session = MouseMovementSession.objects.create(
                user=user,
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
            if not request.user.is_staff:
                return Response(
                    {'error': 'Staff permission required'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
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
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            movement_sequence = request.data.get('sequence')
            if not movement_sequence:
                return Response(
                    {'error': 'Movement sequence required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = verify_user_identity(user.id, movement_sequence)
            
            # Log verification attempt (not for training)
            session = MouseMovementSession.objects.create(
                user=user,
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