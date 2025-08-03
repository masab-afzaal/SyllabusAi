# learning_plan_generator.py - Core service for generating personalized learning plans

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math
from django.utils import timezone
from django.db.models import Avg, Sum
from .models import LearningPlan, LearningSession, Milestone, StudyPreference
from curriculum.models import Topic

class LearningPlanGenerator:
    """
    Advanced learning plan generator that creates personalized, adaptive schedules
    based on student preferences, content analysis, and cognitive science principles.
    """
    
    def __init__(self, user, syllabus):
        self.user = user
        self.syllabus = syllabus
        self.preferences = self._get_or_create_preferences()
        self.topics = Topic.objects.filter(syllabus=syllabus).order_by('order')
        
    def _get_or_create_preferences(self):
        """Get or create default study preferences for user"""
        prefs, created = StudyPreference.objects.get_or_create(
            user=self.user,
            defaults={
                'primary_learning_style': 'visual',
                'difficulty_preference': 'adaptive',
                'preferred_study_time': 'flexible',
                'max_session_duration': 90,
                'break_frequency': 25,
                'spaced_repetition_enabled': True
            }
        )
        return prefs
    
    def generate_learning_plan(self, plan_config: Dict) -> LearningPlan:
        """
        Generate a comprehensive learning plan based on configuration
        
        Args:
            plan_config: Dictionary containing:
                - title: Plan title
                - schedule_type: 'daily', 'weekly', 'monthly'
                - daily_study_hours: Available study hours per day
                - target_completion_date: Optional target date
                - difficulty_progression: 'linear', 'adaptive', 'spiral'
        """
        
        # Create the learning plan
        plan = LearningPlan.objects.create(
            user=self.user,
            syllabus=self.syllabus,
            title=plan_config.get('title', f"Study Plan for {self.syllabus.title}"),
            schedule_type=plan_config.get('schedule_type', 'weekly'),
            difficulty_progression=plan_config.get('difficulty_progression', 'adaptive'),
            daily_study_hours=plan_config.get('daily_study_hours', 2.0),
            total_duration_days=0,  # Will be calculated
            learning_style_weights=self._calculate_learning_style_weights()
        )
        
        # Analyze topics and calculate durations
        topic_analysis = self._analyze_topics()
        
        # Generate optimized schedule
        schedule = self._generate_optimized_schedule(
            topic_analysis, 
            plan_config.get('daily_study_hours', 2.0),
            plan_config.get('target_completion_date')
        )
        
        # Create learning sessions
        self._create_learning_sessions(plan, schedule)
        
        # Create milestones
        self._create_milestones(plan, schedule)
        
        # Update plan duration
        plan.total_duration_days = len(set(session['date'].date() for session in schedule))
        plan.save()
        
        return plan
    
    def _calculate_learning_style_weights(self) -> Dict:
        """Calculate weights for different learning styles"""
        weights = {
            'visual': 0.25,
            'auditory': 0.25,
            'kinesthetic': 0.25,
            'reading': 0.25
        }
        
        # Adjust based on primary learning style
        if self.preferences.primary_learning_style:
            weights[self.preferences.primary_learning_style] = 0.4
            
        # Adjust based on secondary learning style
        if self.preferences.secondary_learning_style:
            weights[self.preferences.secondary_learning_style] = 0.3
            
        # Normalize remaining weights
        remaining_styles = [style for style in weights.keys() 
                          if style not in [self.preferences.primary_learning_style, 
                                         self.preferences.secondary_learning_style]]
        remaining_weight = 1.0 - weights[self.preferences.primary_learning_style or 'visual']
        if self.preferences.secondary_learning_style:
            remaining_weight -= weights[self.preferences.secondary_learning_style]
            
        for style in remaining_styles:
            weights[style] = remaining_weight / len(remaining_styles)
            
        return weights
    
    def _analyze_topics(self) -> List[Dict]:
        """Analyze topics and calculate study requirements"""
        analysis = []
        
        for topic in self.topics:
            # Base study time from AI analysis (from Module 2)
            base_time = topic.estimated_study_time_minutes
            
            # Adjust based on difficulty and user level
            difficulty_multiplier = self._get_difficulty_multiplier(topic.difficulty_score)
            
            # Adjust based on learning style preferences
            style_multiplier = self._get_learning_style_multiplier(topic)
            
            # Calculate total study time
            total_time = base_time * difficulty_multiplier * style_multiplier
            
            # Add buffer time
            buffer_multiplier = 1 + (self.preferences.revision_frequency_days / 100)
            total_time_with_buffer = total_time * buffer_multiplier
            
            analysis.append({
                'topic': topic,
                'base_time_minutes': base_time,
                'adjusted_time_minutes': int(total_time_with_buffer),
                'difficulty_score': topic.difficulty_score,
                'prerequisites': list(topic.prerequisites.all()),
                'cognitive_load': self._calculate_cognitive_load(topic),
                'spaced_repetition_sessions': self._calculate_spaced_repetitions(topic)
            })
            
        return analysis
    
    def _get_difficulty_multiplier(self, difficulty_score: float) -> float:
        """Calculate time multiplier based on difficulty"""
        # Difficulty score is 1-10, multiply time accordingly
        base_multiplier = 0.7 + (difficulty_score / 10) * 0.6  # Range: 0.7 to 1.3
        return base_multiplier
    
    def _get_learning_style_multiplier(self, topic) -> float:
        """Adjust time based on learning style compatibility"""
        # This would ideally use content analysis to determine topic's learning style compatibility
        # For now, use a simplified approach
        style_weights = self.plan.learning_style_weights if hasattr(self, 'plan') else self._calculate_learning_style_weights()
        
        # Assume topics have varying compatibility with learning styles
        # In a real implementation, this would be determined by content analysis
        multiplier = 1.0
        
        if hasattr(topic, 'learning_extension'):
            visual_ratio = topic.learning_extension.visual_content_ratio
            practical_ratio = topic.learning_extension.practical_application_ratio
            
            # Adjust based on content type and user preferences
            if self.preferences.primary_learning_style == 'visual':
                multiplier *= (0.8 + visual_ratio * 0.4)  # 0.8 to 1.2 range
            elif self.preferences.primary_learning_style == 'kinesthetic':
                multiplier *= (0.8 + practical_ratio * 0.4)
        
        return multiplier
    
    def _calculate_cognitive_load(self, topic) -> float:
        """Calculate cognitive load score for topic"""
        base_load = topic.difficulty_score / 10  # Normalize to 0-1
        
        # Adjust based on prerequisites
        prereq_load = len(topic.prerequisites.all()) * 0.1
        
        # Adjust based on content complexity (word count, concept density)
        content_load = min(len(topic.content.split()) / 1000, 1.0) if topic.content else 0
        
        total_load = (base_load + prereq_load + content_load) / 3
        return min(total_load, 1.0)
    
    def _calculate_spaced_repetitions(self, topic) -> List[int]:
        """Calculate spaced repetition intervals (in days)"""
        if not self.preferences.spaced_repetition_enabled:
            return []
            
        # Standard spaced repetition intervals: 1, 3, 7, 14, 30 days
        base_intervals = [1, 3, 7, 14, 30]
        
        # Adjust based on difficulty - harder topics need more repetition
        difficulty_factor = topic.difficulty_score / 10
        adjusted_intervals = []
        
        for interval in base_intervals:
            # More difficult topics get more frequent repetition
            adjusted_interval = max(1, int(interval * (1 - difficulty_factor * 0.3)))
            adjusted_intervals.append(adjusted_interval)
            
        return adjusted_intervals
    
    def _generate_optimized_schedule(self, topic_analysis: List[Dict], 
                                   daily_hours: float, target_date=None) -> List[Dict]:
        """Generate optimized learning schedule"""
        schedule = []
        current_date = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Sort topics based on difficulty preference and prerequisites
        sorted_topics = self._sort_topics_by_strategy(topic_analysis)
        
        # Convert daily hours to minutes
        daily_minutes = int(daily_hours * 60)
        session_duration = self.preferences.max_session_duration
        
        for topic_info in sorted_topics:
            topic = topic_info['topic']
            study_time = topic_info['adjusted_time_minutes']
            
            # Break study time into sessions
            sessions_needed = math.ceil(study_time / session_duration)
            
            for session_num in range(sessions_needed):
                # Calculate session duration
                remaining_time = study_time - (session_num * session_duration)
                current_session_duration = min(session_duration, remaining_time)
                
                # Find next available slot
                session_date = self._find_next_available_slot(
                    current_date, daily_minutes, current_session_duration, schedule
                )
                
                schedule.append({
                    'topic': topic,
                    'date': session_date,
                    'duration_minutes': current_session_duration,
                    'session_type': 'study',
                    'session_number': session_num + 1,
                    'total_sessions': sessions_needed
                })
                
            # Add spaced repetition sessions
            for interval in topic_info['spaced_repetition_sessions']:
                review_date = session_date + timedelta(days=interval)
                review_duration = min(30, current_session_duration // 2)  # Shorter review sessions
                
                schedule.append({
                    'topic': topic,
                    'date': review_date,
                    'duration_minutes': review_duration,
                    'session_type': 'review',
                    'interval_days': interval
                })
        
        return sorted(schedule, key=lambda x: x['date'])
    
    def _sort_topics_by_strategy(self, topic_analysis: List[Dict]) -> List[Dict]:
        """Sort topics based on difficulty preference and prerequisites"""
        
        if self.preferences.difficulty_preference == 'easy_first':
            return sorted(topic_analysis, key=lambda x: x['difficulty_score'])
        elif self.preferences.difficulty_preference == 'hard_first':
            return sorted(topic_analysis, key=lambda x: x['difficulty_score'], reverse=True)
        elif self.preferences.difficulty_preference == 'adaptive':
            # Adaptive strategy: easy topics first, then gradually increase difficulty
            # but respect prerequisites
            return self._adaptive_topic_sorting(topic_analysis)
        else:  # mixed
            return self._mixed_difficulty_sorting(topic_analysis)
    
    def _adaptive_topic_sorting(self, topic_analysis: List[Dict]) -> List[Dict]:
        """Adaptive sorting that balances difficulty progression with prerequisites"""
        sorted_topics = []
        remaining_topics = topic_analysis.copy()
        
        while remaining_topics:
            # Find topics with satisfied prerequisites
            available_topics = [
                topic for topic in remaining_topics
                if all(prereq in [t['topic'] for t in sorted_topics] 
                      for prereq in topic['prerequisites'])
            ]
            
            if not available_topics:
                # If no topics are available (circular dependencies), 
                # pick the one with least prerequisites
                available_topics = [min(remaining_topics, 
                                      key=lambda x: len(x['prerequisites']))]
            
            # Among available topics, pick based on adaptive strategy
            if len(sorted_topics) < 3:  # Start with easier topics
                next_topic = min(available_topics, key=lambda x: x['difficulty_score'])
            else:  # Gradually increase difficulty
                target_difficulty = min(8, 3 + len(sorted_topics) * 0.5)
                next_topic = min(available_topics, 
                               key=lambda x: abs(x['difficulty_score'] - target_difficulty))
            
            sorted_topics.append(next_topic)
            remaining_topics.remove(next_topic)
        
        return sorted_topics
    
    def _mixed_difficulty_sorting(self, topic_analysis: List[Dict]) -> List[Dict]:
        """Mixed difficulty approach - alternate between easy and hard topics"""
        easy_topics = sorted([t for t in topic_analysis if t['difficulty_score'] <= 5],
                           key=lambda x: x['difficulty_score'])
        hard_topics = sorted([t for t in topic_analysis if t['difficulty_score'] > 5],
                           key=lambda x: x['difficulty_score'], reverse=True)
        
        mixed_schedule = []
        max_len = max(len(easy_topics), len(hard_topics))
        
        for i in range(max_len):
            if i < len(easy_topics):
                mixed_schedule.append(easy_topics[i])
            if i < len(hard_topics):
                mixed_schedule.append(hard_topics[i])
        
        return mixed_schedule
    
    def _find_next_available_slot(self, start_date, daily_minutes, 
                                session_duration, existing_schedule) -> datetime:
        """Find next available time slot for a study session"""
        current_date = start_date
        
        while True:
            # Skip weekends if preference is set (can be added to preferences)
            if current_date.weekday() < 5:  # Monday to Friday
                # Calculate time already scheduled for this date
                day_schedule = [s for s in existing_schedule 
                              if s['date'].date() == current_date.date()]
                used_minutes = sum(s['duration_minutes'] for s in day_schedule)
                
                # Check if there's enough time left in the day
                if used_minutes + session_duration <= daily_minutes:
                    # Find the next available time slot
                    if not day_schedule:
                        return current_date
                    else:
                        # Find gap or append to end of day
                        last_session_end = max(
                            s['date'] + timedelta(minutes=s['duration_minutes'])
                            for s in day_schedule
                        )
                        return last_session_end + timedelta(minutes=15)  # 15-min break
            
            # Move to next day
            current_date += timedelta(days=1)
            current_date = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    def _create_learning_sessions(self, plan: LearningPlan, schedule: List[Dict]):
        """Create LearningSession objects from schedule"""
        sessions = []
        
        for session_info in schedule:
            session = LearningSession(
                learning_plan=plan,
                topic=session_info['topic'],
                session_type=session_info['session_type'],
                scheduled_date=session_info['date'],
                estimated_duration_minutes=session_info['duration_minutes'],
                difficulty_level=session_info['topic'].difficulty_score,
                status='pending'
            )
            sessions.append(session)
        
        # Bulk create for efficiency
        LearningSession.objects.bulk_create(sessions)
        
        # Set up prerequisites relationships
        created_sessions = LearningSession.objects.filter(learning_plan=plan)
        self._setup_session_prerequisites(created_sessions)
    
    def _setup_session_prerequisites(self, sessions):
        """Set up prerequisite relationships between sessions"""
        session_map = {session.topic: session for session in sessions}
        
        for session in sessions:
            for prereq_topic in session.topic.prerequisites.all():
                if prereq_topic in session_map:
                    session.prerequisites.add(session_map[prereq_topic])
    
    def _create_milestones(self, plan: LearningPlan, schedule: List[Dict]):
        """Create milestone checkpoints throughout the learning plan"""
        milestones = []
        
        # Group sessions by weeks for weekly milestones
        sessions_by_week = {}
        for session_info in schedule:
            week_start = session_info['date'] - timedelta(days=session_info['date'].weekday())
            week_key = week_start.strftime('%Y-%W')
            
            if week_key not in sessions_by_week:
                sessions_by_week[week_key] = []
            sessions_by_week[week_key].append(session_info)
        
        # Create weekly milestones
        for week_key, week_sessions in sessions_by_week.items():
            week_start = datetime.strptime(week_key + '-1', '%Y-%W-%w')
            week_end = week_start + timedelta(days=6)
            
            topics = list(set(session['topic'] for session in week_sessions))
            
            milestone = Milestone.objects.create(
                learning_plan=plan,
                title=f"Week {len(milestones) + 1} Checkpoint",
                description=f"Complete {len(topics)} topics and review progress",
                milestone_type='weekly',
                target_date=week_end
            )
            milestone.topics.set(topics)
            milestones.append(milestone)
        
        # Create unit completion milestones (every 4 weeks)
        for i in range(0, len(milestones), 4):
            unit_milestones = milestones[i:i+4]
            if len(unit_milestones) >= 2:  # At least 2 weeks to form a unit
                unit_end_date = unit_milestones[-1].target_date
                all_topics = set()
                for milestone in unit_milestones:
                    all_topics.update(milestone.topics.all())
                
                unit_milestone = Milestone.objects.create(
                    learning_plan=plan,
                    title=f"Unit {(i//4) + 1} Assessment",
                    description=f"Comprehensive review of {len(all_topics)} topics",
                    milestone_type='unit',
                    target_date=unit_end_date + timedelta(days=1)
                )
                unit_milestone.topics.set(all_topics)
        
        return milestones