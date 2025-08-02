# curriculum/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

def syllabus_upload_path(instance, filename):
    """Generate upload path for syllabus files"""
    return f'syllabi/{instance.user.id}/{uuid.uuid4()}/{filename}'

class Syllabus(models.Model):
    """Main syllabus document uploaded by user"""
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
        ('completed', 'Plan Generated'),
        ('error', 'Error'),
    ]
    
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('engineering', 'Engineering'),
        ('computer_science', 'Computer Science'),
        ('literature', 'Literature'),
        ('history', 'History'),
        ('languages', 'Languages'),
        ('business', 'Business'),
        ('arts', 'Arts'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='syllabi')
    
    # File Information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=syllabus_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'txt'])]
    )
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    
    # Classification
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES, default='other')
    estimated_duration_weeks = models.PositiveIntegerField(null=True, blank=True)
    
    # Processing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Extracted Content
    extracted_text = models.TextField(blank=True, help_text="Raw extracted text from file")
    cleaned_text = models.TextField(blank=True, help_text="Processed and cleaned text")
    word_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Syllabi"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Topic(models.Model):
    """Individual topics extracted from syllabus"""
    
    DIFFICULTY_CHOICES = [
        (1, 'Very Easy'),
        (2, 'Easy'),
        (3, 'Easy-Medium'),
        (4, 'Medium'),
        (5, 'Medium-Hard'),
        (6, 'Hard'),
        (7, 'Very Hard'),
        (8, 'Expert'),
        (9, 'Master'),
        (10, 'Extreme'),
    ]
    
    TOPIC_TYPE_CHOICES = [
        ('concept', 'Core Concept'),
        ('skill', 'Practical Skill'),
        ('theory', 'Theoretical Knowledge'),
        ('application', 'Application/Practice'),
        ('assessment', 'Assessment/Test'),
        ('project', 'Project Work'),
        ('reading', 'Reading Assignment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='topics')
    
    # Topic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    topic_type = models.CharField(max_length=20, choices=TOPIC_TYPE_CHOICES, default='concept')
    
    # Difficulty and Time Estimation
    difficulty_level = models.PositiveIntegerField(choices=DIFFICULTY_CHOICES, default=5)
    estimated_hours = models.FloatField(help_text="Estimated study hours required")
    confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Prerequisites and Dependencies
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependents')
    
    # Content Analysis
    key_concepts = models.JSONField(default=list, help_text="List of key concepts in this topic")
    learning_objectives = models.JSONField(default=list, help_text="Learning objectives for this topic")
    suggested_resources = models.JSONField(default=list, help_text="Suggested learning resources")
    
    # Order and Grouping
    order_index = models.PositiveIntegerField(default=0, help_text="Order within syllabus")
    chapter_section = models.CharField(max_length=100, blank=True, help_text="Chapter or section reference")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index', 'created_at']
        unique_together = ['syllabus', 'order_index']
    
    def __str__(self):
        return f"{self.title} (Difficulty: {self.difficulty_level})"
