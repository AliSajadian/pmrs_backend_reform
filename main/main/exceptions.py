"""
Custom exception handler for Django REST Framework.
Handles both DRF exceptions and Django exceptions.
"""
import logging
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db import DatabaseError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

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
            "message": response.data.get('detail', response.data)
        }
        response.data = custom_response_data
        return response

    # Handle Django exceptions that DRF doesn't handle
    if isinstance(exc, ObjectDoesNotExist):
        logger.warning("Object not found: %s", str(exc))
        return Response(
            {"status": "error", "message": "Requested resource not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if isinstance(exc, DjangoValidationError):
        logger.info("Validation error: %s", str(exc))
        error_detail = getattr(exc, 'message_dict', str(exc))
        return Response(
            {"status": "error", "message": "Validation failed", "errors": error_detail},
            status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, DatabaseError):
        logger.error("Database error: %s", str(exc), exc_info=True)
        return Response(
            {"status": "error", "message": "A database error occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if isinstance(exc, KeyError):
        logger.warning("Missing key: %s", str(exc))
        return Response(
            {"status": "error", "message": f"Missing required field: {str(exc)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Unhandled exception
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)
    return Response(
        {"status": "error", "message": "An unexpected error occurred"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
