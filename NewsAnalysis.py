import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
# Assuming PromptTemplate is not strictly needed if using System/HumanMessage directly
# from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from NewsEffectsFetch import NewsEffectsFetcher # Ensure this file exists and is correct
# import uuid # uuid was imported but not used, can be removed if not needed elsewhere

# Configure Gemini API Key from a file
try:
    # Construct the path relative to the current script file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    api_key_path = os.path.join(current_dir, "gemini_api_key.txt")
    if not os.path.exists(api_key_path):
        # Fallback for environments where __file__ might not be standard
        api_key_path = "gemini_api_key.txt"

    with open(api_key_path, "r") as file:
        gemini_api_key = file.read().strip()
    os.environ["GEMINI_API_KEY"] = gemini_api_key
except FileNotFoundError:
    st.error(
        "Error: gemini_api_key.txt file not found. "
        "Please create it in the same directory as the script (or in the root for some deployments) "
        "with your API key, or configure Streamlit secrets if deploying to Streamlit Cloud."
    )
    st.stop()
except Exception as e:
    st.error(f"Error reading API key: {str(e)}")
    st.stop()


# Streamlit UI Configuration
st.set_page_config(page_title="News Effects Analyzer", layout="wide")
st.title("📰 NewsEffects")
st.markdown("Analyze and predict stock or company performance based on recent news and events.")
st.markdown("You can ask about a stock e.g. 'Tesla' or about an event 'Trade war and its effects on Indian economy'.")
st.markdown("***Disclaimer:*** This is not financial advice. Please do your own research before making any investment decisions.")

# Initialize session state for storing analysis results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "search_string_type" not in st.session_state:
    st.session_state.search_string_type = None
if "urls" not in st.session_state:
    st.session_state.urls = []
if "last_search_string" not in st.session_state:
    st.session_state.last_search_string = ""


# Sidebar for Input
with st.sidebar:
    st.header("Settings")
    search_string_input = st.text_input("Search Query", placeholder="Ask about an stock or a event", key="search_query_input")
    analyze_button = st.button("Analyze")

# NewsEffectsAnalyzer Class
class NewsEffectsAnalyzer:
    def __init__(self, search_string):
        self.search_string = search_string
        self.num_results = 10  # Number of articles is fixed to 10
        self.search_string_type = ""
        self.urls = []
        self.all_articles_text = ""

    def fetch_and_display_articles(self):
        fetcher = NewsEffectsFetcher(self.search_string, num_results=self.num_results)
        articles = fetcher.get_news_articles()
        self.all_articles_text = ""
        self.urls = []

        if not articles:
            st.warning(f"No articles found for '{self.search_string}'. Please try a different query.")
            return False

        for article in articles:
            if article.get('content'):
                self.all_articles_text += article['content'] + "\n\n"
            if article.get('url'):
                self.urls.append(article['url'])
        
        if not self.all_articles_text.strip() and self.urls:
            st.warning(f"Found {len(self.urls)} article URLs, but could not extract content from them. Analysis might be limited or based on titles/summaries if available to the fetcher (not shown here).")
            # Depending on NewsEffectsFetcher, it might return articles with no 'content'
            # This check ensures we inform the user if content is missing.
            # However, the current logic proceeds if URLs are present, final_analysis will handle empty all_articles_text

        return True


    def search_string_analysis(self, llm):
        system_prompt = (
            "You are a financial news analyst. Identify the context of the search string provided. "
            "Classify it into one of the following types:\n"
            "1. Related to a public company (respond with: type 1)\n"
            "2. Related to a startup or unlisted (respond with: type 2)\n"
            "3. Related to a general event (respond with: type 3)\n"
            "No need for detailed analysis, just mention the type."
        )
        human_prompt = f"Analyze this search string: '{self.search_string}'"
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        response = llm.invoke(messages)
        self.search_string_type = response.content.strip()

    def final_analysis(self, llm):
        if not self.all_articles_text.strip():
             return "Could not perform analysis as no article content was fetched or extracted. This might be due to paywalls, content extraction issues, or no articles found with content."

        if self.search_string_type == "type 1":
            system_prompt = (
                "You are a financial news analyst. Based on the provided news articles, perform a sentiment analysis for the publicly listed company or companies mentioned in the search query. "
                "Predict the potential stock price movement (e.g., upward, downward, neutral, volatile) and provide a brief confidence level (e.g., high, medium, low).\n"
                "Mention the key reasons for your prediction in concise bullet points, citing specific information from the articles if possible.\n"
                "Keep the overall response short and focused, avoiding lengthy explanations."
            )
        elif self.search_string_type == "type 2":
            system_prompt = (
                "You are a financial news analyst. Based on the provided news articles, perform a sentiment analysis for the startup or unlisted company/companies mentioned in the search query. "
                "Predict their future success potential (e.g., high potential, moderate growth, facing challenges) and provide a brief confidence level (e.g., high, medium, low).\n"
                "Mention the key reasons for your prediction in concise bullet points, citing specific information from the articles if possible.\n"
                "Keep the overall response short and focused."
            )
        else:  # type 3 or any other unexpected type
            system_prompt = (
                "You are a financial news analyst. Based on the provided news articles about the event or topic mentioned in the search query, perform a sentiment analysis. "
                "If it's an event, predict the potential stock price movement of relevant companies or sectors associated with this event (e.g., upward for tech stocks, downward for travel industry) and provide a brief confidence level (e.g., high, medium, low).\n"
                "Mention the key reasons for your prediction in concise bullet points, citing specific information from the articles if possible. If specific companies are not easily identifiable from the articles for the event, discuss general sector impacts.\n"
                "Keep the overall response short and focused."
            )

        human_prompt = f"Analyze this search string: '{self.search_string}' with the following articles:\n\n{self.all_articles_text}"
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        return llm.invoke(messages).content

