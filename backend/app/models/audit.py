from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=True)
    resource_name = Column(String(256), nullable=True)
    cluster_name = Column(String(128), nullable=True)
    namespace = Column(String(128), nullable=True)
    detail = Column(Text, nullable=True)
    result = Column(String(16), default="success")
    created_at = Column(DateTime, server_default=func.now(), index=True)
