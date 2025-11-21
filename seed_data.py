"""
Seed database with sample data for testing.
This script creates brands, categories, products, and test users.
"""
from datetime import datetime
from sqlmodel import select

from app.db.database import get_session
from app.db.models import Brand, Category, Product, User
from app.core.security import hash_password


def seed_database():
    """Insert sample data into database."""
    session = next(get_session())
    
    try:
        # 1. Create Brands
        print("Creating brands...")
        brands_data = [
            {"name": "Apple"},
            {"name": "Samsung"},
            {"name": "Google"},
            {"name": "Microsoft"},
            {"name": "Dell"},
            {"name": "HP"},
            {"name": "Lenovo"},
            {"name": "Sony"},
        ]
        
        brands = {}
        for brand_data in brands_data:
            existing = session.exec(select(Brand).where(Brand.name == brand_data["name"])).first()
            
            if not existing:
                brand = Brand(**brand_data)
                session.add(brand)
                session.commit()
                session.refresh(brand)
                brands[brand_data["name"]] = brand
                print(f"  ✓ Created brand: {brand.name} (ID: {brand.id})")
            else:
                brands[brand_data["name"]] = existing
                print(f"  - Brand already exists: {existing.name}")
        
        # 2. Create Categories
        print("\nCreating categories...")
        categories_data = [
            {"name": "Phone"},
            {"name": "Laptop"},
            {"name": "Tablet"},
            {"name": "Accessory"},
            {"name": "Watch"},
            {"name": "Headphones"},
        ]
        
        categories = {}
        for cat_data in categories_data:
            existing = session.exec(select(Category).where(Category.name == cat_data["name"])).first()
            
            if not existing:
                category = Category(**cat_data)
                session.add(category)
                session.commit()
                session.refresh(category)
                categories[cat_data["name"]] = category
                print(f"  ✓ Created category: {category.name} (ID: {category.id})")
            else:
                categories[cat_data["name"]] = existing
                print(f"  - Category already exists: {existing.name}")
        
        # 3. Create Products
        print("\nCreating products...")
        # Note: images_json, highlights_json, and city_availability_json are now Python lists/dicts, not JSON strings
        products_data = [
            # Apple Phones
            {
                "sku": "IPH14-128-MID",
                "title": "iPhone 14 128GB Midnight",
                "model": "iPhone 14",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Certified inspection, Unlocked, Includes charger. Perfect condition with original box.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPhone+14+Midnight"],
                "base_price": 1049.00,
                "list_price": 1049.00,
                "resale_price": 899.00,
                "qty": 5,
                "rating": 4.8,
                "reviews": 128,
                "location": "Ottawa Lab",
                "highlights_json": ["Certified inspection", "Unlocked", "Includes charger", "Original box"],
                "city_availability_json": ["Vancouver", "Ottawa"],
            },
            {
                "sku": "IPH14-256-STAR",
                "title": "iPhone 14 256GB Starlight",
                "model": "iPhone 14",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Like new condition, Unlocked, All accessories included",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPhone+14+Starlight"],
                "base_price": 1149.00,
                "list_price": 1149.00,
                "resale_price": 999.00,
                "qty": 3,
                "rating": 4.7,
                "reviews": 95,
                "location": "Vancouver Hub",
                "highlights_json": ["Like new", "Unlocked", "All accessories", "Warranty"],
                "city_availability_json": ["Vancouver", "Edmonton"],
            },
            {
                "sku": "IPH15-256-BLUE",
                "title": "iPhone 15 256GB Blue",
                "model": "iPhone 15",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Certified inspection, Unlocked, Includes USB-C cable. Latest model with A16 chip.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPhone+15+Blue"],
                "base_price": 1199.00,
                "list_price": 1199.00,
                "resale_price": 1099.00,
                "qty": 8,
                "rating": 4.9,
                "reviews": 203,
                "location": "Vancouver Hub",
                "highlights_json": ["Certified inspection", "Unlocked", "USB-C cable", "A16 chip"],
                "city_availability_json": ["Vancouver", "Ottawa", "Edmonton"],
            },
            {
                "sku": "IPH15-PRO-256-TITAN",
                "title": "iPhone 15 Pro 256GB Titanium",
                "model": "iPhone 15 Pro",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Premium titanium finish, Pro camera system, A17 Pro chip",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPhone+15+Pro"],
                "base_price": 1499.00,
                "list_price": 1499.00,
                "resale_price": 1349.00,
                "qty": 4,
                "rating": 4.9,
                "reviews": 156,
                "location": "Ottawa Lab",
                "highlights_json": ["Titanium finish", "Pro camera", "A17 Pro chip", "Premium"],
                "city_availability_json": ["Ottawa", "Vancouver"],
            },
            # Samsung Phones
            {
                "sku": "GS23-256-PB",
                "title": "Galaxy S23 256GB Phantom Black",
                "model": "Galaxy S23",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Phone"].id,
                "condition": "C",
                "description": "Dynamic AMOLED, Unlocked, Includes fast charger. Minor wear on screen.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Galaxy+S23"],
                "base_price": 999.00,
                "list_price": 999.00,
                "resale_price": 879.00,
                "qty": 6,
                "rating": 4.6,
                "reviews": 142,
                "location": "Vancouver Hub",
                "highlights_json": ["Dynamic AMOLED", "Unlocked", "Fast charger", "Great value"],
                "city_availability_json": ["Vancouver", "Edmonton"],
            },
            {
                "sku": "GS24-512-GR",
                "title": "Galaxy S24 512GB Graphite",
                "model": "Galaxy S24",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Latest Galaxy S24, AI-powered features, Unlocked",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Galaxy+S24"],
                "base_price": 1299.00,
                "list_price": 1299.00,
                "resale_price": 1149.00,
                "qty": 5,
                "rating": 4.8,
                "reviews": 87,
                "location": "Edmonton Studio",
                "highlights_json": ["AI features", "Unlocked", "512GB storage", "Latest model"],
                "city_availability_json": ["Edmonton", "Vancouver"],
            },
            # Google Phones
            {
                "sku": "GP7-128-LEM",
                "title": "Pixel 7 128GB Lemongrass",
                "model": "Pixel 7",
                "brand_id": brands["Google"].id,
                "category_id": categories["Phone"].id,
                "condition": "B",
                "description": "Google Tensor G2, Excellent camera, Unlocked",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Pixel+7"],
                "base_price": 799.00,
                "list_price": 799.00,
                "resale_price": 699.00,
                "qty": 4,
                "rating": 4.5,
                "reviews": 112,
                "location": "Vancouver Hub",
                "highlights_json": ["Tensor G2", "Excellent camera", "Unlocked", "Clean Android"],
                "city_availability_json": ["Vancouver", "Ottawa"],
            },
            {
                "sku": "GP8-256-OBS",
                "title": "Pixel 8 256GB Obsidian",
                "model": "Pixel 8",
                "brand_id": brands["Google"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Latest Pixel with Tensor G3, AI features, 7 years of updates",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Pixel+8"],
                "base_price": 899.00,
                "list_price": 899.00,
                "resale_price": 799.00,
                "qty": 6,
                "rating": 4.7,
                "reviews": 98,
                "location": "Ottawa Lab",
                "highlights_json": ["Tensor G3", "AI features", "7 years updates", "Great camera"],
                "city_availability_json": ["Ottawa", "Vancouver", "Edmonton"],
            },
            # Apple Laptops
            {
                "sku": "MBA-M2-13-512",
                "title": "MacBook Air 13\" M2 (2022)",
                "model": "MacBook Air M2",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Laptop"].id,
                "condition": "B",
                "description": "Battery health 92%, 512GB SSD, 2-year store warranty. Excellent condition.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=MacBook+Air+M2"],
                "base_price": 1599.00,
                "list_price": 1599.00,
                "resale_price": 1349.00,
                "qty": 3,
                "rating": 4.7,
                "reviews": 86,
                "location": "Vancouver Hub",
                "highlights_json": ["M2 chip", "512GB SSD", "2-year warranty", "Battery 92%"],
                "city_availability_json": ["Vancouver", "Edmonton"],
            },
            {
                "sku": "MBP-14-M3-512",
                "title": "MacBook Pro 14\" M3 512GB",
                "model": "MacBook Pro M3",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Laptop"].id,
                "condition": "A",
                "description": "M3 chip, Liquid Retina XDR, 18-hour battery. Like new condition.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=MacBook+Pro+M3"],
                "base_price": 1999.00,
                "list_price": 1999.00,
                "resale_price": 1799.00,
                "qty": 2,
                "rating": 4.8,
                "reviews": 95,
                "location": "Ottawa Lab",
                "highlights_json": ["M3 chip", "Liquid Retina XDR", "18-hour battery", "Like new"],
                "city_availability_json": ["Ottawa", "Vancouver"],
            },
            {
                "sku": "MBP-16-M3-1TB",
                "title": "MacBook Pro 16\" M3 1TB",
                "model": "MacBook Pro M3",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Laptop"].id,
                "condition": "A",
                "description": "M3 Max chip, 1TB SSD, Liquid Retina XDR, Perfect for professionals",
                "images_json": ["https://via.placeholder.com/480x360.png?text=MacBook+Pro+16"],
                "base_price": 3499.00,
                "list_price": 3499.00,
                "resale_price": 3199.00,
                "qty": 1,
                "rating": 4.9,
                "reviews": 42,
                "location": "Vancouver Hub",
                "highlights_json": ["M3 Max chip", "1TB SSD", "XDR display", "Professional"],
                "city_availability_json": ["Vancouver"],
            },
            # Samsung Laptops
            {
                "sku": "GB3-PRO-14-1TB",
                "title": "Galaxy Book3 Pro 14\"",
                "model": "Galaxy Book3",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Laptop"].id,
                "condition": "B",
                "description": "Intel Evo, 1TB SSD, Studio Mode camera. Great for work and creativity.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Galaxy+Book3"],
                "base_price": 1499.00,
                "list_price": 1499.00,
                "resale_price": 1249.00,
                "qty": 2,
                "rating": 4.5,
                "reviews": 57,
                "location": "Ottawa Lab",
                "highlights_json": ["Intel Evo", "1TB SSD", "Studio Mode camera", "Slim design"],
                "city_availability_json": ["Ottawa"],
            },
            # Dell Laptops
            {
                "sku": "DXPS13-512",
                "title": "Dell XPS 13 512GB",
                "model": "XPS 13",
                "brand_id": brands["Dell"].id,
                "category_id": categories["Laptop"].id,
                "condition": "B",
                "description": "Intel Core i7, 512GB SSD, InfinityEdge display",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Dell+XPS+13"],
                "base_price": 1299.00,
                "list_price": 1299.00,
                "resale_price": 1099.00,
                "qty": 3,
                "rating": 4.6,
                "reviews": 73,
                "location": "Edmonton Studio",
                "highlights_json": ["Intel i7", "512GB SSD", "InfinityEdge", "Premium build"],
                "city_availability_json": ["Edmonton", "Vancouver"],
            },
            # Apple Tablets
            {
                "sku": "IPAD-PRO-11-256",
                "title": "iPad Pro 11\" Wi-Fi 256GB",
                "model": "iPad Pro",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Tablet"].id,
                "condition": "A",
                "description": "Apple Pencil 2 support, Liquid Retina, Store warranty. Perfect for creatives.",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPad+Pro"],
                "base_price": 1199.00,
                "list_price": 1199.00,
                "resale_price": 1049.00,
                "qty": 4,
                "rating": 4.9,
                "reviews": 64,
                "location": "Edmonton Studio",
                "highlights_json": ["Apple Pencil 2", "Liquid Retina", "Store warranty", "M2 chip"],
                "city_availability_json": ["Edmonton", "Ottawa"],
            },
            {
                "sku": "IPAD-AIR-64",
                "title": "iPad Air 10.9\" Wi-Fi 64GB",
                "model": "iPad Air",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Tablet"].id,
                "condition": "B",
                "description": "M1 chip, All-screen design, Perfect for everyday use",
                "images_json": ["https://via.placeholder.com/480x360.png?text=iPad+Air"],
                "base_price": 749.00,
                "list_price": 749.00,
                "resale_price": 649.00,
                "qty": 5,
                "rating": 4.7,
                "reviews": 89,
                "location": "Vancouver Hub",
                "highlights_json": ["M1 chip", "All-screen design", "Great value", "Versatile"],
                "city_availability_json": ["Vancouver", "Ottawa", "Edmonton"],
            },
            # Samsung Tablets
            {
                "sku": "GTAB-S9-256",
                "title": "Galaxy Tab S9 Wi-Fi 256GB",
                "model": "Galaxy Tab S9",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Tablet"].id,
                "condition": "A",
                "description": "S Pen included, 120Hz display, IP68 water resistance",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Galaxy+Tab+S9"],
                "base_price": 1099.00,
                "list_price": 1099.00,
                "resale_price": 899.00,
                "qty": 4,
                "rating": 4.7,
                "reviews": 74,
                "location": "Edmonton Studio",
                "highlights_json": ["S Pen included", "120Hz display", "IP68", "Premium"],
                "city_availability_json": ["Edmonton", "Vancouver"],
            },
            # Accessories
            {
                "sku": "APPLE-WATCH-S9-45",
                "title": "Apple Watch Series 9 45mm",
                "model": "Apple Watch S9",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Watch"].id,
                "condition": "A",
                "description": "GPS + Cellular, Always-On Retina display, Health features",
                "images_json": ["https://via.placeholder.com/480x360.png?text=Apple+Watch+S9"],
                "base_price": 529.00,
                "list_price": 529.00,
                "resale_price": 449.00,
                "qty": 6,
                "rating": 4.8,
                "reviews": 156,
                "location": "Vancouver Hub",
                "highlights_json": ["GPS + Cellular", "Always-On display", "Health features", "Latest"],
                "city_availability_json": ["Vancouver", "Ottawa", "Edmonton"],
            },
            {
                "sku": "AIRPODS-PRO-2",
                "title": "AirPods Pro (2nd Generation)",
                "model": "AirPods Pro",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Headphones"].id,
                "condition": "A",
                "description": "Active Noise Cancellation, Spatial Audio, MagSafe Charging Case",
                "images_json": ["https://via.placeholder.com/480x360.png?text=AirPods+Pro"],
                "base_price": 329.00,
                "list_price": 329.00,
                "resale_price": 279.00,
                "qty": 10,
                "rating": 4.9,
                "reviews": 287,
                "location": "Ottawa Lab",
                "highlights_json": ["Noise Cancellation", "Spatial Audio", "MagSafe case", "Premium sound"],
                "city_availability_json": ["Ottawa", "Vancouver", "Edmonton"],
            },
        ]
        
        for product_data in products_data:
            existing = session.exec(select(Product).where(Product.sku == product_data["sku"])).first()
            
            if not existing:
                product = Product(**product_data)
                session.add(product)
                session.commit()
                session.refresh(product)
                print(f"  ✓ Created product: {product.title} (ID: {product.id})")
            else:
                print(f"  - Product already exists: {existing.title}")
        
        # 4. Create test users (optional)
        print("\nCreating test users...")
        test_users_data = [
            {
                "email": "test@example.com",
                "password": "test123",
                "role": "customer",
            },
            {
                "email": "admin@example.com",
                "password": "admin123",
                "role": "admin",
            },
            {
                "email": "evaluator@example.com",
                "password": "eval123",
                "role": "evaluator",
            },
        ]
        
        for user_data in test_users_data:
            existing_user = session.exec(select(User).where(User.email == user_data["email"])).first()
            
            if not existing_user:
                test_user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                )
                session.add(test_user)
                session.commit()
                session.refresh(test_user)
                print(f"  ✓ Created test user: {test_user.email} (ID: {test_user.id}, Role: {test_user.role})")
                print(f"    Password: {user_data['password']}")
            else:
                print(f"  - Test user already exists: {existing_user.email}")
        
        print("\n Database seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  - Brands: {len(brands)}")
        print(f"  - Categories: {len(categories)}")
        print(f"  - Products: {len(products_data)}")
        print(f"  - Test Users: {len(test_users_data)}")
        
    except Exception as e:
        print(f"\n Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

