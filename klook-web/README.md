# Klook Web - 智能抢购助手 🚀

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能强大的 Klook 优惠券抢购助手，提供直观的 Web 界面管理配置和任务，支持毫秒级高精度定时抢购，让你不再错过心仪的优惠券。

## ✨ 项目特色

本项目将原有的 CLI 工具 `klook` 重构为功能完善的 Web 应用，采用现代化技术栈和前后端分离架构：

- **⚡ 后端**: FastAPI + SQLAlchemy + SQLite - 高性能异步处理
- **🎨 前端**: Vue 3 + Vite + Element Plus - 现代化响应式界面
- **🐳 部署**: Docker + Docker Compose - 一键部署，开箱即用
- **⏱️ 高精度**: 毫秒级定时器 + 网络延迟补偿 - 精准到达抢购时刻
- **📊 实时反馈**: SSE 实时推送 - 倒计时、状态更新即时可见

### 📈 项目统计

- **后端代码**: ~2,157 行 Python 代码
- **前端代码**: ~3,059 行 Vue/JavaScript 代码
- **API 接口**: 20+ RESTful API 端点
- **数据模型**: 4 个核心实体（配置、项目、任务、日志）

## 功能特性

### ✅ 已实现

#### 核心功能
- ✅ 项目基础架构搭建
- ✅ 后端 FastAPI 框架配置
- ✅ 前端 Vue 3 + Element Plus 配置
- ✅ 核心 Klook API 客户端重构
- ✅ 高精度定时器实现（毫秒级）
- ✅ SQLite 数据库初始化
- ✅ Docker 容器化配置
- ✅ 健康检查 API

#### 配置管理
- ✅ 配置 CRUD（创建、读取、更新、删除）
- ✅ Headers 管理和验证
- ✅ 配置导入/导出（JSON 格式）
- ✅ 配置列表刷新功能
- ✅ 配置名称支持 1-100 字符

#### 优惠券项目管理
- ✅ 项目 CRUD 操作
- ✅ 项目 UUID 和名称管理
- ✅ 项目列表展示（含创建/更新时间）
- ✅ 项目列表刷新功能
- ✅ 项目名称支持 1-200 字符

#### 任务管理
- ✅ 任务创建和管理界面
- ✅ 实时倒计时显示（WebSocket + SSE）
- ✅ 任务状态管理（待执行、倒计时中、执行中、已完成、失败、已取消）
- ✅ 任务统计信息展示
- ✅ 状态筛选功能
- ✅ 任务操作（启动、取消、删除）
- ✅ 网络延迟补偿配置（默认 250ms）
- ✅ 最大重试次数配置（默认 3 次）
- ✅ 重试间隔配置
- ✅ 快捷跳转（去创建配置/项目）

#### 日志管理
- ✅ 任务执行日志查看
- ✅ 日志级别筛选（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- ✅ 按任务筛选日志
- ✅ 日志分页显示
- ✅ 单条日志删除
- ✅ 清空当前任务日志
- ✅ 清空全部日志

#### 实时功能
- ✅ 倒计时对话框组件
- ✅ 实时状态更新（SSE）
- ✅ 任务执行进度展示
- ✅ 执行结果实时显示

### 📋 待优化

- [ ] 用户认证和权限管理
- [ ] 数据统计图表
- [ ] 历史记录分析
- [ ] WebSocket 长连接优化
- [ ] 批量任务操作
- [ ] 任务模板功能
- [ ] 邮件/消息通知

## 技术栈

### 后端

| 技术         | 版本     | 用途        |
|------------|--------|-----------|
| Python     | 3.12+  | 运行时       |
| FastAPI    | 0.109+ | Web 框架    |
| SQLAlchemy | 2.0+   | ORM       |
| aiosqlite  | 0.19+  | 异步 SQLite |
| uvicorn    | 0.27+  | ASGI 服务器  |
| httpx      | 0.26+  | HTTP 客户端  |
| loguru     | 0.7+   | 日志        |
| Pydantic   | 2.0+   | 数据验证     |

