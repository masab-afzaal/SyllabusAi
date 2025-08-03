# models.py 

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class LearningPlan(models.Model):
    SCHEDULE_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    DIFFICULTY_PROGRESSION = [
        ('linear', 'Linear Progression'),
        ('adaptive', 'Adaptive Progression'),
        ('spiral', 'Spiral Learning'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    syllabus = models.ForeignKey('curriculum.Syllabus', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='weekly')
    difficulty_progression = models.CharField(max_length=20, choices=DIFFICULTY_PROGRESSION, default='adaptive')
    total_duration_days = models.PositiveIntegerField()
    daily_study_hours = models.FloatField(validators=[MinValueValidator(0.5), MaxValueValidator(12)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    completion_percentage = models.FloatField(default=0.0)
    
    # Personalization fields
    learning_style_weights = models.JSONField(default=dict)  # visual, auditory, kinesthetic weights
    buffer_time_percentage = models.FloatField(default=20.0)  # Extra time for revision
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class LearningSession(models.Model):
    SESSION_TYPES = [
        ('study', 'Study Session'),
        ('review', 'Review Session'),
        ('practice', 'Practice Session'),
        ('assessment', 'Assessment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    learning_plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE, related_name='sessions')
    topic = models.ForeignKey('curriculum.Topic', on_delete=models.CASCADE)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='study')
    scheduled_date = models.DateTimeField()
    estimated_duration_minutes = models.PositiveIntegerField()
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    difficulty_level = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Progress tracking
    completion_score = models.FloatField(null=True, blank=True)  # 0-100
    confidence_level = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField(blank=True)
    
    # Prerequisites and dependencies
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.topic.title} - {self.scheduled_date.strftime('%Y-%m-%d')}"

class Milestone(models.Model):
    MILESTONE_TYPES = [
        ('weekly', 'Weekly Checkpoint'),
        ('monthly', 'Monthly Review'),
        ('unit', 'Unit Completion'),
        ('exam', 'Exam Preparation'),
        ('project', 'Project Deadline'),
    ]
    
    learning_plan = models.ForeignKey(LearningPlan, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPES)
    target_date = models.DateTimeField()
    topics = models.ManyToManyField('curriculum.Topic', related_name='milestones')
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['target_date']
    
    def __str__(self):
        return f"{self.title} - {self.target_date.strftime('%Y-%m-%d')}"

class StudyPreference(models.Model):
    LEARNING_STYLES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
        ('reading', 'Reading/Writing'),
    ]
    
    DIFFICULTY_PREFERENCES = [
        ('easy_first', 'Easy Topics First'),
        ('hard_first', 'Challenging Topics First'),
        ('mixed', 'Mixed Difficulty'),
        ('adaptive', 'Adaptive Based on Performance'),
    ]
    
    TIME_PREFERENCES = [
        ('morning', 'Morning (6-12 AM)'),
        ('afternoon', 'Afternoon (12-6 PM)'),
        ('evening', 'Evening (6-10 PM)'),
        ('night', 'Night (10 PM-2 AM)'),
        ('flexible', 'Flexible'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    primary_learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='visual')
    secondary_learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, blank=True)
    difficulty_preference = models.CharField(max_length=20, choices=DIFFICULTY_PREFERENCES, default='adaptive')
    preferred_study_time = models.CharField(max_length=20, choices=TIME_PREFERENCES, default='flexible')
    
    # Study habits
    max_session_duration = models.PositiveIntegerField(default=90)  # minutes
    break_frequency = models.PositiveIntegerField(default=25)  # Pomodoro: 25 min sessions
    break_duration = models.PositiveIntegerField(default=5)  # 5 min breaks
    long_break_duration = models.PositiveIntegerField(default=30)  # Long break after 4 sessions
    
    # Revision preferences
    spaced_repetition_enabled = models.BooleanField(default=True)
    revision_frequency_days = models.PositiveIntegerField(default=7)  # Review every 7 days
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Study Preferences"

# Update existing Topic model with additional fields
class TopicExtension(models.Model):
    """Extension to existing Topic model for learning plan features"""
    topic = models.OneToOneField('curriculum.Topic', on_delete=models.CASCADE, related_name='learning_extension')
    
    # Learning metadata
    cognitive_level = models.CharField(max_length=20, choices=[
        ('remember', 'Remember'),
        ('understand', 'Understand'),
        ('apply', 'Apply'),
        ('analyze', 'Analyze'),
        ('evaluate', 'Evaluate'),
        ('create', 'Create'),
    ], default='understand')
    
    learning_objectives = models.JSONField(default=list)
    recommended_resources = models.JSONField(default=list)
    practice_exercises = models.JSONField(default=list)
    
    # Personalization factors
    visual_content_ratio = models.FloatField(default=0.3)
    practical_application_ratio = models.FloatField(default=0.2)
    theoretical_depth = models.FloatField(default=0.5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Extension for {self.topic.title}"