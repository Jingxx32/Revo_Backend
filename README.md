# Revo Backend API

Backend API for Revo C2B2C Electronics Trade-in Platform

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/revo_db
JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

### 3. 启动服务器
```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. 访问 API 文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📚 API 文档

启动服务器后，访问以下地址查看 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 项目结构

```
app/
├── core/           # 核心配置和安全
├── db/             # 数据库模型和连接
├── routers/        # API 路由
├── schemas/        # Pydantic 模型
└── main.py         # FastAPI 应用入口
```

## 📋 主要功能

- ✅ 用户认证和授权 (JWT)
- ✅ 商品管理
- ✅ 购物车功能
- ✅ 订单管理
- ✅ Trade-in 功能
- ✅ 用户管理
- ✅ 地点管理

## 🔒 安全特性

- JWT Token 认证
- 密码哈希 (bcrypt)
- CORS 支持
- 输入验证

## 📝 环境变量

主要环境变量：
- `DATABASE_URL`: PostgreSQL 数据库连接字符串
- `JWT_SECRET_KEY`: JWT 令牌密钥
- `CORS_ORIGINS`: 允许的 CORS 源（逗号分隔）

## 🚢 部署

参见 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解部署到 Render 平台的详细说明