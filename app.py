import os
import re
import html
import requests
import feedparser
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

FEED_URL = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"

def clean_html(raw_html):
    """Clean the HTML description for cleaner UI presentation and excerpt generation."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Return cleaned text content or minimal safe HTML
    return str(soup)

def extract_text(raw_html):
    """Extract plain text for tweeting."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Get text and clean white spaces
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route("/")
def index():
    # Load index.html directly from the local directory
    try:
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading index.html: {str(e)}", 500

@app.route("/api/releases")
def get_releases():
    try:
        response = requests.get(FEED_URL, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        releases = []
        for entry in feed.entries:
            # Clean summary/content
            content_value = ""
            if 'content' in entry and entry.content:
                content_value = entry.content[0].value
            elif 'summary' in entry:
                content_value = entry.summary
                
            clean_content = clean_html(content_value)
            plain_text = extract_text(content_value)
            
            # Formulate a tweet text (limit to 280 chars minus link)
            tweet_url = entry.link if hasattr(entry, 'link') else "https://cloud.google.com/bigquery/docs/release-notes"
            
            releases.append({
                "id": entry.id if hasattr(entry, 'id') else entry.link,
                "title": entry.title if hasattr(entry, 'title') else "BigQuery Release Note",
                "updated": entry.updated if hasattr(entry, 'updated') else "",
                "link": tweet_url,
                "content": clean_content,
                "plain_text": plain_text
            })
            
        return jsonify({"success": True, "releases": releases})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
