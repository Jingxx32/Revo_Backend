"""
Seed database with sample data for testing.
"""
import json
from datetime import datetime

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
        ]
        
        brands = {}
        for brand_data in brands_data:
            existing = session.exec(
                session.query(Brand).filter(Brand.name == brand_data["name"])
            ).first() if hasattr(session, 'query') else None
            
            if not existing:
                # Check using SQLModel select
                from sqlmodel import select
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
        ]
        
        categories = {}
        for cat_data in categories_data:
            from sqlmodel import select
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
        products_data = [
            {
                "sku": "IPH14-128-MID",
                "title": "iPhone 14 128GB Midnight",
                "model": "iPhone 14",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Certified inspection, Unlocked, Includes charger",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=iPhone+14"]),
                "base_price": 1049.00,
                "list_price": 1049.00,
                "resale_price": 899.00,
                "qty": 5,
                "rating": 4.8,
                "reviews": 128,
                "location": "Ottawa Lab",
                "highlights_json": json.dumps(["Certified inspection", "Unlocked", "Includes charger"]),
                "city_availability_json": json.dumps(["Vancouver", "Ottawa"]),
                "updated_at": "2025-01-04",
            },
            {
                "sku": "MBA-M2-13-512",
                "title": "MacBook Air 13\" M2 (2022)",
                "model": "MacBook Air M2",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Laptop"].id,
                "condition": "B",
                "description": "Battery health 92%, 512GB SSD, 2-year store warranty",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=MacBook+Air"]),
                "base_price": 1599.00,
                "list_price": 1599.00,
                "resale_price": 1349.00,
                "qty": 3,
                "rating": 4.7,
                "reviews": 86,
                "location": "Vancouver Hub",
                "highlights_json": json.dumps(["Battery health 92%", "512GB SSD", "2-year store warranty"]),
                "city_availability_json": json.dumps(["Vancouver", "Edmonton"]),
                "updated_at": "2025-01-02",
            },
            {
                "sku": "IPAD-PRO-11-256",
                "title": "iPad Pro 11\" Wi-Fi 256GB",
                "model": "iPad Pro",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Tablet"].id,
                "condition": "A",
                "description": "Apple Pencil 2 support, Liquid Retina, Store warranty",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=iPad+Pro"]),
                "base_price": 1199.00,
                "list_price": 1199.00,
                "resale_price": 1049.00,
                "qty": 4,
                "rating": 4.9,
                "reviews": 64,
                "location": "Edmonton Studio",
                "highlights_json": json.dumps(["Apple Pencil 2 support", "Liquid Retina", "Store warranty"]),
                "city_availability_json": json.dumps(["Edmonton", "Ottawa"]),
                "updated_at": "2024-12-28",
            },
            {
                "sku": "GS23-256-PB",
                "title": "Galaxy S23 256GB Phantom Black",
                "model": "Galaxy S23",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Phone"].id,
                "condition": "C",
                "description": "Dynamic AMOLED, Unlocked, Includes fast charger",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=Galaxy+S23"]),
                "base_price": 999.00,
                "list_price": 999.00,
                "resale_price": 879.00,
                "qty": 6,
                "rating": 4.6,
                "reviews": 142,
                "location": "Vancouver Hub",
                "highlights_json": json.dumps(["Dynamic AMOLED", "Unlocked", "Includes fast charger"]),
                "city_availability_json": json.dumps(["Vancouver", "Edmonton"]),
                "updated_at": "2025-01-05",
            },
            {
                "sku": "GB3-PRO-14-1TB",
                "title": "Galaxy Book3 Pro 14\"",
                "model": "Galaxy Book3",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Laptop"].id,
                "condition": "B",
                "description": "Intel Evo, 1TB SSD, Studio Mode camera",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=Galaxy+Book3"]),
                "base_price": 1499.00,
                "list_price": 1499.00,
                "resale_price": 1249.00,
                "qty": 2,
                "rating": 4.5,
                "reviews": 57,
                "location": "Ottawa Lab",
                "highlights_json": json.dumps(["Intel Evo", "1TB SSD", "Studio Mode camera"]),
                "city_availability_json": json.dumps(["Ottawa"]),
                "updated_at": "2024-12-21",
            },
            {
                "sku": "GTAB-S9-256",
                "title": "Galaxy Tab S9 Wi-Fi 256GB",
                "model": "Galaxy Tab S9",
                "brand_id": brands["Samsung"].id,
                "category_id": categories["Tablet"].id,
                "condition": "A",
                "description": "S Pen included, 120Hz display, IP68",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=Galaxy+Tab"]),
                "base_price": 1099.00,
                "list_price": 1099.00,
                "resale_price": 899.00,
                "qty": 4,
                "rating": 4.7,
                "reviews": 74,
                "location": "Edmonton Studio",
                "highlights_json": json.dumps(["S Pen included", "120Hz display", "IP68"]),
                "city_availability_json": json.dumps(["Edmonton", "Vancouver"]),
                "updated_at": "2025-01-03",
            },
            {
                "sku": "IPH15-256-BLUE",
                "title": "iPhone 15 256GB Blue",
                "model": "iPhone 15",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Phone"].id,
                "condition": "A",
                "description": "Certified inspection, Unlocked, Includes USB-C cable",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=iPhone+15"]),
                "base_price": 1199.00,
                "list_price": 1199.00,
                "resale_price": 1099.00,
                "qty": 8,
                "rating": 4.9,
                "reviews": 203,
                "location": "Vancouver Hub",
                "highlights_json": json.dumps(["Certified inspection", "Unlocked", "Includes USB-C cable"]),
                "city_availability_json": json.dumps(["Vancouver", "Ottawa", "Edmonton"]),
                "updated_at": "2025-01-06",
            },
            {
                "sku": "MBP-14-M3-512",
                "title": "MacBook Pro 14\" M3 512GB",
                "model": "MacBook Pro M3",
                "brand_id": brands["Apple"].id,
                "category_id": categories["Laptop"].id,
                "condition": "A",
                "description": "M3 chip, Liquid Retina XDR, 18-hour battery",
                "images_json": json.dumps(["https://via.placeholder.com/480x360.png?text=MacBook+Pro"]),
                "base_price": 1999.00,
                "list_price": 1999.00,
                "resale_price": 1799.00,
                "qty": 2,
                "rating": 4.8,
                "reviews": 95,
                "location": "Ottawa Lab",
                "highlights_json": json.dumps(["M3 chip", "Liquid Retina XDR", "18-hour battery"]),
                "city_availability_json": json.dumps(["Ottawa", "Vancouver"]),
                "updated_at": "2025-01-07",
            },
        ]
        
        for product_data in products_data:
            from sqlmodel import select
            existing = session.exec(select(Product).where(Product.sku == product_data["sku"])).first()
            
            if not existing:
                product = Product(**product_data)
                session.add(product)
                session.commit()
                session.refresh(product)
                print(f"  ✓ Created product: {product.title} (ID: {product.id})")
            else:
                print(f"  - Product already exists: {existing.title}")
        
        # 4. Create a test user (optional)
        print("\nCreating test user...")
        from sqlmodel import select
        existing_user = session.exec(select(User).where(User.email == "test@example.com")).first()
        
        if not existing_user:
            test_user = User(
                email="test@example.com",
                password_hash=hash_password("test123"),
                role="customer",
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            print(f"  ✓ Created test user: {test_user.email} (ID: {test_user.id})")
            print("  Password: test123")
        else:
            print(f"  - Test user already exists: {existing_user.email}")
        
        print("\n✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

