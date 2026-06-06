from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import get_logs

router = APIRouter()


@router.get("")
def list_audit_logs(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    logs = get_logs(db, skip, limit)
    return [
        {
            "id": l.id,
            "username": l.username,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_name": l.resource_name,
            "cluster_name": l.cluster_name,
            "namespace": l.namespace,
            "detail": l.detail,
            "result": l.result,
            "created_at": str(l.created_at) if l.created_at else None,
        }
        for l in logs
    ]