### 前端

| 技术           | 版本   | 用途       |
|--------------|------|----------|
| Vue          | 3.4+ | 前端框架     |
| Vite         | 5.0+ | 构建工具     |
| Element Plus | 2.5+ | UI 组件库   |
| Vue Router   | 4.2+ | 路由       |
| Axios        | 1.6+ | HTTP 客户端 |

## 项目结构

```
klook-web/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── config.py      # 配置管理接口
│   │   │   ├── program.py     # 优惠券项目接口
│   │   │   ├── task.py        # 任务管理接口
│   │   │   ├── log.py         # 日志管理接口
│   │   │   └── health.py      # 健康检查接口
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── klook_client.py # Klook API 客户端
│   │   │   └── timer.py       # 高精度定时器
│   │   ├── models/            # Pydantic 数据模型
│   │   │   ├── config.py      # 配置模型
│   │   │   ├── program.py     # 优惠券项目模型
│   │   │   ├── task.py        # 任务模型
│   │   │   └── log.py         # 日志模型
│   │   ├── services/          # 业务逻辑
│   │   │   └── task_executor.py # 任务执行服务
│   │   └── storage/           # 数据持久化
│   │       ├── database.py    # 数据库配置
│   │       ├── models.py      # SQLAlchemy 模型
│   │       ├── config_store.py # 配置存储
│   │       ├── program_store.py # 项目存储
│   │       ├── task_store.py  # 任务存储
│   │       └── log_store.py   # 日志存储
│   ├── main.py                # 应用入口
│   └── Dockerfile             # 后端容器配置
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── ConfigView.vue # 配置管理
│   │   │   ├── ProgramView.vue # 优惠券项目管理
│   │   │   ├── TaskView.vue   # 任务管理
│   │   │   └── LogView.vue    # 日志查看
│   │   ├── components/        # 通用组件
│   │   │   └── TaskCountdown.vue # 倒计时组件
│   │   ├── api/               # API 调用
│   │   │   ├── config.js      # 配置 API
│   │   │   ├── program.js     # 项目 API
│   │   │   ├── task.js        # 任务 API
│   │   │   └── log.js         # 日志 API
│   │   ├── router/            # 路由配置
│   │   │   └── index.js       # 路由定义
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 应用入口
│   ├── public/                # 静态资源
│   ├── index.html             # HTML 模板
│   ├── package.json           # NPM 配置
│   ├── vite.config.js         # Vite 配置
│   ├── nginx.conf             # Nginx 配置
│   └── Dockerfile             # 前端容器配置
│
├── docker-compose.yml          # 生产环境编排
├── docker-compose.dev.yml      # 开发环境编排
├── .gitignore
└── README.md
```

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 22+
- uv (Python 包管理器)
- npm

### 本地开发

#### 1. 安装依赖

```bash
# 在项目根目录安装 Python 依赖（使用外层 uv）
cd /path/to/python-project
uv sync

# 安装前端依赖
cd klook-web/frontend
npm install
```

#### 2. 启动后端

```bash
cd klook-web/backend
python main.py
```

后端将在 `http://localhost:8000` 启动。

访问 API 文档: `http://localhost:8000/docs`

#### 3. 启动前端

```bash
cd klook-web/frontend
npm run dev
```

前端将在 `http://localhost:5173` 启动。

### Docker 部署

后端使用 **uv** 管理依赖，Docker 构建时会自动从项目根目录的 `pyproject.toml` 和 `uv.lock` 安装依赖。

#### 开发环境（支持热重载）

```bash
cd klook-web
docker-compose -f docker-compose.dev.yml up --build
```

- 前端: `http://localhost:5173`
- 后端: `http://localhost:8000`
- API 文档: `http://localhost:8000/docs`

**开发环境特性**:
- ✅ 后端支持热重载（代码修改自动生效）
- ✅ 前端 Vite 开发服务器（HMR）
- ✅ 数据持久化到独立的 Docker volume

#### 生产环境

```bash
cd klook-web
docker-compose up -d --build
```

