from sqlalchemy.orm import Session

from .models import AuditEvent


def audit(session: Session, tenant_id: int, actor: str, action: str, **data) -> None:
    session.add(AuditEvent(tenant_id=tenant_id, actor=actor, action=action, data=data))
