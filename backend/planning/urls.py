# planning/urls.py
from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    # Learning Plan endpoints
    path('plans/', views.LearningPlanListView.as_view(), name='learning-plan-list'),
    path('syllabi/<uuid:syllabus_id>/create-plan/', views.create_learning_plan, name='create-learning-plan'),
    path('plans/<uuid:pk>/', views.LearningPlanDetailView.as_view(), name='learning-plan-detail'),
    
    # Schedule Block endpoints
    path('plans/<uuid:plan_id>/schedule/', views.ScheduleBlockListView.as_view(), name='schedule-block-list'),
    path('schedule/<uuid:pk>/', views.ScheduleBlockDetailView.as_view(), name='schedule-block-detail'),
    
    # Study Session endpoints
    path('schedule/<uuid:block_id>/start-session/', views.start_study_session, name='start-study-session'),
    path('sessions/<uuid:session_id>/end/', views.end_study_session, name='end-study-session'),
]
