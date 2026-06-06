from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def log_action(
    db: Session,
    username: str,
    action: str,
    resource_type: str = "",
    resource_name: str = "",
    cluster_name: str = "",
    namespace: str = "",
    detail: str = "",
    result: str = "success",
):
    entry = AuditLog(
        username=username,
        action=action,
        resource_type=resource_type,
        resource_name=resource_name,
        cluster_name=cluster_name,
        namespace=namespace,
        detail=detail,
        result=result,
    )
    db.add(entry)
    db.commit()


def get_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
