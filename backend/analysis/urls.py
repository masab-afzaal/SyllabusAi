# analysis/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # Analysis Job endpoints
    path('jobs/', views.AnalysisJobListView.as_view(), name='analysis-job-list'),
    path('jobs/<uuid:pk>/', views.AnalysisJobDetailView.as_view(), name='analysis-job-detail'),
    path('jobs/<uuid:analysis_job_id>/progress/', views.analysis_progress_view, name='analysis-progress'),
    
    # Reanalysis endpoints
    path('syllabi/<uuid:syllabus_id>/reanalyze/', views.reanalyze_syllabus_view, name='reanalyze-syllabus'),
    path('batch-analyze/', views.batch_analyze_view, name='batch-analyze'),
    
    # Topic Analysis endpoints
    path('topic-analysis/<uuid:pk>/', views.TopicAnalysisDetailView.as_view(), name='topic-analysis-detail'),
    path('topics/<uuid:topic_id>/update-difficulty/', views.update_topic_difficulty_view, name='update-topic-difficulty'),
    
    # Insights and Recommendations
    path('insights/', views.analysis_insights_view, name='analysis-insights'),
    path('syllabi/<uuid:syllabus_id>/recommendations/', views.topic_recommendations_view, name='topic-recommendations'),
]
