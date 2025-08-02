# planning/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import LearningPlan, ScheduleBlock, StudySession
from .serializers import (
    LearningPlanSerializer, LearningPlanCreateSerializer,
    ScheduleBlockSerializer, StudySessionSerializer
)
from curriculum.models import Syllabus
from .tasks import generate_learning_plan  # We'll create this in Module 3

class LearningPlanListView(generics.ListAPIView):
    """List user's learning plans"""
    serializer_class = LearningPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPlan.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_learning_plan(request, syllabus_id):
    """Create a new learning plan for a syllabus"""
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=request.user)
    
    if syllabus.status != 'analyzed':
        return Response({
            'error': 'Syllabus must be analyzed before creating a learning plan'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = LearningPlanCreateSerializer(data=request.data, context={
        'request': request,
        'syllabus': syllabus
    })
    
    if serializer.is_valid():
        learning_plan = serializer.save()
        # Trigger async plan generation
        generate_learning_plan.delay(learning_plan.id)
        
        return Response({
            'learning_plan': LearningPlanSerializer(learning_plan).data,
            'message': 'Learning plan creation started'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LearningPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a learning plan"""
    serializer_class = LearningPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPlan.objects.filter(user=self.request.user)

class ScheduleBlockListView(generics.ListAPIView):
    """List schedule blocks for a learning plan"""
    serializer_class = ScheduleBlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        plan_id = self.kwargs['plan_id']
        plan = get_object_or_404(LearningPlan, id=plan_id, user=self.request.user)
        return ScheduleBlock.objects.filter(learning_plan=plan)

class ScheduleBlockDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a schedule block"""
    serializer_class = ScheduleBlockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ScheduleBlock.objects.filter(learning_plan__user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_study_session(request, block_id):
    """Start a study session for a schedule block"""
    block = get_object_or_404(ScheduleBlock, 
                             id=block_id, 
                             learning_plan__user=request.user)
    
    # Check if session already exists
    if hasattr(block, 'study_session'):
        return Response({
            'error': 'Study session already exists for this block'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create study session
    session = StudySession.objects.create(
        user=request.user,
        schedule_block=block,
        started_at=timezone.now()
    )
    
    # Update block status
    block.status = 'in_progress'
    block.save()
    
    return Response({
        'session': StudySessionSerializer(session).data,
        'message': 'Study session started'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_study_session(request, session_id):
    """End a study session"""
    session = get_object_or_404(StudySession, 
                               id=session_id, 
                               user=request.user)
    
    if session.ended_at:
        return Response({
            'error': 'Session already ended'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update session
    session.ended_at = timezone.now()
    
    # Update with provided data
    serializer = StudySessionSerializer(session, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Update schedule block
        block = session.schedule_block
        block.status = 'completed'
        block.actual_duration = (session.ended_at - session.started_at).total_seconds() / 60
        block.save()
        
        return Response({
            'session': serializer.data,
            'message': 'Study session completed'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)