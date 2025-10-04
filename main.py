#!/usr/bin/env python3
"""
NASA Hackathon Project - Main Entry Point
LLM Scraper for NASA Space Biology Publications
"""

import sys
from pathlib import Path

from config import CSV_PATH, GOOGLE_AI_API_KEY, OUTPUT_PATH
from llm_scraper import LLMScraper

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))


def main():
    """
    Main function to run the LLM scraper on all NASA publications
    """
    print("=" * 60)
    print("NASA Hackathon Project - LLM Scraper")
    print("=" * 60)
    print("Starting NASA Publications LLM Scraper...")

    # Check for API key
    if not GOOGLE_AI_API_KEY:
        print("Error: GOOGLE_AI_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_AI_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("GOOGLE_AI_API_KEY=your-api-key-here")
        return

    # Check if CSV file exists
    if not Path(CSV_PATH).exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    try:
        # Initialize scraper
        scraper = LLMScraper()

        # Process all publications
        results = scraper.process_publications_csv(
            csv_path=CSV_PATH,
            output_path=OUTPUT_PATH,
            start_index=0,
            max_publications=1,  # Process all publications
        )

        print(f"\n✅ Scraping complete! Processed {len(results)} publications")
        print(f"📁 Results saved to: {OUTPUT_PATH}")

        # Show brief sample of results
        if results:
            print("\n📋 Sample result:")
            sample = results[0]
            print(f"   Title: {sample['title']}")
            print(f"   Theme: {sample['theme']}")
            print(f"   Authors: {len(sample['authors'])} authors")
            print(f"   Summary: {sample['summary'][:100]}...")

    except Exception as e:
        print(f"Error running scraper: {e}")


if __name__ == "__main__":
    main()
