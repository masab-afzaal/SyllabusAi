# analysis/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from .models import AnalysisJob, TopicAnalysis
from .serializers import (
    AnalysisJobSerializer, AnalysisJobSummarySerializer, TopicAnalysisSerializer,
    ReanalysisRequestSerializer, BatchAnalysisRequestSerializer,
    TopicDifficultyUpdateSerializer, AnalysisInsightsSerializer
)
from curriculum.models import Syllabus, Topic
from .tasks import reanalyze_syllabus, batch_process_syllabi
import logging

logger = logging.getLogger(__name__)

class AnalysisJobListView(generics.ListAPIView):
    """List user's analysis jobs"""
    serializer_class = AnalysisJobSummarySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'analysis_depth']
    search_fields = ['syllabus__title']
    ordering_fields = ['created_at', 'completed_at', 'processing_time_seconds']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return AnalysisJob.objects.filter(
            syllabus__user=self.request.user
        ).select_related('syllabus')

class AnalysisJobDetailView(generics.RetrieveAPIView):
    """Retrieve detailed analysis job information"""
    serializer_class = AnalysisJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisJob.objects.filter(
            syllabus__user=self.request.user
        ).select_related('syllabus').prefetch_related('topic_analyses__topic')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reanalyze_syllabus_view(request, syllabus_id):
    """Trigger reanalysis of a syllabus"""
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=request.user)
    
    serializer = ReanalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    # Check if recent analysis exists and force_reprocess is False
    if not validated_data.get('force_reprocess', False):
        recent_analysis = AnalysisJob.objects.filter(
            syllabus=syllabus,
            status='completed',
            completed_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).first()
        
        if recent_analysis:
            return Response({
                'message': 'Recent analysis found. Use force_reprocess=true to override.',
                'analysis_job': AnalysisJobSummarySerializer(recent_analysis).data
            }, status=status.HTTP_200_OK)
    
    # Delete existing analysis to start fresh
    AnalysisJob.objects.filter(syllabus=syllabus).delete()
    
    # Trigger reanalysis task
    try:
        task = reanalyze_syllabus.delay(
            str(syllabus_id),
            validated_data['analysis_depth']
        )
        
        return Response({
            'message': 'Reanalysis started',
            'task_id': task.id,
            'syllabus_id': str(syllabus_id),
            'analysis_depth': validated_data['analysis_depth']
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error starting reanalysis for {syllabus_id}: {str(e)}")
        return Response({
            'error': 'Failed to start reanalysis',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_analyze_view(request):
    """Trigger batch analysis of multiple syllabi"""
    serializer = BatchAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    syllabus_ids = validated_data['syllabus_ids']
    
    # Verify all syllabi belong to the user
    user_syllabi = Syllabus.objects.filter(
        id__in=syllabus_ids,
        user=request.user
    ).values_list('id', flat=True)
    
    if len(user_syllabi) != len(syllabus_ids):
        return Response({
            'error': 'Some syllabi not found or not owned by user'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Trigger batch processing
    try:
        task = batch_process_syllabi.delay(
            [str(sid) for sid in syllabus_ids],
            validated_data['analysis_depth']
        )
        
        return Response({
            'message': 'Batch analysis started',
            'task_id': task.id,
            'syllabus_count': len(syllabus_ids),
            'analysis_depth': validated_data['analysis_depth']
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error starting batch analysis: {str(e)}")
        return Response({
            'error': 'Failed to start batch analysis',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopicAnalysisDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update topic analysis"""
    serializer_class = TopicAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TopicAnalysis.objects.filter(
            topic__syllabus__user=self.request.user
        ).select_related('topic', 'analysis_job')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_topic_difficulty_view(request, topic_id):
    """Update topic difficulty based on user feedback"""
    topic = get_object_or_404(Topic, id=topic_id, syllabus__user=request.user)
    
    serializer = TopicDifficultyUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    # Update topic difficulty
    old_difficulty = topic.difficulty_level
    topic.difficulty_level = validated_data['difficulty_level']
    topic.save()
    
    # Update analysis if exists
    try:
        analysis = topic.analysis
        analysis.cognitive_load = validated_data['difficulty_level'] / 10.0
        analysis.save()
    except TopicAnalysis.DoesNotExist:
        pass
    
    # Log user feedback
    logger.info(f"User {request.user.username} updated topic {topic_id} difficulty: {old_difficulty} -> {validated_data['difficulty_level']}")
    
    return Response({
        'message': 'Topic difficulty updated successfully',
        'topic_id': str(topic_id),
        'old_difficulty': old_difficulty,
        'new_difficulty': validated_data['difficulty_level'],
        'user_feedback': validated_data.get('user_feedback', '')
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_insights_view(request):
    """Get analysis insights and statistics for the user"""
    user = request.user
    
    # Analysis jobs statistics
    analysis_jobs = AnalysisJob.objects.filter(syllabus__user=user)
    
    total_jobs = analysis_jobs.count()
    completed_jobs = analysis_jobs.filter(status='completed').count()
    failed_jobs = analysis_jobs.filter(status='failed').count()
    
    avg_processing_time = analysis_jobs.filter(
        status='completed',
        processing_time_seconds__isnull=False
    ).aggregate(avg_time=Avg('processing_time_seconds'))['avg_time'] or 0.0
    
    # Topic statistics
    topics = Topic.objects.filter(syllabus__user=user)
    total_topics = topics.count()
    
    # Difficulty distribution
    difficulty_dist = {}
    for i in range(1, 11):
        count = topics.filter(difficulty_level=i).count()
        difficulty_dist[str(i)] = count
    
    # Subject distribution
    subject_dist = {}
    syllabi = Syllabus.objects.filter(user=user)
    for syllabus in syllabi:
        subject = syllabus.get_subject_display()
        subject_dist[subject] = subject_dist.get(subject, 0) + 1
    
    # Learning style suitability analysis
    topic_analyses = TopicAnalysis.objects.filter(
        topic__syllabus__user=user
    )
    
    if topic_analyses.exists():
        learning_style_avg = topic_analyses.aggregate(
            visual=Avg('visual_learning_score'),
            auditory=Avg('auditory_learning_score'),
            kinesthetic=Avg('kinesthetic_learning_score'),
            reading=Avg('reading_learning_score')
        )
        
        learning_style_suitability = {
            'visual': round(learning_style_avg['visual'] or 0.5, 2),
            'auditory': round(learning_style_avg['auditory'] or 0.5, 2),
            'kinesthetic': round(learning_style_avg['kinesthetic'] or 0.5, 2),
            'reading': round(learning_style_avg['reading'] or 0.5, 2)
        }
    else:
        learning_style_suitability = {
            'visual': 0.5, 'auditory': 0.5, 'kinesthetic': 0.5, 'reading': 0.5
        }
    
    insights_data = {
        'total_analysis_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'failed_jobs': failed_jobs,
        'average_processing_time': round(avg_processing_time, 2),
        'total_topics_analyzed': total_topics,
        'difficulty_distribution': difficulty_dist,
        'subject_distribution': subject_dist,
        'learning_style_suitability': learning_style_suitability
    }
    
    serializer = AnalysisInsightsSerializer(insights_data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def topic_recommendations_view(request, syllabus_id):
    """Get AI-powered topic recommendations for study planning"""
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=request.user)
    
    if syllabus.status != 'analyzed':
        return Response({
            'error': 'Syllabus must be analyzed first'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    topics = syllabus.topics.all().order_by('order_index')
    
    recommendations = []
    
    for topic in topics:
        try:
            analysis = topic.analysis
            
            # Calculate personalized difficulty adjustment
            user_style_score = getattr(analysis, f'{user.learning_style}_learning_score', 0.5)
            
            # Adjust for user's knowledge level
            knowledge_multiplier = {
                'beginner': 1.3,
                'intermediate': 1.0,
                'advanced': 0.8,
                'expert': 0.6
            }.get(user.knowledge_level, 1.0)
            
            adjusted_difficulty = min(topic.difficulty_level * knowledge_multiplier, 10)
            
            # Calculate recommended study time
            base_time = topic.estimated_hours
            style_adjustment = 1.0 + (0.5 - user_style_score)  # More time if style doesn't match
            recommended_time = base_time * style_adjustment
            
            recommendations.append({
                'topic_id': str(topic.id),
                'title': topic.title,
                'original_difficulty': topic.difficulty_level,
                'personalized_difficulty': round(adjusted_difficulty, 1),
                'original_time_hours': base_time,
                'recommended_time_hours': round(recommended_time, 1),
                'learning_style_match': user_style_score,
                'bloom_level': analysis.bloom_taxonomy_level,
                'key_challenges': analysis.extracted_keywords[:3],
                'study_priority': 'high' if adjusted_difficulty > 7 else 'medium' if adjusted_difficulty > 4 else 'low'
            })
            
        except TopicAnalysis.DoesNotExist:
            # Basic recommendation without detailed analysis
            recommendations.append({
                'topic_id': str(topic.id),
                'title': topic.title,
                'original_difficulty': topic.difficulty_level,
                'personalized_difficulty': topic.difficulty_level,
                'original_time_hours': topic.estimated_hours,
                'recommended_time_hours': topic.estimated_hours,
                'learning_style_match': 0.5,
                'bloom_level': 'understand',
                'key_challenges': [],
                'study_priority': 'medium'
            })
    
    return Response({
        'syllabus_id': str(syllabus_id),
        'user_profile': {
            'learning_style': user.learning_style,
            'knowledge_level': user.knowledge_level,
            'daily_study_hours': user.daily_study_hours
        },
        'recommendations': recommendations,
        'summary': {
            'total_topics': len(recommendations),
            'high_priority': len([r for r in recommendations if r['study_priority'] == 'high']),
            'estimated_total_hours': sum(r['recommended_time_hours'] for r in recommendations),
            'avg_difficulty': sum(r['personalized_difficulty'] for r in recommendations) / len(recommendations) if recommendations else 0
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_progress_view(request, analysis_job_id):
    """Get real-time progress of an analysis job"""
    analysis_job = get_object_or_404(
        AnalysisJob, 
        id=analysis_job_id, 
        syllabus__user=request.user
    )
    
    progress_data = {
        'job_id': str(analysis_job.id),
        'status': analysis_job.status,
        'started_at': analysis_job.started_at,
        'progress_percentage': 0,
        'current_step': 'Pending',
        'estimated_completion': None,
        'topics_processed': 0,
        'total_topics_estimated': 0
    }
    
    if analysis_job.status == 'processing':
        # Calculate progress based on created topics and analyses
        topics_created = analysis_job.syllabus.topics.count()
        analyses_completed = analysis_job.topic_analyses.count()
        
        if topics_created > 0:
            progress_percentage = (analyses_completed / topics_created) * 100
            progress_data.update({
                'progress_percentage': min(progress_percentage, 95),  # Never show 100% until complete
                'current_step': f'Analyzing topic {analyses_completed + 1} of {topics_created}',
                'topics_processed': analyses_completed,
                'total_topics_estimated': topics_created
            })
            
            # Estimate completion time
            if analyses_completed > 0 and analysis_job.started_at:
                elapsed = (timezone.now() - analysis_job.started_at).total_seconds()
                avg_time_per_topic = elapsed / analyses_completed
                remaining_topics = topics_created - analyses_completed
                estimated_remaining = remaining_topics * avg_time_per_topic
                
                progress_data['estimated_completion'] = timezone.now() + timezone.timedelta(seconds=estimated_remaining)
        else:
            progress_data.update({
                'progress_percentage': 25,
                'current_step': 'Extracting topics from syllabus'
            })
    
    elif analysis_job.status == 'completed':
        progress_data.update({
            'progress_percentage': 100,
            'current_step': 'Analysis completed',
            'topics_processed': analysis_job.total_topics_extracted,
            'total_topics_estimated': analysis_job.total_topics_extracted,
            'completed_at': analysis_job.completed_at,
            'processing_time_seconds': analysis_job.processing_time_seconds
        })
    
    elif analysis_job.status == 'failed':
        progress_data.update({
            'progress_percentage': 0,
            'current_step': 'Analysis failed',
            'error_message': analysis_job.error_message
        })
    
    return Response(progress_data)
