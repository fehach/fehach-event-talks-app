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
    # Serve static HTML page directly without render_template / render_template_string
    # to avoid any Jinja2 engine parsing errors caused by template literals in CSS or JavaScript
    return HTML_CONTENT

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

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BigQuery Release Notes Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --accent-hover: #0ea5e9;
            --border-color: #334155;
            --twitter-color: #1d9bf0;
            --twitter-hover: #1a8cd8;
            --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --header-border: #334155;
        }

        /* Light Theme Overrides */
        body.light-theme {
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --accent-color: #0284c7;
            --accent-hover: #0369a1;
            --header-border: #cbd5e1;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: var(--font-family);
            line-height: 1.6;
            padding: 2rem 1rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        header {
            width: 100%;
            max-width: 900px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--header-border);
            padding-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-color), #818cf8);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
        }

        h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(to right, var(--text-primary), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .btn {
            background-color: var(--accent-color);
            color: #ffffff;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-family: var(--font-family);
            transition: all 0.2s ease;
            text-decoration: none;
        }

        body:not(.light-theme) .btn:not(.btn-secondary):not(.btn-twitter) {
            color: #0f172a;
        }

        .btn:hover {
            background-color: var(--accent-hover);
            transform: translateY(-1px);
        }

        .btn:active {
            transform: translateY(1px);
        }

        .btn-secondary {
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }

        .btn-secondary:hover {
            background-color: rgba(148, 163, 184, 0.1);
            border-color: var(--text-secondary);
        }

        .btn-twitter {
            background-color: var(--twitter-color);
            color: white;
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
        }

        .btn-twitter:hover {
            background-color: var(--twitter-hover);
        }

        /* Toggle switch styling */
        .theme-toggle-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--border-color);
            transition: .3s;
            border-radius: 24px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: var(--text-primary);
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent-color);
        }

        input:checked + .slider:before {
            transform: translateX(20px);
        }

        /* Spinner Animation */
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top: 2px solid currentColor;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: none;
        }

        .loading .spinner {
            display: inline-block;
        }

        .loading .btn-text {
            display: none;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        main {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .error-message {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            padding: 1rem;
            border-radius: 8px;
            display: none;
            text-align: center;
        }

        body.light-theme .error-message {
            background-color: #fef2f2;
            color: #991b1b;
            border-color: #fca5a5;
        }

        .release-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: border-color 0.2s ease, transform 0.2s ease, background-color 0.3s ease;
        }

        .release-card:hover {
            border-color: var(--accent-color);
            transform: translateY(-2px);
        }

        .release-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            gap: 1rem;
        }

        .release-meta {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .release-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .release-date {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }

        .release-content {
            font-size: 0.95rem;
            color: var(--text-primary);
            opacity: 0.9;
            margin-bottom: 1.25rem;
        }

        .release-content a {
            color: var(--accent-color);
            text-decoration: none;
        }

        .release-content a:hover {
            text-decoration: underline;
        }

        .release-content ul {
            margin-left: 1.5rem;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .release-content li {
            margin-bottom: 0.25rem;
        }

        .release-actions {
            display: flex;
            gap: 0.75rem;
            align-items: center;
            border-top: 1px solid var(--border-color);
            padding-top: 1rem;
            flex-wrap: wrap;
        }

        /* Toast feedback */
        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background-color: var(--text-primary);
            color: var(--bg-color);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            z-index: 2000;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: none;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
        }

        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }

        body.light-theme .modal-overlay {
            background-color: rgba(15, 23, 42, 0.4);
        }

        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .modal {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            padding: 1.5rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            transform: scale(0.95);
            transition: transform 0.2s ease, background-color 0.3s ease;
        }

        .modal-overlay.active .modal {
            transform: scale(1);
        }

        .modal-header {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
        }

        .tweet-textarea {
            width: 100%;
            height: 120px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem;
            color: var(--text-primary);
            font-family: var(--font-family);
            font-size: 0.95rem;
            resize: none;
            margin-bottom: 0.5rem;
            transition: background-color 0.3s ease;
        }

        .tweet-textarea:focus {
            outline: none;
            border-color: var(--accent-color);
        }

        .char-counter {
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-align: right;
            margin-bottom: 1rem;
        }

        .char-counter.limit-exceeded {
            color: #ef4444;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-container">
            <div class="logo-icon">BQ</div>
            <h1>BigQuery Release Notes</h1>
        </div>
        <div class="header-actions">
            <div class="theme-toggle-container">
                <span>Light Mode</span>
                <label class="switch">
                    <input type="checkbox" id="theme-checkbox">
                    <span class="slider"></span>
                </label>
            </div>
            <button id="export-btn" class="btn btn-secondary" style="font-size: 0.9rem; padding: 0.5rem 1rem;">
                Export CSV
            </button>
            <button id="refresh-btn" class="btn">
                <span class="spinner"></span>
                <span class="btn-text">Refresh</span>
            </button>
        </div>
    </header>

    <main>
        <div id="error-box" class="error-message"></div>
        <div id="releases-container">
            <!-- Cards will be populated here -->
        </div>
    </main>

    <!-- Tweet Customization Modal -->
    <div id="tweet-modal" class="modal-overlay">
        <div class="modal">
            <div class="modal-header">
                <span>Customize Tweet</span>
                <button class="modal-close" id="close-modal">&times;</button>
            </div>
            <textarea id="tweet-text" class="tweet-textarea" placeholder="What's happening?"></textarea>
            <div class="char-counter" id="char-counter">0 / 280</div>
            <div class="modal-footer">
                <button class="btn btn-secondary" id="cancel-tweet">Cancel</button>
                <button class="btn btn-twitter" id="send-tweet">Tweet</button>
            </div>
        </div>
    </div>

    <!-- Toast message overlay -->
    <div id="toast-message" class="toast">Copied to clipboard!</div>

    <script>
        const refreshBtn = document.getElementById('refresh-btn');
        const exportBtn = document.getElementById('export-btn');
        const container = document.getElementById('releases-container');
        const errorBox = document.getElementById('error-box');
        const themeCheckbox = document.getElementById('theme-checkbox');
        const toastMessage = document.getElementById('toast-message');
        
        // Modal elements
        const tweetModal = document.getElementById('tweet-modal');
        const tweetText = document.getElementById('tweet-text');
        const charCounter = document.getElementById('char-counter');
        const closeModal = document.getElementById('close-modal');
        const cancelTweet = document.getElementById('cancel-tweet');
        const sendTweet = document.getElementById('send-tweet');

        let currentReleases = [];

        // Theme preference management
        if (localStorage.getItem('theme') === 'light') {
            document.body.classList.add('light-theme');
            themeCheckbox.checked = true;
        }

        themeCheckbox.addEventListener('change', () => {
            if (themeCheckbox.checked) {
                document.body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
            } else {
                document.body.classList.remove('light-theme');
                localStorage.setItem('theme', 'dark');
            }
        });

        // Copy Clipboard utility
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                toastMessage.classList.add('show');
                setTimeout(() => {
                    toastMessage.classList.remove('show');
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        }

        // CSV Export utility
        exportBtn.addEventListener('click', () => {
            if (currentReleases.length === 0) return;
            
            // CSV columns header
            const headers = ['Title', 'Date', 'URL', 'Plain Summary'];
            
            // Helper to escape values for CSV
            const escapeCsvValue = (val) => {
                if (val === null || val === undefined) return '';
                let stringVal = String(val);
                // Escape double quotes by doubling them
                stringVal = stringVal.replace(/"/g, '""');
                // Wrap in double quotes if there are commas, double quotes, or newlines
                if (/[",\n\r]/.test(stringVal)) {
                    stringVal = `"${stringVal}"`;
                }
                return stringVal;
            };

            const rows = currentReleases.map(rel => [
                rel.title,
                rel.updated,
                rel.link,
                rel.plain_text
            ]);

            const csvContent = [
                headers.map(escapeCsvValue).join(','),
                ...rows.map(row => row.map(escapeCsvValue).join(','))
            ].join('\n');

            // Download trigger
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', 'bigquery_releases_export.csv');
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });

        async function fetchReleases() {
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
            errorBox.style.display = 'none';
            
            try {
                const response = await fetch('/api/releases');
                const data = await response.json();
                
                if (data.success) {
                    currentReleases = data.releases;
                    renderReleases(data.releases);
                } else {
                    showError(data.error || 'Failed to fetch release notes');
                }
            } catch (err) {
                showError('Network error, please try again.');
            } finally {
                refreshBtn.classList.remove('loading');
                refreshBtn.disabled = false;
            }
        }

        function showError(msg) {
            errorBox.textContent = msg;
            errorBox.style.display = 'block';
        }

        function renderReleases(releases) {
            if (!releases || releases.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary); margin-top: 3rem;">No release notes found.</div>';
                return;
            }

            let htmlString = '';
            for (let i = 0; i < releases.length; i++) {
                const rel = releases[i];
                let formattedDate = rel.updated;
                try {
                    const dateObj = new Date(rel.updated);
                    formattedDate = dateObj.toLocaleDateString(undefined, { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    });
                } catch(e) {}

                // Escape text content for safe javascript passing
                const safePlainText = rel.plain_text.replace(/`/g, '\\`').replace(/\$/g, '\\$');

                htmlString += '<article class="release-card">' +
                    '<div class="release-header">' +
                        '<div class="release-meta">' +
                            '<h2 class="release-title">' + rel.title + '</h2>' +
                            '<span class="release-date">' + formattedDate + '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="release-content">' +
                        rel.content +
                    '</div>' +
                    '<div class="release-actions">' +
                        '<button class="btn btn-twitter" onclick="openTweetModal(' + i + ')">Tweet Update</button>' +
                        '<button class="btn btn-secondary" onclick="copyToClipboard(\'' + safePlainText.replace(/'/g, "\\'") + '\')" style="font-size: 0.9rem; padding: 0.5rem 1rem;">Copy Info</button>' +
                        '<a href="' + rel.link + '" target="_blank" class="btn btn-secondary" style="font-size: 0.9rem; padding: 0.5rem 1rem; text-decoration: none;">View Source</a>' +
                    '</div>' +
                '</article>';
            }
            container.innerHTML = htmlString;
        }

        // Tweet Modal Logics
        function openTweetModal(index) {
            const rel = currentReleases[index];
            if (!rel) return;

            // Generate clean draft
            let draft = "BigQuery Update: " + rel.title + "\\n\\n";
            
            // Try to append part of the text
            const maxSnippetLen = 180;
            let snippet = rel.plain_text;
            if (snippet.length > maxSnippetLen) {
                snippet = snippet.substring(0, maxSnippetLen) + "...";
            }
            
            draft += snippet + "\\n\\nMore info: " + rel.link;
            
            tweetText.value = draft;
            updateCharCount();
            tweetModal.classList.add('active');
        }

        function closeTweetModalFunc() {
            tweetModal.classList.remove('active');
        }

        function updateCharCount() {
            const count = tweetText.value.length;
            charCounter.textContent = count + " / 280";
            if (count > 280) {
                charCounter.classList.add('limit-exceeded');
                sendTweet.disabled = true;
                sendTweet.style.opacity = 0.5;
            } else {
                charCounter.classList.remove('limit-exceeded');
                sendTweet.disabled = false;
                sendTweet.style.opacity = 1;
            }
        }

        tweetText.addEventListener('input', updateCharCount);
        closeModal.addEventListener('click', closeTweetModalFunc);
        cancelTweet.addEventListener('click', closeTweetModalFunc);

        sendTweet.addEventListener('click', () => {
            const text = encodeURIComponent(tweetText.value);
            window.open("https://twitter.com/intent/tweet?text=" + text, "_blank");
            closeTweetModalFunc();
        });

        // Initialize
        refreshBtn.addEventListener('click', fetchReleases);
        fetchReleases();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=8080)
