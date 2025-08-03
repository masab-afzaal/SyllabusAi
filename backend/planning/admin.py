# planning/admin.py
from django.contrib import admin
from .models import LearningPlan, ScheduleBlock, StudySession

class ScheduleBlockInline(admin.TabularInline):
    """Inline admin for ScheduleBlock model"""
    model = ScheduleBlock
    extra = 0
    fields = ('title', 'block_type', 'status', 'scheduled_date', 'start_time', 'estimated_duration')
    readonly_fields = ('id',)

@admin.register(LearningPlan)
class LearningPlanAdmin(admin.ModelAdmin):
    """Admin configuration for LearningPlan model"""
    
    list_display = ('title', 'user', 'syllabus', 'plan_type', 'status', 'start_date', 'completion_percentage')
    list_filter = ('status', 'plan_type', 'start_date')
    search_fields = ('title', 'user__username', 'syllabus__title')
    readonly_fields = ('id', 'completion_percentage', 'created_at', 'updated_at')
    inlines = [ScheduleBlockInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'syllabus', 'title', 'plan_type', 'status')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_end_date', 'actual_end_date')
        }),
        ('Plan Metrics', {
            'fields': ('total_estimated_hours', 'total_topics', 'average_difficulty')
        }),
        ('Progress Tracking', {
            'fields': ('completed_hours', 'completed_topics', 'completion_percentage', 
                      'current_streak', 'longest_streak')
        }),
        ('Settings', {
            'fields': ('daily_study_hours', 'session_length', 'break_length')
        }),
        ('Adaptive Features', {
            'fields': ('difficulty_adjustment', 'time_adjustment'),
            'classes': ('collapse',)
        })
    )

@admin.register(ScheduleBlock)
class ScheduleBlockAdmin(admin.ModelAdmin):
    """Admin configuration for ScheduleBlock model"""
    
    list_display = ('title', 'learning_plan', 'block_type', 'status', 'scheduled_date', 'start_time')
    list_filter = ('block_type', 'status', 'scheduled_date')
    search_fields = ('title', 'learning_plan__title', 'topic__title')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'learning_plan', 'topic', 'title', 'block_type', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'start_time', 'end_time', 'estimated_duration', 'actual_duration')
        }),
        ('Progress', {
            'fields': ('completion_percentage', 'difficulty_rating', 'satisfaction_rating')
        }),
        ('Notes', {
            'fields': ('notes', 'challenges_faced', 'achievements'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('id',)

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    """Admin configuration for StudySession model"""
    
    list_display = ('schedule_block', 'user', 'started_at', 'ended_at', 'focus_score')
    list_filter = ('started_at', 'focus_score', 'understanding_score')
    search_fields = ('schedule_block__title', 'user__username')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'schedule_block')
        }),
        ('Session Timeline', {
            'fields': ('started_at', 'ended_at', 'paused_duration')
        }),
        ('Performance Metrics', {
            'fields': ('focus_score', 'understanding_score', 'retention_confidence')
        }),
        ('Session Data', {
            'fields': ('concepts_mastered', 'concepts_struggling', 'questions_raised', 'resources_used'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('session_notes', 'next_session_goals'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('id',)
