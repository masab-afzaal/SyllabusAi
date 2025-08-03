# urls.py - URL patterns for Module 3

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LearningPlanViewSet, LearningSessionViewSet, 
    MilestoneViewSet, StudyPreferenceViewSet
)

router = DefaultRouter()
router.register(r'learning-plans', LearningPlanViewSet, basename='learningplan')
router.register(r'learning-sessions', LearningSessionViewSet, basename='learningsession')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'study-preferences', StudyPreferenceViewSet, basename='studypreference')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]