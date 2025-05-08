# 📰 NewsEffects  
## 🔍 About NewsEffects

**NewsEffects** is an AI-powered application built on **Gemini Flash 1.5** ⚡.  
It analyzes news articles from reputable sources 🗞️ to detect sentiment around specific stocks or companies 📈.  
It can also evaluate major events 🌍 and suggest how related companies or stocks might perform based on those events 💡.

The app uses **Google Search** 🔎 to retrieve relevant news and supports articles from a wide range of trusted publications, including:

🌐 cnn.com  
🌐 bbc.com  
🌐 reuters.com  
🌐 foxnews.com  
🌐 nytimes.com  
🌐 wsj.com  
🌐 nbcnews.com  
🌐 abcnews.go.com  
🌐 forbes.com  
🌐 bloomberg.com  
🌐 cnbc.com  
🌐 marketwatch.com  
🌐 usatoday.com  
🌐 theguardian.com  
🌐 hindustantimes.com  
🌐 economictimes.indiatimes.com  
🌐 moneycontrol.com  
🌐 livemint.com  
🌐 ndtv.com  
🌐 dw.com  
🌐 handelsblatt.com  
🌐 telegraph.co.uk  
🌐 ft.com

### ⚙️ How Does It Work?

NewsEffects has two major components:

1. 🧲 **NewsFetch**  
   A custom-built Python library developed on top of `googlesearch`. It searches for news articles related to a specific stock or company and fetches the most relevant ones from trusted sources.

2. 🧠 **NewsAnalysis**  
   Built using **LangChain**, this component takes the collected corpus of news articles and feeds them into a **Large Language Model (LLM)**. The LLM then analyzes the content to extract sentiment, assess impact, and generate actionable insights.

Together, these components allow NewsEffects to deliver intelligent, sentiment-driven analysis based on real-time news coverage.

> ⚠️ **Note:** To use NewsEffects, you’ll need access to the **Gemini API**. You can obtain API credentials from [https://ai.google.dev](https://ai.google.dev).

### 🎥 Demo Videos

#### 📊 Stock Sentiment Analysis
[![Stock Demo](https://img.youtube.com/vi/n9H7SG0QWuQ/0.jpg)](https://youtu.be/n9H7SG0QWuQ)

#### 🌐 Event Impact Analysis
[![Event Demo](https://img.youtube.com/vi/DbQxOBBs4y0/0.jpg)](https://youtu.be/DbQxOBBs4y0)

MIT License
