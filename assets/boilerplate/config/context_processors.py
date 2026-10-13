from django.conf import settings


def app_context(request):
    return {
        "app_name": settings.APP_NAME,
        "enable_fullstack": settings.ENABLE_FULLSTACK,
        "enable_api": settings.ENABLE_API,
    }
