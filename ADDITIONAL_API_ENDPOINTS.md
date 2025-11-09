# 新增的 API 接口文档（中低优先级）

## 1. GET /api/orders/me - 获取用户订单列表

### 描述
获取当前用户的订单列表，支持按状态筛选和分页。

### 请求
- **方法**: `GET`
- **路径**: `/api/orders/me`
- **认证**: 需要 Bearer Token
- **查询参数**:
  - `status` (可选): 订单状态筛选 (pending, paid, shipped, completed, refunded)
  - `limit` (可选, 默认50): 返回的最大订单数量
  - `offset` (可选, 默认0): 分页偏移量

### 响应
返回订单列表，每个订单包含：
- 订单基本信息（id, status, total等）
- 订单商品列表（items）
- 支付信息（payment）

```json
[
    {
        "id": 1,
        "user_id": 1,
        "status": "paid",
        "subtotal": 899.00,
        "tax": 0.0,
        "shipping_fee": 0.0,
        "total": 899.00,
        "created_at": "2025-01-05T10:00:00",
        "items": [
            {
                "product_id": 1,
                "title": "iPhone 14 128GB Midnight",
                "unit_price": 899.00,
                "qty": 1,
                "line_total": 899.00,
                "product": {
                    "id": 1,
                    "title": "iPhone 14 128GB Midnight",
                    "image": "https://..."
                }
            }
        ],
        "payment": {
            "status": "succeeded",
            "amount": 899.00,
            "currency": "usd"
        }
    }
]
```

### 使用示例
```bash
# 获取所有订单
curl -X GET "http://127.0.0.1:8000/api/orders/me" \
  -H "Authorization: Bearer <token>"

# 获取已支付的订单
curl -X GET "http://127.0.0.1:8000/api/orders/me?status=paid" \
  -H "Authorization: Bearer <token>"

# 分页获取订单
curl -X GET "http://127.0.0.1:8000/api/orders/me?limit=10&offset=0" \
  -H "Authorization: Bearer <token>"
```

---

## 2. GET /api/users/me/items - 获取用户交易历史

### 描述
获取当前用户的所有交易历史，包括订单和回收请求，用于"My Items"页面。

### 请求
- **方法**: `GET`
- **路径**: `/api/users/me/items`
- **认证**: 需要 Bearer Token
- **查询参数**:
  - `limit` (可选, 默认50): 返回的最大项目数量
  - `offset` (可选, 默认0): 分页偏移量

### 响应
返回用户的交易历史，包括：
- 订单列表（orders）
- 回收请求列表（pickup_requests）
- 合并排序后的所有项目（all_items）
- 统计信息（total_orders, total_tradeins）

```json
{
    "orders": [
        {
            "id": 1,
            "type": "order",
            "status": "paid",
            "total": 899.00,
            "created_at": "2025-01-05T10:00:00",
            "items": [...]
        }
    ],
    "pickup_requests": [
        {
            "id": 1,
            "type": "tradein",
            "brand_name": "Apple",
            "model_text": "iPhone 14",
            "condition": "A",
            "status": "requested",
            "created_at": "2025-01-06T10:00:00"
        }
    ],
    "total_orders": 5,
    "total_tradeins": 3,
    "all_items": [
        // 合并后的所有项目，按时间倒序排列
    ]
}
```

### 使用示例
```bash
# 获取所有交易历史
curl -X GET "http://127.0.0.1:8000/api/users/me/items" \
  -H "Authorization: Bearer <token>"

# 分页获取
curl -X GET "http://127.0.0.1:8000/api/users/me/items?limit=20&offset=0" \
  -H "Authorization: Bearer <token>"
```

---

## 3. GET /api/locations - 获取地点列表

### 描述
获取可用的地点列表，用于地点选择器。

### 请求
- **方法**: `GET`
- **路径**: `/api/locations`
- **认证**: 不需要认证（公开接口）

### 响应
返回地点列表：

```json
[
    {
        "id": "vancouver",
        "name": "Vancouver",
        "code": "VAN",
        "hub_name": "Vancouver Hub"
    },
    {
        "id": "ottawa",
        "name": "Ottawa",
        "code": "OTT",
        "hub_name": "Ottawa Lab"
    },
    {
        "id": "edmonton",
        "name": "Edmonton",
        "code": "EDM",
        "hub_name": "Edmonton Studio"
    }
]
```

### 使用示例
```bash
# 获取所有地点
curl "http://127.0.0.1:8000/api/locations"

# 获取特定地点
curl "http://127.0.0.1:8000/api/locations/vancouver"
```

---

## 接口总结

### 已实现的所有首页相关接口

#### 高优先级 ✅
1. ✅ `GET /api/auth/me` - 用户信息
2. ✅ `GET /api/products/search` - 商品搜索
3. ✅ `GET /api/products/deals` - 优惠商品
4. ✅ `GET /api/cart/count` - 购物车数量

#### 中优先级 ✅
5. ✅ `GET /api/orders/me` - 订单列表
6. ✅ `GET /api/users/me/items` - 用户交易历史

#### 低优先级 ✅
7. ✅ `GET /api/locations` - 地点列表

---

## 测试建议

### 1. 测试订单列表接口
1. 先创建一个订单（通过 `/api/orders`）
2. 使用 token 调用 `/api/orders/me`
3. 测试状态筛选：`?status=paid`

### 2. 测试用户交易历史
1. 确保用户有订单和回收请求
2. 调用 `/api/users/me/items`
3. 检查返回的 `all_items` 是否按时间正确排序

### 3. 测试地点列表
1. 调用 `/api/locations` 查看所有地点
2. 调用 `/api/locations/vancouver` 查看特定地点

---

## Swagger UI 测试

所有接口都可以在 Swagger UI 中测试：
- 访问: http://127.0.0.1:8000/docs
- 找到对应的接口
- 点击 "Try it out" 进行测试

---

## 注意事项

1. **认证接口** (`/api/orders/me`, `/api/users/me/items`) 需要 Bearer Token
2. **地点接口** (`/api/locations`) 是公开接口，不需要认证
3. **分页参数** 在所有列表接口中都支持
4. **排序** 所有列表接口都按时间倒序排列（最新的在前）
5. **订单状态** 可以是：pending, paid, shipped, completed, refunded
6. **回收请求状态** 可以是：requested, collected, evaluating, offered, accepted, rejected

