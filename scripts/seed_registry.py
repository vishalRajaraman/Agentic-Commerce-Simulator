import sqlite3
import os
import sys

# Add root directory to sys.path so we can import from db and core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import vector_store
from core import crypto_utils

DB_PATH = "registry.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create merchants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            merchant_id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            endpoint_interact TEXT,
            public_key TEXT
        )
    ''')
    
    # Check if empty, then seed
    cursor.execute('SELECT COUNT(*) FROM merchants')
    count = cursor.fetchone()[0]
    if count == 0:
        base_merchants = [
            # Electronics
            ("merchant_001_electronics", "Electro World", "electronics, laptops, smartphones", "http://localhost:8002/api/merchant/merchant_001_electronics/interact"),
            ("merchant_002_electronics", "Tech Haven", "electronics, gadgets, accessories", "http://localhost:8002/api/merchant/merchant_002_electronics/interact"),
            ("merchant_003_electronics", "Gizmo Hub", "electronics, smart home, audio", "http://localhost:8002/api/merchant/merchant_003_electronics/interact"),
            
            # Clothing
            ("merchant_004_clothing", "Fashion Forward", "clothing, apparel, fashion", "http://localhost:8002/api/merchant/merchant_004_clothing/interact"),
            ("merchant_005_clothing", "Urban Wear", "clothing, streetwear, shoes", "http://localhost:8002/api/merchant/merchant_005_clothing/interact"),
            
            # Groceries
            ("merchant_006_groceries", "Fresh Market", "groceries, fresh produce, meat", "http://localhost:8002/api/merchant/merchant_006_groceries/interact"),
            ("merchant_007_groceries", "Pantry Essentials", "groceries, dry goods, snacks", "http://localhost:8002/api/merchant/merchant_007_groceries/interact")
        ]
        
        merchants_data = []
        os.makedirs("merchant_keys", exist_ok=True)
        
        for m in base_merchants:
            merchant_id = m[0]
            # Generate PKI key pair for the merchant
            priv_pem, pub_pem = crypto_utils.generate_rsa_key_pair()
            # Save private key securely
            with open(f"merchant_keys/{merchant_id}_private.pem", "w") as f:
                f.write(priv_pem)
            
            # Append public key to row
            merchants_data.append((*m, pub_pem))
            
        cursor.executemany('''
            INSERT INTO merchants (merchant_id, name, category, endpoint_interact, public_key)
            VALUES (?, ?, ?, ?, ?)
        ''', merchants_data)
        conn.commit()
        
        # Upsert into Pinecone Vector DB ONLY upon seeding the DB
        print("Seeding local database and upserting vectors to Pinecone...")
        vector_store.upsert_merchants(base_merchants)
        
        products_data = [
            {
                "product_id": "prod_001_socks",
                "merchant_id": "merchant_004_clothing",
                "description": "High-quality black cotton socks",
                "base_price": 20.0,
                "bundle_rules": "Buy 2 for $35"
            },
            {
                "product_id": "prod_002_socks",
                "merchant_id": "merchant_005_clothing",
                "description": "Premium black socks",
                "base_price": 22.0,
                "bundle_rules": "Free shipping over $40"
            }
        ]
        print("Seeding mock products into Pinecone...")
        vector_store.upsert_products(products_data)
    
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and synced with Pinecone.")
