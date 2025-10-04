#!/usr/bin/env python3
"""
Start the simple semantic search system
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Start the simple system"""
    print("🚀 Starting Simple NASA Semantic Search")
    print("=" * 50)

    # Check if embeddings exist
    if not Path("embeddings.json").exists():
        print("❌ Embeddings not found!")
        print("Run: python convert_to_embeddings.py")
        return

    # Check API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("❌ Set GOOGLE_AI_API_KEY environment variable")
        return

    print("✅ Embeddings found")
    print("✅ API key set")

    print("\n🌐 Starting API server...")
    print("📡 API: http://localhost:8000")
    print("\n🖥️  To start frontend:")
    print("   cd frontend")
    print("   npm start")
    print("\n🔍 Then switch to 'Semantic Search' mode in the UI!")
    print("\nPress Ctrl+C to stop")

    try:
        subprocess.run([sys.executable, "simple_api.py"])
    except KeyboardInterrupt:
        print("\n👋 Stopped")


if __name__ == "__main__":
    main()
