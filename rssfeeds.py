import sys
import json
import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextBrowser,
    QLineEdit, QLabel, QComboBox, QPushButton, QSplitter, QMainWindow, QInputDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

# File to store saved RSS feeds
FEEDS_FILE = "feeds.json"

# Default RSS Feeds
DEFAULT_FEEDS = {
    "Nottingham Forest": "https://www.nottinghampost.com/all-about/nottingham-forest-fc?service=rss",
    "BBC Sport": "http://feeds.bbci.co.uk/sport/rss.xml?edition=uk",
    "TechCrunch": "https://techcrunch.com/feed/"
}

class NewsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('📰 RSS News Reader')
        self.setGeometry(100, 100, 1200, 800)

        # Load saved feeds from JSON file
        self.load_feeds()

        # Network Manager for downloading images
        self.network_manager = QNetworkAccessManager(self)

        # Main Layout
        main_layout = QVBoxLayout()

        # Feed Selection Layout
        feed_layout = QHBoxLayout()
        self.feed_dropdown = QComboBox()
        self.feed_dropdown.addItems(self.feeds.keys())
        self.feed_dropdown.currentIndexChanged.connect(self.fetch_news)

        add_feed_button = QPushButton("➕ Add Feed")
        add_feed_button.clicked.connect(self.add_feed)

        feed_layout.addWidget(self.feed_dropdown)
        feed_layout.addWidget(add_feed_button)

        main_layout.addLayout(feed_layout)

        # Search Bar to filter news articles
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search news...")
        self.search_bar.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0; padding: 8px; font-size: 16px;")
        self.search_bar.textChanged.connect(self.filter_news)
        main_layout.addWidget(self.search_bar)

        # Split View to adjust sizes dynamically
        self.splitter = QSplitter(Qt.Horizontal)

        # Left: News List
        self.news_list = QListWidget()
        self.news_list.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0; font-size: 14px;")
        self.news_list.itemClicked.connect(self.display_article)
        self.splitter.addWidget(self.news_list)

        # Right: Article Display
        article_layout = QVBoxLayout()
        self.article_view = QTextBrowser()
        self.article_view.setOpenExternalLinks(True)
        self.article_view.setStyleSheet("background-color: #1E1E1E; color: #E0E0E0; font-size: 16px; padding: 10px;")

        # Label for displaying images
        self.image_label = QLabel(self)

        # Open in New Window Button
        open_in_window_button = QPushButton("🖥️ Open in New Window")
        open_in_window_button.clicked.connect(self.open_in_new_window)

        # Add widgets to layout
        article_layout.addWidget(self.article_view)
        article_layout.addWidget(self.image_label)
        article_layout.addWidget(open_in_window_button)

        article_container = QWidget()
        article_container.setLayout(article_layout)

        self.splitter.addWidget(article_container)
        self.splitter.setSizes([300, 700])  # Adjust default sizes

        main_layout.addWidget(self.splitter)

        # Set Main Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.fetch_news()

    def load_feeds(self):
        """Load saved feeds from JSON or use defaults"""
        try:
            with open(FEEDS_FILE, "r") as file:
                self.feeds = json.load(file)
        except FileNotFoundError:
            self.feeds = DEFAULT_FEEDS
            self.save_feeds()

    def save_feeds(self):
        """Save the RSS feeds list to a JSON file"""
        with open(FEEDS_FILE, "w") as file:
            json.dump(self.feeds, file, indent=4)

    def add_feed(self):
        """Prompt user to add a new feed with a name and URL"""
        feed_name, name_ok = QInputDialog.getText(self, "Add Feed", "Enter Feed Name (e.g., 'BBC News'):")
        if not name_ok or not feed_name.strip():
            return

        new_feed_url, url_ok = QInputDialog.getText(self, "Add Feed URL", f"Enter RSS Feed URL for '{feed_name}':")
        if name_ok and url_ok and new_feed_url.strip():
            self.feeds[feed_name] = new_feed_url
            self.feed_dropdown.addItem(feed_name)
            self.save_feeds()

    def fetch_news(self):
        """Fetch news from the selected RSS feed"""
        feed_url = self.feeds[self.feed_dropdown.currentText()]
        feed = feedparser.parse(feed_url)

        self.news_data = []
        self.news_list.clear()

        for entry in feed.entries:
            self.news_data.append({
                'title': entry.title,
                'summary': entry.summary,
                'link': entry.link
            })
            self.news_list.addItem(entry.title)

    def filter_news(self):
        """Filter news articles based on search input"""
        query = self.search_bar.text().lower()
        self.news_list.clear()

        self.filtered_news = [article for article in self.news_data if query in article['title'].lower()]
        
        for article in self.filtered_news:
            self.news_list.addItem(article['title'])

    def display_article(self, item):
        """Display the selected article and fetch its content"""
        selected_article = next((article for article in self.news_data if article['title'] == item.text()), None)

        if selected_article:
            article_content, images = self.fetch_full_article(selected_article['link'])

            html_content = f"<h2 style='color:#FF6F00;'>{selected_article['title']}</h2><br>"
            html_content += f"<p>{article_content}</p>"
            html_content += f"<br><a href='{selected_article['link']}' style='color:#FF6F00;'>Read full article</a>"

            self.article_view.setHtml(html_content)

            if images:
                self.display_image(images[0])

    def fetch_full_article(self, url):
        """Retrieve article content and images"""
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = [p.get_text() for p in soup.find_all('p')]
        text_content = "<br>".join(paragraphs)

        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src') or img.get('data-src')
            if img_url and img_url.startswith('http'):
                images.append(img_url)

        return text_content, images

    def display_image(self, image_url):
        """Download and display article image"""
        request = QNetworkRequest(QUrl(image_url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.load_image(reply))

    def load_image(self, reply):
        """Load and show the image in QLabel"""
        image_data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio))

    def open_in_new_window(self):
        """Open the selected article in a separate window"""
        current_item = self.news_list.currentItem()
        if current_item:
            selected_article = next((article for article in self.news_data if article['title'] == current_item.text()), None)
            if selected_article:
                self.article_window = ArticleWindow(selected_article)
                self.article_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    news_app = NewsApp()
    news_app.show()
    sys.exit(app.exec_())
