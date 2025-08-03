# core/filters.py
import django_filters
from curriculum.models import Syllabus, Topic
from planning.models import LearningPlan, ScheduleBlock

class SyllabusFilter(django_filters.FilterSet):
    """Filter for Syllabus model"""
    subject = django_filters.ChoiceFilter(choices=Syllabus.SUBJECT_CHOICES)
    status = django_filters.ChoiceFilter(choices=Syllabus.STATUS_CHOICES)
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    word_count_min = django_filters.NumberFilter(field_name='word_count', lookup_expr='gte')
    word_count_max = django_filters.NumberFilter(field_name='word_count', lookup_expr='lte')
    
    class Meta:
        model = Syllabus
        fields = ['subject', 'status']

class TopicFilter(django_filters.FilterSet):
    """Filter for Topic model"""
    difficulty_min = django_filters.NumberFilter(field_name='difficulty_level', lookup_expr='gte')
    difficulty_max = django_filters.NumberFilter(field_name='difficulty_level', lookup_expr='lte')
    hours_min = django_filters.NumberFilter(field_name='estimated_hours', lookup_expr='gte')
    hours_max = django_filters.NumberFilter(field_name='estimated_hours', lookup_expr='lte')
    topic_type = django_filters.ChoiceFilter(choices=Topic.TOPIC_TYPE_CHOICES)
    
    class Meta:
        model = Topic
        fields = ['topic_type', 'difficulty_level']

class LearningPlanFilter(django_filters.FilterSet):
    """Filter for LearningPlan model"""
    status = django_filters.ChoiceFilter(choices=LearningPlan.STATUS_CHOICES)
    plan_type = django_filters.ChoiceFilter(choices=LearningPlan.PLAN_TYPE_CHOICES)
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    class Meta:
        model = LearningPlan
        fields = ['status', 'plan_type']

class ScheduleBlockFilter(django_filters.FilterSet):
    """Filter for ScheduleBlock model"""
    status = django_filters.ChoiceFilter(choices=ScheduleBlock.STATUS_CHOICES)
    block_type = django_filters.ChoiceFilter(choices=ScheduleBlock.BLOCK_TYPE_CHOICES)
    scheduled_date = django_filters.DateFilter()
    scheduled_date_after = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_date_before = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='lte')
    
    class Meta:
        model = ScheduleBlock
        fields = ['status', 'block_type', 'scheduled_date']
