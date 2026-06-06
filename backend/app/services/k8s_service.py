import yaml
from kubernetes import client, config


def _make_client(kubeconfig_yaml: str) -> client.ApiClient:
    cfg_dict = yaml.safe_load(kubeconfig_yaml)
    if not isinstance(cfg_dict, dict):
        raise ValueError("kubeconfig must be a valid YAML object")
    if "current-context" not in cfg_dict:
        raise ValueError("kubeconfig missing required key: current-context")
    return config.new_client_from_config_dict(cfg_dict)


def get_cluster_version(kubeconfig_yaml: str) -> str:
    api = _make_client(kubeconfig_yaml)
    v1 = client.VersionApi(api)
    info = v1.get_code()
    return info.git_version


def list_namespaces(kubeconfig_yaml: str) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.CoreV1Api(api)
    result = []
    for ns in v1.list_namespace().items:
        result.append({
            "name": ns.metadata.name,
            "status": ns.status.phase,
            "labels": ns.metadata.labels or {},
            "created_at": str(ns.metadata.creation_timestamp) if ns.metadata.creation_timestamp else None,
        })
    return result


def list_pods(kubeconfig_yaml: str, namespace: str = None) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.CoreV1Api(api)
    result = []
    if namespace and namespace != "all":
        pods = v1.list_namespaced_pod(namespace).items
    else:
        pods = v1.list_pod_for_all_namespaces().items
    for pod in pods:
        ready = f"{sum(1 for c in pod.status.container_statuses or [] if c.ready)}/{len(pod.status.container_statuses or [])}"
        restart = sum(c.restart_count for c in pod.status.container_statuses or [])
        result.append({
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase or "Unknown",
            "node": pod.spec.node_name,
            "ip": pod.status.pod_ip,
            "restarts": restart,
            "ready": ready,
            "age": _age(pod.metadata.creation_timestamp),
        })
    return result


def list_deployments(kubeconfig_yaml: str, namespace: str = None) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.AppsV1Api(api)
    result = []
    if namespace and namespace != "all":
        deps = v1.list_namespaced_deployment(namespace).items
    else:
        deps = v1.list_deployment_for_all_namespaces().items
    for dep in deps:
        result.append({
            "name": dep.metadata.name,
            "namespace": dep.metadata.namespace,
            "replicas": f"{dep.status.ready_replicas or 0}/{dep.spec.replicas}",
            "ready": (dep.status.ready_replicas or 0) >= (dep.spec.replicas or 1),
            "age": _age(dep.metadata.creation_timestamp),
        })
    return result


def list_services(kubeconfig_yaml: str, namespace: str = None) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.CoreV1Api(api)
    result = []
    if namespace and namespace != "all":
        svcs = v1.list_namespaced_service(namespace).items
    else:
        svcs = v1.list_service_for_all_namespaces().items
    for svc in svcs:
        ports = ",".join(f"{p.port}/{p.protocol}" for p in svc.spec.ports or [])
        result.append({
            "name": svc.metadata.name,
            "namespace": svc.metadata.namespace,
            "type": svc.spec.type or "ClusterIP",
            "cluster_ip": svc.spec.cluster_ip,
            "ports": ports,
            "age": _age(svc.metadata.creation_timestamp),
        })
    return result


def list_nodes(kubeconfig_yaml: str) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.CoreV1Api(api)
    result = []
    for node in v1.list_node().items:
        roles = []
        if node.metadata.labels:
            for k, v in node.metadata.labels.items():
                if k.startswith("node-role.kubernetes.io/"):
                    roles.append(k.split("/")[1])
        internal_ip = ""
        for addr in (node.status.addresses or []):
            if addr.type == "InternalIP":
                internal_ip = addr.address
        ready = "Unknown"
        for cond in (node.status.conditions or []):
            if cond.type == "Ready":
                ready = "Ready" if cond.status == "True" else "NotReady"
        result.append({
            "name": node.metadata.name,
            "status": ready,
            "roles": ",".join(roles) if roles else "worker",
            "version": node.status.node_info.kubelet_version if node.status.node_info else "",
            "internal_ip": internal_ip,
            "age": _age(node.metadata.creation_timestamp),
        })
    return result


def list_events(kubeconfig_yaml: str, namespace: str = None) -> list[dict]:
    api = _make_client(kubeconfig_yaml)
    v1 = client.CoreV1Api(api)
    result = []
    if namespace and namespace != "all":
        evs = v1.list_namespaced_event(namespace).items
    else:
        evs = v1.list_event_for_all_namespaces().items
    for ev in evs:
        result.append({
            "type": ev.type or "Normal",
            "reason": ev.reason or "",
            "message": ev.message or "",
            "object_name": ev.involved_object.name if ev.involved_object else "",
            "first_time": str(ev.first_timestamp) if ev.first_timestamp else None,
            "last_time": str(ev.last_timestamp) if ev.last_timestamp else None,
        })
    return result


