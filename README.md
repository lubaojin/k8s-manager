# K8s Manager

多集群 Kubernetes 可视化管理平台，支持集群管理、工作负载监控、节点资源、审计日志及用户权限控制。

## 功能

- **仪表盘** — 聚合展示所有集群的节点、Pod 运行状态及资源使用率
- **集群管理** — 添加/删除集群，实时检测连通性，查看命名空间、Pods、Deployments、Events
- **工作负载** — 按命名空间查看 Pods 和 Deployments
- **服务网络** — 查看 Service 及其端口映射
- **节点管理** — 查看节点状态、CPU/内存容量与使用率
- **审计日志** — 记录用户操作行为
- **用户管理** — 支持 admin/viewer 角色，admin 可增删改用户及修改密码
- **登录认证** — JWT 鉴权，路由守卫，角色权限控制

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Element Plus + Pinia + Vue Router |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy + PyMySQL |
| 数据库 | MySQL 8.0 |
| K8s SDK | kubernetes (python) |
| 部署 | Docker Compose |

## 快速启动

### Docker Compose（推荐）

```bash
git clone git@github.com:lubaojin/k8s-manager.git
cd k8s-manager
docker-compose up -d
```

访问：
- 前端: http://localhost:3000
- 后端 API 文档: http://localhost:8000/docs

### 本地开发

**后端**

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 修改 backend/app/core/config.py 中的 MySQL 连接信息
python run.py
```

**前端**

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
k8s-manager/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由 (auth, cluster, k8s, audit)
│   │   ├── core/         # 配置、数据库、安全模块
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   ├── schemas/      # Pydantic 请求/响应模型
│   │   └── services/     # 业务逻辑 (K8s, Auth, Audit)
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios 封装
│   │   ├── router/       # 路由 & 鉴权守卫
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/        # 页面组件 (dashboard, cluster, user 等)
│   └── vite.config.js
├── docker-compose.yml
└── start.sh
```

## API 接口

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/auth/login` | 登录 | 公开 |
| POST | `/api/v1/auth/register` | 创建用户 | admin |
| GET | `/api/v1/auth/users` | 用户列表 | 登录 |
| PATCH | `/api/v1/auth/users/{id}` | 修改用户 | admin |
| DELETE | `/api/v1/auth/users/{id}` | 删除用户 | admin |
| GET | `/api/v1/clusters` | 集群列表 | 登录 |
| POST | `/api/v1/clusters` | 添加集群 | admin |
| DELETE | `/api/v1/clusters/{id}` | 删除集群 | admin |
| GET | `/api/v1/clusters/dashboard` | 仪表盘数据 | 登录 |
| GET | `/api/v1/k8s/{id}/pods` | Pod 列表 | 登录 |
| GET | `/api/v1/k8s/{id}/nodes` | 节点列表 | 登录 |

## 角色权限

| 操作 | admin | viewer |
|---|---|---|
| 查看仪表盘/集群/节点 | ✅ | ✅ |
| 添加/删除集群 | ✅ | ❌ |
| 管理用户 | ✅ | ❌ |

## 配置

默认配置文件 `backend/app/core/config.py`，支持 `.env` 覆盖：

```env
DB_HOST=192.168.3.31
DB_PORT=3307
DB_USER=root
DB_PASSWORD=123456
DB_NAME=k8s_manager
SECRET_KEY=your-secret-key
```
