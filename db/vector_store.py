import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "merchant-registry"
DIMENSION = 384 # all-MiniLM-L6-v2 outputs 384-dimensional vectors

pc = Pinecone(api_key=PINECONE_API_KEY)

# Load the local embedding model
# This runs locally and does not require an external API
print("Loading local embedding model (this may take a moment on first run)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_or_create_index():
    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {INDEX_NAME}...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return pc.Index(INDEX_NAME)

def upsert_merchants(merchants_data):
    """
    merchants_data is a list of dicts/tuples: (merchant_id, name, category, endpoint_interact)
    We will embed the 'category' string and upsert it into Pinecone.
    """
    index = get_or_create_index()
    
    vectors_to_upsert = []
    for m in merchants_data:
        merchant_id = m[0]
        category = m[2]
        
        # Generate the embedding vector
        embedding = model.encode(category).tolist()
        
        # Pinecone vector format: (id, values, metadata)
        vectors_to_upsert.append((merchant_id, embedding, {"category": category}))
        
    if vectors_to_upsert:
        print(f"Upserting {len(vectors_to_upsert)} merchants into Pinecone...")
        index.upsert(vectors=vectors_to_upsert)

def semantic_search(query: str, top_k: int = 2):
    """
    Embeds the buyer's query and searches Pinecone for the closest merchants.
    Returns a list of matching merchant_ids.
    """
    index = get_or_create_index()
    
    # 1. Embed the specific query
    query_embedding = model.encode(query).tolist()
    
    # 2. Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=False
    )
    
    # 3. Extract matching merchant_ids
    matched_ids = [match['id'] for match in results['matches']]
    return matched_ids

def upsert_products(products_data):
    """
    products_data is a list of dicts: {"product_id": str, "merchant_id": str, "description": str, "base_price": float, "bundle_rules": str}
    """
    index = get_or_create_index()
    
    vectors_to_upsert = []
    for p in products_data:
        # Embed the description and bundle rules for semantic search
        text_to_embed = f"{p['description']} {p.get('bundle_rules', '')}"
        embedding = model.encode(text_to_embed).tolist()
        
        # Metadata includes merchant_id for filtering
        metadata = {
            "merchant_id": p["merchant_id"],
            "description": p["description"],
            "base_price": p["base_price"],
            "bundle_rules": p.get("bundle_rules", "")
        }
        
        vectors_to_upsert.append((p["product_id"], embedding, metadata))
        
    if vectors_to_upsert:
        print(f"Upserting {len(vectors_to_upsert)} products into Pinecone...")
        index.upsert(vectors=vectors_to_upsert)

def search_merchant_catalog(merchant_id: str, query: str, top_k: int = 5):
    """
    Embeds the buyer's query and searches Pinecone for the closest products,
    filtering strictly by the given merchant_id.
    """
    index = get_or_create_index()
    
    query_embedding = model.encode(query).tolist()
    
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={
            "merchant_id": {"$eq": merchant_id}
        },
        include_metadata=True
    )
    
    matched_products = []
    for match in results['matches']:
        product = match['metadata']
        product['product_id'] = match['id']
        matched_products.append(product)
        
    return matched_products
