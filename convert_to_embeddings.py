#!/usr/bin/env python3
"""
Convert JSON publications to embeddings and save
"""

import os

from simple_semantic_search import generate_embeddings_from_json


def main():
    """Convert publications JSON to embeddings"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ Set GOOGLE_AI_API_KEY environment variable")
        return

    # Convert JSON to embeddings
    generate_embeddings_from_json(
        json_file="nasa_space_biology_publications.json",
        api_key=api_key,
        output_file="embeddings.json",
    )


if __name__ == "__main__":
    main()
