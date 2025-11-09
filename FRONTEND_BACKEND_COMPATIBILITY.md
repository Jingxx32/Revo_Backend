# 前后端 API 适配检查报告

## 🔴 不匹配的接口

### 1. **登录接口**
- **前端调用**: `POST /api/login`
- **后端实现**: `POST /api/auth/token`
- **问题**: 
  - 路径不匹配
  - 响应格式不匹配
  - 前端期望: `{success: true, token: "...", user: {...}}`
  - 后端返回: `{access_token: "...", token_type: "bearer"}`

### 2. **注册接口**
- **前端调用**: `api.register(userData)` (期望返回 `{success, token, user}`)
- **后端实现**: `POST /api/auth/register` (返回 `{access_token, token_type}`)
- **问题**: 响应格式不匹配

### 3. **商品列表接口**
- **前端调用**: `api.getProducts({ city })`
- **后端实现**: `GET /api/products`
- **问题**: 
  - 后端不支持 `city` 参数筛选
  - 前端期望直接返回数组，后端返回数组（✅ 匹配）

### 4. **分类接口**
- **前端调用**: `api.getCategories()` 
- **前端期望**: `[{id, name, icon}, ...]`
- **后端实现**: `GET /api/categories`
- **问题**: 后端返回的分类可能没有 `icon` 字段

### 5. **购物车接口**
- **前端**: 使用 localStorage (`cartStore`)
- **后端**: 有 `/api/cart` 接口
- **问题**: 前端没有调用后端购物车接口，全部使用本地存储

### 6. **订单/结账接口**
- **前端调用**: `api.checkout(orderData)` (期望返回 `{success, orderId}`)
- **后端实现**: `POST /api/orders` (返回 `{order_id, client_secret}`)
- **问题**: 响应格式不匹配

### 7. **Trade-in 评估接口**
- **前端调用**: `POST /api/estimate`
- **后端实现**: `POST /api/tradein/pickup-requests`
- **问题**: 路径不匹配，参数格式可能不同

### 8. **Trade-in 提交接口**
- **前端调用**: `api.requestPickup(deviceId, pickupDetails)` → `POST /api/pickup/request`
- **后端实现**: `POST /api/tradein/pickup-requests`
- **问题**: 路径不匹配

### 9. **钱包接口**
- **前端调用**: `GET /api/wallet`
- **后端实现**: ❌ **未实现**

### 10. **优惠券接口**
- **前端调用**: `GET /api/coupons`
- **后端实现**: ❌ **未实现**

### 11. **设备接口**
- **前端调用**: `GET /api/devices`, `GET /api/devices/{id}`
- **后端实现**: ❌ **未实现** (可能是 trade-in 相关)

## 🟡 需要调整的接口

### 1. **商品搜索**
- **前端**: 在 `api.getProducts()` 中本地搜索
- **后端**: `GET /api/products/search?q=...`
- **建议**: 前端应该调用后端搜索接口

### 2. **优惠商品**
- **前端**: 在 `home.js` 中本地筛选和排序
- **后端**: `GET /api/products/deals`
- **建议**: 前端应该调用后端 deals 接口

### 3. **用户信息**
- **前端**: 从 localStorage 读取
- **后端**: `GET /api/auth/me`
- **建议**: 前端应该调用后端接口验证 token

## ✅ 已适配的接口

1. **健康检查**: `GET /api/health` ✅
2. **商品详情**: `GET /api/products/{id}` ✅ (格式匹配)
3. **分类列表**: `GET /api/categories` ✅ (基本匹配，缺icon)

## 📋 需要修复的问题清单

### 高优先级

1. **创建兼容的登录接口**
   - 添加 `POST /api/login` 作为 `/api/auth/token` 的别名
   - 调整响应格式匹配前端期望

2. **创建兼容的注册接口响应**
   - 调整 `POST /api/auth/register` 响应格式

3. **添加商品 city 筛选**
   - 在 `GET /api/products` 中添加 `city` 参数支持

4. **分类添加 icon 字段**
   - 在分类数据中添加 `icon` 字段

5. **创建兼容的结账接口**
   - 调整 `POST /api/orders` 响应格式
   - 或添加 `POST /api/checkout` 作为兼容接口

### 中优先级

6. **创建 Trade-in 评估接口**
   - 添加 `POST /api/estimate` 接口
   - 或修改前端调用 `/api/tradein/pickup-requests`

7. **创建钱包接口**
   - 实现 `GET /api/wallet`

8. **创建优惠券接口**
   - 实现 `GET /api/coupons`

### 低优先级

9. **购物车同步**
   - 前端改用后端购物车接口
   - 或保持本地存储（如果不需要服务端购物车）

10. **设备接口**
    - 如果需要，实现设备相关接口

