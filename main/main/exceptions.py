"""
Custom exception handler for Django REST Framework.
Handles both DRF exceptions and Django exceptions.
"""
import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError, \
    PermissionDenied as DjangoPermissionDenied
from django.db import DatabaseError
from django.http import Http404
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAuthenticated
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Handles both DRF exceptions and Django exceptions.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF handled it, customize the format
        custom_response_data = {
            "status": "error",
            'message': get_error_message(exc),
            'errors': response.data 
                if isinstance(response.data, dict)
                else {'detail': response.data}
        }
        response.data = custom_response_data
        return response

    # Define exception mappings
    exception_handlers = [
        (Http404, _handle_http404),
        (ObjectDoesNotExist, _handle_object_not_found),
        (DjangoPermissionDenied, _handle_permission_denied),
        (DjangoValidationError, _handle_validation_error),
        (DatabaseError, _handle_database_error),
        (KeyError, _handle_key_error),
    ]

    # Find and execute appropriate handler
    for exception_type, handler in exception_handlers:
        if isinstance(exc, exception_type):
            error_data = handler(exc)
            return Response(error_data['response'], status=error_data['status'])

    # Default: unhandled exception
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return Response(
        {'status': 'error', 'message': 'An unexpected error occurred'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _handle_http404(exc):
    logger.warning("404 error: %s", str(exc))
    return {
        'response': {'status': 'error', 'message': 'Resource not found'},
        'status': status.HTTP_404_NOT_FOUND
    }


def _handle_object_not_found(exc):
    logger.warning("Object not found: %s", str(exc))
    return {
        'response': {'status': 'error', 'message': 'Requested resource not found'},
        'status': status.HTTP_404_NOT_FOUND
    }


def _handle_permission_denied(exc):
    logger.warning("Permission denied: %s", str(exc))
    return {
        'response': {
            'status': 'error',
            'message': 'You do not have permission to perform this action'
        },
        'status': status.HTTP_403_FORBIDDEN
    }


def _handle_validation_error(exc):
    logger.info("Validation error: %s", str(exc))
    error_detail = getattr(exc, 'message_dict', str(exc))
    return {
        'response': {
            'status': 'error',
            'message': 'Validation failed',
            'errors': error_detail
        },
        'status': status.HTTP_400_BAD_REQUEST
    }


def _handle_database_error(exc):
    logger.error("Database error: %s", str(exc), exc_info=True)
    return {
        'response': {'status': 'error', 'message': 'A database error occurred'},
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR
    }


def _handle_key_error(exc):
    logger.warning("Missing key: %s", str(exc))
    return {
        'response': {
            'status': 'error',
            'message': f"Missing required field: {str(exc)}"
        },
        'status': status.HTTP_400_BAD_REQUEST
    }
def get_error_message(exc):
    """Extract appropriate error message from exception."""
    message = 'An error occurred'
    if isinstance(exc, ValidationError):
        message = 'Validation error'
    elif isinstance(exc, AuthenticationFailed):
        message = 'Authentication failed'
    elif isinstance(exc, NotAuthenticated):
        message = 'Authentication credentials were not provided'
    elif isinstance(exc, PermissionDenied):
        message = 'Permission denied'
    elif isinstance(exc, NotFound):
        message = 'Resource not found'
    elif isinstance(exc, MethodNotAllowed):
        message = 'Method not allowed'
    else:
        message = 'An error occurred'
    return message
