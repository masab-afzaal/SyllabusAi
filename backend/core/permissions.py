# core/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user

class IsSyllabusOwner(permissions.BasePermission):
    """
    Custom permission for syllabus-related objects
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a syllabus attribute
        if hasattr(obj, 'syllabus'):
            return obj.syllabus.user == request.user
        # Check if the object has a learning_plan attribute
        elif hasattr(obj, 'learning_plan'):
            return obj.learning_plan.user == request.user
        # Default to checking user attribute
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
