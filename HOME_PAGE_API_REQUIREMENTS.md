# 首页 API 接口需求分析

## 已存在的接口 ✅

1. **分类接口**
   - ✅ `GET /api/categories` - 获取商品分类（Phone, Laptop, Tablet, Accessory）

2. **商品接口**
   - ✅ `GET /api/products` - 获取商品列表（支持筛选：category, brand, condition, price）
   - ✅ `GET /api/products/{product_id}` - 获取商品详情

3. **购物车接口**
   - ✅ `GET /api/cart` - 获取购物车（包含商品数量）

4. **认证接口**
   - ✅ `POST /api/auth/token` - 登录
   - ✅ `POST /api/auth/register` - 注册

5. **订单接口**
   - ✅ `POST /api/orders` - 创建订单

6. **Trade-in 接口**
   - ✅ `GET /api/tradein/brands` - 获取品牌列表
   - ✅ `GET /api/tradein/pickup-requests/me` - 获取用户的回收请求

---

## 需要补充的接口 🔴

### 1. **用户信息接口**
- **接口**: `GET /api/auth/me`
- **用途**: 获取当前登录用户信息（用于右上角账户图标、判断登录状态）
- **返回**: 用户基本信息（email, role等）
- **权限**: 需要认证

### 2. **商品搜索接口**
- **接口**: `GET /api/products/search?q={keyword}`
- **用途**: 根据关键词搜索商品（用于顶部搜索框）
- **参数**: 
  - `q`: 搜索关键词
  - 可选：`category`, `brand`, `min_price`, `max_price`
- **返回**: 匹配的商品列表

### 3. **优惠商品接口（Deals Center）**
- **接口**: `GET /api/products/deals`
- **用途**: 获取有折扣的优惠商品列表
- **参数**: 
  - 可选：`limit` (默认返回前几个)
  - 可选：`min_discount` (最小折扣百分比)
- **返回**: 包含折扣信息的商品列表
- **计算**: 折扣百分比 = (originalPrice - price) / originalPrice * 100

### 4. **购物车商品数量接口**
- **接口**: `GET /api/cart/count`
- **用途**: 快速获取购物车商品数量（用于右上角购物车图标显示数字）
- **权限**: 需要认证
- **返回**: `{"count": 3}`

### 5. **用户订单列表接口**
- **接口**: `GET /api/orders/me`
- **用途**: 获取当前用户的订单列表（用于"My Items"区域）
- **参数**: 
  - 可选：`status` (pending, paid, shipped, completed)
  - 可选：`limit`, `offset` (分页)
- **权限**: 需要认证
- **返回**: 订单列表，包含订单状态、商品信息等

### 6. **地点列表接口**
- **接口**: `GET /api/locations`
- **用途**: 获取可用地点列表（Vancouver, Ottawa, Edmonton）
- **返回**: 地点列表，包含名称、代码等
- **说明**: 可以硬编码或从数据库读取

### 7. **用户交易历史接口（My Items）**
- **接口**: `GET /api/users/me/items`
- **用途**: 获取用户的所有交易和购买的设备（用于"My Items"区域）
- **返回**: 
  - 购买的订单（orders）
  - 回收请求（pickup_requests）
- **权限**: 需要认证

---

## 优先级建议

### 高优先级（首页核心功能）
1. 🔴 `GET /api/auth/me` - 用户信息
2. 🔴 `GET /api/products/search` - 商品搜索
3. 🔴 `GET /api/products/deals` - 优惠商品
4. 🔴 `GET /api/cart/count` - 购物车数量

### 中优先级（用户体验）
5. 🔴 `GET /api/orders/me` - 订单列表
6. 🔴 `GET /api/users/me/items` - 用户交易历史

### 低优先级（辅助功能）
7. 🔴 `GET /api/locations` - 地点列表

---

## 接口设计建议

### 1. 用户信息接口
```python
GET /api/auth/me
Response: {
    "id": 1,
    "email": "user@example.com",
    "role": "customer",
    "created_at": "2025-01-01"
}
```

### 2. 商品搜索接口
```python
GET /api/products/search?q=iPhone&category=Phone
Response: [ProductResponse, ...]
```

### 3. 优惠商品接口
```python
GET /api/products/deals?limit=10&min_discount=10
Response: [
    {
        ...ProductResponse,
        "discount_percent": 16,
        "voucher_label": "+16% Voucher"
    },
    ...
]
```

### 4. 购物车数量接口
```python
GET /api/cart/count
Response: {
    "count": 3,
    "total_items": 5  # 商品总件数（考虑数量）
}
```

### 5. 订单列表接口
```python
GET /api/orders/me?status=paid&limit=10
Response: [
    {
        "id": 1,
        "status": "paid",
        "total": 899.00,
        "created_at": "2025-01-05",
        "items": [...]
    },
    ...
]
```

### 6. 地点列表接口
```python
GET /api/locations
Response: [
    {"id": "vancouver", "name": "Vancouver", "code": "VAN"},
    {"id": "ottawa", "name": "Ottawa", "code": "OTT"},
    {"id": "edmonton", "name": "Edmonton", "code": "EDM"}
]
```

### 7. 用户交易历史接口
```python
GET /api/users/me/items
Response: {
    "orders": [...],
    "pickup_requests": [...],
    "total_orders": 5,
    "total_tradeins": 3
}
```

