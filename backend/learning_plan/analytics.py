# analytics.py - Learning analytics and insights

from django.db.models import Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from typing import Dict, List
import json

class LearningAnalytics:
    """Analytics class for generating learning insights and reports"""
    
    def __init__(self, user):
        self.user = user
    
    def get_learning_insights(self, plan_id=None) -> Dict:
        """Generate comprehensive learning insights for user"""
        from .models import LearningPlan, LearningSession
        
        # Filter by specific plan or all user's plans
        if plan_id:
            plans = LearningPlan.objects.filter(id=plan_id, user=self.user)
        else:
            plans = LearningPlan.objects.filter(user=self.user)
        
        sessions = LearningSession.objects.filter(learning_plan__in=plans)
        
        insights = {
            'overview': self._get_overview_stats(plans, sessions),
            'performance': self._get_performance_stats(sessions),
            'time_analysis': self._get_time_analysis(sessions),
            'difficulty_analysis': self._get_difficulty_analysis(sessions),
            'learning_patterns': self._get_learning_patterns(sessions),
            'recommendations': self._generate_recommendations(sessions)
        }
        
        return insights
    
    def _get_overview_stats(self, plans, sessions) -> Dict:
        """Get overview statistics"""
        total_plans = plans.count()
        active_plans = plans.filter(is_active=True).count()
        completed_plans = plans.filter(completion_percentage=100).count()
        
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        pending_sessions = sessions.filter(status='pending').count()
        
        total_study_time = sessions.filter(
            status='completed',
            actual_duration_minutes__isnull=False
        ).aggregate(total=Count('actual_duration_minutes'))['total'] or 0
        
        return {
            'total_plans': total_plans,
            'active_plans': active_plans,
            'completed_plans': completed_plans,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'pending_sessions': pending_sessions,
            'completion_rate': round((completed_sessions / total_sessions * 100), 1) if total_sessions > 0 else 0,
            'total_study_hours': round(total_study_time / 60, 1)
        }
    
    def _get_performance_stats(self, sessions) -> Dict:
        """Analyze learning performance"""
        completed_sessions = sessions.filter(status='completed')
        
        if not completed_sessions.exists():
            return {'message': 'No completed sessions for analysis'}
        
        avg_completion_score = completed_sessions.aggregate(
            avg_score=Avg('completion_score')
        )['avg_score'] or 0
        
        avg_confidence = completed_sessions.aggregate(
            avg_confidence=Avg('confidence_level')
        )['avg_confidence'] or 0
        
        # Performance by difficulty level
        performance_by_difficulty = {}
        for difficulty in range(1, 11):
            difficulty_sessions = completed_sessions.filter(difficulty_level=difficulty)
            if difficulty_sessions.exists():
                avg_score = difficulty_sessions.aggregate(Avg('completion_score'))['completion_score__avg']
                performance_by_difficulty[str(difficulty)] = round(avg_score or 0, 1)
        
        # Recent performance trend (last 7 days)
        recent_date = timezone.now() - timedelta(days=7)
        recent_sessions = completed_sessions.filter(updated_at__gte=recent_date)
        recent_avg_score = recent_sessions.aggregate(Avg('completion_score'))['completion_score__avg'] or 0
        
        return {
            'avg_completion_score': round(avg_completion_score, 1),
            'avg_confidence_level': round(avg_confidence, 1),
            'performance_by_difficulty': performance_by_difficulty,
            'recent_performance': round(recent_avg_score, 1),
            'total_completed_sessions': completed_sessions.count()
        }
    
    def _get_time_analysis(self, sessions) -> Dict:
        """Analyze time usage patterns"""
        completed_sessions = sessions.filter(
            status='completed',
            actual_duration_minutes__isnull=False
        )
        
        if not completed_sessions.exists():
            return {'message': 'No time data available'}
        
        # Time efficiency (actual vs estimated)
        time_efficiency = completed_sessions.aggregate(
            avg_actual=Avg('actual_duration_minutes'),
            avg_estimated=Avg('estimated_duration_minutes')
        )
        
        efficiency_ratio = 0
        if time_efficiency['avg_estimated'] and time_efficiency['avg_estimated'] > 0:
            efficiency_ratio = time_efficiency['avg_actual'] / time_efficiency['avg_estimated']
        
        # Study time by day of week
        study_by_weekday = {}
        for session in completed_sessions:
            weekday = session.updated_at.strftime('%A')
            if weekday not in study_by_weekday:
                study_by_weekday[weekday] = 0
            study_by_weekday[weekday] += session.actual_duration_minutes
        
        # Study time by hour of day
        study_by_hour = {}
        for session in completed_sessions:
            hour = session.updated_at.hour
            if hour not in study_by_hour:
                study_by_hour[hour] = 0
            study_by_hour[hour] += session.actual_duration_minutes
        
        return {
            'avg_actual_duration': round(time_efficiency['avg_actual'] or 0, 1),
            'avg_estimated_duration': round(time_efficiency['avg_estimated'] or 0, 1),
            'time_efficiency_ratio': round(efficiency_ratio, 2),
            'study_by_weekday': study_by_weekday,
            'peak_study_hour': max(study_by_hour, key=study_by_hour.get) if study_by_hour else None,
            'total_study_minutes': sum(study_by_hour.values()) if study_by_hour else 0
        }
    
    def _get_difficulty_analysis(self, sessions) -> Dict:
        """Analyze performance across difficulty levels"""
        completed_sessions = sessions.filter(status='completed')
        
        difficulty_stats = {}
        for difficulty in range(1, 11):
            difficulty_sessions = completed_sessions.filter(difficulty_level=difficulty)
            if difficulty_sessions.exists():
                stats = difficulty_sessions.aggregate(
                    count=Count('id'),
                    avg_score=Avg('completion_score'),
                    avg_confidence=Avg('confidence_level'),
                    avg_duration=Avg('actual_duration_minutes')
                )
                difficulty_stats[str(difficulty)] = {
                    'session_count': stats['count'],
                    'avg_completion_score': round(stats['avg_score'] or 0, 1),
                    'avg_confidence': round(stats['avg_confidence'] or 0, 1),
                    'avg_duration_minutes': round(stats['avg_duration'] or 0, 1)
                }
        
        # Find strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for level, stats in difficulty_stats.items():
            if stats['avg_completion_score'] >= 80:
                strengths.append(f"Difficulty Level {level}")
            elif stats['avg_completion_score'] < 60:
                weaknesses.append(f"Difficulty Level {level}")
        
        return {
            'difficulty_breakdown': difficulty_stats,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'avg_difficulty_handled': round(
                sum(int(k) * v['session_count'] for k, v in difficulty_stats.items()) /
                sum(v['session_count'] for v in difficulty_stats.values()), 1
            ) if difficulty_stats else 0
        }
    
    def _get_learning_patterns(self, sessions) -> Dict:
        """Identify learning patterns and habits"""
        completed_sessions = sessions.filter(status='completed').order_by('updated_at')
        
        if completed_sessions.count() < 5:
            return {'message': 'Need more completed sessions to identify patterns'}
        
        # Study streak analysis
        current_streak = self._calculate_current_streak(completed_sessions)
        longest_streak = self._calculate_longest_streak(completed_sessions)
        
        # Session type preferences
        session_types = completed_sessions.values('session_type').annotate(
            count=Count('id'),
            avg_score=Avg('completion_score')
        )
        
        # Most productive time analysis
        hourly_performance = {}
        for session in completed_sessions:
            hour = session.updated_at.hour
            if hour not in hourly_performance:
                hourly_performance[hour] = {'scores': [], 'count': 0}
            
            if session.completion_score:
                hourly_performance[hour]['scores'].append(session.completion_score)
                hourly_performance[hour]['count'] += 1
        
        # Calculate average scores by hour
        best_hours = []
        for hour, data in hourly_performance.items():
            if data['count'] >= 3:  # At least 3 sessions for reliability
                avg_score = sum(data['scores']) / len(data['scores'])
                best_hours.append((hour, avg_score))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'current_streak_days': current_streak,
            'longest_streak_days': longest_streak,
            'session_type_performance': list(session_types),
            'best_performance_hours': [hour for hour, score in best_hours[:3]],
            'total_active_days': len(set(s.updated_at.date() for s in completed_sessions))
        }
    
    def _calculate_current_streak(self, sessions) -> int:
        """Calculate current consecutive study days"""
        if not sessions:
            return 0
        
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        # Get unique study dates
        study_dates = set(s.updated_at.date() for s in sessions)
        
        while current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    def _calculate_longest_streak(self, sessions) -> int:
        """Calculate longest consecutive study streak"""
        if not sessions:
            return 0
        
        study_dates = sorted(set(s.updated_at.date() for s in sessions))
        
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(study_dates)):
            if study_dates[i] - study_dates[i-1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return longest_streak
    
    def _generate_recommendations(self, sessions) -> List[str]:
        """Generate personalized recommendations based on learning data"""
        recommendations = []
        
        completed_sessions = sessions.filter(status='completed')
        if completed_sessions.count() < 3:
            recommendations.append("Complete more sessions to receive personalized recommendations.")
            return recommendations
        
        # Performance-based recommendations
        avg_score = completed_sessions.aggregate(Avg('completion_score'))['completion_score__avg'] or 0
        
        if avg_score < 70:
            recommendations.append("Consider reviewing topics more thoroughly before moving to new material.")
        elif avg_score > 90:
            recommendations.append("You're performing excellently! Consider tackling more challenging topics.")
        
        # Time-based recommendations
        avg_actual = completed_sessions.aggregate(Avg('actual_duration_minutes'))['actual_duration_minutes__avg'] or 0
        avg_estimated = completed_sessions.aggregate(Avg('estimated_duration_minutes'))['estimated_duration_minutes__avg'] or 0
        
        if avg_actual and avg_estimated and avg_actual > avg_estimated * 1.3:
            recommendations.append("Sessions are taking longer than expected. Consider breaking them into smaller chunks.")
        
        # Streak recommendations
        recent_sessions = completed_sessions.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if recent_sessions.count() < 3:
            recommendations.append("Try to maintain more consistent study habits for better retention.")
        
        # Difficulty recommendations
        difficulty_scores = [s.difficulty_level for s in completed_sessions.filter(completion_score__gte=80)]
        if difficulty_scores:
            avg_mastered_difficulty = sum(difficulty_scores) / len(difficulty_scores)
            if avg_mastered_difficulty < 6:
                recommendations.append("You're ready to tackle more challenging topics!")
        
        return recommendations[:5]  # Limit to top 5 recommendations
