# 部署说明 - Render 平台

## PostgreSQL 数据库配置

### 1. 在 Render 上创建 PostgreSQL 数据库

1. 登录 Render 控制台
2. 创建新的 PostgreSQL 数据库服务
3. 记录数据库连接字符串（会自动设置 `DATABASE_URL` 环境变量）

### 2. 环境变量配置

在 Render 的 Web Service 中设置以下环境变量：

```bash
# 数据库连接（Render 会自动提供）
DATABASE_URL=postgresql://user:password@host:port/database

# JWT 密钥（生产环境请使用强密钥）
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置（根据你的前端域名）
CORS_ORIGINS=https://your-frontend-domain.com

# Stripe 配置（如果需要）
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# 其他可选配置
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=us-east-1
```

### 3. Render 部署配置

#### 方法 1: 使用启动脚本（推荐）

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `./start.sh`

#### 方法 2: 直接使用 gunicorn

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 4. 数据库迁移

首次部署后，需要初始化数据库表结构。可以通过以下方式：

1. **使用 Render Shell**:
   ```bash
   python -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
   ```

2. **或者在应用启动时自动创建**（当前代码已实现）

### 5. 本地开发配置

#### 使用 PostgreSQL（推荐）

创建 `.env` 文件：
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/revo_db
JWT_SECRET_KEY=your-local-secret-key
```

#### 使用 SQLite（开发环境）

如果不设置 `DATABASE_URL` 或使用 SQLite URL，应用会自动回退到 SQLite（仅用于本地开发）。

## 依赖说明

- **psycopg2-binary**: PostgreSQL 数据库适配器
- **gunicorn**: 生产环境 WSGI 服务器
- **uvicorn[standard]**: ASGI 服务器（gunicorn 使用 UvicornWorker）

## 注意事项

1. **数据库连接池**: PostgreSQL 配置了连接池（pool_size=5, max_overflow=10）
2. **连接健康检查**: 启用了 `pool_pre_ping=True` 以确保连接有效性
3. **端口配置**: Render 会自动设置 `PORT` 环境变量，应用会自动使用
4. **日志**: 生产环境建议设置适当的日志级别

## 故障排除

### 数据库连接问题

如果遇到数据库连接问题，检查：
1. `DATABASE_URL` 环境变量是否正确设置
2. PostgreSQL 数据库是否正在运行
3. 网络连接是否正常
4. 数据库用户权限是否正确

### 应用启动问题

如果应用无法启动：
1. 检查 `requirements.txt` 中的所有依赖是否已安装
2. 检查启动命令是否正确
3. 查看 Render 日志获取详细错误信息

