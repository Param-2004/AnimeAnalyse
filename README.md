# 🎌 Anime Analyser 
Anime Drop Rate Analyzer is a Streamlit web app that lets you explore viewing patterns and drop rates for anime series using the public Jikan API. It offers two main modes:

✅ Search by Anime Name – fetch stats, synopsis, and drop rate for any anime.  
✅ General Statistics – explore top 10 anime by genre with drop rate visualizations.  

## 🚀 Features:

### 🔍 Anime Search:
Enter any anime name and see:
Official image and synopsis
Viewer stats: watching, completed, on-hold, dropped, plan-to-watch
Drop rate calculated and highlighted
Bar chart of engagement stats

### 📊 Genre Analysis:
Pick from popular genres (e.g. Shounen, Isekai, Romance, Horror)
View the top 10 highest-rated anime in that genre
For each, see viewer engagement and calculated drop rate
Interactive progress display while loading

### 🎨 Custom Styling:
Gradient header animation
Styled info/error badges
Stat cards and charts for a polished dashboard look

📦 Tech Stack
Frontend: Streamlit
Backend: Python with:
requests – for calling the Jikan API
matplotlib – for engagement bar charts
numpy – data handling
