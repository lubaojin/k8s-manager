from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ClusterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    kubeconfig: str
    environment: str = "dev"


class ClusterUpdate(BaseModel):
    description: Optional[str] = None
    kubeconfig: Optional[str] = None
    environment: Optional[str] = None


class ClusterOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment: str
    status: str
    version: Optional[str]
    node_count: int
    created_at: datetime

    class Config:
        from_attributes = True