- 前端: `http://localhost`
- 后端 API: `http://localhost/api`
- API 文档: `http://localhost:8000/docs`

**生产环境特性**:
- ✅ Nginx 反向代理
- ✅ 优化的构建产物
- ✅ 后台运行（-d 参数）

#### 重新构建镜像

如果更新了依赖（修改了 `pyproject.toml` 或 `uv.lock`），需要重新构建：

```bash
cd klook-web
# 开发环境
docker-compose -f docker-compose.dev.yml build --no-cache

# 生产环境
docker-compose build --no-cache
```

#### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 仅查看后端日志
docker-compose logs -f backend

# 仅查看前端日志
docker-compose logs -f frontend
```

#### 停止服务

```bash
# 停止并删除容器
cd klook-web
docker-compose down

# 同时删除 volumes（会清空数据库）
docker-compose down -v
```

## API 文档

所有 API 接口都使用 `/api` 前缀。完整的交互式 API 文档可访问 `http://localhost:8000/docs`。

### 核心接口

#### 健康检查

```bash
GET /api/health
```

响应示例:

```json
{
  "status": "healthy",
  "timestamp": "2026-01-20T10:00:00.000000",
  "service": "klook-web-backend"
}
```

#### 根路径

```bash
GET /api/
```

响应示例:

```json
{
  "message": "Klook Web API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

### 配置管理

- `GET /api/configs` - 获取配置列表
- `POST /api/configs` - 创建新配置
- `GET /api/configs/{id}` - 获取单个配置
- `PUT /api/configs/{id}` - 更新配置
- `DELETE /api/configs/{id}` - 删除配置
- `POST /api/configs/import` - 导入配置
- `GET /api/configs/{id}/export` - 导出配置

### 优惠券项目管理

- `GET /api/programs` - 获取项目列表
- `POST /api/programs` - 创建新项目
- `GET /api/programs/{id}` - 获取单个项目
- `PUT /api/programs/{id}` - 更新项目
- `DELETE /api/programs/{id}` - 删除项目

### 任务管理

- `GET /api/tasks` - 获取任务列表（支持状态筛选）
- `POST /api/tasks` - 创建新任务
- `GET /api/tasks/{id}` - 获取任务详情
- `PUT /api/tasks/{id}` - 更新任务
- `DELETE /api/tasks/{id}` - 删除任务
- `POST /api/tasks/{id}/start` - 启动任务
- `POST /api/tasks/{id}/cancel` - 取消任务
- `GET /api/tasks/stats` - 获取任务统计信息
- `GET /api/tasks/{id}/stream` - 实时获取任务状态（SSE）

### 日志管理

- `GET /api/logs` - 获取日志列表（支持任务ID和级别筛选）
- `GET /api/logs/{id}` - 获取单条日志
- `DELETE /api/logs/{id}` - 删除单条日志
- `DELETE /api/logs` - 清空所有日志
- `GET /api/tasks/{task_id}/logs` - 获取任务的日志列表
- `DELETE /api/tasks/{task_id}/logs` - 清空任务的所有日志

## 配置说明

### 后端配置

编辑 `backend/app/core/config.py` 或创建 `.env` 文件：

```env
# 应用配置
APP_NAME=Klook Web
VERSION=0.1.0
DEBUG=true

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./klook-web.db

# Klook API
KLOOK_BASE_URL=https://www.klook.cn

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 前端配置

编辑 `frontend/vite.config.js` 修改代理配置：

