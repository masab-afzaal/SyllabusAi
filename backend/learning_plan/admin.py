# admin.py - Django admin interface for Module 3

from django.contrib import admin
from .models import LearningPlan, LearningSession, Milestone, StudyPreference, TopicExtension

@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'syllabus', 'schedule_type', 'completion_percentage', 'is_active', 'created_at')
    list_filter = ('schedule_type', 'difficulty_progression', 'is_active', 'created_at')
    search_fields = ('title', 'user__username', 'syllabus__title')
    readonly_fields = ('completion_percentage', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'syllabus', 'title', 'is_active')
        }),
        ('Schedule Configuration', {
            'fields': ('schedule_type', 'difficulty_progression', 'daily_study_hours', 'total_duration_days')
        }),
        ('Progress', {
            'fields': ('completion_percentage', 'learning_style_weights', 'buffer_time_percentage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'learning_plan', 'session_type', 'scheduled_date', 'status', 'difficulty_level')
    list_filter = ('session_type', 'status', 'difficulty_level', 'scheduled_date')
    search_fields = ('topic__title', 'learning_plan__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('learning_plan', 'topic', 'session_type', 'scheduled_date')
        }),
        ('Duration & Difficulty', {
            'fields': ('estimated_duration_minutes', 'actual_duration_minutes', 'difficulty_level')
        }),
        ('Progress & Feedback', {
            'fields': ('status', 'completion_score', 'confidence_level', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_plan', 'milestone_type', 'target_date', 'is_completed')
    list_filter = ('milestone_type', 'is_completed', 'target_date')
    search_fields = ('title', 'learning_plan__title')
    filter_horizontal = ('topics',)

@admin.register(StudyPreference)
class StudyPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_learning_style', 'difficulty_preference', 'preferred_study_time')
    list_filter = ('primary_learning_style', 'difficulty_preference', 'preferred_study_time')
    search_fields = ('user__username',)

@admin.register(TopicExtension)
class TopicExtensionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'cognitive_level', 'visual_content_ratio', 'practical_application_ratio')
    list_filter = ('cognitive_level',)
    search_fields = ('topic__title',)
        