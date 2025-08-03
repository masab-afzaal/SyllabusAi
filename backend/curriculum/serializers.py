# curriculum/serializers.py

from rest_framework import serializers
from .models import Syllabus, Topic
from planning.models import LearningPlan

class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model"""
    prerequisites_count = serializers.SerializerMethodField()
    dependents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'description', 'topic_type', 'difficulty_level',
            'estimated_hours', 'confidence_score', 'key_concepts',
            'learning_objectives', 'suggested_resources', 'order_index',
            'chapter_section', 'prerequisites_count', 'dependents_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_prerequisites_count(self, obj):
        return obj.prerequisites.count()
    
    def get_dependents_count(self, obj):
        return obj.dependents.count()

class SyllabusListSerializer(serializers.ModelSerializer):
    """Serializer for syllabus list view"""
    topics_count = serializers.SerializerMethodField()
    learning_plans_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Syllabus
        fields = [
            'id', 'title', 'description', 'subject', 'status',
            'estimated_duration_weeks', 'word_count', 'topics_count',
            'learning_plans_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'word_count', 'created_at', 'updated_at']
    
    def get_topics_count(self, obj):
        return obj.topics.count()
    
    def get_learning_plans_count(self, obj):
        return obj.learning_plans.count()

class SyllabusDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for syllabus with topics"""
    topics = TopicSerializer(many=True, read_only=True)
    topics_count = serializers.SerializerMethodField()
    average_difficulty = serializers.SerializerMethodField()
    total_estimated_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Syllabus
        fields = [
            'id', 'title', 'description', 'file', 'file_size', 'subject',
            'estimated_duration_weeks', 'status', 'processing_started_at',
            'processing_completed_at', 'error_message', 'extracted_text',
            'word_count', 'topics', 'topics_count', 'average_difficulty',
            'total_estimated_hours', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'status', 'processing_started_at',
            'processing_completed_at', 'error_message', 'extracted_text',
            'word_count', 'created_at', 'updated_at'
        ]
    
    def get_topics_count(self, obj):
        return obj.topics.count()
    
    def get_average_difficulty(self, obj):
        topics = obj.topics.all()
        if not topics:
            return 0
        return sum(topic.difficulty_level for topic in topics) / len(topics)
    
    def get_total_estimated_hours(self, obj):
        return sum(topic.estimated_hours for topic in obj.topics.all())

class SyllabusCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new syllabus"""
    
    class Meta:
        model = Syllabus
        fields = ['title', 'description', 'file', 'subject', 'estimated_duration_weeks']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
