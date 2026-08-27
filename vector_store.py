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
