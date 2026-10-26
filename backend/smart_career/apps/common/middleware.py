import logging

from django.utils.deprecation import MiddlewareMixin

from .models import AuditLog

logger = logging.getLogger(__name__)

AUDITED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

ACTION_BY_METHOD = {
    'POST': 'CREATE',
    'PUT': 'UPDATE',
    'PATCH': 'UPDATE',
    'DELETE': 'DELETE',
}

ENTITY_BY_SEGMENT = {
    'candidates': 'CANDIDATE',
    'jobs': 'JOB',
    'applications': 'APPLICATION',
    'documents': 'DOCUMENT',
    'medical': 'MEDICAL',
    'visa': 'VISA',
    'tickets': 'TICKET',
    'deployments': 'DEPLOYMENT',
    'invoices': 'INVOICE',
    'payments': 'PAYMENT',
    'tasks': 'TASK',
    'alerts': 'ALERT',
}


def _client_ip(request):
    # REMOTE_ADDR only. X-Forwarded-For is client-controlled, so it is trusted
    # only once a reverse proxy / Cloudflare Tunnel is configured (see DEPLOYMENT.md).
    return request.META.get('REMOTE_ADDR')


class AuditLoggingMiddleware(MiddlewareMixin):
    """Records every successful-or-failed write request made to the API by an authenticated user."""

    def process_response(self, request, response):
        if request.method not in AUDITED_METHODS:
            return response
        if not request.path.startswith('/api/'):
            return response
        if request.path.startswith('/api/auth/'):
            return response

        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return response

        parts = request.path.strip('/').split('/')
        segment = parts[1] if len(parts) > 1 else ''
        entity_id = parts[2] if len(parts) > 2 else 'list'

        try:
            AuditLog.objects.create(
                user=user,
                action=ACTION_BY_METHOD[request.method],
                entity_type=ENTITY_BY_SEGMENT.get(segment, 'OTHER'),
                entity_id=entity_id,
                description=f"{request.method} {request.path}",
                http_method=request.method,
                http_path=request.path[:500],
                status_code=response.status_code,
                ip_address=_client_ip(request),
            )
        except Exception:
            # Audit failure must not break the user's request, but it must never be silent.
            logger.exception("Failed to write audit log for %s %s", request.method, request.path)

        return response