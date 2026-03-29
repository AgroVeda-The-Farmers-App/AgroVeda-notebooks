import streamlit as st
import requests
import os
import feedparser
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
OPENWEATHER_KEY  = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="AgroVeda News", layout="wide")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 16px 48px; font-size: 18px; min-width: 160px; justify-content: center; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

st.title("AgroVeda News & Updates")
st.caption("Latest agricultural news from India")

JUNK = ["quiz","testbook","sscadda","gradeup","oliveboard","exampur","adda247","mocktest","currentaffairs"]
JUNK_TITLES = ["quiz","mcq","objective question","exam","test series","mock test","current affairs pdf"]

def is_junk(article):
    url   = article.get("link","").lower()
    title = article.get("title","").lower()
    return any(j in url for j in JUNK) or any(j in title for j in JUNK_TITLES)

def format_date(s):
    try:    return datetime.strptime(s[:10],"%Y-%m-%d").strftime("%d %b %Y")
    except: return s[:10] if s else "—"

# ── KEY FIX: cache_data so NewsData is only called ONCE per query ─────────────
@st.cache_data(ttl=1800)  # cache for 30 minutes
def fetch_newsdata(queries_tuple, size=9):
    all_articles, seen = [], set()
    for q in queries_tuple:
        if len(all_articles) >= size: break
        try:
            r = requests.get("https://newsdata.io/api/1/news", timeout=8, params={
                "apikey": NEWSDATA_API_KEY, "q": q,
                "country": "in", "language": "en", "size": size
            })
            for a in r.json().get("results", []):
                if is_junk(a) or a.get("title","") in seen: continue
                seen.add(a.get("title",""))
                all_articles.append(a)
        except:
            continue
    return all_articles[:size]

@st.cache_data(ttl=1800)  # cache RSS for 30 minutes too
def fetch_rss(feeds_tuple, max_per_feed=4):
    articles, seen = [], set()
    for url in feeds_tuple:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= max_per_feed: break
                title = entry.get("title","")
                if title in seen: continue
                seen.add(title)
                articles.append({
                    "title":       title,
                    "link":        entry.get("link",""),
                    "description": entry.get("summary","")[:200],
                    "pubDate":     entry.get("published",""),
                    "source":      feed.feed.get("title",""),
                })
                count += 1
        except: continue
    return articles

def render_newsdata_cards(articles):
    if not articles:
        st.warning("No articles found right now. Try again later.")
        return
    cols = st.columns(3)
    for i, a in enumerate(articles):
        with cols[i % 3]:
            with st.container(border=True):
                img = a.get("image_url")
                if img:
                    try: st.image(img, use_container_width=True)
                    except: pass
                src = a.get("source_name") or a.get("source_id","Unknown")
                st.caption(f"📅 {format_date(a.get('pubDate',''))}  ·  🏛️ {src}")
                st.markdown(f"**{a.get('title','No title')}**")
                desc = a.get("description") or a.get("content") or ""
                st.write(desc[:180] + "..." if len(desc) > 180 else desc)
                if a.get("link"):
                    st.link_button("Read Full Article →", a["link"], use_container_width=True)

def render_rss_cards(articles):
    if not articles:
        st.warning("Could not load RSS feeds. Check your connection.")
        return
    cols = st.columns(3)
    for i, a in enumerate(articles):
        with cols[i % 3]:
            with st.container(border=True):
                st.caption(f"📡 {a['source']}  ·  {a.get('pubDate','')[:16]}")
                st.markdown(f"**{a['title']}**")
                st.write(a["description"] + "..." if a["description"] else "")
                if a["link"]:
                    st.link_button("Read Full Article →", a["link"], use_container_width=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    " General", " Organic", " MSP & Prices", " Agri-Tech", " Weather"
])

with tab1:
    st.subheader("General Agriculture News")
    with st.spinner("Loading..."):
        articles = fetch_newsdata((
            "agriculture India farming",
            "farmer India crop harvest",
            "Indian agriculture ministry"
        ))
    render_newsdata_cards(articles)

with tab2:
    st.subheader("Organic Farming News")
    with st.spinner("Loading..."):
        articles = fetch_newsdata((
            "organic farming India",
            "natural farming India zero budget",
            "organic certification India farmer"
        ))
    render_newsdata_cards(articles)

