from fastapi import APIRouter, Depends
from app.api import auth, cluster, k8s, audit

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# 以下路由需要鉴权
router.include_router(cluster.router, prefix="/clusters", tags=["Cluster"], dependencies=[Depends(auth.require_auth)])
router.include_router(k8s.router, prefix="/k8s", tags=["K8s"], dependencies=[Depends(auth.require_auth)])
router.include_router(audit.router, prefix="/audit", tags=["Audit"], dependencies=[Depends(auth.require_auth)])