
from rest_framework import serializers
from .models import LearningPlan, LearningSession, Milestone, StudyPreference, TopicExtension

class StudyPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPreference
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class LearningPlanSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.ReadOnlyField()
    total_sessions = serializers.SerializerMethodField()
    completed_sessions = serializers.SerializerMethodField()
    next_session = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPlan
        fields = '__all__'
        read_only_fields = ('user', 'completion_percentage', 'created_at', 'updated_at')
    
    def get_total_sessions(self, obj):
        return obj.sessions.count()
    
    def get_completed_sessions(self, obj):
        return obj.sessions.filter(status='completed').count()
    
    def get_next_session(self, obj):
        next_session = obj.sessions.filter(status='pending').order_by('scheduled_date').first()
        if next_session:
            return LearningSessionSerializer(next_session).data
        return None

class LearningSessionSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    is_available = serializers.SerializerMethodField()
    prerequisites_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningSession
        fields = '__all__'
        read_only_fields = ('learning_plan', 'created_at', 'updated_at')
    
    def get_is_available(self, obj):
        """Check if all prerequisites are completed"""
        return all(
            prereq_session.status == 'completed' 
            for prereq_session in obj.prerequisites.all()
        )
    
    def get_prerequisites_completed(self, obj):
        total_prereqs = obj.prerequisites.count()
        completed_prereqs = obj.prerequisites.filter(status='completed').count()
        return {
            'total': total_prereqs,
            'completed': completed_prereqs,
            'percentage': (completed_prereqs / total_prereqs * 100) if total_prereqs > 0 else 100
        }

class MilestoneSerializer(serializers.ModelSerializer):
    topics_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('learning_plan', 'created_at')
    
    def get_topics_count(self, obj):
        return obj.topics.count()
    
    def get_progress_percentage(self, obj):
        total_topics = obj.topics.count()
        if total_topics == 0:
            return 100
        
        # Calculate progress based on completed sessions for these topics
        completed_sessions = LearningSession.objects.filter(
            learning_plan=obj.learning_plan,
            topic__in=obj.topics.all(),
            status='completed'
        ).count()
        
        total_sessions = LearningSession.objects.filter(
            learning_plan=obj.learning_plan,
            topic__in=obj.topics.all()
        ).count()
        
        return (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

class TopicExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicExtension
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