# Main Logic
if analyze_button and search_string_input:
    if search_string_input != st.session_state.last_search_string:
        st.session_state.analysis_result = None
        st.session_state.search_string_type = None
        st.session_state.urls = []
    st.session_state.last_search_string = search_string_input

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.2,
            max_tokens=2048
        )

        analyzer = NewsEffectsAnalyzer(search_string_input)

        articles_fetched_successfully = False
        with st.spinner("Fetching articles..."):
            articles_fetched_successfully = analyzer.fetch_and_display_articles()

        if articles_fetched_successfully and (analyzer.urls or analyzer.all_articles_text.strip()):
            # Proceed if URLs were found, even if content extraction was partial or failed for some
            # The final_analysis method has a check for empty all_articles_text
            with st.spinner("Analyzing search string type..."):
                analyzer.search_string_analysis(llm)
            
            if not analyzer.all_articles_text.strip() and analyzer.urls:
                # If we have URLs but no content, we can't do LLM analysis on content
                st.warning("Article URLs were found, but no content could be extracted. Cannot perform detailed analysis.")
                st.session_state.analysis_result = "Analysis could not be performed as no article content was available."
                st.session_state.urls = analyzer.urls # Still show the URLs
            elif not analyzer.urls and not analyzer.all_articles_text.strip():
                # This case should ideally be caught by articles_fetched_successfully being False
                st.warning("No articles or content found to analyze.")
                st.session_state.analysis_result = "No articles or content found."
                st.session_state.urls = []
            else:
                # This means we have some article text to analyze
                with st.spinner("Performing final analysis... This may take a moment."):
                    result = analyzer.final_analysis(llm)
                st.session_state.analysis_result = result
                st.session_state.search_string_type = analyzer.search_string_type # Store type if analysis was done
                st.session_state.urls = analyzer.urls

        elif not articles_fetched_successfully:
            # fetch_and_display_articles already showed a warning if no articles found
            if st.session_state.analysis_result is None:
                 st.session_state.analysis_result = "Failed to fetch articles. Analysis cannot proceed."
            st.session_state.urls = []


    except Exception as e:
        st.error(f"An unexpected error occurred during analysis: {str(e)}")
        # import traceback
        st.session_state.analysis_result = "An error occurred during analysis."
        st.session_state.urls = []


# Display Results
if st.session_state.analysis_result:
    st.subheader(f"Analysis for: \"{st.session_state.last_search_string}\"")
    st.markdown("**Analysis**:")
    st.markdown(st.session_state.analysis_result) # This will display text like "No articles found..." if that was the case

    if st.session_state.urls:
        st.subheader("Source Articles")
        for i, url in enumerate(st.session_state.urls, 1):
            st.markdown(f"{i}. [{url}]({url})")
elif analyze_button and search_string_input:
    # This handles the case where analyze_button was pressed, input exists, but analysis_result is still None
    if not st.session_state.get("analysis_result"): # Check if analysis_result is None or empty
        st.info(f"No analysis results to display for '{search_string_input}'. This might be due to no articles being found or an issue during processing.")