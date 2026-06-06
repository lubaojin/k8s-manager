from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class NamespaceInfo(BaseModel):
    name: str
    status: str
    labels: dict = {}
    created_at: Optional[str] = None


class PodInfo(BaseModel):
    name: str
    namespace: str
    status: str
    node: Optional[str] = None
    ip: Optional[str] = None
    restarts: int = 0
    ready: str = "0/0"
    age: Optional[str] = None


class DeploymentInfo(BaseModel):
    name: str
    namespace: str
    replicas: str = "0/0"
    ready: bool = False
    age: Optional[str] = None


class ServiceInfo(BaseModel):
    name: str
    namespace: str
    type: str = "ClusterIP"
    cluster_ip: Optional[str] = None
    ports: str = ""
    age: Optional[str] = None


class NodeInfo(BaseModel):
    name: str
    status: str
    roles: str = ""
    version: str = ""
    internal_ip: Optional[str] = None
    age: Optional[str] = None


class EventInfo(BaseModel):
    type: str
    reason: str
    message: str
    object_name: str
    first_time: Optional[str] = None
    last_time: Optional[str] = None
