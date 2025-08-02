from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from curriculum.models import Syllabus, Topic
from planning.models import LearningPlan, ScheduleBlock, StudySession

@api_view(['GET'])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Smart Syllabus Summarizer API is running'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Get user statistics dashboard data"""
    user = request.user
    
    # Syllabus stats
    syllabi_stats = Syllabus.objects.filter(user=user).aggregate(
        total_syllabi=Count('id'),
        completed_syllabi=Count('id', filter=models.Q(status='completed')),
        total_topics=Count('topics'),
        avg_difficulty=Avg('topics__difficulty_level')
    )
    
    # Learning plan stats
    plan_stats = LearningPlan.objects.filter(user=user).aggregate(
        total_plans=Count('id'),
        active_plans=Count('id', filter=models.Q(status='active')),
        completed_plans=Count('id', filter=models.Q(status='completed')),
        total_study_hours=Sum('completed_hours'),
        current_streak=Avg('current_streak')
    )
    
    # Recent activity
    recent_sessions = StudySession.objects.filter(user=user).order_by('-created_at')[:5]
    recent_activity = []
    
    for session in recent_sessions:
        recent_activity.append({
            'type': 'study_session',
            'title': session.schedule_block.title,
            'date': session.created_at,
            'duration': session.actual_duration if session.ended_at else None
        })
    
    return Response({
        'syllabi_stats': syllabi_stats,
        'plan_stats': plan_stats,
        'recent_activity': recent_activity
    })
