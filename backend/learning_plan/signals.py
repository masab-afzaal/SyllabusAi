# signals.py - Django signals for automatic plan adjustments

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LearningSession, LearningPlan

@receiver(post_save, sender=LearningSession)
def update_plan_progress(sender, instance, **kwargs):
    """Automatically update plan progress when session status changes"""
    if instance.status == 'completed':
        plan = instance.learning_plan
        
        # Update completion percentage
        total_sessions = plan.sessions.count()
        completed_sessions = plan.sessions.filter(status='completed').count()
        
        if total_sessions > 0:
            plan.completion_percentage = (completed_sessions / total_sessions) * 100
            plan.save()
        
        # Check if low performance - suggest additional review sessions
        if (instance.completion_score and instance.completion_score < 70) or \
           (instance.confidence_level and instance.confidence_level < 3):
            create_review_session(instance)

def create_review_session(original_session):
    """Create additional review session for topics with low performance"""
    from datetime import timedelta
    
    # Schedule review session 3 days after original
    review_date = original_session.scheduled_date + timedelta(days=3)
    
    LearningSession.objects.create(
        learning_plan=original_session.learning_plan,
        topic=original_session.topic,
        session_type='review',
        scheduled_date=review_date,
        estimated_duration_minutes=original_session.estimated_duration_minutes // 2,  # Shorter review
        difficulty_level=original_session.difficulty_level,
        status='pending'
    )