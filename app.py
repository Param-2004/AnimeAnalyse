import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import time

# --- CONFIG ---
JIKAN_BASE = "https://api.jikan.moe/v4"
DELAY = 0.75

DESIRED_GENRES = [
    "Shounen", "Shoujo", "Action", "Romance", "Horror", "Mystery", "Drama", "Isekai", "Comedy"
]

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Anime Analyzer",
    page_icon="🎌",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
        .hero-title {
            text-align: center;
            font-size: 3em;
            font-weight: 800;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 5s ease infinite;
            margin-bottom: 0.5rem;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .subtitle, .section-header, .drop-rate {
            text-align: center;
        }
        .subtitle {
            color: #444;
            font-size: 1.3em;
            margin-bottom: 2rem;
        }
        .section-header {
            font-size: 2em;
            font-weight: 700;
            margin: 2rem 0 1rem 0;
            color: #333;
        }
        .success-badge, .error-badge {
            text-align: center;
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            font-weight: 600;
            color: white;
        }
        .success-badge { background: #45b7d1; }
        .error-badge { background: #e74c3c; }
        .stat-card {
            background: #f0f4f8;
            padding: 1rem;
            border-radius: 10px;
            font-weight: 600;
            color: #333;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='hero-title'>🎌 Anime Drop Rate Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Discover viewing patterns and drop rates across the anime universe</div>", unsafe_allow_html=True)

# --- HELPERS ---
@st.cache_data(show_spinner=False)
def fetch_all_genres():
    res = requests.get(f"{JIKAN_BASE}/genres/anime")
    res.raise_for_status()
    return res.json()["data"]

def filter_desired_genres(all_genres):
    target = {g.lower() for g in DESIRED_GENRES}
    return sorted(
        [ {"id": g["mal_id"], "name": g["name"]} for g in all_genres if g["name"].strip().lower() in target ],
        key=lambda x: x["name"].lower()
    )

def search_anime(name):
    res = requests.get(f"{JIKAN_BASE}/anime", params={"q": name, "limit": 5})
    res.raise_for_status()
    data = res.json()["data"]
    if not data:
        raise ValueError("No anime found!")

    for anime in data:
        if anime.get("type", "").lower() == "tv":
            title = anime.get("title_english") or f"{anime['title']} (English title not available)"
            return anime["mal_id"], title, anime["images"]["jpg"]["large_image_url"], anime.get("synopsis", "No synopsis available.")
    
    anime = data[0]
    title = anime.get("title_english") or f"{anime['title']} (English title not available)"
    return anime["mal_id"], title, anime["images"]["jpg"]["large_image_url"], anime.get("synopsis", "No synopsis available.")

def get_anime_stats(anime_id):
    time.sleep(DELAY)
    res = requests.get(f"{JIKAN_BASE}/anime/{anime_id}/statistics")
    res.raise_for_status()
    return res.json()["data"]

def get_anime_details(anime_id):
    res = requests.get(f"{JIKAN_BASE}/anime/{anime_id}")
    res.raise_for_status()
    return res.json()["data"].get("status", "")

def get_top_anime_for_genre(genre_id, limit=10):
    res = requests.get(f"{JIKAN_BASE}/anime", params={
        "genres": genre_id,
        "order_by": "score",
        "sort": "desc",
        "limit": limit
    })
    res.raise_for_status()
    data = res.json()["data"]
    results = []
    for anime in data:
        title = anime.get("title_english") or f"{anime['title']} (English title not available)"
        results.append((anime["mal_id"], title))
    return results

def plot_engagement_bar(stats):
    keys = ["dropped", "plan_to_watch", "watching"]
    values = [stats.get(k, 0) for k in keys]
    labels = ["Dropped", "Plan to Watch", "Watching"]
    colors = ['#e74c3c', '#9b59b6', '#4ecdc4']

    fig, ax = plt.subplots(figsize=(6,4))
    bars = ax.bar(labels, values, color=colors)
    for bar in bars:
        ax.annotate(f'{bar.get_height()}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), ha='center', va='bottom')
    ax.set_facecolor('#f8f9fa')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig

def display_stat_boxes(stats, airing_status):
    labels = ["Watching", "Completed", "On Hold", "Dropped", "Plan to Watch"]
    keys = ["watching", "completed", "on_hold", "dropped", "plan_to_watch"]
    
    cols = st.columns(len(labels))
    for i in range(len(labels)):
        val = stats.get(keys[i], 0)
        if labels[i] == "Completed" and airing_status and "airing" in airing_status.lower():
            val = "Still Airing"
        with cols[i]:
            st.markdown(f"<div class='stat-card'>{labels[i]}<br>{val}</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    mode = st.radio("Select Analysis Mode", ["🔍 Search by Anime Name", "📊 General Statistics"])

# --- MAIN CONTENT ---
if mode == "🔍 Search by Anime Name":
    with st.sidebar:
        anime_name = st.text_input("Enter anime name:", value="")
        fetch = st.button("Fetch Anime Data")

    if fetch:
        with st.spinner("Fetching data..."):
            try:
                anime_id, title, image_url, synopsis = search_anime(anime_name)
                stats = get_anime_stats(anime_id)
                airing_status = get_anime_details(anime_id).lower()

                st.markdown(f"<div class='success-badge'>✅ Loaded: {title}</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if image_url:
                        st.image(image_url, use_container_width=True)
                with col2:
                    st.markdown("### 📖 Synopsis", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center;'>{synopsis}</div>", unsafe_allow_html=True)

                st.markdown("<div class='section-header'>📊 Stats</div>", unsafe_allow_html=True)
                display_stat_boxes(stats, airing_status)

                st.markdown("<div class='section-header'>📊 Chart</div>", unsafe_allow_html=True)
                st.pyplot(plot_engagement_bar(stats), use_container_width=True)

                total_engaged = stats.get("dropped",0) + stats.get("completed",0) + stats.get("watching",0)
                if total_engaged > 0:
                    drop_rate = (stats["dropped"] / total_engaged) * 100
                    st.markdown(f"<div class='drop-rate' style='font-size: 1.5em; color: #e74c3c;'>Drop Rate: {drop_rate:.1f}%</div>", unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div class='error-badge'>❌ Error: {e}</div>", unsafe_allow_html=True)

elif mode == "📊 General Statistics":
    st.markdown("<div class='section-header'>📈 Genre Analysis</div>", unsafe_allow_html=True)

    try:
        all_genres = fetch_all_genres()
        allowed_genres = filter_desired_genres(all_genres)
        genre_name_to_id = {g["name"]: g["id"] for g in allowed_genres}
        genre_options = list(genre_name_to_id.keys())

        if not genre_options:
            st.error("No matching genres found in API response!")
        else:
            selected_genre_name = st.selectbox("Select a Genre:", [""] + genre_options, index=0, format_func=lambda x: "Select a genre" if x == "" else x)
            
            if selected_genre_name != "":
                selected_genre_id = genre_name_to_id[selected_genre_name]
                st.markdown(f"<div class='section-header'>⭐ Top 10 {selected_genre_name} Anime</div>", unsafe_allow_html=True)
                
                with st.spinner("Loading data..."):
                    top_anime = get_top_anime_for_genre(selected_genre_id, limit=10)
                    progress_bar = st.progress(0)
                    for i, (aid, title) in enumerate(top_anime):
                        st.markdown(f"<h3 style='text-align: center;'>⭐ {title}</h3>", unsafe_allow_html=True)
                        stats = get_anime_stats(aid)
                        st.pyplot(plot_engagement_bar(stats), use_container_width=True)

                        total_engaged = stats.get("dropped",0) + stats.get("completed",0) + stats.get("watching",0)
                        if total_engaged > 0:
                            drop_rate = (stats["dropped"] / total_engaged) * 100
                            st.markdown(f"<div class='drop-rate' style='font-size: 1.2em; color: #e74c3c;'>Drop Rate: {drop_rate:.1f}%</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='text-align: center; color: gray;'>No engagement data available.</div>", unsafe_allow_html=True)
                        progress_bar.progress((i + 1) / len(top_anime))

    except Exception as e:
        st.markdown(f"<div class='error-badge'>❌ Error: {e}</div>", unsafe_allow_html=True)
