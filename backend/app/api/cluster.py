from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.cluster import ClusterConfig
from app.schemas.cluster import ClusterCreate, ClusterUpdate, ClusterOut
from app.services.k8s_service import get_cluster_version, get_cluster_stats, get_dashboard_data
from app.services.audit_service import log_action
from app.api.auth import require_admin

router = APIRouter()


# ── 仪表盘聚合（静态路由，必须在动态路由之前） ──

@router.get("/dashboard")
def dashboard_overview(db: Session = Depends(get_db)):
    """仪表盘聚合：所有集群概览 + 节点资源"""
    clusters = db.query(ClusterConfig).all()
    result = []

    total_ns = 0
    total_nodes = 0
    total_pods = 0
    total_running = 0
    total_pending = 0
    total_failed = 0
    all_nodes = []

    for c in clusters:
        try:
            data = get_dashboard_data(c.id, c.name, c.kubeconfig)
            result.append(data)
            total_ns += data["namespaces"]
            total_nodes += data["nodes"]
            total_pods += data["pods_total"]
            total_running += data["pods_running"]
            total_pending += data["pods_pending"]
            total_failed += data["pods_failed"]
            all_nodes.extend(data["node_list"])
            # 同步更新 DB 中的状态和节点数
            c.status = "connected"
            c.node_count = data["nodes"]
        except Exception:
            c.status = "error"
            result.append({
                "cluster_id": c.id,
                "cluster_name": c.name,
                "cluster_status": c.status,
                "namespaces": 0,
                "nodes": 0,
                "pods_total": 0,
                "pods_running": 0,
                "pods_pending": 0,
                "pods_failed": 0,
                "node_list": [],
            })
    db.commit()

    return {
        "clusters": result,
        "summary": {
            "clusters": len(clusters),
            "namespaces": total_ns,
            "nodes": total_nodes,
            "pods_total": total_pods,
            "pods_running": total_running,
            "pods_pending": total_pending,
            "pods_failed": total_failed,
        },
        "all_nodes": all_nodes,
    }


# ── 集群 CRUD ──

@router.get("", response_model=list[ClusterOut])
def list_clusters(db: Session = Depends(get_db)):
    clusters = db.query(ClusterConfig).all()
    for c in clusters:
        try:
            c.version = get_cluster_version(c.kubeconfig)
            stats = get_cluster_stats(c.kubeconfig)
            c.node_count = stats.get("nodes", 0)
            c.status = "connected"
        except Exception:
            c.status = "error"
    db.commit()
    return clusters


@router.post("", response_model=ClusterOut)
def add_cluster(data: ClusterCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(ClusterConfig).filter(ClusterConfig.name == data.name).first():
        raise HTTPException(400, "Cluster name already exists")
    import yaml
    cfg = yaml.safe_load(data.kubeconfig)
    if not isinstance(cfg, dict) or "current-context" not in cfg:
        raise HTTPException(400, "Invalid kubeconfig: missing current-context")
    cluster = ClusterConfig(**data.model_dump())
    try:
        cluster.version = get_cluster_version(data.kubeconfig)
        stats = get_cluster_stats(data.kubeconfig)
        cluster.node_count = stats.get("nodes", 0)
        cluster.status = "connected"
    except Exception:
        cluster.status = "error"
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    log_action(db, "system", "create", "cluster", data.name, data.name, detail="Cluster registered")
    return cluster


@router.get("/{cluster_id}", response_model=ClusterOut)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    c = db.query(ClusterConfig).filter(ClusterConfig.id == cluster_id).first()
    if not c:
        raise HTTPException(404, "Cluster not found")
    return c


@router.delete("/{cluster_id}")
def delete_cluster(cluster_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = db.query(ClusterConfig).filter(ClusterConfig.id == cluster_id).first()
    if not c:
        raise HTTPException(404, "Cluster not found")
    db.delete(c)
    db.commit()
    log_action(db, "system", "delete", "cluster", c.name)
    return {"ok": True}


@router.patch("/{cluster_id}", response_model=ClusterOut)
def update_cluster(cluster_id: int, data: ClusterUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    c = db.query(ClusterConfig).filter(ClusterConfig.id == cluster_id).first()
    if not c:
        raise HTTPException(404, "Cluster not found")
    if data.description is not None:
        c.description = data.description
    if data.kubeconfig is not None:
        import yaml
        cfg = yaml.safe_load(data.kubeconfig)
        if not isinstance(cfg, dict) or "current-context" not in cfg:
            raise HTTPException(400, "Invalid kubeconfig: missing current-context")
        c.kubeconfig = data.kubeconfig
        try:
            c.version = get_cluster_version(data.kubeconfig)
            c.status = "connected"
        except Exception:
            c.status = "error"
    if data.environment is not None:
        c.environment = data.environment
    db.commit()
    db.refresh(c)
    return c


@router.get("/{cluster_id}/stats")
def cluster_stats(cluster_id: int, db: Session = Depends(get_db)):
    c = db.query(ClusterConfig).filter(ClusterConfig.id == cluster_id).first()
    if not c:
        raise HTTPException(404, "Cluster not found")
    try:
        stats = get_cluster_stats(c.kubeconfig)
    except Exception as e:
        raise HTTPException(502, f"K8s API error: {str(e)}")
    return stats
