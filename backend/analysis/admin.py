# analysis/admin.py
from django.contrib import admin
from .models import AnalysisJob, TopicAnalysis

@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    """Admin configuration for AnalysisJob model"""
    
    list_display = ('syllabus', 'status', 'analysis_depth', 'total_topics_extracted', 
                   'average_confidence', 'processing_time_seconds', 'created_at')
    list_filter = ('status', 'analysis_depth', 'use_groq', 'use_huggingface', 'created_at')
    search_fields = ('syllabus__title', 'syllabus__user__username')
    readonly_fields = ('id', 'processing_time_seconds', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'syllabus', 'status', 'analysis_depth')
        }),
        ('Configuration', {
            'fields': ('use_groq', 'use_huggingface')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'processing_time_seconds')
        }),
        ('Results', {
            'fields': ('total_topics_extracted', 'average_confidence', 'error_message')
        }),
        ('AI Models', {
            'fields': ('groq_model_used', 'huggingface_model_used'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('retry_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(TopicAnalysis)
class TopicAnalysisAdmin(admin.ModelAdmin):
    """Admin configuration for TopicAnalysis model"""
    
    list_display = ('topic', 'complexity_score', 'bloom_taxonomy_level', 
                   'topic_extraction_confidence', 'created_at')
    list_filter = ('bloom_taxonomy_level', 'analysis_job__status', 'created_at')
    search_fields = ('topic__title', 'topic__syllabus__title', 'ai_summary')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'topic', 'analysis_job', 'ai_summary')
        }),
        ('Content Analysis', {
            'fields': ('extracted_keywords', 'semantic_tags', 'bloom_taxonomy_level')
        }),
        ('Difficulty Metrics', {
            'fields': ('complexity_score', 'cognitive_load', 'prerequisite_complexity')
        }),
        ('Time Estimates', {
            'fields': ('reading_time_minutes', 'practice_time_minutes', 
                      'mastery_time_minutes', 'review_time_minutes')
        }),
        ('Learning Styles', {
            'fields': ('visual_learning_score', 'auditory_learning_score',
                      'kinesthetic_learning_score', 'reading_learning_score'),
            'classes': ('collapse',)
        }),
        ('Confidence Scores', {
            'fields': ('topic_extraction_confidence', 'difficulty_confidence', 
                      'time_estimation_confidence'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
