from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """Handler de excepciones de DRF. Punto de extensión para formato uniforme de errores."""
    return drf_exception_handler(exc, context)
