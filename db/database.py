import sqlite3
import os
from db import vector_store


DB_PATH = "registry.db"



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

def get_merchant_endpoint(merchant_id: str) -> str:
    """Fetch the fully qualified endpoint URL for a given merchant"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT endpoint_interact FROM merchants WHERE merchant_id = ?', (merchant_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return ""

def get_merchant_public_key(merchant_id: str) -> str:
    """Fetch the public key for a given merchant"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT public_key FROM merchants WHERE merchant_id = ?', (merchant_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return ""


