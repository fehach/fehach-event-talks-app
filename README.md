# BigQuery Release Notes Tracker

A modern Python Flask web application that parses the official Google Cloud BigQuery Release Notes feed, visualizes them in an interactive dashboard, and facilitates tweeting about specific updates.

## Features
- **Real-Time Feed Ingestion**: Dynamically fetches and parses the BigQuery release notes RSS XML feed.
- **Content Cleaning**: Uses BeautifulSoup to sanitize the Google HTML markup for web view rendering and plaintext extraction.
- **Twitter Web Integration**: Provides a custom tweet validation modal. Pre-populates the tweet with clean titles, content snippets, and direct links while tracking the 280-character limit.
- **Premium Dark Mode Interface**: Built with modern slate-blue glassmorphism styling, clean animations, and a loading spinner on refresh.

## Project Structure
```text
releases/
├── app.py              # Main Flask server code (combines backend API and frontend template)
├── requirements.txt    # Python package dependencies
└── .gitignore          # Git exclusion rules
```

## Requirements
- Python 3.7 or higher
- Packages listed in `requirements.txt` (`Flask`, `requests`, `beautifulsoup4`, `feedparser`)

## Installation and Running

1. Clone or navigate to the directory:
   ```bash
   cd releases
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to:
   ```text
   http://127.0.0.1:8080
   ```

## License
MIT License
