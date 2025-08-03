# core/validators.py
from django.core.exceptions import ValidationError
import os

def validate_file_size(file):
    """Validate uploaded file size (max 50MB)"""
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size > max_size:
        raise ValidationError(f'File size cannot exceed 50MB. Current size: {file.size / (1024*1024):.1f}MB')

def validate_file_extension(file):
    """Validate file extension"""
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'File type {ext} is not supported. Allowed types: {", ".join(allowed_extensions)}')
