# curriculum/views.py (Updated to fix import)
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Syllabus, Topic
from .serializers import (
    SyllabusListSerializer, SyllabusDetailSerializer, SyllabusCreateSerializer,
    TopicSerializer
)
from analysis.tasks import process_syllabus  # Import from analysis app

class SyllabusListCreateView(generics.ListCreateAPIView):
    """List user's syllabi or create new one"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SyllabusCreateSerializer
        return SyllabusListSerializer
    
    def get_queryset(self):
        return Syllabus.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        syllabus = serializer.save()
        # Trigger async processing
        process_syllabus.delay(str(syllabus.id))
        return syllabus

class SyllabusDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific syllabus"""
    serializer_class = SyllabusDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Syllabus.objects.filter(user=self.request.user)

class TopicListView(generics.ListAPIView):
    """List topics for a specific syllabus"""
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        syllabus_id = self.kwargs['syllabus_id']
        syllabus = get_object_or_404(Syllabus, id=syllabus_id, user=self.request.user)
        return Topic.objects.filter(syllabus=syllabus)

class TopicDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a specific topic"""
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Topic.objects.filter(syllabus__user=self.request.user)
