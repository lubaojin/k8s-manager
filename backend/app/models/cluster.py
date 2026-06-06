from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class ClusterConfig(Base):
    __tablename__ = "cluster_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    kubeconfig = Column(Text, nullable=False)
    environment = Column(String(32), default="dev")
    status = Column(String(32), default="unknown")
    version = Column(String(32), nullable=True)
    node_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
