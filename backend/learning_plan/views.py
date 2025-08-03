# views.py - Module 3 API views

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from .models import LearningPlan, LearningSession, Milestone, StudyPreference
from curriculum.models import Syllabus
from .learning_plan_generator import LearningPlanGenerator
from .serializers import (
    LearningPlanSerializer, LearningSessionSerializer, 
    MilestoneSerializer, StudyPreferenceSerializer
)

class LearningPlanViewSet(viewsets.ModelViewSet):
    serializer_class = LearningPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningPlan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate_plan(self, request):
        """Generate a new learning plan from syllabus"""
        try:
            syllabus_id = request.data.get('syllabus_id')
            syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=request.user)
            
            plan_config = {
                'title': request.data.get('title', f'Study Plan for {syllabus.title}'),
                'schedule_type': request.data.get('schedule_type', 'weekly'),
                'daily_study_hours': float(request.data.get('daily_study_hours', 2.0)),
                'difficulty_progression': request.data.get('difficulty_progression', 'adaptive'),
                'target_completion_date': request.data.get('target_completion_date')
            }
            
            # Validate daily study hours
            if not 0.5 <= plan_config['daily_study_hours'] <= 12:
                return Response(
                    {'error': 'Daily study hours must be between 0.5 and 12'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            generator = LearningPlanGenerator(request.user, syllabus)
            plan = generator.generate_learning_plan(plan_config)
            
            serializer = self.get_serializer(plan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate learning plan: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get comprehensive dashboard data for a learning plan"""
        plan = self.get_object()
        
        # Calculate progress statistics
        total_sessions = plan.sessions.count()
        completed_sessions = plan.sessions.filter(status='completed').count()
        pending_sessions = plan.sessions.filter(status='pending').count()
        
        # Get next upcoming sessions
        upcoming_sessions = plan.sessions.filter(
            status='pending',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:5]
        
        # Get recent completed sessions
        recent_sessions = plan.sessions.filter(
            status='completed'
        ).order_by('-updated_at')[:5]
        
        # Calculate study streak
        study_streak = self._calculate_study_streak(plan)
        
        # Get milestone progress
        milestones = plan.milestones.all().order_by('target_date')
        
        # Calculate average session completion time
        avg_completion_time = plan.sessions.filter(
            status='completed',
            actual_duration_minutes__isnull=False
        ).aggregate(Avg('actual_duration_minutes'))['actual_duration_minutes__avg'] or 0
        
        dashboard_data = {
            'plan': LearningPlanSerializer(plan).data,
            'progress': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'pending_sessions': pending_sessions,
                'completion_percentage': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'study_streak_days': study_streak,
                'avg_session_duration': round(avg_completion_time, 1)
            },
            'upcoming_sessions': LearningSessionSerializer(upcoming_sessions, many=True).data,
            'recent_sessions': LearningSessionSerializer(recent_sessions, many=True).data,
            'milestones': MilestoneSerializer(milestones, many=True).data
        }
        
        return Response(dashboard_data)
    
    def _calculate_study_streak(self, plan):
        """Calculate current study streak in days"""
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            sessions_on_date = plan.sessions.filter(
                status='completed',
                updated_at__date=current_date
            ).exists()
            
            if sessions_on_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
                
        return streak
    
    @action(detail=True, methods=['post'])
    def rebalance(self, request, pk=None):
        """Rebalance the learning plan based on current progress"""
        plan = self.get_object()
        
        try:
            # Get rebalancing parameters
            new_daily_hours = request.data.get('daily_study_hours', plan.daily_study_hours)
            new_target_date = request.data.get('target_completion_date')
            
            # Calculate remaining work
            pending_sessions = plan.sessions.filter(status='pending')
            total_remaining_time = sum(s.estimated_duration_minutes for s in pending_sessions)
            
            # Reschedule pending sessions
            current_date = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
            daily_minutes = int(new_daily_hours * 60)
            
            for session in pending_sessions:
                # Find next available slot
                new_date = self._find_next_slot(current_date, daily_minutes, session.estimated_duration_minutes)
                session.scheduled_date = new_date
                session.save()
                current_date = new_date
            
            # Update plan
            plan.daily_study_hours = new_daily_hours
            plan.save()
            
            return Response({'message': 'Learning plan rebalanced successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to rebalance plan: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _find_next_slot(self, start_date, daily_minutes, session_duration):
        """Simple slot finding for rebalancing"""
        current_date = start_date
        while True:
            if current_date.weekday() < 5:  # Weekdays only
                return current_date
            current_date += timedelta(days=1)

class LearningSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LearningSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningSession.objects.filter(learning_plan__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Start a learning session"""
        session = self.get_object()
        
        if session.status != 'pending':
            return Response(
                {'error': 'Session is not in pending status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check prerequisites
        incomplete_prereqs = session.prerequisites.exclude(status='completed')
        if incomplete_prereqs.exists():
            return Response(
                {'error': 'Prerequisites not completed', 'incomplete_prerequisites': list(incomplete_prereqs.values_list('id', flat=True))},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'in_progress'
        session.save()
        
        return Response(LearningSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def complete_session(self, request, pk=None):
        """Complete a learning session with feedback"""
        session = self.get_object()
        
        if session.status != 'in_progress':
            return Response(
                {'error': 'Session is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update session with completion data
        session.status = 'completed'
        session.actual_duration_minutes = request.data.get('actual_duration_minutes', session.estimated_duration_minutes)
        session.completion_score = request.data.get('completion_score', 100)
        session.confidence_level = request.data.get('confidence_level', 3)
        session.notes = request.data.get('notes', '')
        session.save()
        
        # Update learning plan progress
        self._update_plan_progress(session.learning_plan)
        
        return Response(LearningSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule a learning session"""
        session = self.get_object()
        
        if session.status not in ['pending', 'in_progress']:
            return Response(
                {'error': 'Cannot reschedule completed or skipped sessions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_date = request.data.get('scheduled_date')
        if not new_date:
            return Response(
                {'error': 'New scheduled date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_date = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            session.scheduled_date = new_date
            session.status = 'rescheduled' if session.status == 'in_progress' else 'pending'
            session.save()
            
            return Response(LearningSessionSerializer(session).data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _update_plan_progress(self, plan):
        """Update learning plan completion percentage"""
        total_sessions = plan.sessions.count()
        completed_sessions = plan.sessions.filter(status='completed').count()
        
        if total_sessions > 0:
            plan.completion_percentage = (completed_sessions / total_sessions) * 100
            plan.save()

class MilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Milestone.objects.filter(learning_plan__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark milestone as completed"""
        milestone = self.get_object()
        milestone.is_completed = True
        milestone.completion_percentage = 100.0
        milestone.save()
        
        return Response(MilestoneSerializer(milestone).data)

class StudyPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = StudyPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StudyPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's study preferences"""
        try:
            preferences = StudyPreference.objects.get(user=request.user)
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        except StudyPreference.DoesNotExist:
            return Response(
                {'message': 'No preferences found. Create preferences first.'},
                status=status.HTTP_404_NOT_FOUND
            )

