# Klook Web Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 Klook Web 项目。

## 项目结构

```
klook-web/
├── backend/                  # 后端服务（FastAPI）
│   ├── app/                 # 应用代码
│   ├── main.py              # 入口文件
│   ├── requirements.txt     # Python 依赖
│   ├── Dockerfile           # 后端 Docker 配置
│   └── .dockerignore        # Docker 忽略文件
├── frontend/                # 前端服务（Vue 3 + Vite）
│   ├── src/                 # 源代码
│   ├── package.json         # Node 依赖
│   ├── nginx.conf           # Nginx 配置
│   ├── Dockerfile           # 前端 Docker 配置
│   └── .dockerignore        # Docker 忽略文件
├── docker-compose.yml       # 生产环境编排
└── docker-compose.dev.yml   # 开发环境编排
```

## 技术栈

### 后端
- Python 3.11
- FastAPI
- SQLAlchemy + aiosqlite
- Uvicorn

### 前端
- Vue 3
- Vite
- Element Plus
- Nginx (生产环境)

## 快速开始

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

### 生产环境部署

1. **构建并启动所有服务**
```bash
cd klook-web
docker-compose up -d --build
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **查看日志**
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

4. **访问应用**
- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

5. **停止服务**
```bash
docker-compose down
```

6. **停止服务并删除数据卷**
```bash
docker-compose down -v
```

### 开发环境部署

开发环境支持热重载，代码更改会自动生效。

1. **启动开发环境**
```bash
cd klook-web
docker-compose -f docker-compose.dev.yml up -d --build
```

2. **访问应用**
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

3. **停止开发环境**
```bash
docker-compose -f docker-compose.dev.yml down
```

## 服务配置

### 后端环境变量

可以在 `docker-compose.yml` 或 `docker-compose.dev.yml` 中修改以下环境变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DEBUG | false (生产) / true (开发) | 调试模式 |
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 8000 | 监听端口 |
| DATABASE_URL | sqlite+aiosqlite:///./klook-web.db | 数据库连接 |

### 端口映射

| 服务 | 容器端口 | 主机端口（生产） | 主机端口（开发） |
|------|----------|-----------------|-----------------|
| 后端 | 8000 | 8000 | 8000 |
| 前端 | 80 (生产) / 5173 (开发) | 80 | 5173 |

## 数据持久化

- **生产环境**: 后端数据库文件保存在 Docker 卷 `backend-data` 中
- **开发环境**: 后端数据库文件保存在 Docker 卷 `backend-dev-data` 中

查看数据卷：
```bash
docker volume ls
```

备份数据库：
```bash
# 生产环境
docker run --rm -v klook-web_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/backend-data-backup.tar.gz -C /data .

# 开发环境
docker run --rm -v klook-web_backend-dev-data:/data -v $(pwd):/backup alpine tar czf /backup/backend-dev-data-backup.tar.gz -C /data .
```

## 常用命令

### 重新构建服务
```bash
# 重新构建所有服务
docker-compose build

# 重新构建特定服务
docker-compose build backend
docker-compose build frontend
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend sh

# 进入前端容器（生产环境）
docker-compose exec frontend sh

# 进入前端容器（开发环境）
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### 查看资源使用情况
```bash
docker stats
```

### 清理未使用的资源
```bash
# 清理所有未使用的容器、网络、镜像
docker system prune -a

# 清理所有未使用的数据卷
docker volume prune
```

## 健康检查

生产环境配置了健康检查：

- **后端**: 每 30 秒检查一次 `/api/health` 端点
- **前端**: 每 30 秒检查一次根路径

查看健康状态：
```bash
docker-compose ps
```

## 故障排查

### 后端无法启动
1. 检查日志：`docker-compose logs backend`
2. 确认依赖是否正确安装
3. 检查数据库连接是否正常

### 前端无法访问后端
1. 检查 nginx.conf 中的代理配置
2. 确认后端服务是否正常运行：`docker-compose ps`
3. 检查网络连接：`docker-compose exec frontend ping backend`

### 端口冲突
如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:80"  # 将主机 8080 端口映射到容器 80 端口
```

## 生产环境建议

1. **使用环境变量文件**
   创建 `.env` 文件管理敏感配置：
   ```bash
   DEBUG=false
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/klook
   ```

2. **使用外部数据库**
   在生产环境建议使用 PostgreSQL 或 MySQL：
   ```yaml
   environment:
     - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/klook
   ```

3. **启用 HTTPS**
   配置 Nginx SSL 证书或使用反向代理（如 Traefik、Nginx Proxy Manager）

4. **配置日志收集**
   使用 ELK Stack 或其他日志系统收集容器日志

5. **监控和告警**
   集成 Prometheus + Grafana 进行监控

6. **备份策略**
   定期备份数据库和重要数据

## 性能优化

1. **使用多阶段构建**
   前端 Dockerfile 已使用多阶段构建，最小化镜像大小

2. **启用缓存**
   构建时利用 Docker 层缓存：
   ```bash
   docker-compose build --parallel
   ```

3. **资源限制**
   在 docker-compose.yml 中添加资源限制：
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

## 安全建议

1. **不要在镜像中包含敏感信息**
2. **定期更新基础镜像**
3. **使用非 root 用户运行容器**
4. **限制容器权限**
5. **扫描镜像漏洞**：`docker scan klook-web-backend`

## 更新和维护

### 更新应用
```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并重启服务
docker-compose up -d --build

# 3. 检查服务状态
docker-compose ps
```

### 版本回滚
```bash
# 1. 回退到之前的提交
git checkout <commit-hash>

# 2. 重新构建并重启
docker-compose up -d --build
```

## 技术支持

如遇问题，请查看：
1. 容器日志：`docker-compose logs`
2. 健康检查状态：`docker-compose ps`
3. 资源使用情况：`docker stats`
