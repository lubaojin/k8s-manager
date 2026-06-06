from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut, TokenOut, LoginIn
from app.services.auth_service import (
    create_user, authenticate, list_users, update_user, delete_user, get_current_user
)

router = APIRouter()


# ── 鉴权依赖 ──

def require_auth(authorization: str = Header(None), db: Session = Depends(get_db)):
    """从 Authorization: Bearer <token> 中解析当前用户"""
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(401, "Missing authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        from fastapi import HTTPException
        raise HTTPException(401, "Invalid authorization scheme")
    return get_current_user(db, token)


def require_admin(current_user=Depends(require_auth)):
    """要求 admin 角色"""
    if current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(403, "Admin role required")
    return current_user


# ── 公开接口 ──

@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return create_user(db, data)


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    from app.models.user import User
    user = db.query(User).filter(User.username == data.username).first()
    token = authenticate(db, data.username, data.password)
    return {"access_token": token, "token_type": "bearer", "username": user.username, "role": user.role}


# ── 用户管理（需登录） ──

@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db), _=Depends(require_auth)):
    return list_users(db)


@router.patch("/users/{user_id}", response_model=UserOut)
def patch_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return update_user(db, user_id, data)


@router.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    delete_user(db, user_id)
    return {"ok": True}