import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from textblob import TextBlob
from googlesearch import search

# Function to extract article content from Google
def extract_article_content(article_name):
    try:
        query = article_name + " article"
        search_results = search(query, num_results=1)  # Specify the number of results to fetch

        article_url = next(search_results)

        response = requests.get(article_url)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        article_content = ""
        for paragraph in soup.find_all('p'):
            article_content += paragraph.get_text() + "\n"

        return article_content, article_url

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None


# Function to summarize the article content
def summarize_article(article_content):
    try:
        tokenizer = AutoTokenizer.from_pretrained("t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

        inputs = tokenizer.encode("summarize: " + article_content, return_tensors="pt", max_length=4096,
                                  truncation=True)
        summary_ids = model.generate(inputs, max_length=1000, min_length=300, length_penalty=2.0, num_beams=4,
                                      early_stopping=True)

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    except Exception as e:
        st.error(f"An error occurred during summarization: {e}")
        return None


# Function to extract keywords from the summary
def extract_keywords(summary):
    blob = TextBlob(summary)
    return blob.noun_phrases


# Function to find related articles based on keywords
def find_related_articles(keywords):
    related_articles = []
    for keyword in keywords:
        query = f"{keyword} in India"
        search_results = search(query, num_results=5)  # Limit to 5 articles
        related_articles.extend(search_results)
    return related_articles


# Function to highlight keywords in summary
def highlight_keywords(summary, keywords):
    for keyword in keywords:
        summary = summary.replace(keyword, f"<span style='font-size: 20px'><b>{keyword}</b></span>")
    return summary


# Main function for UI
def main():
    st.set_page_config(page_title="Name Error - Article Extraction", page_icon=":newspaper:", layout="wide")
    
    st.markdown("<h1 style='text-align: center; color: green;'>Name Error</h1>", unsafe_allow_html=True)
    st.header("Article Extraction")

    article_name = st.text_input("Enter the name of the article:", key="article_input")

    # Automatically trigger "Summarize" when Enter is pressed
    if st.session_state.article_input and st.session_state.article_input != article_name:
        st.session_state.article_input = article_name
        st.experimental_rerun()
    
    if st.button("Summarize"):
        content, url = extract_article_content(article_name)
        if content:
            summary = summarize_article(content)
            if summary:
                keywords = extract_keywords(summary)
                related_articles = find_related_articles(keywords)

                highlighted_summary = highlight_keywords(summary, keywords)

                st.subheader("Summarization Points:")
                st.markdown(f"<p style='font-size: 16px;'>{highlighted_summary}</p>", unsafe_allow_html=True)

                st.subheader("Related Articles:")
                for i, article in enumerate(related_articles[:5], start=1):
                    st.write(f"{i}. {article}")

                st.subheader("Original Article URL:")
                st.write(url)
        else:
            st.error("Failed to extract article content.")


if __name__ == "__main__":
    main()

