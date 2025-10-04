# NASA Hackathon Project - LLM Scraper

A Python project for the NASA Hackathon featuring an LLM-powered scraper that extracts structured data from NASA Space Biology publications using Google's Gemini AI.

## Features

- **LLM-Powered Scraping**: Uses Google Gemini to extract structured data from publication webpages
- **Comprehensive Data Extraction**: Extracts title, authors, abstract, headings, DOI, publication date, journal, and keywords
- **Robust Web Scraping**: Uses Playwright for reliable webpage content extraction
- **Batch Processing**: Processes all 608 NASA Space Biology publications with progress tracking
- **Error Handling**: Includes retry logic and graceful error handling
- **JSON Output**: Saves extracted data in structured JSON format

## Quick Start

### 1. Automated Setup
```bash
# Run the setup script (installs dependencies and configures environment)
python setup.py
```

### 2. Get Google AI API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
```bash
GOOGLE_AI_API_KEY=your-actual-api-key-here
```

### 3. Test the Setup
```bash
# Run tests to verify everything is working
python test_scraper.py
```

### 4. Run the Scraper
```bash
# Start the interactive scraper
python main.py
```

## Manual Setup (Alternative)

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure API Key
Create a `.env` file with your Google AI API key:
```bash
GOOGLE_AI_API_KEY=your-google-ai-api-key-here
```

## Usage

### Interactive Mode
```bash
python main.py
```
Choose from the menu:
- Test with 5 publications
- Process all 608 publications
- Custom settings (start index, max publications)

### Programmatic Usage
```python
from llm_scraper import LLMScraper

# Initialize scraper
scraper = LLMScraper()

# Process publications
results = scraper.process_publications_csv(
    csv_path="SB_publications-main/SB_publication_PMC.csv",
    output_path="scraped_publications.json",
    max_publications=10  # Process first 10 publications
)
```

## Output Format

The scraper generates JSON files with the following structure:

```json
[
  {
    "index": 0,
    "title": "Full publication title",
    "authors": ["Author 1", "Author 2", "..."],
    "abstract": "Complete abstract text...",
    "headings": ["Introduction", "Methods", "Results", "..."],
    "doi": "10.1234/example.doi",
    "publication_date": "2023-01-01",
    "journal": "Journal Name",
    "keywords": ["keyword1", "keyword2", "..."],
    "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/...",
    "original_title": "Original title from CSV"
  }
]
```

## Project Structure
```
NASA-Hackathon/
├── main.py                 # Main application with interactive menu
├── llm_scraper.py         # Core LLM scraper implementation
├── config.py              # Configuration settings
├── setup.py               # Automated setup script
├── test_scraper.py        # Test suite
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Code formatting configuration
├── README.md             # This file
├── .env                  # Environment variables (create this)
├── dev-tools/            # Development utilities
│   ├── __init__.py
│   └── dev_server.py     # Development environment
└── SB_publications-main/ # NASA Space Biology publications data
    ├── README.md
    └── SB_publication_PMC.csv  # 608 publications since 2010
```

## Development

### Development Mode
```bash
# Start development environment (auto-reload + auto-format + linting)
python dev-tools/dev_server.py
```

### Code Quality
The project includes automated code formatting and linting:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting

## Data Source

The project includes NASA Space Biology publications data:
- **608 publications** published since 2010
- **Open access** full-text articles from PubMed Central
- **Diverse topics**: Microgravity effects, space radiation, bone/muscle atrophy, plant biology, immune system changes, gene expression studies

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Google AI API key is correctly set in the `.env` file
2. **Playwright Issues**: Run `playwright install chromium` to install browser dependencies
3. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
4. **CSV Not Found**: Verify the `SB_publications-main/SB_publication_PMC.csv` file exists

### Getting Help

1. Run the test suite: `python test_scraper.py`
2. Check the logs for detailed error messages
3. Start with a small number of publications for testing

## Performance Notes

- **Processing Time**: ~2-3 seconds per publication (includes API calls and web scraping)
- **Rate Limiting**: Built-in 2-second delay between requests to be respectful to servers
- **Memory Usage**: Processes publications in batches to manage memory
- **Resume Capability**: Can resume from any index if interrupted

## Contributing

This project follows simple, non-over-engineered code principles. Contributions are welcome!
