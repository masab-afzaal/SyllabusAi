# planning/models.py
from django.db import models
from django.contrib.auth import get_user_model
from curriculum.models import Syllabus, Topic
import uuid

User = get_user_model()

class LearningPlan(models.Model):
    """Generated learning plan for a syllabus"""
    
    PLAN_TYPE_CHOICES = [
        ('daily', 'Daily Plan'),
        ('weekly', 'Weekly Plan'),
        ('monthly', 'Monthly Plan'),
        ('custom', 'Custom Plan'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_plans')
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='learning_plans')
    
    # Plan Configuration
    title = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='weekly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timeline
    start_date = models.DateField()
    target_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Plan Metrics
    total_estimated_hours = models.FloatField(default=0.0)
    total_topics = models.PositiveIntegerField(default=0)
    average_difficulty = models.FloatField(default=0.0)
    
    # Progress Tracking
    completed_hours = models.FloatField(default=0.0)
    completed_topics = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    
    # Plan Settings
    daily_study_hours = models.FloatField(help_text="Planned daily study hours")
    session_length = models.PositiveIntegerField(help_text="Study session length in minutes")
    break_length = models.PositiveIntegerField(help_text="Break length in minutes")
    
    # Adaptive Features
    difficulty_adjustment = models.FloatField(default=1.0, help_text="Difficulty multiplier based on performance")
    time_adjustment = models.FloatField(default=1.0, help_text="Time multiplier based on actual vs estimated")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.total_topics == 0:
            return 0
        return (self.completed_topics / self.total_topics) * 100

class ScheduleBlock(models.Model):
    """Individual study blocks in the learning plan"""
    
    BLOCK_TYPE_CHOICES = [
        ('study', 'Study Session'),
        ('review', 'Review Session'),
        ('assessment', 'Assessment'),
        ('break', 'Break'),
        ('buffer', 'Buffer Time'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learning_plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE, related_name='schedule_blocks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='schedule_blocks', null=True, blank=True)
    
    # Schedule Information
    title = models.CharField(max_length=255)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, default='study')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Timing
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    actual_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Actual duration in minutes")
    
    # Progress Tracking
    completion_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    difficulty_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    satisfaction_rating = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Notes and Feedback
    notes = models.TextField(blank=True)
    challenges_faced = models.JSONField(default=list)
    achievements = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date', 'start_time']
        unique_together = ['learning_plan', 'scheduled_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date} {self.start_time}"

class StudySession(models.Model):
    """Detailed study session tracking"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    schedule_block = models.OneToOneField(ScheduleBlock, on_delete=models.CASCADE, related_name='study_session')
    
    # Session Details
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    paused_duration = models.PositiveIntegerField(default=0, help_text="Total paused time in minutes")
    
    # Performance Metrics
    focus_score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    understanding_score = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    retention_confidence = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Session Data
    concepts_mastered = models.JSONField(default=list)
    concepts_struggling = models.JSONField(default=list)
    questions_raised = models.JSONField(default=list)
    resources_used = models.JSONField(default=list)
    
    # Feedback
    session_notes = models.TextField(blank=True)
    next_session_goals = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session for {self.schedule_block.title} - {self.user.username}"