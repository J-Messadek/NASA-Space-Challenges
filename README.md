# NASA Space Biology Publications Platform

A comprehensive platform for exploring NASA Space Biology publications featuring semantic search, knowledge graph visualization, and advanced analytics.

## Features

### 🔍 **Semantic Search**
- **AI-Powered Search**: Uses Google Gemini embeddings for semantic similarity search
- **Smart Fallback**: Automatic semantic search when keyword search returns no results
- **High-Quality Results**: Only returns results with 80%+ similarity scores
- **Real-time Search**: Fast keyword search with intelligent semantic enhancement

### 📊 **Knowledge Graph**
- **Interactive Visualization**: Explore relationships between authors, publications, and themes
- **Network Analysis**: View collaboration networks and research connections
- **Centrality Analysis**: Identify key researchers and influential publications
- **Dynamic Filtering**: Search and filter nodes in real-time

### 📈 **Analytics Dashboard**
- **Publication Statistics**: Comprehensive overview of research trends
- **Author Analysis**: Research output and collaboration patterns
- **Theme Distribution**: Visual breakdown of research areas
- **Impact Metrics**: Publication and citation analysis

### 🚀 **Modern Web Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live search results and graph interactions
- **Intuitive Navigation**: Easy switching between search, graph, and analytics
- **Performance Optimized**: Fast loading and smooth interactions
- **NASA Design System**: Official NASA Space Challenges branding with Overpass and Fira Sans typography
- **Bioverses Branding**: Custom logo and favicon integration

## Quick Start

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file with your API keys:
```bash
# Google AI API Key for semantic search
GOOGLE_AI_API_KEY=your-google-ai-api-key-here

# API URL for frontend (optional - defaults to localhost:5000)
REACT_APP_API_URL=http://localhost:5000
```

### 3. Get Google AI API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### 4. Start the Application
```bash
# Start the backend API server
python app.py

# In a new terminal, start the frontend
cd frontend
npm install
npm start
```

### 5. Access the Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

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
├── app.py                    # Main Flask API server
├── simple_semantic_search.py # Semantic search implementation
├── embeddings.json          # Pre-generated embeddings for semantic search
├── nasa_space_biology_publications.json # Processed publications data
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── App.js          # Main application component
│   │   ├── components/
│   │   │   ├── GraphVisualization.js # Knowledge graph component
│   │   │   └── GraphAnalysis.js     # Analytics dashboard
│   │   └── .env            # Frontend environment variables
│   └── package.json        # Frontend dependencies
├── scripts/                 # Data processing scripts
│   ├── build_knowledge_graph.py # Knowledge graph builder
│   ├── llm_scraper.py      # Publication scraper
│   └── simple_semantic_search.py # Semantic search utilities
├── data/                    # Data files
│   ├── knowledge_graph/    # Knowledge graph data
│   └── embeddings.json     # Semantic search embeddings
└── SB_publications-main/   # Source publication data
    └── SB_publication_PMC.csv
```

## API Configuration

### Environment Variables
The application uses environment variables for configuration:

```bash
# Required: Google AI API Key for semantic search
GOOGLE_AI_API_KEY=your-google-ai-api-key-here

# Optional: API URL for frontend (defaults to localhost:5000)
REACT_APP_API_URL=http://localhost:5000
```

### Changing API URLs
To use a different backend server:

1. **Update the .env file:**
   ```bash
   REACT_APP_API_URL=https://your-api-server.com
   ```

2. **Copy to frontend:**
   ```bash
   cp .env frontend/.env
   ```

3. **Restart the frontend:**
   ```bash
   cd frontend
   npm start
   ```

### API Endpoints
- `GET /api/health` - Health check
- `GET /api/graph/statistics` - Graph statistics
- `GET /api/graph/data` - Complete graph data
- `GET /api/graph/centrality` - Centrality analysis
- `GET /api/graph/search` - Graph search
- `POST /api/search/semantic` - Semantic search

## Development

### Development Mode
```bash
# Start backend in development mode
python app.py

# Start frontend in development mode
cd frontend
npm start
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
