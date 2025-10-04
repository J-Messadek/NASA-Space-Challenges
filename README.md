# NASA Hackathon Project

A Python project for the NASA Hackathon.

## Setup Instructions

### 1. Create a Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application

#### Option A: Development Mode (Recommended)
```bash
# Install development dependencies first
pip install -r requirements.txt

# Start development environment (auto-reload + auto-format + linting)
python dev-tools/dev_server.py
```

#### Option B: Run Once (Simple)
```bash
# Just run the main file directly
python main.py
```

## Project Structure
```
NASA-Hackathon/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Code formatting configuration
├── README.md              # This file
├── dev-tools/             # Development utilities
│   ├── __init__.py
│   └── dev_server.py      # Development environment (auto-reload + format)
└── SB_publications-main/  # NASA Space Biology publications data
    ├── README.md
    └── SB_publication_PMC.csv
```

## Getting Started
The `main.py` file contains a simple hello world function to get you started. You can modify this file to build your NASA Hackathon project.

## Data
The project includes NASA Space Biology publications data in the `SB_publications-main/` directory with 608 publications since 2010.
