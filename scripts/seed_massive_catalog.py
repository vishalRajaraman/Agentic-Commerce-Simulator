from db import vector_store

products_data = [
    {
        "product_id": "prod_103_laptop",
        "merchant_id": "merchant_001_electronics",
        "description": "Pro Gaming Laptop 16GB RAM 1TB SSD",
        "base_price": 96000.0,
        "bundle_rules": "Include free gaming mouse if price > ₹92000. 10% off total if bought with a monitor."
    },
    {
        "product_id": "prod_103_laptop_alt",
        "merchant_id": "merchant_002_electronics",
        "description": "Pro Gaming Laptop 16GB RAM 1TB SSD (Alt)",
        "base_price": 86400.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_104_monitor",
        "merchant_id": "merchant_001_electronics",
        "description": "27-inch 4K Gaming Monitor",
        "base_price": 28000.0,
        "bundle_rules": "Buy 2 monitors for ₹48000 total"
    },
    {
        "product_id": "prod_104_monitor_alt",
        "merchant_id": "merchant_002_electronics",
        "description": "27-inch 4K Gaming Monitor (Alt)",
        "base_price": 25200.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_105_headphones",
        "merchant_id": "merchant_001_electronics",
        "description": "Wireless Noise Cancelling Headphones",
        "base_price": 20000.0,
        "bundle_rules": "Free shipping. Buy with any laptop for ₹4000 off."
    },
    {
        "product_id": "prod_105_headphones_alt",
        "merchant_id": "merchant_002_electronics",
        "description": "Wireless Noise Cancelling Headphones (Alt)",
        "base_price": 18000.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_106_smartwatch",
        "merchant_id": "merchant_002_electronics",
        "description": "Fitness Tracking Smartwatch Pro",
        "base_price": 12000.0,
        "bundle_rules": "Buy 2 for ₹20000. Includes extra strap."
    },
    {
        "product_id": "prod_106_smartwatch_alt",
        "merchant_id": "merchant_003_electronics",
        "description": "Fitness Tracking Smartwatch Pro (Alt)",
        "base_price": 10800.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_107_tablet",
        "merchant_id": "merchant_002_electronics",
        "description": "10-inch Android Tablet 64GB",
        "base_price": 17600.0,
        "bundle_rules": "No free shipping. Bundle with smartwatch for 15% discount on total."
    },
    {
        "product_id": "prod_107_tablet_alt",
        "merchant_id": "merchant_003_electronics",
        "description": "10-inch Android Tablet 64GB (Alt)",
        "base_price": 15840.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_301_tshirt",
        "merchant_id": "merchant_004_clothing",
        "description": "Organic Cotton Graphic T-Shirt",
        "base_price": 2000.0,
        "bundle_rules": "Buy 3 for ₹4800 total. Free shipping on orders over ₹4000."
    },
    {
        "product_id": "prod_301_tshirt_alt",
        "merchant_id": "merchant_005_clothing",
        "description": "Organic Cotton Graphic T-Shirt (Alt)",
        "base_price": 1800.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_302_jeans",
        "merchant_id": "merchant_004_clothing",
        "description": "Classic Blue Denim Jeans",
        "base_price": 4800.0,
        "bundle_rules": "Buy a T-shirt and Jeans together for ₹6000."
    },
    {
        "product_id": "prod_302_jeans_alt",
        "merchant_id": "merchant_005_clothing",
        "description": "Classic Blue Denim Jeans (Alt)",
        "base_price": 4320.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_303_jacket",
        "merchant_id": "merchant_004_clothing",
        "description": "Winter Puffer Jacket Waterproof",
        "base_price": 9600.0,
        "bundle_rules": "Free winter beanie with purchase. 20% off if buying 2 jackets."
    },
    {
        "product_id": "prod_303_jacket_alt",
        "merchant_id": "merchant_005_clothing",
        "description": "Winter Puffer Jacket Waterproof (Alt)",
        "base_price": 8640.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_401_apples",
        "merchant_id": "merchant_006_groceries",
        "description": "Organic Fuji Apples 1kg pack",
        "base_price": 400.0,
        "bundle_rules": "Buy 5 packs for ₹1600. Freshness guaranteed."
    },
    {
        "product_id": "prod_401_apples_alt",
        "merchant_id": "merchant_007_groceries",
        "description": "Organic Fuji Apples 1kg pack (Alt)",
        "base_price": 360.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_402_milk",
        "merchant_id": "merchant_006_groceries",
        "description": "Whole Milk 1 Gallon",
        "base_price": 360.0,
        "bundle_rules": "Buy 2 get 1 free"
    },
    {
        "product_id": "prod_402_milk_alt",
        "merchant_id": "merchant_007_groceries",
        "description": "Whole Milk 1 Gallon (Alt)",
        "base_price": 324.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_403_bread",
        "merchant_id": "merchant_006_groceries",
        "description": "Artisan Sourdough Loaf",
        "base_price": 480.0,
        "bundle_rules": "Pair with Milk or Apples for ₹80 off bread."
    },
    {
        "product_id": "prod_403_bread_alt",
        "merchant_id": "merchant_007_groceries",
        "description": "Artisan Sourdough Loaf (Alt)",
        "base_price": 432.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_404_pasta",
        "merchant_id": "merchant_007_groceries",
        "description": "Italian Penne Pasta 500g",
        "base_price": 200.0,
        "bundle_rules": "Buy 10 packs for ₹1600"
    },
    {
        "product_id": "prod_404_pasta_alt",
        "merchant_id": "merchant_001_groceries",
        "description": "Italian Penne Pasta 500g (Alt)",
        "base_price": 180.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_405_sauce",
        "merchant_id": "merchant_007_groceries",
        "description": "Tomato Basil Pasta Sauce 400g jar",
        "base_price": 320.0,
        "bundle_rules": "Pasta Bundle: Buy 2 pasta packs + 2 sauce jars for ₹800 total."
    },
    {
        "product_id": "prod_405_sauce_alt",
        "merchant_id": "merchant_001_groceries",
        "description": "Tomato Basil Pasta Sauce 400g jar (Alt)",
        "base_price": 288.0,
        "bundle_rules": "No bundle rules"
    }
]

print("Seeding massive catalog into Pinecone...")
vector_store.upsert_products(products_data)
print(f"Successfully upserted {len(products_data)} products into Pinecone!")
