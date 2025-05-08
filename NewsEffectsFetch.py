from googlesearch import search
import requests
from readability import Document
from bs4 import BeautifulSoup
import time

class NewsEffectsFetcher:
    def __init__(self, query, num_results=10):
        self.query = query
        self.num_results = num_results
        self.articles = []

    def fetch_article(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            doc = Document(response.text)
            soup = BeautifulSoup(doc.summary(), 'html.parser')

            return {
                "title": doc.title(),
                "url": url,
                "content": soup.get_text(separator='\n').strip()
            }
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")
            return None
    
    def get_news_articles(self):
        print(f"🔍 Searching for: {self.query}")
        urls = search(f"{self.query} site:cnn.com OR site:bbc.com OR site:reuters.com OR site:foxnews.com OR site:nytimes.com OR site:wsj.com OR site:nbcnews.com OR site:abcnews.go.com OR site:forbes.com OR site:bloomberg.com OR site:cnbc.com OR site:marketwatch.com OR site:usatoday.com OR site:theguardian.com OR site:hindustantimes.com OR site:economictimes.indiatimes.com OR site:moneycontrol.com OR site:livemint.com OR site:ndtv.com OR site:dw.com OR site:handelsblatt.com OR site:telegraph.co.uk OR site:ft.com", num_results=self.num_results,)
        
        self.articles = []
        for i, url in enumerate(urls, 1):
            print(f"\n🌐 [{i}] Trying: {url}")
            article = self.fetch_article(url)
            if article:
                print(f"✅ Got: {article['title']}")
                self.articles.append(article)
            time.sleep(1)
        return self.articles