import streamlit as st
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

GENIUS_API_TOKEN = None

try:
    GENIUS_API_TOKEN = st.secrets["GENIUS_API_TOKEN"]
except (st.errors.StreamlitAPIException, KeyError):
    load_dotenv()
    GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")

if not GENIUS_API_TOKEN:
    st.error("Genius API Token not found. Please check your .env or Streamlit secrets.")
# Function to fetch lyrics
def get_lyrics(song_title):
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"Taylor Swift {song_title}"}

    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        return None, "Error fetching data from Genius API"

    hits = response.json()["response"]["hits"]
    if not hits:
        return None, "Song not found"

    song_url = hits[0]["result"]["url"]

    # Scrape lyrics from the song page
    page = requests.get(song_url, headers={"User-Agent": "Mozilla/5.0"})
    if page.status_code != 200:
        return None, "Error fetching song page"

    soup = BeautifulSoup(page.text, "html.parser")
    lyrics = ""

    for tag in soup.find_all("div", class_=lambda x: x and "Lyrics__Container" in x):
        lyrics += tag.get_text(separator="\n", strip=True) + "\n"

    if not lyrics.strip():
        return None, "Lyrics not found"

    return lyrics, None

# Streamlit UI
st.set_page_config(
    page_title="Swiftie Lyrics & Word Cloud",
    page_icon="🎤",
    layout="centered"
)

st.title("🎤 Taylor Swift Lyrics & Word Cloud Generator")
st.write("Enter a **Taylor Swift** song title to fetch the lyrics and generate a word cloud!")

song_title = st.text_input("Song Title", placeholder="Ex: Love Story")

if st.button("Get Lyrics"):
    if not song_title.strip():
        st.error("Please enter a song title.")
    else:
        with st.spinner("Fetching lyrics..."):
            lyrics, error = get_lyrics(song_title)

        if error:
            st.error(error)
        else:
            st.subheader("🎶 Lyrics:")
            st.text_area("Lyrics", lyrics, height=300)

            st.subheader("☁️ Word Cloud:")
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(lyrics)

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(plt)
