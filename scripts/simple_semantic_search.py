#!/usr/bin/env python3
"""
Simple semantic search - just one endpoint
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List

import google.generativeai as genai
import numpy as np
import dotenv

dotenv.load_dotenv()


def generate_embedding(text: str, api_key: str) -> List[float]:
    """Generate embedding using Gemini"""
    try:
        genai.configure(api_key=api_key)
        result = genai.embed_content(
            model="gemini-embedding-001", content=text, task_type="semantic_similarity"
        )
        return result["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []


def create_embedding_content(pub: Dict) -> str:
    """Create content for embedding from publication data"""
    keywords = pub.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []

    content = f"""
    Title: {pub.get('title', '')}
    Summary: {pub.get('summary', '')}
    Impact: {pub.get('impact', '')}
    Theme: {pub.get('theme', '')}
    Keywords: {', '.join(keywords)}
    """
    return content.strip()


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not a or not b or len(a) != len(b):
        return 0.0

    a = np.array(a)
    b = np.array(b)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def semantic_search(
    query: str,
    publications: List[Dict],
    embeddings: List[List[float]],
    api_key: str,
    limit: int = 10,
) -> List[Dict]:
    """Simple semantic search function"""
    # Generate embedding for query
    query_embedding = generate_embedding(query, api_key)
    if not query_embedding:
        return []

    # Calculate similarities
    similarities = []
    for i, embedding in enumerate(embeddings):
        if embedding:  # Skip empty embeddings
            similarity = cosine_similarity(query_embedding, embedding)
            similarities.append((i, similarity))

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Get top results
    results = []
    for idx, similarity in similarities[:limit]:
        pub = publications[idx].copy()
        pub["similarity_score"] = round(similarity, 4)
        results.append(pub)

    return results


def load_embeddings(filename: str = "../data/embeddings.json") -> tuple:
    """Load publications and embeddings from file"""
    if not Path(filename).exists():
        return [], []

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("publications", []), data.get("embeddings", [])


def save_embeddings(
    publications: List[Dict],
    embeddings: List[List[float]],
    filename: str = "../data/embeddings.json",
):
    """Save publications and embeddings to file"""
    data = {
        "publications": publications,
        "embeddings": embeddings,
        "metadata": {
            "model": "gemini-embedding-001",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_publications": len(publications),
        },
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Embeddings saved to {filename}")


def generate_embeddings_from_json(
    json_file: str, api_key: str, output_file: str = "../data/embeddings.json"
):
    """Convert JSON publications to embeddings and save"""

    with open(json_file, "r", encoding="utf-8") as f:
        publications = json.load(f)

    print(f"Generating embeddings for {len(publications)} publications...")
    embeddings = []

    for i, pub in enumerate(publications):
        print(
            f"Processing {i+1}/{len(publications)}: {pub.get('title', 'Unknown')[:50]}..."
        )

        # Create content for embedding
        content = create_embedding_content(pub)

        # Generate embedding
        embedding = generate_embedding(content, api_key)
        embeddings.append(embedding)

        # Rate limiting
        time.sleep(1)

    # Save embeddings
    save_embeddings(publications, embeddings, output_file)
    print(f"✅ Generated {len(embeddings)} embeddings")


# Simple usage example
if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("Set GOOGLE_AI_API_KEY environment variable")
        exit(1)



    # Generate embeddings
    generate_embeddings_from_json("../data/scraped_publications.json", api_key, "../data/embeddings.json")

    # Load data
    publications, embeddings = load_embeddings("../data/embeddings.json")

    if not publications:
        print("No embeddings found. Generate them first.")
        exit(1)

    # Search
    results = semantic_search(
        "bone loss in space", publications, embeddings, api_key, limit=3
    )

    print("Search results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title'][:60]}... (Score: {result['similarity_score']})")
