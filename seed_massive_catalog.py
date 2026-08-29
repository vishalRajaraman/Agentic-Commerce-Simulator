import vector_store

products_data = [
    # Electronics - merchant_001_electronics
    {
        "product_id": "prod_103_laptop",
        "merchant_id": "merchant_001_electronics",
        "description": "Pro Gaming Laptop 16GB RAM 1TB SSD",
        "base_price": 1200.0,
        "bundle_rules": "Include free gaming mouse if price > $1150. 10% off total if bought with a monitor."
    },
    {
        "product_id": "prod_104_monitor",
        "merchant_id": "merchant_001_electronics",
        "description": "27-inch 4K Gaming Monitor",
        "base_price": 350.0,
        "bundle_rules": "Buy 2 monitors for $600 total"
    },
    {
        "product_id": "prod_105_headphones",
        "merchant_id": "merchant_001_electronics",
        "description": "Wireless Noise Cancelling Headphones",
        "base_price": 250.0,
        "bundle_rules": "Free shipping. Buy with any laptop for $50 off."
    },
    
    # Electronics - merchant_002_electronics
    {
        "product_id": "prod_106_smartwatch",
        "merchant_id": "merchant_002_electronics",
        "description": "Fitness Tracking Smartwatch Pro",
        "base_price": 150.0,
        "bundle_rules": "Buy 2 for $250. Includes extra strap."
    },
    {
        "product_id": "prod_107_tablet",
        "merchant_id": "merchant_002_electronics",
        "description": "10-inch Android Tablet 64GB",
        "base_price": 220.0,
        "bundle_rules": "No free shipping. Bundle with smartwatch for 15% discount on total."
    },
    
    # Clothing - merchant_004_clothing
    {
        "product_id": "prod_301_tshirt",
        "merchant_id": "merchant_004_clothing",
        "description": "Organic Cotton Graphic T-Shirt",
        "base_price": 25.0,
        "bundle_rules": "Buy 3 for $60 total. Free shipping on orders over $50."
    },
    {
        "product_id": "prod_302_jeans",
        "merchant_id": "merchant_004_clothing",
        "description": "Classic Blue Denim Jeans",
        "base_price": 60.0,
        "bundle_rules": "Buy a T-shirt and Jeans together for $75."
    },
    {
        "product_id": "prod_303_jacket",
        "merchant_id": "merchant_004_clothing",
        "description": "Winter Puffer Jacket Waterproof",
        "base_price": 120.0,
        "bundle_rules": "Free winter beanie with purchase. 20% off if buying 2 jackets."
    },

    # Groceries - merchant_006_groceries
    {
        "product_id": "prod_401_apples",
        "merchant_id": "merchant_006_groceries",
        "description": "Organic Fuji Apples 1kg pack",
        "base_price": 5.0,
        "bundle_rules": "Buy 5 packs for $20. Freshness guaranteed."
    },
    {
        "product_id": "prod_402_milk",
        "merchant_id": "merchant_006_groceries",
        "description": "Whole Milk 1 Gallon",
        "base_price": 4.5,
        "bundle_rules": "Buy 2 get 1 free"
    },
    {
        "product_id": "prod_403_bread",
        "merchant_id": "merchant_006_groceries",
        "description": "Artisan Sourdough Loaf",
        "base_price": 6.0,
        "bundle_rules": "Pair with Milk or Apples for $1 off bread."
    },

    # Groceries - merchant_007_groceries
    {
        "product_id": "prod_404_pasta",
        "merchant_id": "merchant_007_groceries",
        "description": "Italian Penne Pasta 500g",
        "base_price": 2.5,
        "bundle_rules": "Buy 10 packs for $20"
    },
    {
        "product_id": "prod_405_sauce",
        "merchant_id": "merchant_007_groceries",
        "description": "Tomato Basil Pasta Sauce 400g jar",
        "base_price": 4.0,
        "bundle_rules": "Pasta Bundle: Buy 2 pasta packs + 2 sauce jars for $10 total."
    }
]

print("Seeding massive catalog into Pinecone...")
vector_store.upsert_products(products_data)
print(f"Successfully upserted {len(products_data)} products into Pinecone!")
