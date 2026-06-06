from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.cluster import ClusterConfig
from app.services import k8s_service

router = APIRouter()


def _get_kubeconfig(cluster_id: int, db: Session) -> str:
    c = db.query(ClusterConfig).filter(ClusterConfig.id == cluster_id).first()
    if not c:
        raise HTTPException(404, "Cluster not found")
    return c.kubeconfig


@router.get("/{cluster_id}/namespaces")
def list_ns(cluster_id: int, db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_namespaces(kubeconfig)


@router.get("/{cluster_id}/pods")
def list_pods(cluster_id: int, namespace: str = Query("all"), db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_pods(kubeconfig, namespace)


@router.get("/{cluster_id}/deployments")
def list_deps(cluster_id: int, namespace: str = Query("all"), db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_deployments(kubeconfig, namespace)


@router.get("/{cluster_id}/services")
def list_svcs(cluster_id: int, namespace: str = Query("all"), db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_services(kubeconfig, namespace)


@router.get("/{cluster_id}/nodes")
def list_nodes(cluster_id: int, db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_nodes(kubeconfig)


@router.get("/{cluster_id}/events")
def list_events(cluster_id: int, namespace: str = Query("all"), db: Session = Depends(get_db)):
    kubeconfig = _get_kubeconfig(cluster_id, db)
    return k8s_service.list_events(kubeconfig, namespace)
