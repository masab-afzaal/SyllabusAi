# analysis/models.py
from django.db import models
from curriculum.models import Syllabus, Topic
import uuid

class AnalysisJob(models.Model):
    """Track AI analysis jobs for syllabi"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    syllabus = models.OneToOneField(Syllabus, on_delete=models.CASCADE, related_name='analysis_job')
    
    # Job Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Analysis Configuration
    use_groq = models.BooleanField(default=True)
    use_huggingface = models.BooleanField(default=True)
    analysis_depth = models.CharField(
        max_length=20,
        choices=[('basic', 'Basic'), ('detailed', 'Detailed'), ('comprehensive', 'Comprehensive')],
        default='detailed'
    )
    
    # Analysis Results
    total_topics_extracted = models.PositiveIntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    processing_time_seconds = models.FloatField(default=0.0)
    
    # AI Model Metadata
    groq_model_used = models.CharField(max_length=100, blank=True)
    huggingface_model_used = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analysis for {self.syllabus.title} - {self.status}"

class TopicAnalysis(models.Model):
    """Detailed analysis results for individual topics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='analysis')
    analysis_job = models.ForeignKey(AnalysisJob, on_delete=models.CASCADE, related_name='topic_analyses')
    
    # AI-Generated Content
    ai_summary = models.TextField(help_text="AI-generated topic summary")
    extracted_keywords = models.JSONField(default=list, help_text="AI-extracted keywords")
    semantic_tags = models.JSONField(default=list, help_text="Semantic classification tags")
    
    # Difficulty Analysis
    complexity_score = models.FloatField(help_text="AI-calculated complexity (0-1)")
    cognitive_load = models.FloatField(help_text="Estimated cognitive load (0-1)")
    prerequisite_complexity = models.FloatField(default=0.0, help_text="Prerequisites complexity impact")
    
    # Time Estimation Factors
    reading_time_minutes = models.FloatField(default=0.0)
    practice_time_minutes = models.FloatField(default=0.0)
    mastery_time_minutes = models.FloatField(default=0.0)
    review_time_minutes = models.FloatField(default=0.0)
    
    # Learning Style Adaptations
    visual_learning_score = models.FloatField(default=0.5, help_text="Visual learning suitability (0-1)")
    auditory_learning_score = models.FloatField(default=0.5, help_text="Auditory learning suitability (0-1)")
    kinesthetic_learning_score = models.FloatField(default=0.5, help_text="Kinesthetic learning suitability (0-1)")
    reading_learning_score = models.FloatField(default=0.5, help_text="Reading/writing learning suitability (0-1)")
    
    # Content Classification
    bloom_taxonomy_level = models.CharField(
        max_length=20,
        choices=[
            ('remember', 'Remember'),
            ('understand', 'Understand'),
            ('apply', 'Apply'),
            ('analyze', 'Analyze'),
            ('evaluate', 'Evaluate'),
            ('create', 'Create'),
        ],
        default='understand'
    )
    
    # AI Confidence Scores
    topic_extraction_confidence = models.FloatField(default=0.0)
    difficulty_confidence = models.FloatField(default=0.0)
    time_estimation_confidence = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analysis for {self.topic.title}"
