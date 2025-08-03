# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Extended user model with profile information"""
    
    GRADE_CHOICES = [
        ('elementary', 'Elementary (K-5)'),
        ('middle', 'Middle School (6-8)'),
        ('high', 'High School (9-12)'),
        ('college', 'College/University'),
        ('graduate', 'Graduate School'),
        ('professional', 'Professional Development'),
    ]
    
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual Learner'),
        ('auditory', 'Auditory Learner'),
        ('kinesthetic', 'Kinesthetic Learner'),
        ('reading', 'Reading/Writing Learner'),
        ('mixed', 'Mixed/Multimodal'),
    ]
    
    KNOWLEDGE_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    # Profile Information
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(5), MaxValueValidator(100)])
    grade_level = models.CharField(max_length=20, choices=GRADE_CHOICES, default='college')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, default='mixed')
    knowledge_level = models.CharField(max_length=20, choices=KNOWLEDGE_LEVEL_CHOICES, default='intermediate')
    
    # Study Preferences
    daily_study_hours = models.FloatField(default=2.0, validators=[MinValueValidator(0.5), MaxValueValidator(24.0)])
    preferred_session_length = models.PositiveIntegerField(default=60, help_text="Preferred study session length in minutes")
    break_interval = models.PositiveIntegerField(default=15, help_text="Preferred break interval in minutes")
    
    # Learning Goals
    target_completion_days = models.PositiveIntegerField(null=True, blank=True, help_text="Target days to complete syllabus")
    difficulty_preference = models.CharField(
        max_length=20,
        choices=[('gradual', 'Gradual Increase'), ('mixed', 'Mixed Difficulty'), ('challenging', 'Challenge First')],
        default='gradual'
    )
    
    # Peak Performance Times
    morning_productivity = models.PositiveIntegerField(default=7, validators=[MinValueValidator(1), MaxValueValidator(10)])
    afternoon_productivity = models.PositiveIntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(10)])
    evening_productivity = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.grade_level})"