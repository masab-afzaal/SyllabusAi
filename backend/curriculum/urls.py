# curriculum/urls.py
from django.urls import path
from . import views

app_name = 'curriculum'

urlpatterns = [
    # Syllabus endpoints
    path('syllabi/', views.SyllabusListCreateView.as_view(), name='syllabus-list-create'),
    path('syllabi/<uuid:pk>/', views.SyllabusDetailView.as_view(), name='syllabus-detail'),
    
    # Topic endpoints
    path('syllabi/<uuid:syllabus_id>/topics/', views.TopicListView.as_view(), name='topic-list'),
    path('topics/<uuid:pk>/', views.TopicDetailView.as_view(), name='topic-detail'),
]