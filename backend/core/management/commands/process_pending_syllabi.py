# core/management/commands/process_pending_syllabi.py
from django.core.management.base import BaseCommand
from curriculum.models import Syllabus
from curriculum.tasks import process_syllabus

class Command(BaseCommand):
    help = 'Process all pending syllabi'
    
    def handle(self, *args, **options):
        pending_syllabi = Syllabus.objects.filter(status='uploaded')
        
        self.stdout.write(f'Found {pending_syllabi.count()} pending syllabi')
        
        for syllabus in pending_syllabi:
            try:
                process_syllabus.delay(syllabus.id)
                self.stdout.write(f'Queued processing for: {syllabus.title}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error queuing {syllabus.title}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS('All pending syllabi queued for processing'))
