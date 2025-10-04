#!/usr/bin/env python3
"""
Configuration file for NASA Hackathon LLM Scraper
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# File paths
CSV_PATH = "SB_publications-main/SB_publication_PMC.csv"
OUTPUT_PATH = "nasa_space_biology_publications.json"
