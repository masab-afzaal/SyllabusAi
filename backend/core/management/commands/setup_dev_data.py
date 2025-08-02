from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from curriculum.models import Syllabus, Topic
from planning.models import LearningPlan
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up development data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=3,
            help='Number of test users to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up development data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        
        # Create test users
        test_users = []
        for i in range(options['users']):
            username = f'testuser{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'test{i+1}@example.com',
                    password='testpass123',
                    first_name=f'Test{i+1}',
                    last_name='User',
                    age=20 + i,
                    grade_level='college',
                    learning_style='mixed',
                    daily_study_hours=2.0 + i
                )
                test_users.append(user)
                self.stdout.write(f'Created test user: {username}/testpass123')
        
        # Create sample syllabi
        sample_topics = [
            {
                'title': 'Introduction to Data Structures',
                'description': 'Basic concepts of arrays, linked lists, and stacks',
                'difficulty_level': 3,
                'estimated_hours': 8.0,
                'topic_type': 'concept'
            },
            {
                'title': 'Algorithm Analysis',
                'description': 'Big O notation and complexity analysis',
                'difficulty_level': 5,
                'estimated_hours': 12.0,
                'topic_type': 'theory'
            },
            {
                'title': 'Sorting Algorithms',
                'description': 'Implementation of various sorting techniques',
                'difficulty_level': 4,
                'estimated_hours': 10.0,
                'topic_type': 'skill'
            }
        ]
        
        for user in test_users:
            if not Syllabus.objects.filter(user=user).exists():
                syllabus = Syllabus.objects.create(
                    user=user,
                    title=f'Computer Science Fundamentals - {user.username}',
                    description='Complete course on computer science fundamentals',
                    subject='computer_science',
                    status='analyzed',
                    word_count=5000,
                    extracted_text='Sample syllabus content for CS fundamentals course...'
                )
                
                # Create topics for the syllabus
                for idx, topic_data in enumerate(sample_topics):
                    Topic.objects.create(
                        syllabus=syllabus,
                        order_index=idx,
                        **topic_data
                    )
                
                self.stdout.write(f'Created sample syllabus for {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Development data setup complete!'))
