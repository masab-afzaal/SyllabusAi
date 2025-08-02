# core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Custom exception handler for API responses"""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data
        }
        
        # Log the error
        logger.error(f"API Error: {exc} - Context: {context}")
        
        # Customize error messages based on status code
        if response.status_code == 400:
            custom_response_data['message'] = 'Bad Request - Please check your input'
        elif response.status_code == 401:
            custom_response_data['message'] = 'Unauthorized - Please log in'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Forbidden - You do not have permission'
        elif response.status_code == 404:
            custom_response_data['message'] = 'Not Found - The requested resource does not exist'
        elif response.status_code == 500:
            custom_response_data['message'] = 'Internal Server Error - Please try again later'
        
        response.data = custom_response_data
    
    return response
