from .models import AuditLog


def record_audit_event(*, request, action, entity_type, entity_id, status_code,
                       user=None, description='', details=None):
    """Write an explicit audit row from a view. Used where middleware cannot see the outcome."""
    AuditLog.objects.create(
        user=user if user is not None and user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id)[:100],
        description=description,
        http_method=request.method,
        http_path=request.path[:500],
        status_code=status_code,
        ip_address=request.META.get('REMOTE_ADDR'),
        details=details or {},
    )