#!/usr/bin/env python3
"""
LLM Scraper for NASA Space Biology Publications
Uses Google Gemini to extract structured data from publication webpages
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import Browser, Page, sync_playwright

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PublicationData:
    """Data structure for extracted publication information"""

    title: str
    authors: List[str]
    abstract: str
    headings: List[str]
    summary: str = ""  # AI-generated summary
    impact: str = ""  # AI-generated impact assessment
    theme: str = ""  # AI-generated theme string
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    journal: Optional[str] = None
    keywords: List[str] = None
    url: str = ""


class LLMScraper:
    """LLM-powered scraper for extracting structured data from publication webpages"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM scraper with Gemini API

        Args:
            api_key: Google AI API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google AI API key is required. Set GOOGLE_AI_API_KEY environment variable."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Initialize browser
        self.browser: Optional[Browser] = None
        self.playwright = None

    def start_browser(self):
        """Start the Playwright browser"""
        if not self.browser:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)

    def close_browser(self):
        """Close the Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def extract_text_from_url(self, url: str) -> str:
        """
        Extract text content from a URL using Playwright

        Args:
            url: The URL to scrape

        Returns:
            Extracted text content
        """
        try:
            self.start_browser()
            page = self.browser.new_page()

            # Set a reasonable timeout
            page.set_default_timeout(30000)

            # Navigate to the page
            page.goto(url, wait_until="networkidle")

            # Wait a bit for dynamic content to load
            page.wait_for_timeout(2000)

            # Extract text content
            text_content = page.evaluate(
                """
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(el => el.remove());
                    
                    // Get main content area (common selectors for academic papers)
                    const contentSelectors = [
                        'article',
                        '.article-content',
                        '.content',
                        '.main-content',
                        '#content',
                        '.abstract',
                        '.full-text',
                        'main'
                    ];
                    
                    let content = null;
                    for (const selector of contentSelectors) {
                        content = document.querySelector(selector);
                        if (content) break;
                    }
                    
                    // Fallback to body if no specific content area found
                    if (!content) {
                        content = document.body;
                    }
                    
                    return content ? content.innerText : document.body.innerText;
                }
            """
            )

            page.close()
            return text_content

        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return ""

    def generate_analysis(
        self,
        title: str,
        abstract: str,
        headings: List[str],
        authors: List[str] = None,
        journal: str = None,
        keywords: List[str] = None,
        doi: str = None,
    ) -> Dict[str, str]:
        """
        Generate summary, impact assessment, and theme in a single API call

        Args:
            title: Publication title
            abstract: Publication abstract
            headings: List of section headings
            authors: List of authors
            journal: Journal name
            keywords: List of keywords
            doi: DOI identifier

        Returns:
            Dictionary with 'summary', 'impact', and 'theme' keys
        """
        try:
            # Create a comprehensive analysis prompt
            prompt = f"""
            Analyze this NASA Space Biology publication and provide three components in JSON format.
            
            Title: {title}
            
            Authors: {', '.join(authors) if authors else 'Not available'}
            
            Journal: {journal if journal else 'Not specified'}
            
            DOI: {doi if doi else 'Not available'}
            
            Abstract: {abstract}
            
            Section Headings: {', '.join(headings) if headings else 'Not available'}
            
            Keywords: {', '.join(keywords) if keywords else 'Not available'}
            
            Please provide a JSON response with exactly these four fields:
            
            {{
                "summary": "A 2-3 sentence summary that captures: 1) The main research question or objective, 2) Key findings or conclusions (include specific numbers, percentages, or statistics if mentioned), 3) Significance or implications. Use all available information and include concrete statistics if available.",
                
                "impact": "A 2-3 sentence impact assessment that evaluates: 1) Scientific significance (advances in knowledge, methodology, or understanding), 2) Practical applications (space missions, astronaut health, countermeasures, etc.), 3) Broader implications (terrestrial applications, future research directions). Consider journal prestige, author expertise, and include concrete statistics if available.",
                
                "theme": "A concise theme string that best categorizes this publication. Choose from: Microgravity Effects, Space Radiation, Bone & Muscle Health, Cardiovascular System, Immune System, Plant Biology, Cell Biology, Genetics & Genomics, Countermeasures, Technology Development, Mission Planning, Health Monitoring. Be specific and descriptive (e.g., 'Microgravity Effects on Bone Health' or 'Space Radiation Genetics').",
                
                "keywords": "A list of 5-8 relevant keywords that describe this publication. If keywords are already provided in the input, use those exact keywords. If no keywords are available, generate appropriate keywords based on the content. Focus on scientific terms, biological systems, space-related concepts, and research methods. Return as a JSON array of strings."
            }}
            
            Return ONLY valid JSON, no additional text or explanations.
            """

            response = self.model.generate_content(prompt)

            # Parse the JSON response
            try:
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                analysis_data = json.loads(response_text)

                return {
                    "summary": analysis_data.get("summary", ""),
                    "impact": analysis_data.get("impact", ""),
                    "theme": analysis_data.get("theme", ""),
                    "keywords": analysis_data.get("keywords", []),
                }

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse analysis JSON response: {e}")
                logger.error(f"Response was: {response.text}")
                return {"summary": "", "impact": "", "theme": "", "keywords": []}

        except Exception as e:
            logger.error(f"Error generating analysis: {e}")
            return {"summary": "", "impact": "", "theme": "", "keywords": []}

    def extract_publication_data(self, url: str, title: str) -> PublicationData:
        """
        Extract structured publication data using Gemini LLM

        Args:
            url: The publication URL
            title: The publication title from CSV

        Returns:
            PublicationData object with extracted information
        """
        try:
            # Extract text content from the webpage
            text_content = self.extract_text_from_url(url)

            if not text_content:
                logger.warning(f"No content extracted from {url}")
                return PublicationData(
                    title=title, authors=[], abstract="", headings=[], url=url
                )

            # Truncate content if too long (Gemini has token limits)
            max_chars = 50000  # Conservative limit
            if len(text_content) > max_chars:
                text_content = text_content[:max_chars] + "..."

            # Create prompt for Gemini
            prompt = f"""
            Extract structured information from this academic publication webpage content.
            
            Original title from dataset: "{title}"
            URL: {url}
            
            Webpage content:
            {text_content}
            
            Please extract the following information and return it as a JSON object:
            {{
                "title": "The full title of the publication",
                "authors": ["List of author names"],
                "abstract": "The abstract or summary of the paper",
                "headings": ["List of main section headings"],
                "doi": "DOI if available, otherwise null",
                "publication_date": "Publication date if available, otherwise null",
                "journal": "Journal name if available, otherwise null",
                "keywords": ["List of keywords if available"]
            }}
            
            Important guidelines:
            - If information is not available, use null for strings or empty arrays for lists
            - Extract the most relevant and accurate information
            - For headings, focus on main sections like Introduction, Methods, Results, Discussion, Conclusion
            - For authors, extract all author names as they appear
            - For abstract, get the complete abstract text
            - Return ONLY valid JSON, no additional text or explanations
            """

            # Call Gemini API
            response = self.model.generate_content(prompt)

            # Parse the JSON response
            try:
                # Extract JSON from response (sometimes Gemini adds extra text)
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

                data = json.loads(response_text)

                # Generate all analysis components in a single API call
                analysis = self.generate_analysis(
                    title=data.get("title", title),
                    abstract=data.get("abstract", ""),
                    headings=data.get("headings", []),
                    authors=data.get("authors", []),
                    journal=data.get("journal"),
                    keywords=data.get("keywords", []),
                    doi=data.get("doi"),
                )

                summary = analysis["summary"]
                impact = analysis["impact"]
                theme = analysis["theme"]
                generated_keywords = analysis["keywords"]

                # Use original keywords if available, otherwise use generated keywords
                original_keywords = data.get("keywords", [])
                if original_keywords:
                    # Use original keywords as-is (they're already provided by the publication)
                    all_keywords = original_keywords
                else:
                    # Use generated keywords only if no original keywords
                    all_keywords = generated_keywords

                return PublicationData(
                    title=data.get("title", title),
                    authors=data.get("authors", []),
                    abstract=data.get("abstract", ""),
                    headings=data.get("headings", []),
                    summary=summary,
                    impact=impact,
                    theme=theme,
                    doi=data.get("doi"),
                    publication_date=data.get("publication_date"),
                    journal=data.get("journal"),
                    keywords=all_keywords,
                    url=url,
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Gemini: {e}")
                logger.error(f"Response was: {response.text}")
                return PublicationData(
                    title=title, authors=[], abstract="", headings=[], url=url
                )

        except Exception as e:
            logger.error(f"Error extracting data from {url}: {e}")
            return PublicationData(
                title=title, authors=[], abstract="", headings=[], url=url
            )

    def process_publications_csv(
        self,
        csv_path: str,
        output_path: str,
        start_index: int = 0,
        max_publications: Optional[int] = None,
    ) -> List[Dict]:
        """
        Process all publications from the CSV file

        Args:
            csv_path: Path to the CSV file
            output_path: Path to save the JSON output
            start_index: Index to start processing from (for resuming)
            max_publications: Maximum number of publications to process (None for all)

        Returns:
            List of processed publication data
        """
        # Read CSV file
        df = pd.read_csv(csv_path)

        # Apply limits
        if max_publications:
            df = df.iloc[start_index : start_index + max_publications]
        else:
            df = df.iloc[start_index:]

        logger.info(
            f"Processing {len(df)} publications starting from index {start_index}"
        )

        results = []

        try:
            for index, row in df.iterrows():
                title = row["Title"]
                url = row["Link"]

                logger.info(f"Processing {index + 1}/{len(df)}: {title[:50]}...")

                # Extract data using LLM
                publication_data = self.extract_publication_data(url, title)

                # Convert to dictionary for JSON serialization
                result_dict = {
                    "index": int(index),
                    "title": publication_data.title,
                    "authors": publication_data.authors,
                    "abstract": publication_data.abstract,
                    "headings": publication_data.headings,
                    "summary": publication_data.summary,
                    "impact": publication_data.impact,
                    "theme": publication_data.theme,
                    "doi": publication_data.doi,
                    "publication_date": publication_data.publication_date,
                    "journal": publication_data.journal,
                    "keywords": publication_data.keywords,
                    "url": publication_data.url,
                    "original_title": title,
                }

                results.append(result_dict)

                # Save intermediate results every 10 publications
                if (index + 1) % 10 == 0:
                    self._save_results(results, output_path)
                    logger.info(
                        f"Saved intermediate results after {index + 1} publications"
                    )

                # Add delay to be respectful to the servers
                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("Processing interrupted by user")
        except Exception as e:
            logger.error(f"Error during processing: {e}")
        finally:
            # Save final results
            self._save_results(results, output_path)
            self.close_browser()

        logger.info(f"Processing complete. Results saved to {output_path}")
        return results

    def _save_results(self, results: List[Dict], output_path: str):
        """Save results to JSON file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


def main():
    """Main function to run the scraper"""
    # Check for API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("Error: GOOGLE_AI_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_AI_API_KEY='your-api-key-here'")
        return

    # Initialize scraper
    scraper = LLMScraper()

    # Process publications
    csv_path = "../data/SB_publications-main/SB_publication_PMC.csv"
    output_path = "../data/scraped_publications.json"


    # check the index to resume from
    start_index = 0
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        start_index = len(results)
    
    print(f"Resuming from index {start_index}")

    # For testing, process only first 5 publications
    # Remove max_publications parameter to process all
    results = scraper.process_publications_csv(
        csv_path=csv_path,
        output_path=output_path,
        start_index=start_index,
        max_publications=None,  # Remove this line to process all publications
    )

    print(f"Scraping complete! Processed {len(results)} publications")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
