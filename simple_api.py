#!/usr/bin/env python3
"""
Simple API server for semantic search
"""

import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simple_semantic_search import load_embeddings, semantic_search

# Initialize FastAPI app
app = FastAPI(title="Simple Semantic Search API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data
publications = []
embeddings = []


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


@app.on_event("startup")
async def startup():
    """Load data on startup"""
    global publications, embeddings
    publications, embeddings = load_embeddings()
    print(f"Loaded {len(publications)} publications with embeddings")


@app.post("/search")
async def search(request: SearchRequest):
    """Simple search endpoint"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        return {"error": "API key not set"}

    results = semantic_search(
        request.query, publications, embeddings, api_key, request.limit
    )

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Simple Semantic Search API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
