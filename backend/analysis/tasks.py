# analysis/tasks.py
from celery import shared_task
from django.utils import timezone
import logging
from .services.content_analyzer import ContentAnalyzer
from curriculum.models import Syllabus
from core.utils import extract_text_from_file

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_syllabus(self, syllabus_id):
    """
    Celery task to process uploaded syllabus file
    """
    try:
        syllabus = Syllabus.objects.get(id=syllabus_id)
        
        # Update status
        syllabus.status = 'processing'
        syllabus.processing_started_at = timezone.now()
        syllabus.save()
        
        # Step 1: Extract text from file
        if syllabus.file:
            extracted_text, error = extract_text_from_file(syllabus.file.path)
            
            if error:
                raise Exception(f"Text extraction failed: {error}")
            
            syllabus.extracted_text = extracted_text
            syllabus.word_count = len(extracted_text.split())
            syllabus.file_size = syllabus.file.size
            syllabus.save()
        
        # Step 2: AI Analysis
        analyzer = ContentAnalyzer()
        analysis_job = analyzer.analyze_syllabus(syllabus_id)
        
        logger.info(f"Successfully processed syllabus {syllabus_id}")
        
        return {
            'syllabus_id': str(syllabus_id),
            'status': 'completed',
            'topics_extracted': analysis_job.total_topics_extracted,
            'processing_time': analysis_job.processing_time_seconds
        }
        
    except Exception as e:
        logger.error(f"Error processing syllabus {syllabus_id}: {str(e)}")
        
        # Update syllabus with error
        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
            syllabus.status = 'error'
            syllabus.error_message = str(e)
            syllabus.save()
        except:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying syllabus processing for {syllabus_id}")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        raise

@shared_task
def reanalyze_syllabus(syllabus_id, analysis_depth='detailed'):
    """
    Task to reanalyze an existing syllabus with different settings
    """
    try:
        analyzer = ContentAnalyzer()
        analysis_job = analyzer.analyze_syllabus(syllabus_id, analysis_depth)
        
        return {
            'syllabus_id': str(syllabus_id),
            'status': 'completed',
            'analysis_depth': analysis_depth,
            'topics_extracted': analysis_job.total_topics_extracted
        }
        
    except Exception as e:
        logger.error(f"Error reanalyzing syllabus {syllabus_id}: {str(e)}")
        raise

@shared_task
def batch_process_syllabi(syllabus_ids, analysis_depth='detailed'):
    """
    Task to process multiple syllabi in batch
    """
    results = []
    analyzer = ContentAnalyzer()
    
    for syllabus_id in syllabus_ids:
        try:
            analysis_job = analyzer.analyze_syllabus(syllabus_id, analysis_depth)
            results.append({
                'syllabus_id': str(syllabus_id),
                'status': 'completed',
                'topics_extracted': analysis_job.total_topics_extracted
            })
        except Exception as e:
            logger.error(f"Error in batch processing syllabus {syllabus_id}: {str(e)}")
            results.append({
                'syllabus_id': str(syllabus_id),
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'processed_count': len(results),
        'results': results
    }
