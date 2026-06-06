-- ============================================================
-- K8s Manager 一键部署数据库脚本
-- 用法: mysql -u root -p < sql/init.sql
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS k8s_manager
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE k8s_manager;

-- ============================================================
-- 2. 数据表
-- ============================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username        VARCHAR(64)  NOT NULL UNIQUE COMMENT '用户名',
    email           VARCHAR(128) NULL UNIQUE COMMENT '邮箱',
    hashed_password VARCHAR(256) NOT NULL COMMENT 'bcrypt 加密密码',
    role            VARCHAR(32)  NOT NULL DEFAULT 'viewer' COMMENT '角色: admin / viewer',
    is_active       TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '启用: 1, 禁用: 0',
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 集群配置表
CREATE TABLE IF NOT EXISTS cluster_configs (
    id          INT AUTO_INCREMENT PRIMARY KEY COMMENT '集群ID',
    name        VARCHAR(128) NOT NULL UNIQUE COMMENT '集群名称',
    description TEXT         NULL COMMENT '描述',
    kubeconfig  TEXT         NOT NULL COMMENT 'Kubeconfig YAML',
    environment VARCHAR(32)  NOT NULL DEFAULT 'dev' COMMENT '环境: dev / staging / prod',
    status      VARCHAR(32)  NOT NULL DEFAULT 'unknown' COMMENT '状态: connected / error',
    version     VARCHAR(32)  NULL COMMENT 'K8s 版本',
    node_count  INT          NOT NULL DEFAULT 0 COMMENT '节点数量',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='集群配置表';

-- 审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    username    VARCHAR(64)  NOT NULL COMMENT '操作用户',
    action      VARCHAR(32)  NOT NULL COMMENT '操作: create / delete / update',
    resource    VARCHAR(64)  NOT NULL COMMENT '资源类型: cluster / user',
    detail      TEXT         NULL COMMENT '操作详情',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- ============================================================
-- 3. 初始化管理员
--    默认账号: admin / admin123
--    登录后请立即修改密码
-- ============================================================

INSERT INTO users (username, email, hashed_password, role, is_active)
VALUES ('admin',
        'admin@k8s.local',
        '$2b$12$5moymNAA/OeW2tALcNo7jOR.2iVxrujgF/ewge6QHJsBsdNIw2n5a',
        'admin',
        1)
ON DUPLICATE KEY UPDATE username = username;
