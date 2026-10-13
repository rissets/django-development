from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def domain_exception_handler(error, context):
    if isinstance(error, DjangoValidationError):
        data = error.message_dict if hasattr(error, "message_dict") else {"detail": error.messages}
        return Response(data, status=400)
    return exception_handler(error, context)
