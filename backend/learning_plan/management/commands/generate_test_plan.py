# management/commands/generate_test_plan.py - Test command for learning plan generation

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from syllabus_app.models import Syllabus, Topic, LearningPlan, StudyPreference
from syllabus_app.learning_plan_generator import LearningPlanGenerator
import random

class Command(BaseCommand):
    help = 'Generate a test learning plan for development and testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=int,
            help='User ID to generate plan for',
        )
        parser.add_argument(
            '--syllabus_id',
            type=int,
            help='Syllabus ID to generate plan from',
        )
        parser.add_argument(
            '--daily_hours',
            type=float,
            default=2.0,
            help='Daily study hours (default: 2.0)',
        )
        parser.add_argument(
            '--schedule_type',
            type=str,
            default='weekly',
            choices=['daily', 'weekly', 'monthly'],
            help='Schedule type (default: weekly)',
        )
        parser.add_argument(
            '--create_sample_data',
            action='store_true',
            help='Create sample syllabus and topics if none exist',
        )
    
    def handle(self, *args, **options):
        try:
            # Get or create user
            if options['user_id']:
                user = User.objects.get(id=options['user_id'])
            else:
                user, created = User.objects.get_or_create(
                    username='testuser',
                    defaults={
                        'email': 'test@example.com',
                        'first_name': 'Test',
                        'last_name': 'User'
                    }
                )
                if created:
                    user.set_password('testpass123')
                    user.save()
                    self.stdout.write(f'Created test user: {user.username}')
            
            # Create sample data if requested
            if options['create_sample_data']:
                syllabus = self.create_sample_syllabus(user)
            else:
                # Get existing syllabus
                if options['syllabus_id']:
                    syllabus = Syllabus.objects.get(id=options['syllabus_id'], user=user)
                else:
                    syllabus = Syllabus.objects.filter(user=user).first()
                    if not syllabus:
                        raise CommandError('No syllabus found. Use --create_sample_data to create one.')
            
            # Create or update study preferences
            preferences, created = StudyPreference.objects.get_or_create(
                user=user,
                defaults={
                    'primary_learning_style': 'visual',
                    'difficulty_preference': 'adaptive',
                    'preferred_study_time': 'morning',
                    'max_session_duration': 90,
                    'spaced_repetition_enabled': True
                }
            )
            
            if created:
                self.stdout.write(f'Created study preferences for {user.username}')
            
            # Generate learning plan
            plan_config = {
                'title': f'Test Learning Plan - {syllabus.title}',
                'schedule_type': options['schedule_type'],
                'daily_study_hours': options['daily_hours'],
                'difficulty_progression': 'adaptive'
            }
            
            generator = LearningPlanGenerator(user, syllabus)
            plan = generator.generate_learning_plan(plan_config)
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated learning plan: {plan.title}')
            )
            
            # Display plan statistics
            total_sessions = plan.sessions.count()
            total_duration = sum(s.estimated_duration_minutes for s in plan.sessions.all())
            
            self.stdout.write(f'Plan Details:')
            self.stdout.write(f'  - Total Sessions: {total_sessions}')
            self.stdout.write(f'  - Total Duration: {total_duration//60}h {total_duration%60}m')
            self.stdout.write(f'  - Duration: {plan.total_duration_days} days')
            self.stdout.write(f'  - Milestones: {plan.milestones.count()}')
            
            # Display first few sessions
            upcoming_sessions = plan.sessions.all()[:5]
            self.stdout.write(f'\nFirst 5 Sessions:')
            for i, session in enumerate(upcoming_sessions, 1):
                self.stdout.write(
                    f'  {i}. {session.topic.title} - {session.scheduled_date.strftime("%Y-%m-%d %H:%M")} '
                    f'({session.estimated_duration_minutes}min)'
                )
            
        except Exception as e:
            raise CommandError(f'Error generating learning plan: {str(e)}')
    
    def create_sample_syllabus(self, user):
        """Create a sample syllabus with topics for testing"""
        syllabus = Syllabus.objects.create(
            user=user,
            title='Sample Data Science Course',
            description='A comprehensive data science course covering statistics, machine learning, and Python programming.',
            subject='Computer Science',
            grade_level='undergraduate'
        )
        
        # Sample topics with varying difficulty
        sample_topics = [
            {
                'title': 'Introduction to Python',
                'content': 'Basic Python syntax, variables, data types, and control structures. Understanding the fundamentals of programming in Python.',
                'difficulty_score': 3,
                'estimated_study_time_minutes': 120,
                'order': 1
            },
            {
                'title': 'Data Structures and Algorithms',
                'content': 'Lists, dictionaries, sets, and tuples. Basic algorithms for searching and sorting. Time complexity analysis.',
                'difficulty_score': 6,
                'estimated_study_time_minutes': 180,
                'order': 2
            },
            {
                'title': 'NumPy and Pandas',
                'content': 'Data manipulation with NumPy arrays and Pandas DataFrames. Data cleaning and preprocessing techniques.',
                'difficulty_score': 5,
                'estimated_study_time_minutes': 150,
                'order': 3
            },
            {
                'title': 'Data Visualization',
                'content': 'Creating charts and graphs with Matplotlib and Seaborn. Understanding principles of effective data visualization.',
                'difficulty_score': 4,
                'estimated_study_time_minutes': 100,
                'order': 4
            },
            {
                'title': 'Statistics Fundamentals',
                'content': 'Descriptive statistics, probability distributions, hypothesis testing, and confidence intervals.',
                'difficulty_score': 7,
                'estimated_study_time_minutes': 200,
                'order': 5
            },
            {
                'title': 'Machine Learning Basics',
                'content': 'Introduction to supervised and unsupervised learning. Linear regression and classification algorithms.',
                'difficulty_score': 8,
                'estimated_study_time_minutes': 240,
                'order': 6
            },
            {
                'title': 'Model Evaluation',
                'content': 'Cross-validation, metrics for classification and regression, overfitting and underfitting.',
                'difficulty_score': 7,
                'estimated_study_time_minutes': 160,
                'order': 7
            },
            {
                'title': 'Deep Learning Introduction',
                'content': 'Neural networks, backpropagation, and introduction to TensorFlow/Keras.',
                'difficulty_score': 9,
                'estimated_study_time_minutes': 300,
                'order': 8
            }
        ]
        
        created_topics = []
        for topic_data in sample_topics:
            topic = Topic.objects.create(
                syllabus=syllabus,
                **topic_data
            )
            created_topics.append(topic)
        
        # Set up some prerequisites
        created_topics[1].prerequisites.add(created_topics[0])  # Data Structures needs Python
        created_topics[2].prerequisites.add(created_topics[0])  # NumPy/Pandas needs Python
        created_topics[3].prerequisites.add(created_topics[2])  # Visualization needs Pandas
        created_topics[5].prerequisites.add(created_topics[2], created_topics[4])  # ML needs Pandas and Stats
        created_topics[6].prerequisites.add(created_topics[5])  # Model Evaluation needs ML Basics
        created_topics[7].prerequisites.add(created_topics[5])  # Deep Learning needs ML Basics
        
        self.stdout.write(f'Created sample syllabus with {len(created_topics)} topics')
        return syllabus