with tab3:
    st.subheader("MSP & Crop Price News")
    with st.spinner("Loading..."):
        articles = fetch_newsdata((
            "minimum support price India wheat rice",
            "mandi price crop India market",
            "PM-KISAN farmer income India"
        ))
    render_newsdata_cards(articles)

with tab4:
    st.subheader("Agri-Tech News")
    st.caption("Live from Krishi Jagran · Just Agriculture · RuralVoice · Agrifarming")
    with st.spinner("Loading RSS feeds..."):
        articles = fetch_rss((
            "https://krishijagran.com/feed",
            "https://justagriculture.in/feed",
            "https://eng.ruralvoice.in/feed",
            "https://agrifarming.in/feed",
        ), max_per_feed=3)
    render_rss_cards(articles)

with tab5:
    st.subheader("Live Farm Weather")
    st.caption("Real-time weather for your farming location")

    MAJOR_AGRI_CITIES = [
        "Patna", "Lucknow", "Bhopal", "Jaipur", "Hyderabad",
        "Pune", "Nagpur", "Chandigarh", "Bhubaneswar", "Guwahati",
        "Kolkata", "Chennai", "Bangalore", "Ahmedabad", "Indore"
    ]

    col1, col2 = st.columns([2,1])
    with col1:
        city = st.selectbox("Select your city/district", sorted(MAJOR_AGRI_CITIES))
    with col2:
        custom = st.text_input("Or type any city", placeholder="e.g. Varanasi")

    target_city = custom.strip() if custom.strip() else city

    if st.button("Get Weather", use_container_width=True):
        if not OPENWEATHER_KEY:
            st.error("Add OPENWEATHER_API_KEY to your .env file. Free at openweathermap.org")
        else:
            try:
                r = requests.get("https://api.openweathermap.org/data/2.5/weather", params={
                    "q": f"{target_city},IN", "appid": OPENWEATHER_KEY, "units": "metric"
                }, timeout=8)
                w = r.json()

                if r.status_code != 200:
                    st.error(f"City not found: {target_city}")
                else:
                    st.success(f"Weather for **{w['name']}**, India")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("🌡️ Temperature", f"{w['main']['temp']:.1f} °C")
                    c2.metric("💧 Humidity",     f"{w['main']['humidity']} %")
                    c3.metric("💨 Wind Speed",   f"{w['wind']['speed']} m/s")
                    c4.metric("☁️ Condition",    w['weather'][0]['description'].title())
                    st.divider()

                    temp = w['main']['temp']
                    hum  = w['main']['humidity']
                    cond = w['weather'][0]['main']

                    st.subheader("🌱 Farming Advisory")
                    if cond == "Rain":
                        st.info("🌧️ **Rain detected** — Avoid spraying pesticides today. Good time for transplanting.")
                    elif cond == "Thunderstorm":
                        st.warning("⛈️ **Thunderstorm** — Keep farm workers indoors. Secure equipment and young crops.")
                    elif temp > 38:
                        st.warning("🔥 **Very high temperature** — Irrigate early morning or evening. Mulch to retain moisture.")
                    elif temp < 10:
                        st.info("❄️ **Cold conditions** — Protect seedlings. Good time for Rabi crop sowing.")
                    elif hum > 80:
                        st.warning("💦 **High humidity** — Watch for fungal diseases. Ensure good air circulation.")
                    else:
                        st.success("✅ **Good farming conditions** — Suitable for field work, spraying and irrigation.")

                    st.subheader("📅 5-Day Forecast")
                    fr = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={
                        "q": f"{target_city},IN", "appid": OPENWEATHER_KEY, "units": "metric"
                    }, timeout=8).json()

                    seen_days, forecast_items = set(), []
                    for item in fr.get("list", []):
                        day = item["dt_txt"][:10]
                        if day not in seen_days:
                            seen_days.add(day)
                            forecast_items.append(item)
                        if len(forecast_items) == 5: break

                    fcols = st.columns(5)
                    for i, item in enumerate(forecast_items):
                        with fcols[i]:
                            day_label = datetime.strptime(item["dt_txt"][:10], "%Y-%m-%d").strftime("%a %d %b")
                            st.markdown(f"**{day_label}**")
                            st.write(f"{item['main']['temp']:.0f}°C")
                            st.caption(item['weather'][0]['description'].title())

            except Exception as e:
                st.error(f"Weather fetch failed: {e}")

st.divider()