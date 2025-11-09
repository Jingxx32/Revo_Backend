# 新实现的 API 接口文档

## 1. GET /api/auth/me - 获取当前用户信息

### 描述
获取当前已认证用户的基本信息。

### 请求
- **方法**: `GET`
- **路径**: `/api/auth/me`
- **认证**: 需要 Bearer Token

### 响应
```json
{
    "id": 1,
    "email": "user@example.com",
    "role": "customer",
    "created_at": "2025-01-01T00:00:00"
}
```

### 使用示例
```bash
curl -X GET "http://127.0.0.1:8000/api/auth/me" \
  -H "Authorization: Bearer <token>"
```

---

## 2. GET /api/products/search - 商品搜索

### 描述
根据关键词搜索商品，支持在商品标题、型号、描述中搜索。

### 请求
- **方法**: `GET`
- **路径**: `/api/products/search`
- **查询参数**:
  - `q` (必需): 搜索关键词
  - `category` (可选): 分类筛选
  - `brand` (可选): 品牌筛选
  - `min_price` (可选): 最低价格
  - `max_price` (可选): 最高价格

### 响应
返回商品列表（ProductResponse 格式）

### 使用示例
```bash
# 基本搜索
curl "http://127.0.0.1:8000/api/products/search?q=iPhone"

# 带筛选的搜索
curl "http://127.0.0.1:8000/api/products/search?q=iPhone&category=Phone&min_price=500&max_price=1500"
```

---

## 3. GET /api/products/deals - 优惠商品列表

### 描述
获取有折扣的优惠商品列表，按折扣百分比降序排列。

### 请求
- **方法**: `GET`
- **路径**: `/api/products/deals`
- **查询参数**:
  - `limit` (可选, 默认10): 返回的最大商品数量
  - `min_discount` (可选): 最小折扣百分比

### 响应
返回商品列表，每个商品包含额外的折扣信息：
```json
[
    {
        ...ProductResponse,
        "discount_percent": 14.3,
        "voucher_label": "+14% Voucher"
    },
    ...
]
```

### 使用示例
```bash
# 获取前10个优惠商品
curl "http://127.0.0.1:8000/api/products/deals"

# 获取折扣至少15%的商品
curl "http://127.0.0.1:8000/api/products/deals?min_discount=15&limit=5"
```

### 折扣计算逻辑
- 当前价格: `resale_price` 或 `list_price`
- 原价: `base_price` 或 `list_price`
- 折扣百分比: `(原价 - 当前价格) / 原价 * 100`

---

## 4. GET /api/cart/count - 购物车商品数量

### 描述
快速获取购物车中的商品数量和总件数。

### 请求
- **方法**: `GET`
- **路径**: `/api/cart/count`
- **认证**: 需要 Bearer Token

### 响应
```json
{
    "count": 3,          // 商品种类数
    "total_items": 5     // 商品总件数（考虑数量）
}
```

### 使用示例
```bash
curl -X GET "http://127.0.0.1:8000/api/cart/count" \
  -H "Authorization: Bearer <token>"
```

---

## 测试建议

### 1. 测试用户信息接口
1. 先登录获取 token
2. 使用 token 调用 `/api/auth/me`

### 2. 测试商品搜索
1. 使用关键词搜索: `?q=iPhone`
2. 测试组合筛选: `?q=MacBook&category=Laptop`

### 3. 测试优惠商品
1. 调用 `/api/products/deals` 查看所有优惠
2. 测试最小折扣筛选: `?min_discount=10`

### 4. 测试购物车数量
1. 先添加商品到购物车
2. 调用 `/api/cart/count` 查看数量

---

## Swagger UI 测试

所有接口都可以在 Swagger UI 中测试：
- 访问: http://127.0.0.1:8000/docs
- 找到对应的接口
- 点击 "Try it out" 进行测试

---

## 注意事项

1. **认证接口** (`/api/auth/me`, `/api/cart/count`) 需要 Bearer Token
2. **搜索接口** 支持大小写不敏感的搜索
3. **优惠商品接口** 只返回有折扣的商品（price < originalPrice）
4. **购物车数量接口** 返回两个值：
   - `count`: 商品种类数（不同商品的数量）
   - `total_items`: 商品总件数（所有商品数量的总和）