```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────┐         ┌──────────────────┐
│   浏览器客户端    │         │   Nginx (生产)    │
│   Vue 3 SPA     │◄────────┤   反向代理        │
└────────┬────────┘         └──────────────────┘
         │
         │ HTTP/SSE
         ▼
┌─────────────────────────────────────────────┐
│           FastAPI 后端服务                    │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │  API 路由    │  │   核心服务            │  │
│  │  - 配置管理  │  │  - 高精度定时器       │  │
│  │  - 项目管理  │  │  - Klook API 客户端  │  │
│  │  - 任务管理  │  │  - 任务执行器        │  │
│  │  - 日志管理  │  │  - WebSocket 管理器  │  │
│  └─────────────┘  └─────────────────────┘  │
│           │                    │            │
│           ▼                    ▼            │
│  ┌──────────────────────────────────────┐  │
│  │         数据访问层 (Store)            │  │
│  │  SQLAlchemy ORM + aiosqlite          │  │
│  └──────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  SQLite 数据库    │
         │  - configs        │
         │  - programs       │
         │  - tasks          │
         │  - logs           │
         └──────────────────┘
```

### 核心技术亮点

#### 1. 高精度定时器 ⏱️

重构自原 `klook/main.py`，采用自适应间隔策略实现毫秒级精度：

```python
# backend/app/core/timer.py (99 行)
class PrecisionTimer:
    """
    智能倒计时算法:
    - 远离目标时间 (>60s)  : 10 秒间隔 - 节省 CPU 资源
    - 接近目标 (60-2s)     : 1 秒间隔 - 保持响应性
    - 临近触发 (2-0.5s)    : 0.1 秒间隔 - 提高精度
    - 最后冲刺 (<0.5s)     : 0.01 秒间隔 - 毫秒级精度
    """
```

**特性**:
- ✅ 网络延迟自动补偿（默认 250ms，可配置）
- ✅ 异步非阻塞设计，支持多任务并发
- ✅ 实时进度回调，支持 SSE 推送
- ✅ 可取消机制，优雅终止任务

#### 2. Klook API 客户端 🔌

基于 httpx 的异步 HTTP 客户端，支持上下文管理器：

```python
# backend/app/core/klook_client.py (104 行)
async with KlookClient() as client:
    # 获取用户信息
    success, result = await client.get_user_profile(headers)

    # 手动兑换优惠券
    success, result = await client.manual_redeem(
        program_uuid="8a6d71f",
        headers={"Authorization": "Bearer xxx"}
    )
```

**特性**:
- ✅ 30 秒请求超时保护
- ✅ 自动连接池管理
- ✅ 完整的错误处理和日志记录
- ✅ 支持 async/await 异步模式

#### 3. 任务执行引擎 🚀

智能任务调度和执行系统：

```python
# backend/app/services/task_executor.py
class TaskExecutor:
    """
    - 任务生命周期管理（待执行 → 倒计时 → 执行中 → 完成/失败）
    - 自动重试机制（可配置次数和间隔）
    - 实时状态推送（SSE）
    - 并发任务管理（asyncio）
    """
```

**执行流程**:
1. **准备阶段**: 验证配置、加载项目信息
2. **倒计时阶段**: 高精度定时器 + SSE 实时推送
3. **执行阶段**: 调用 Klook API + 重试机制
4. **完成阶段**: 记录结果 + 更新状态 + 写入日志

#### 4. 实时通信系统 📡

基于 Server-Sent Events (SSE) 的单向推送：

```javascript
// frontend/src/api/task.js
export function streamTask(taskId) {
  return new EventSource(`/api/tasks/${taskId}/stream`)
}

// 自动接收服务器推送:
// - 倒计时剩余时间更新 (每秒)
// - 任务状态变更 (实时)
// - 执行结果反馈 (即时)
```

**优势**:
- ✅ 比 WebSocket 更轻量，单向推送场景更高效
- ✅ 自动重连机制，网络波动不影响体验
- ✅ 浏览器原生支持，无需额外依赖
- ✅ HTTP/2 多路复用，性能优秀

## 开发指南

### 添加新的 API 路由

1. 在 `backend/app/api/` 创建新模块
2. 在 `backend/main.py` 注册路由

```python
from app.api import my_module

app.include_router(my_module.router, prefix="/api/my", tags=["我的模块"])
```

### 添加新的前端页面

1. 在 `frontend/src/views/` 创建 Vue 组件
2. 在 `frontend/src/router/index.js` 添加路由

```javascript
{
  path: '/my-page',
  name: 'MyPage',
  component: () => import('../views/MyPage.vue'),
}
```

