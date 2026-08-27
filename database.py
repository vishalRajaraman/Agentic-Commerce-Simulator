import sqlite3
import os
import vector_store

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
            endpoint_interact TEXT
        )
    ''')
    
    # Check if empty, then seed
    cursor.execute('SELECT COUNT(*) FROM merchants')
    count = cursor.fetchone()[0]
    if count == 0:
        merchants_data = [
            ("merch_premium_beans", "Premium Beans Co.", "coffee, whole bean, espresso", "/api/merchant/merch_premium_beans/interact"),
            ("merch_budget_roasters", "Budget Roasters", "coffee, bulk, drip", "/api/merchant/merch_budget_roasters/interact"),
            ("merch_tea_house", "The Tea House", "tea, loose leaf", "/api/merchant/merch_tea_house/interact")
        ]
        cursor.executemany('''
            INSERT INTO merchants (merchant_id, name, category, endpoint_interact)
            VALUES (?, ?, ?, ?)
        ''', merchants_data)
        conn.commit()
        
        # Upsert into Pinecone Vector DB ONLY upon seeding the DB
        print("Seeding local database and upserting vectors to Pinecone...")
        vector_store.upsert_merchants(merchants_data)
    
    conn.close()

def search_merchants_by_category(query: str):
    # 1. Query Pinecone for the closest semantic matches
    matched_merchant_ids = vector_store.semantic_search(query)
    
    if not matched_merchant_ids:
        return []

    # 2. Fetch those exact merchants from SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Securely format the IN clause for SQLite
    placeholders = ','.join('?' * len(matched_merchant_ids))
    sql = f'SELECT * FROM merchants WHERE merchant_id IN ({placeholders})'
    
    cursor.execute(sql, matched_merchant_ids)
    all_merchants = cursor.fetchall()
    
    results = [dict(row) for row in all_merchants]
    conn.close()
    
    return results

if __name__ == "__main__":
    init_db()
    print("Database initialized and synced with Pinecone.")
