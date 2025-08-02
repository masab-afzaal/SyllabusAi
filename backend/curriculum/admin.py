# curriculum/admin.py
from django.contrib import admin
from .models import Syllabus, Topic

@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    """Admin configuration for Syllabus model"""
    
    list_display = ('title', 'user', 'subject', 'status', 'word_count', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('title', 'user__username', 'description')
    readonly_fields = ('id', 'file_size', 'word_count', 'extracted_text', 'processing_started_at', 
                      'processing_completed_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'description', 'file', 'file_size')
        }),
        ('Classification', {
            'fields': ('subject', 'estimated_duration_weeks')
        }),
        ('Processing Status', {
            'fields': ('status', 'processing_started_at', 'processing_completed_at', 'error_message')
        }),
        ('Extracted Content', {
            'fields': ('word_count', 'extracted_text', 'cleaned_text'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

class TopicInline(admin.TabularInline):
    """Inline admin for Topic model"""
    model = Topic
    extra = 0
    fields = ('title', 'topic_type', 'difficulty_level', 'estimated_hours', 'order_index')
    readonly_fields = ('id',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin configuration for Topic model"""
    
    list_display = ('title', 'syllabus', 'topic_type', 'difficulty_level', 'estimated_hours', 'order_index')
    list_filter = ('topic_type', 'difficulty_level', 'syllabus__subject')
    search_fields = ('title', 'description', 'syllabus__title')
    filter_horizontal = ('prerequisites',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'syllabus', 'title', 'description', 'topic_type')
        }),
        ('Difficulty & Time', {
            'fields': ('difficulty_level', 'estimated_hours', 'confidence_score')
        }),
        ('Content Analysis', {
            'fields': ('key_concepts', 'learning_objectives', 'suggested_resources'),
            'classes': ('collapse',)
        }),
        ('Order & Dependencies', {
            'fields': ('order_index', 'chapter_section', 'prerequisites')
        })
    )
    
    readonly_fields = ('id',)
