import vector_store

products_data = [
    {
        "product_id": "prod_101_phone",
        "merchant_id": "merchant_001_electronics",
        "description": "Latest 5G Smartphone with 128GB storage",
        "base_price": 600.0,
        "bundle_rules": "Include free protective case if price > $550"
    },
    {
        "product_id": "prod_102_phone",
        "merchant_id": "merchant_002_electronics",
        "description": "Budget 4G Smartphone",
        "base_price": 200.0,
        "bundle_rules": "No bundle rules"
    },
    {
        "product_id": "prod_201_coffee",
        "merchant_id": "merchant_007_groceries",
        "description": "Premium Arabica Coffee Beans 1kg",
        "base_price": 30.0,
        "bundle_rules": "Buy 3 for $75"
    }
]

print("Seeding extra mock products into Pinecone...")
vector_store.upsert_products(products_data)
print("Done!")
