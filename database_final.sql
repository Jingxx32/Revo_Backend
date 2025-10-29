
PRAGMA foreign_keys = ON;

-- Core reference tables
CREATE TABLE brands (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

-- Users
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT CHECK(role IN ('customer','admin','evaluator')) NOT NULL DEFAULT 'customer',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  sku TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  brand_id INTEGER,
  category_id INTEGER,
  condition TEXT CHECK(condition IN ('A','B','C')),
  verified INTEGER DEFAULT 0,
  description TEXT,
  images_json TEXT,
  cost_components_json TEXT,
  base_price REAL,
  list_price REAL,
  resale_price REAL,
  qty INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT,
  FOREIGN KEY(brand_id) REFERENCES brands(id),
  FOREIGN KEY(category_id) REFERENCES categories(id)
);

-- Carts
CREATE TABLE carts (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL CHECK(qty > 0),
  PRIMARY KEY (cart_id, product_id),
  FOREIGN KEY(cart_id) REFERENCES carts(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

-- Orders
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  status TEXT CHECK(status IN ('pending','paid','shipped','completed','refunded')) NOT NULL DEFAULT 'pending',
  subtotal REAL NOT NULL,
  tax REAL NOT NULL,
  shipping_fee REAL NOT NULL DEFAULT 0,
  total REAL NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  title_snapshot TEXT NOT NULL,
  unit_price REAL NOT NULL,
  qty INTEGER NOT NULL CHECK(qty > 0),
  line_total REAL NOT NULL,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

-- Payments (allow multiple attempts per order)
CREATE TABLE payments (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  stripe_pi TEXT NOT NULL,
  amount REAL NOT NULL,
  currency TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(order_id) REFERENCES orders(id)
);

-- Pickup / evaluation
CREATE TABLE pickup_requests (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  brand_id INTEGER,
  model_text TEXT,
  condition TEXT,
  address_json TEXT,
  scheduled_at TEXT,
  deposit_amount REAL,
  status TEXT CHECK(status IN ('requested','collected','evaluating','offered','accepted','rejected')),
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(brand_id) REFERENCES brands(id)
);

CREATE TABLE evaluations (
  id INTEGER PRIMARY KEY,
  pickup_id INTEGER NOT NULL,
  tester_id INTEGER,
  diagnostics_json TEXT,
  parts_replaced_json TEXT,
  evaluation_cost REAL,
  final_offer REAL,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(pickup_id) REFERENCES pickup_requests(id) ON DELETE CASCADE,
  FOREIGN KEY(tester_id) REFERENCES users(id)
);

-- Audit logs
CREATE TABLE audit_logs (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  action TEXT NOT NULL,
  entity TEXT NOT NULL,
  entity_id INTEGER,
  payload_json TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Helpful indexes
CREATE INDEX idx_products_brand_category ON products(brand_id, category_id);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_eval_pickup ON evaluations(pickup_id);
