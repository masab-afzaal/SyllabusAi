# core/management/commands/cleanup_old_files.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from curriculum.models import Syllabus
import os

class Command(BaseCommand):
    help = 'Clean up old syllabus files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete files older than N days'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=options['days'])
        old_syllabi = Syllabus.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['error', 'completed']
        )
        
        total_size = 0
        files_deleted = 0
        
        for syllabus in old_syllabi:
            if syllabus.file and os.path.exists(syllabus.file.path):
                file_size = os.path.getsize(syllabus.file.path)
                total_size += file_size
                
                if not options['dry_run']:
                    try:
                        os.remove(syllabus.file.path)
                        syllabus.file = None
                        syllabus.save()
                        files_deleted += 1
                        self.stdout.write(f'Deleted: {syllabus.title}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error deleting {syllabus.title}: {str(e)}')
                        )
                else:
                    self.stdout.write(f'Would delete: {syllabus.title} ({file_size} bytes)')
                    files_deleted += 1
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {files_deleted} files, '
                    f'freeing {total_size / (1024*1024):.2f} MB'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {files_deleted} files, '
                    f'freed {total_size / (1024*1024):.2f} MB'
                )
            )
