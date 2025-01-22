import os
import feedparser
import requests
import time
from flask import Flask

# Replace these with your Fandom RSS feed URL and Discord webhook URL
RSS_FEED_URL = "https://phoenix-county.fandom.com/wiki/Special:RecentChanges?feed=rss"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1331651071571136544/g0w3weEo0oDRC3XSy2jlN5Bq3KophaK6J9lOA4ujT-x67MdwDxJO-FJD5OaV2t53WSTE"

# Initialize Flask app
app = Flask(__name__)

def fetch_feed():
    return feedparser.parse(RSS_FEED_URL).entries

def format_message(entry):
    # Extract data from the feed entry
    user = entry.author if 'author' in entry else 'Unknown User'
    where = entry.title
    description = entry.summary if 'summary' in entry else 'No description provided'
    tags = ", ".join(tag['term'] for tag in entry.tags) if 'tags' in entry else "No tags"
    edit_type = "Source edit"  # Customize if needed
    timestamp = entry.published if 'published' in entry else "Unknown time"

    # Format the message for Discord
    return {
        "content": (
            f"**{user}** (user)\n"
            f"**{where}** (where)\n"
            f"**{description}** (desc)\n"
            f"**{tags}** (tags)\n"
            f"**{edit_type}**\n"
            f"**{timestamp}** (when)"
        )
    }

def send_to_discord(message):
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

# Flask route to check if server is running
@app.route('/')
def home():
    return 'RSS Feed Discord Bot is running!'

# If you have other routes or features, you can define them below as needed

# Start Flask app in a background thread while running the feed fetch loop
def start_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

if __name__ == "__main__":
    from threading import Thread

    # Start Flask server in a separate thread
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True  # This ensures the Flask server runs in the background
    flask_thread.start()

    # Now, continue with your existing feed-fetching logic
    seen_entries = set()

    while True:
        feed = fetch_feed()
        for entry in feed:
            if entry.id not in seen_entries:
                message = format_message(entry)
                send_to_discord(message)
                seen_entries.add(entry.id)
        time.sleep(60)  # Wait for 1 minute before checking again
