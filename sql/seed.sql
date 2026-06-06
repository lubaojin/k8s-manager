-- K8s Manager 初始化管理员用户
-- 默认账号: admin / admin123

USE k8s_manager;

INSERT INTO users (username, email, hashed_password, role, is_active)
VALUES ('admin', 'admin@k8s.local',
        '$2b$12$5moymNAA/OeW2tALcNo7jOR.2iVxrujgF/ewge6QHJsBsdNIw2n5a',
        'admin', 1)
ON DUPLICATE KEY UPDATE username = username;
