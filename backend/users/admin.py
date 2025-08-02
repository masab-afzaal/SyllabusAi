from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for extended User model"""

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('age', 'grade_level', 'learning_style', 'knowledge_level')
        }),
        ('Study Preferences', {
            'fields': ('daily_study_hours', 'preferred_session_length', 'break_interval', 
                      'target_completion_days', 'difficulty_preference')
        }),
        ('Productivity Times', {
            'fields': ('morning_productivity', 'afternoon_productivity', 'evening_productivity')
        }),
    )
    
    list_display = ('username', 'email', 'grade_level', 'learning_style', 'daily_study_hours', 'is_active')
    list_filter = ('grade_level', 'learning_style', 'knowledge_level', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