def get_cluster_stats(kubeconfig_yaml: str) -> dict:
    api = _make_client(kubeconfig_yaml)
    core = client.CoreV1Api(api)
    apps = client.AppsV1Api(api)

    namespaces = len(core.list_namespace().items)
    nodes = len(core.list_node().items)
    deployments = 0
    pods_total = 0
    pods_running = 0

    for ns in core.list_namespace().items:
        ns_name = ns.metadata.name
        pods = core.list_namespaced_pod(ns_name).items
        pods_total += len(pods)
        pods_running += sum(1 for p in pods if p.status.phase == "Running")
        deployments += len(apps.list_namespaced_deployment(ns_name).items)

    return {
        "namespaces": namespaces,
        "nodes": nodes,
        "deployments": deployments,
        "pods_total": pods_total,
        "pods_running": pods_running,
    }


def _age(ts) -> str:
    if not ts:
        return ""
    from datetime import datetime, timezone
    delta = datetime.now(timezone.utc) - ts
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes = rem // 60
    if days > 0:
        return f"{days}d"
    if hours > 0:
        return f"{hours}h"
    return f"{minutes}m"


def get_node_resources(kubeconfig_yaml: str) -> list[dict]:
    """获取所有节点的 CPU/内存容量、分配量和使用量"""
    api = _make_client(kubeconfig_yaml)
    core = client.CoreV1Api(api)

    # 尝试从 metrics-server 获取实时用量（可能不可用）
    metrics = {}
    try:
        custom = client.CustomObjectsApi(api)
        node_metrics = custom.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
        for item in node_metrics.get("items", []):
            name = item["metadata"]["name"]
            cpu_raw = item["usage"].get("cpu", "0")
            mem_raw = item["usage"].get("memory", "0")
            metrics[name] = {
                "cpu_usage": _parse_cpu(cpu_raw),
                "mem_usage": _parse_mem(mem_raw),
            }
    except Exception:
        pass  # metrics-server 不可用时静默跳过

    nodes = []
    for node in core.list_node().items:
        name = node.metadata.name
        capacity_cpu = _parse_cpu(node.status.capacity.get("cpu", "0"))
        capacity_mem = _parse_mem(node.status.capacity.get("memory", "0"))
        allocatable_cpu = _parse_cpu(node.status.allocatable.get("cpu", "0")) if node.status.allocatable else 0
        allocatable_mem = _parse_mem(node.status.allocatable.get("memory", "0")) if node.status.allocatable else 0

        m = metrics.get(name, {})
        cpu_usage = m.get("cpu_usage", None)
        mem_usage = m.get("mem_usage", None)

        # 计算百分比
        cpu_pct = round(cpu_usage / capacity_cpu * 100, 1) if cpu_usage else None
        mem_pct = round(mem_usage / capacity_mem * 100, 1) if mem_usage else None

        ready = "Unknown"
        for cond in (node.status.conditions or []):
            if cond.type == "Ready":
                ready = "Ready" if cond.status == "True" else "NotReady"

        nodes.append({
            "name": name,
            "status": ready,
            "capacity_cpu": capacity_cpu,
            "capacity_mem": capacity_mem,
            "allocatable_cpu": round(allocatable_cpu, 2),
            "allocatable_mem": allocatable_mem,
            "cpu_usage": round(cpu_usage, 2) if cpu_usage else None,
            "mem_usage": mem_usage if mem_usage else None,
            "cpu_pct": cpu_pct,
            "mem_pct": mem_pct,
        })

    return nodes


def get_dashboard_data(cluster_id: int, cluster_name: str, kubeconfig_yaml: str) -> dict:
    """聚合仪表盘所需的所有数据"""
    api = _make_client(kubeconfig_yaml)
    core = client.CoreV1Api(api)

    # 基础统计
    namespaces = core.list_namespace().items
    ns_count = len(namespaces)
    nodes = get_node_resources(kubeconfig_yaml)
    node_count = len(nodes)

    # Pod 统计
    pods_total = 0
    pods_running = 0
    pods_pending = 0
    pods_failed = 0
    for ns in namespaces:
        for pod in core.list_namespaced_pod(ns.metadata.name).items:
            pods_total += 1
            phase = pod.status.phase
            if phase == "Running":
                pods_running += 1
            elif phase == "Pending":
                pods_pending += 1
            elif phase in ("Failed", "Error"):
                pods_failed += 1

    return {
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
        "cluster_status": "connected",
        "namespaces": ns_count,
        "nodes": node_count,
        "pods_total": pods_total,
        "pods_running": pods_running,
        "pods_pending": pods_pending,
        "pods_failed": pods_failed,
        "node_list": nodes,
    }


def _parse_cpu(cpu_str: str) -> float:
    """解析 K8s CPU 字符串为核数"""
    if not cpu_str:
        return 0.0
    cpu_str = str(cpu_str)
    if cpu_str.endswith("m"):
        return float(cpu_str[:-1]) / 1000
    if cpu_str.endswith("n"):
        return float(cpu_str[:-1]) / 1_000_000_000
    return float(cpu_str)


def _parse_mem(mem_str: str) -> int:
    """解析 K8s 内存字符串为字节数"""
    if not mem_str:
        return 0
    mem_str = str(mem_str)
    units = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4,
             "K": 1000, "M": 1000**2, "G": 1000**3, "T": 1000**4,
             "k": 1000}
    for suffix, mult in units.items():
        if mem_str.endswith(suffix):
            return int(float(mem_str[:-len(suffix)]) * mult)
    return int(float(mem_str))
