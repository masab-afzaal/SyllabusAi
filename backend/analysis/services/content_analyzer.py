# analysis/services/content_analyzer.py
import logging
from typing import Dict, List, Optional
from django.utils import timezone
from curriculum.models import Syllabus, Topic
from users.models import User
from .groq_service import GroqAnalysisService
from .huggingface_service import HuggingFaceAnalysisService
from ..models import AnalysisJob, TopicAnalysis
from core.utils import clean_extracted_text, calculate_text_complexity

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Main service for comprehensive content analysis"""
    
    def __init__(self):
        self.groq_service = GroqAnalysisService()
        self.hf_service = HuggingFaceAnalysisService()
    
    def analyze_syllabus(self, syllabus_id: str, analysis_depth: str = 'detailed') -> AnalysisJob:
        """
        Main method to analyze a complete syllabus
        """
        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
            
            # Create or get analysis job
            analysis_job, created = AnalysisJob.objects.get_or_create(
                syllabus=syllabus,
                defaults={
                    'status': 'processing',
                    'started_at': timezone.now(),
                    'analysis_depth': analysis_depth,
                    'groq_model_used': 'llama3-8b-8192',
                    'huggingface_model_used': 'multiple_models'
                }
            )
            
            if not created and analysis_job.status == 'completed':
                return analysis_job
            
            # Update status
            analysis_job.status = 'processing'
            analysis_job.started_at = timezone.now()
            analysis_job.save()
            
            # Step 1: Clean and prepare text
            cleaned_text = clean_extracted_text(syllabus.extracted_text)
            syllabus.cleaned_text = cleaned_text
            syllabus.save()
            
            # Step 2: Extract topics using Groq
            topics_data = self.groq_service.extract_topics_from_text(
                cleaned_text, 
                syllabus.subject
            )
            
            # Step 3: Create Topic objects
            created_topics = self._create_topics_from_data(syllabus, topics_data)
            
            # Step 4: Analyze each topic in detail
            for topic in created_topics:
                self._analyze_individual_topic(topic, analysis_job, syllabus.user)
            
            # Step 5: Identify prerequisites relationships
            self._identify_prerequisites(created_topics)
            
            # Step 6: Cluster related topics
            self._cluster_related_topics(created_topics)
            
            # Step 7: Update analysis job completion
            analysis_job.status = 'completed'
            analysis_job.completed_at = timezone.now()
            analysis_job.total_topics_extracted = len(created_topics)
            analysis_job.processing_time_seconds = (
                timezone.now() - analysis_job.started_at
            ).total_seconds()
            
            # Calculate average confidence
            topic_analyses = TopicAnalysis.objects.filter(analysis_job=analysis_job)
            if topic_analyses:
                avg_confidence = sum(
                    ta.topic_extraction_confidence for ta in topic_analyses
                ) / len(topic_analyses)
                analysis_job.average_confidence = avg_confidence
            
            analysis_job.save()
            
            # Update syllabus status
            syllabus.status = 'analyzed'
            syllabus.processing_completed_at = timezone.now()
            syllabus.save()
            
            return analysis_job
            
        except Exception as e:
            logger.error(f"Error analyzing syllabus {syllabus_id}: {str(e)}")
            
            # Update job with error
            if 'analysis_job' in locals():
                analysis_job.status = 'failed'
                analysis_job.error_message = str(e)
                analysis_job.save()
            
            # Update syllabus status
            syllabus.status = 'error'
            syllabus.error_message = str(e)
            syllabus.save()
            
            raise
    
    def _create_topics_from_data(self, syllabus: Syllabus, topics_data: List[Dict]) -> List[Topic]:
        """Create Topic objects from extracted data"""
        created_topics = []
        
        for idx, topic_data in enumerate(topics_data):
            try:
                topic = Topic.objects.create(
                    syllabus=syllabus,
                    title=topic_data.get('title', f'Topic {idx + 1}'),
                    description=topic_data.get('description', ''),
                    topic_type=topic_data.get('type', 'concept'),
                    difficulty_level=min(max(topic_data.get('difficulty_estimate', 5), 1), 10),
                    key_concepts=topic_data.get('key_concepts', []),
                    chapter_section=topic_data.get('chapter_section', ''),
                    order_index=idx,
                    confidence_score=topic_data.get('confidence', 0.7)
                )
                created_topics.append(topic)
                
            except Exception as e:
                logger.error(f"Error creating topic {idx}: {str(e)}")
                continue
        
        return created_topics
    
    def _analyze_individual_topic(self, topic: Topic, analysis_job: AnalysisJob, user: User) -> TopicAnalysis:
        """Perform detailed analysis on individual topic"""
        try:
            # Get user profile for personalized analysis
            user_profile = {
                'grade_level': user.grade_level,
                'knowledge_level': user.knowledge_level,
                'learning_style': user.learning_style,
                'daily_study_hours': user.daily_study_hours
            }
            
            # Groq analysis
            difficulty_analysis = self.groq_service.analyze_topic_difficulty(
                f"{topic.title}: {topic.description}",
                f"Subject: {topic.syllabus.subject}"
            )
            
            time_estimation = self.groq_service.estimate_learning_time(
                f"{topic.title}: {topic.description}",
                topic.difficulty_level,
                user_profile
            )
            
            learning_objectives = self.groq_service.generate_learning_objectives(
                f"{topic.title}: {topic.description}",
                difficulty_analysis.get('bloom_taxonomy', 'understand')
            )
            
            # HuggingFace analysis
            content_classification = self.hf_service.classify_educational_content(
                f"{topic.title} {topic.description}"
            )
            
            key_concepts = self.hf_service.extract_key_concepts(
                f"{topic.title} {topic.description}"
            )
            
            complexity_metrics = self.hf_service.assess_text_complexity(
                topic.description
            )
            
            learning_style_suitability = self.hf_service.analyze_learning_style_suitability(
                topic.description
            )
            
            # Create TopicAnalysis record
            topic_analysis = TopicAnalysis.objects.create(
                topic=topic,
                analysis_job=analysis_job,
                
                # AI-generated content
                ai_summary=f"AI-analyzed topic: {topic.title}",
                extracted_keywords=[concept['concept'] for concept in key_concepts[:5]],
                semantic_tags=[content_classification.get('classification', 'general')],
                
                # Difficulty analysis
                complexity_score=complexity_metrics.get('complexity_score', 0.5),
                cognitive_load=difficulty_analysis.get('cognitive_load', 0.5),
                prerequisite_complexity=difficulty_analysis.get('prerequisite_complexity', 0.3),
                
                # Time estimation
                reading_time_minutes=time_estimation.get('reading_time_minutes', 30),
                practice_time_minutes=time_estimation.get('practice_time_minutes', 60),
                mastery_time_minutes=time_estimation.get('mastery_time_minutes', 45),
                review_time_minutes=time_estimation.get('review_time_minutes', 20),
                
                # Learning style scores
                visual_learning_score=learning_style_suitability.get('visual', 0.5),
                auditory_learning_score=learning_style_suitability.get('auditory', 0.5),
                kinesthetic_learning_score=learning_style_suitability.get('kinesthetic', 0.5),
                reading_learning_score=learning_style_suitability.get('reading', 0.5),
                
                # Bloom's taxonomy
                bloom_taxonomy_level=difficulty_analysis.get('bloom_taxonomy', 'understand'),
                
                # Confidence scores
                topic_extraction_confidence=topic.confidence_score,
                difficulty_confidence=difficulty_analysis.get('confidence', 0.7),
                time_estimation_confidence=time_estimation.get('confidence', 0.7)
            )
            
            # Update topic with enhanced information
            total_time = (
                topic_analysis.reading_time_minutes +
                topic_analysis.practice_time_minutes +
                topic_analysis.mastery_time_minutes +
                topic_analysis.review_time_minutes
            ) / 60  # Convert to hours
            
            topic.estimated_hours = total_time
            topic.learning_objectives = learning_objectives
            topic.suggested_resources = self._generate_suggested_resources(topic, content_classification)
            
            # Adjust difficulty based on AI analysis
            ai_difficulty = difficulty_analysis.get('difficulty_level', topic.difficulty_level)
            topic.difficulty_level = int((topic.difficulty_level + ai_difficulty) / 2)
            
            topic.save()
            
            return topic_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing topic {topic.id}: {str(e)}")
            # Create basic analysis record
            return TopicAnalysis.objects.create(
                topic=topic,
                analysis_job=analysis_job,
                ai_summary=f"Basic analysis for {topic.title}",
                complexity_score=0.5,
                topic_extraction_confidence=0.5
            )
    
    def _identify_prerequisites(self, topics: List[Topic]) -> None:
        """Identify prerequisite relationships between topics"""
        try:
            topic_titles = [topic.title for topic in topics]
            
            for topic in topics:
                # Use Groq to identify prerequisites
                prerequisites_data = self.groq_service.identify_prerequisites(
                    f"{topic.title}: {topic.description}",
                    topic_titles
                )
                
                # Add prerequisite relationships
                for prereq_data in prerequisites_data:
                    prereq_title = prereq_data.get('prerequisite_topic')
                    confidence = prereq_data.get('confidence', 0.0)
                    
                    if confidence > 0.7:  # High confidence threshold
                        try:
                            prereq_topic = next(
                                t for t in topics if t.title == prereq_title
                            )
                            topic.prerequisites.add(prereq_topic)
                        except StopIteration:
                            continue
                
        except Exception as e:
            logger.error(f"Error identifying prerequisites: {str(e)}")
    
    def _cluster_related_topics(self, topics: List[Topic]) -> None:
        """Cluster related topics for better organization"""
        try:
            if len(topics) < 3:
                return
            
            # Prepare text for clustering
            topics_text = [f"{topic.title} {topic.description}" for topic in topics]
            
            # Use HuggingFace clustering
            clustering_result = self.hf_service.cluster_topics(topics_text)
            
            clusters = clustering_result.get('clusters', [])
            cluster_descriptions = clustering_result.get('cluster_descriptions', [])
            
            # Update topics with cluster information
            for i, topic in enumerate(topics):
                if i < len(clusters):
                    cluster_id = clusters[i]
                    if cluster_id < len(cluster_descriptions):
                        # Add cluster info to topic's metadata
                        if not hasattr(topic, 'cluster_info'):
                            topic.cluster_info = {}
                        
                        topic.cluster_info = {
                            'cluster_id': cluster_id,
                            'cluster_description': cluster_descriptions[cluster_id]
                        }
                        
                        # Update chapter_section if not set
                        if not topic.chapter_section:
                            topic.chapter_section = f"Module {cluster_id + 1}"
                        
                        topic.save()
            
        except Exception as e:
            logger.error(f"Error clustering topics: {str(e)}")
    
    def _generate_suggested_resources(self, topic: Topic, classification: Dict) -> List[str]:
        """Generate suggested learning resources based on topic analysis"""
        resources = []
        
        subject = classification.get('classification', 'general')
        difficulty = topic.difficulty_level
        
        # Basic resources based on subject
        subject_resources = {
            'mathematics': [
                'Khan Academy Mathematics',
                'Wolfram Alpha for calculations',
                'MIT OpenCourseWare Mathematics'
            ],
            'science': [
                'National Geographic Science',
                'Scientific American articles',
                'Coursera Science courses'
            ],
            'computer_science': [
                'Stack Overflow discussions',
                'GitHub repositories',
                'GeeksforGeeks tutorials'
            ],
            'engineering': [
                'Engineering toolbox resources',
                'IEEE publications',
                'Engineering simulation software'
            ]
        }
        
        resources.extend(subject_resources.get(subject, [
            'Wikipedia articles',
            'YouTube educational videos',
            'Online course materials'
        ]))
        
        # Add difficulty-specific resources
        if difficulty <= 3:
            resources.append('Beginner-friendly tutorials')
        elif difficulty >= 7:
            resources.extend([
                'Advanced research papers',
                'Expert-level documentation'
            ])
        
        return resources[:5]  # Limit to top 5 resources
