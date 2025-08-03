# analysis/serializers.py
from rest_framework import serializers
from .models import AnalysisJob, TopicAnalysis
from curriculum.serializers import TopicSerializer

class TopicAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for TopicAnalysis model"""
    topic = TopicSerializer(read_only=True)
    
    class Meta:
        model = TopicAnalysis
        fields = [
            'id', 'topic', 'ai_summary', 'extracted_keywords', 'semantic_tags',
            'complexity_score', 'cognitive_load', 'prerequisite_complexity',
            'reading_time_minutes', 'practice_time_minutes', 'mastery_time_minutes',
            'review_time_minutes', 'visual_learning_score', 'auditory_learning_score',
            'kinesthetic_learning_score', 'reading_learning_score', 'bloom_taxonomy_level',
            'topic_extraction_confidence', 'difficulty_confidence', 'time_estimation_confidence',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AnalysisJobSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisJob model"""
    syllabus_title = serializers.CharField(source='syllabus.title', read_only=True)
    topic_analyses = TopicAnalysisSerializer(many=True, read_only=True)
    
    class Meta:
        model = AnalysisJob
        fields = [
            'id', 'syllabus_title', 'status', 'started_at', 'completed_at',
            'error_message', 'retry_count', 'use_groq', 'use_huggingface',
            'analysis_depth', 'total_topics_extracted', 'average_confidence',
            'processing_time_seconds', 'groq_model_used', 'huggingface_model_used',
            'topic_analyses', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AnalysisJobSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for AnalysisJob (without nested data)"""
    syllabus_title = serializers.CharField(source='syllabus.title', read_only=True)
    topics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisJob
        fields = [
            'id', 'syllabus_title', 'status', 'started_at', 'completed_at',
            'analysis_depth', 'total_topics_extracted', 'average_confidence',
            'processing_time_seconds', 'topics_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_topics_count(self, obj):
        return obj.topic_analyses.count()

class ReanalysisRequestSerializer(serializers.Serializer):
    """Serializer for reanalysis requests"""
    analysis_depth = serializers.ChoiceField(
        choices=[('basic', 'Basic'), ('detailed', 'Detailed'), ('comprehensive', 'Comprehensive')],
        default='detailed'
    )
    use_groq = serializers.BooleanField(default=True)
    use_huggingface = serializers.BooleanField(default=True)
    force_reprocess = serializers.BooleanField(default=False)

class BatchAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for batch analysis requests"""
    syllabus_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10
    )
    analysis_depth = serializers.ChoiceField(
        choices=[('basic', 'Basic'), ('detailed', 'Detailed'), ('comprehensive', 'Comprehensive')],
        default='detailed'
    )

class TopicDifficultyUpdateSerializer(serializers.Serializer):
    """Serializer for updating topic difficulty"""
    difficulty_level = serializers.IntegerField(min_value=1, max_value=10)
    user_feedback = serializers.CharField(max_length=500, required=False)

class AnalysisInsightsSerializer(serializers.Serializer):
    """Serializer for analysis insights and statistics"""
    total_analysis_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    average_processing_time = serializers.FloatField()
    total_topics_analyzed = serializers.IntegerField()
    difficulty_distribution = serializers.DictField()
    subject_distribution = serializers.DictField()
    learning_style_suitability = serializers.DictField()
