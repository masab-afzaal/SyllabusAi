# planning/serializers.py
from rest_framework import serializers
from .models import LearningPlan, ScheduleBlock, StudySession
from curriculum.serializers import TopicSerializer

class ScheduleBlockSerializer(serializers.ModelSerializer):
    """Serializer for schedule blocks"""
    topic = TopicSerializer(read_only=True)
    topic_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ScheduleBlock
        fields = [
            'id', 'title', 'block_type', 'status', 'scheduled_date',
            'start_time', 'end_time', 'estimated_duration', 'actual_duration',
            'completion_percentage', 'difficulty_rating', 'satisfaction_rating',
            'notes', 'challenges_faced', 'achievements', 'topic', 'topic_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class StudySessionSerializer(serializers.ModelSerializer):
    """Serializer for study sessions"""
    schedule_block = ScheduleBlockSerializer(read_only=True)
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'started_at', 'ended_at', 'paused_duration',
            'focus_score', 'understanding_score', 'retention_confidence',
            'concepts_mastered', 'concepts_struggling', 'questions_raised',
            'resources_used', 'session_notes', 'next_session_goals',
            'schedule_block', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class LearningPlanSerializer(serializers.ModelSerializer):
    """Serializer for learning plans"""
    syllabus_title = serializers.CharField(source='syllabus.title', read_only=True)
    schedule_blocks = ScheduleBlockSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = LearningPlan
        fields = [
            'id', 'title', 'plan_type', 'status', 'start_date',
            'target_end_date', 'actual_end_date', 'total_estimated_hours',
            'total_topics', 'average_difficulty', 'completed_hours',
            'completed_topics', 'current_streak', 'longest_streak',
            'daily_study_hours', 'session_length', 'break_length',
            'difficulty_adjustment', 'time_adjustment', 'syllabus_title',
            'schedule_blocks', 'completion_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_estimated_hours', 'total_topics', 'average_difficulty',
            'completed_hours', 'completed_topics', 'current_streak',
            'longest_streak', 'created_at', 'updated_at'
        ]

class LearningPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating learning plans"""
    
    class Meta:
        model = LearningPlan
        fields = [
            'title', 'plan_type', 'start_date', 'target_end_date',
            'daily_study_hours', 'session_length', 'break_length'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['syllabus'] = self.context['syllabus']
        return super().create(validated_data)