### 数据库迁移

如果修改了数据库模型，需要删除旧数据库重新初始化：

```bash
rm klook-web/backend/klook.db
# 重启后端服务会自动重新创建
```

## 📖 使用指南

### 1. 创建配置

1. 进入"配置管理"页面
2. 点击"新建配置"
3. 填写配置名称和 Headers（JSON 格式）
4. 保存配置

**配置示例**:
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
  "X-Klook-Currency": "CNY"
}
```

**提示**: 配置可以导入/导出为 JSON 文件，方便备份和迁移。建议为不同账号创建不同配置。

### 2. 创建优惠券项目

1. 进入"优惠券项目"页面
2. 点击"新建项目"
3. 填写项目 UUID（从 Klook 获取）和项目名称
4. 保存项目

**如何获取 UUID**:
- 从 Klook 优惠券页面 URL 中提取
- 格式通常为: `https://www.klook.cn/promo/xxxxxxxx`
- UUID 即为 `xxxxxxxx` 部分

### 3. 创建抢购任务

1. 进入"任务管理"页面
2. 点击"新建任务"
3. 选择配置和优惠券项目
4. 设置抢购时间（精确到秒）
5. 配置网络延迟补偿（默认 250ms，建议根据实际网络情况调整）
6. 设置最大重试次数（默认 3 次）和重试间隔（默认 1 秒）
7. 创建任务

**重要参数说明**:
- **抢购时间**: 优惠券开始发放的精确时间
- **网络延迟补偿**: 考虑网络延迟，系统会提前这个时间发起请求（单位：毫秒）
  - 本地网络良好: 150-200ms
  - 一般网络环境: 200-300ms
  - 网络较差: 300-500ms
- **重试次数**: 首次失败后的重试次数
- **重试间隔**: 每次重试之间的等待时间

### 4. 执行任务

1. 在任务列表中找到待执行的任务
2. 点击"启动"按钮
3. 系统会自动进入倒计时模式，显示实时倒计时
4. 在目标时间（减去延迟补偿）自动执行抢购
5. 查看执行结果和日志

**任务状态说明**:
- 🟡 **待执行**: 任务已创建，等待手动启动
- 🔵 **倒计时中**: 任务已启动，正在倒计时
- 🟢 **执行中**: 正在调用 Klook API 抢购
- ✅ **已完成**: 抢购成功
- ❌ **失败**: 抢购失败（可查看日志了解原因）
- 🚫 **已取消**: 任务被手动取消

### 5. 查看日志

1. 进入"日志查看"页面
2. 可以按任务筛选或按日志级别筛选
3. 支持分页浏览，每页显示 20 条日志
4. 可以删除单条日志或清空所有日志

**日志级别说明**:
- **DEBUG**: 调试信息（详细的执行步骤）
- **INFO**: 一般信息（正常的执行流程）
- **WARNING**: 警告信息（需要注意但不影响执行）
- **ERROR**: 错误信息（执行失败的原因）
- **CRITICAL**: 严重错误（系统级错误）

## ❓ 常见问题 (FAQ)

### Q1: 如何获取 Klook 的 Authorization Token?

**A**:
1. 使用浏览器登录 Klook 网站
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签
4. 刷新页面或进行任意操作
5. 查找任意 API 请求，在 Request Headers 中找到 `Authorization` 字段
6. 复制完整的值（包括 `Bearer` 前缀）

### Q2: 任务一直执行失败，如何排查？

**A**:
1. **检查 Token 是否过期**: Klook 的 Token 通常有时效性，需要定期更新
2. **检查网络延迟补偿**: 如果总是抢不到，可能是发起请求的时间太晚，尝试增加延迟补偿值
3. **查看日志**: 在日志页面筛选失败任务的日志，查看具体错误信息
4. **检查优惠券状态**: 确认优惠券是否已经被抢完或活动已结束

### Q3: 可以同时运行多个任务吗？

