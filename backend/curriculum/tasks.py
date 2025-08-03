# curriculum/tasks.py
from celery import shared_task
from analysis.tasks import process_syllabus as analysis_process_syllabus

# Re-export the task from analysis app for backward compatibility
@shared_task(bind=True, max_retries=3)
def process_syllabus(self, syllabus_id):
    """
    Wrapper task for backward compatibility
    Delegates to the main analysis task
    """
    return analysis_process_syllabus(syllabus_id)