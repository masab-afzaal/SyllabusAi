# utils/plan_optimizer.py - Utility functions for plan optimization

from datetime import datetime, timedelta
from django.utils import timezone
from typing import List, Dict, Tuple
import math

class PlanOptimizer:
    """Utility class for optimizing learning plans"""
    
    @staticmethod
    def calculate_optimal_session_duration(topic_difficulty: float, user_max_duration: int) -> int:
        """Calculate optimal session duration based on topic difficulty and user preferences"""
        base_duration = user_max_duration
        
        # Adjust based on difficulty (harder topics = shorter sessions for better focus)
        if topic_difficulty >= 8:
            optimal_duration = int(base_duration * 0.7)  # 70% of max for very hard topics
        elif topic_difficulty >= 6:
            optimal_duration = int(base_duration * 0.85)  # 85% of max for hard topics
        else:
            optimal_duration = base_duration  # Full duration for easier topics
        
        # Ensure minimum 30 minutes
        return max(30, optimal_duration)
    
    @staticmethod
    def calculate_cognitive_load_distribution(sessions: List[Dict], daily_limit_hours: float) -> List[Dict]:
        """Distribute sessions to manage cognitive load throughout the day"""
        daily_limit_minutes = daily_limit_hours * 60
        
        # Sort sessions by difficulty (easier first)
        sessions.sort(key=lambda x: x.get('difficulty_score', 5))
        
        distributed_sessions = []
        current_day_load = 0
        current_date = None
        
        for session in sessions:
            session_duration = session['duration_minutes']
            session_difficulty = session.get('difficulty_score', 5)
            
            # Calculate cognitive load points (harder topics consume more cognitive resources)
            cognitive_points = session_duration * (session_difficulty / 10)
            
            # If this is a new day or current day is full
            if (current_date is None or 
                current_date != session['date'].date() or 
                current_day_load + cognitive_points > daily_limit_minutes):
                
                current_date = session['date'].date()
                current_day_load = cognitive_points
            else:
                current_day_load += cognitive_points
            
            session['cognitive_load'] = cognitive_points
            session['daily_cognitive_load'] = current_day_load
            distributed_sessions.append(session)
        
        return distributed_sessions
    
    @staticmethod
    def optimize_break_intervals(sessions: List[Dict], break_preferences: Dict) -> List[Dict]:
        """Add optimal break intervals between sessions"""
        if not sessions:
            return sessions
        
        break_frequency = break_preferences.get('break_frequency', 25)  # Pomodoro default
        break_duration = break_preferences.get('break_duration', 5)
        long_break_duration = break_preferences.get('long_break_duration', 30)
        
        optimized_sessions = []
        session_count = 0
        
        for i, session in enumerate(sessions):
            optimized_sessions.append(session)
            session_count += 1
            
            # Add break after session (except for the last one)
            if i < len(sessions) - 1:
                next_session = sessions[i + 1]
                
                # Determine break duration
                if session_count % 4 == 0:  # Long break every 4 sessions
                    break_minutes = long_break_duration
                else:
                    break_minutes = break_duration
                
                # Add break to next session start time
                original_start = next_session['date']
                next_session['date'] = original_start + timedelta(minutes=break_minutes)
                next_session['break_before'] = break_minutes
        
        return optimized_sessions
    
    @staticmethod
    def analyze_plan_efficiency(plan) -> Dict:
        """Analyze learning plan efficiency and provide recommendations"""
        sessions = plan.sessions.all()
        
        if not sessions:
            return {'error': 'No sessions found in plan'}
        
        # Calculate various metrics
        total_duration = sum(s.estimated_duration_minutes for s in sessions)
        avg_session_duration = total_duration / sessions.count()
        
        # Difficulty distribution
        difficulties = [s.difficulty_level for s in sessions]
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        # Session distribution by day
        sessions_by_day = {}
        for session in sessions:
            day = session.scheduled_date.date()
            if day not in sessions_by_day:
                sessions_by_day[day] = []
            sessions_by_day[day].append(session)
        
        daily_loads = [
            sum(s.estimated_duration_minutes for s in day_sessions)
            for day_sessions in sessions_by_day.values()
        ]
        
        avg_daily_load = sum(daily_loads) / len(daily_loads) if daily_loads else 0
        max_daily_load = max(daily_loads) if daily_loads else 0
        min_daily_load = min(daily_loads) if daily_loads else 0
        
        # Generate recommendations
        recommendations = []
        
        if max_daily_load > plan.daily_study_hours * 60 * 1.2:  # 20% over limit
            recommendations.append("Some days are overloaded. Consider redistributing sessions.")
        
        if avg_session_duration > 120:  # Over 2 hours
            recommendations.append("Sessions are quite long. Consider breaking them into smaller chunks.")
        
        if avg_difficulty > 7:
            recommendations.append("Plan has many difficult topics. Add more review sessions.")
        
        return {
            'total_sessions': sessions.count(),
            'total_duration_hours': round(total_duration / 60, 1),
            'avg_session_duration_minutes': round(avg_session_duration, 1),
            'avg_difficulty': round(avg_difficulty, 1),
            'total_days': len(sessions_by_day),
            'avg_daily_load_minutes': round(avg_daily_load, 1),
            'max_daily_load_minutes': max_daily_load,
            'min_daily_load_minutes': min_daily_load,
            'load_balance_ratio': round(min_daily_load / max_daily_load, 2) if max_daily_load > 0 else 0,
            'recommendations': recommendations
        }