**A**: 可以。系统支持多任务并发执行，每个任务都在独立的异步任务中运行，互不干扰。但建议不要同时启动过多任务，避免系统资源占用过高。

### Q4: 网络延迟补偿应该设置多少？

**A**: 这取决于你的网络环境：
- 可以使用 `ping www.klook.cn` 命令测试延迟
- 建议设置为 ping 延迟的 2-3 倍
- 例如：ping 延迟 80ms，建议设置 200-250ms

### Q5: 数据会被同步到云端吗？

**A**: 不会。所有数据（配置、任务、日志）都存储在本地 SQLite 数据库中，完全私有化部署，不会上传到任何云端服务器。

### Q6: Docker 部署和本地开发有什么区别？

**A**:
- **Docker 部署**: 适合生产环境，配置简单，一键启动，自动管理依赖
- **本地开发**: 适合开发调试，支持热重载，可以实时修改代码并查看效果

### Q7: 如何备份我的配置和任务？

**A**:
1. **配置备份**: 在配置管理页面使用"导出"功能，保存为 JSON 文件
2. **数据库备份**: 复制 `backend/klook-web.db` 文件到安全位置
3. **容器部署备份**: 数据库存储在 Docker volume `klook-db` 中，可以使用 `docker volume` 命令备份

### Q8: 为什么倒计时显示的时间和系统时间不一致？

**A**: 倒计时显示的是"距离发起请求的剩余时间"，已经减去了网络延迟补偿。例如：
- 目标时间: 10:00:00
- 延迟补偿: 250ms
- 实际发起请求时间: 09:59:59.750
- 所以倒计时会在 09:59:59.750 时归零

## 测试

### 后端测试

```bash
cd klook-web/backend
pytest
```

### 前端测试

```bash
cd klook-web/frontend
npm run test
```

## 故障排查

### 后端无法启动

1. 检查 Python 版本: `python --version` (需要 3.12+)
2. 检查依赖安装: `uv sync`
3. 查看日志: 检查终端输出
4. 检查端口占用: `lsof -i :8000`

### 前端无法启动

1. 检查 Node.js 版本: `node --version` (需要 22+)
2. 检查依赖安装: `npm install`
3. 清除缓存: `rm -rf node_modules && npm install`
4. 检查端口占用: `lsof -i :5173`

### 数据库错误

删除数据库文件重新初始化:

```bash
rm klook-web/backend/klook-web.db
# 重启后端服务会自动重新创建
```

### 任务执行失败

1. 检查配置中的 Headers 是否正确
2. 检查网络连接
3. 查看任务日志了解具体错误
4. 调整网络延迟补偿值
5. 增加重试次数

### SSE 连接断开

1. 检查浏览器是否支持 EventSource
2. 检查网络连接稳定性
3. 查看浏览器控制台错误信息
4. 组件会自动重连，等待片刻

## 性能优化建议

1. **数据库**: 定期清理旧日志，避免数据库膨胀
2. **任务并发**: 避免同时启动过多任务
3. **网络延迟**: 根据实际网络情况调整延迟补偿
4. **日志级别**: 生产环境建议设置为 INFO 或 WARNING

## 安全建议

1. **生产部署**: 修改默认端口，配置防火墙
2. **Headers 保护**: 不要将包含敏感信息的配置分享给他人
3. **CORS 配置**: 生产环境限制 CORS 来源
4. **数据备份**: 定期备份数据库文件

## 贡献指南

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/my-feature`
3. 提交更改: `git commit -m 'Add my feature'`
4. 推送分支: `git push origin feature/my-feature`
5. 提交 Pull Request

## 更新日志

### v0.1.0 (2026-01-20)

- ✅ 完成核心功能开发
- ✅ 配置管理完整功能
- ✅ 优惠券项目管理
- ✅ 任务管理和执行
- ✅ 日志管理
- ✅ 实时倒计时显示
- ✅ Docker 容器化部署

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

---

**注意**: 本工具仅供学习交流使用，请遵守 Klook 服务条款，合理使用。请勿用于商业用途或恶意刷单行为。