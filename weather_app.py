import numpy as np
import pandas as pd
import requests as req
import streamlit as st
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from datetime import datetime, timedelta
import pytz

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RainSense · Weather Intelligence",
    page_icon="🌧️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0b0f1a;
    color: #e8eaf0;
}
.stApp { background-color: #0b0f1a; }

/* ── Header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 60%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p {
    color: #6b7280;
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.04em;
}

/* ── Search bar ── */
.stTextInput > div > div > input {
    background: #141829 !important;
    border: 1.5px solid #1e2540 !important;
    border-radius: 14px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1.2rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,0.15) !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2.2rem !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Stat cards ── */
.card-grid { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0; }
.stat-card {
    background: #141829;
    border: 1px solid #1e2540;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    flex: 1;
    min-width: 140px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
.stat-card .label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4b5563;
    margin-bottom: 0.5rem;
}
.stat-card .value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
}
.stat-card .unit {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.3rem;
}
.stat-card .icon {
    position: absolute;
    top: 1rem; right: 1.1rem;
    font-size: 1.5rem;
    opacity: 0.18;
}

/* ── Rain badge ── */
.rain-banner {
    border-radius: 18px;
    padding: 1.8rem 2rem;
    text-align: center;
    margin: 1rem 0 1.5rem;
    font-family: 'Syne', sans-serif;
}
.rain-yes {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a2a4a 100%);
    border: 1.5px solid #3b82f6;
}
.rain-no {
    background: linear-gradient(135deg, #1a3a2a 0%, #112a1e 100%);
    border: 1.5px solid #22c55e;
}
.rain-banner .big { font-size: 2.8rem; margin-bottom: 0.2rem; }
.rain-banner .title { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px; }
.rain-banner .sub { color: #9ca3af; font-size: 0.9rem; margin-top: 0.3rem; font-family: 'DM Sans', sans-serif; }

/* ── Section headers ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #4b5563;
    margin: 2rem 0 1rem;
    border-left: 3px solid #3b82f6;
    padding-left: 0.8rem;
}

/* ── City header ── */
.city-header {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin-bottom: 0.1rem;
}
.city-sub { color: #6b7280; font-size: 0.95rem; text-transform: capitalize; }

/* ── Divider ── */
hr { border-color: #1e2540 !important; }

/* ── Plotly dark patch ── */
.js-plotly-plot { border-radius: 18px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Backend functions (all bugs fixed) ────────────────────────────────────────
API_KEY = 'f38bb78f99b35bcb38646b2b9d13be59'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

COMPASS_POINTS = [
    ("N", 0, 11.25), ("NNE", 11.25, 33.75), ("NE", 33.75, 56.25),
    ("ENE", 56.25, 78.75), ("E", 78.75, 101.25), ("ESE", 101.25, 123.75),
    ("SE", 123.75, 146.25), ("SSE", 146.25, 168.75), ("S", 168.75, 191.25),
    ("SSW", 191.25, 213.75), ("SW", 213.75, 236.25), ("WSW", 236.25, 258.75),
    ("W", 258.75, 281.25), ("WNW", 281.25, 303.75), ("NW", 303.75, 326.25),
    ("NNW", 326.25, 348.75), ("N", 348.75, 360),
]


def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = req.get(url)
    if response.status_code != 200:
        return None
    data = response.json()          # ← FIX: was .json (missing parentheses)
    return {
        'city':           data['name'],
        'current_temp':   round(data['main']['temp']),
        'feels_like':     round(data['main']['feels_like']),
        'temp_min':       round(data['main']['temp_min']),
        'temp_max':       round(data['main']['temp_max']),
        'humidity':       round(data['main']['humidity']),
        'description':    data['weather'][0]['description'],
        'country':        data['sys']['country'],
        'wind_gust_dir':  data['wind']['deg'],
        'pressure':       data['main']['pressure'],
        'wind_gust_speed': data['wind']['speed'],
    }


def read_historical_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df = df.drop_duplicates()
    return df


def prepare_data(data):
    encode = LabelEncoder()
    data = data.copy()
    data['WindGustDir']   = encode.fit_transform(data['WindGustDir'])
    data['RainTomorrow']  = encode.fit_transform(data['RainTomorrow'])
    # FIX: was 'Pressure,Temp' (typo) and single brackets
    X = data[['MinTemp', 'MaxTemp', 'WindGustDir', 'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
    y = data['RainTomorrow']
    return X, y, encode


def train_model(X, y):
    # FIX: correct unpacking order
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    # FIX: predict takes only X_test
    y_pred = model.predict(X_test)
    return model


def prepare_forecasting(data, feature):
    X, y = [], []
    for i in range(len(data) - 1):
        X.append(data[feature].iloc[i])
        y.append(data[feature].iloc[i + 1])
    return np.array(X).reshape(-1, 1), np.array(y)


def train_regressor_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def predict_future(model, current_value):
    predictions = [current_value]
    for _ in range(5):
        next_val = model.predict(np.array([[predictions[-1]]]))
        predictions.append(next_val[0])
    return predictions[1:]


def get_future_times():
    timezone = pytz.timezone('Asia/Kolkata')   # FIX: was 'Asis/Kolkata'
    now = datetime.now(timezone)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    # FIX: strftime on full expression, correct list comprehension
    return [(next_hour + timedelta(hours=i)).strftime("%H:00") for i in range(5)]


def deg_to_compass(deg):
    wind_deg = deg % 360
    return next(pt for pt, start, end in COMPASS_POINTS if start <= wind_deg < end)


# ── Plotly chart helpers ───────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#9ca3af'),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(showgrid=False, color='#374151'),
    yaxis=dict(showgrid=True, gridcolor='#1e2540', color='#374151'),
)


def temp_chart(times, values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=values,
        mode='lines+markers',
        line=dict(color='#f97316', width=2.5, shape='spline'),
        marker=dict(size=7, color='#f97316', line=dict(color='#0b0f1a', width=2)),
        fill='tozeroy',
        fillcolor='rgba(249,115,22,0.08)',
        name='Temperature',
    ))
    fig.update_layout(**CHART_LAYOUT, title=dict(text='Temperature Forecast (°C)', font=dict(size=13, color='#6b7280')))
    return fig


def humid_chart(times, values):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=times, y=values,
        marker=dict(
            color=values,
            colorscale=[[0, '#1d4ed8'], [1, '#60a5fa']],
            line=dict(color='rgba(0,0,0,0)'),
        ),
        name='Humidity',
    ))
    fig.update_layout(**CHART_LAYOUT, title=dict(text='Humidity Forecast (%)', font=dict(size=13, color='#6b7280')))
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌧 RainSense</h1>
  <p>Real-time weather intelligence · ML-powered rainfall prediction</p>
</div>
""", unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    city_input = st.text_input("", placeholder="Enter city name  e.g. Kolkata, Mumbai, Delhi …", label_visibility="collapsed")
with col_btn:
    st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
    search = st.button("Analyse →")
    st.markdown("</div>", unsafe_allow_html=True)

uploaded = st.file_uploader("Upload your `weather.csv` historical data file", type=["csv"])

st.markdown("<hr>", unsafe_allow_html=True)

if search and city_input:
    if not uploaded:
        st.warning("⚠️  Please upload your `weather.csv` file above to enable ML predictions.")
        st.stop()

    with st.spinner("Fetching weather data …"):
        weather = get_current_weather(city_input.strip())

    if weather is None:
        st.error("❌  City not found. Check the spelling and try again.")
        st.stop()

    with st.spinner("Training ML models on your historical data …"):
        hist = read_historical_data(uploaded)
        X, y, encoder = prepare_data(hist)
        rain_model = train_model(X, y)

        compass = deg_to_compass(weather['wind_gust_dir'])
        compass_enc = encoder.transform([compass])[0] if compass in encoder.classes_ else -1

        current_df = pd.DataFrame([{
            'MinTemp':      weather['temp_min'],
            'MaxTemp':      weather['temp_max'],
            'WindGustDir':  compass_enc,
            'WindGustSpeed': weather['wind_gust_speed'],
            'Humidity':     weather['humidity'],
            'Pressure':     weather['pressure'],
            'Temp':         weather['current_temp'],
        }])
        rain_pred = rain_model.predict(current_df)[0]

        X_temp,  y_temp  = prepare_forecasting(hist, 'Temp')
        X_humid, y_humid = prepare_forecasting(hist, 'Humidity')
        temp_model  = train_regressor_model(X_temp,  y_temp)
        humid_model = train_regressor_model(X_humid, y_humid)

        fut_temp  = predict_future(temp_model,  weather['temp_min'])
        fut_humid = predict_future(humid_model, weather['humidity'])
        fut_times = get_future_times()

    # ── City banner ──
    st.markdown(f"""
    <div class="city-header">📍 {weather['city']}, {weather['country']}</div>
    <div class="city-sub">{weather['description']} · Wind {compass} · {weather['wind_gust_speed']} m/s</div>
    """, unsafe_allow_html=True)

    # ── Rain prediction banner ──
    if rain_pred:
        st.markdown("""
        <div class="rain-banner rain-yes">
          <div class="big">🌧️</div>
          <div class="title">Rain Expected Tomorrow</div>
          <div class="sub">ML model predicts rainfall based on current conditions</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="rain-banner rain-no">
          <div class="big">☀️</div>
          <div class="title">No Rain Tomorrow</div>
          <div class="sub">ML model predicts clear skies based on current conditions</div>
        </div>""", unsafe_allow_html=True)

    # ── Stat cards ──
    st.markdown('<div class="section-title">Current Conditions</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card-grid">
      <div class="stat-card">
        <div class="icon">🌡️</div>
        <div class="label">Temperature</div>
        <div class="value">{weather['current_temp']}°</div>
        <div class="unit">Celsius</div>
      </div>
      <div class="stat-card">
        <div class="icon">🤔</div>
        <div class="label">Feels Like</div>
        <div class="value">{weather['feels_like']}°</div>
        <div class="unit">Celsius</div>
      </div>
      <div class="stat-card">
        <div class="icon">🔻</div>
        <div class="label">Min Temp</div>
        <div class="value">{weather['temp_min']}°</div>
        <div class="unit">Celsius</div>
      </div>
      <div class="stat-card">
        <div class="icon">🔺</div>
        <div class="label">Max Temp</div>
        <div class="value">{weather['temp_max']}°</div>
        <div class="unit">Celsius</div>
      </div>
      <div class="stat-card">
        <div class="icon">💧</div>
        <div class="label">Humidity</div>
        <div class="value">{weather['humidity']}%</div>
        <div class="unit">Relative</div>
      </div>
      <div class="stat-card">
        <div class="icon">🌀</div>
        <div class="label">Pressure</div>
        <div class="value">{weather['pressure']}</div>
        <div class="unit">hPa</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Forecast charts ──
    st.markdown('<div class="section-title">5-Hour Forecast</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(temp_chart(fut_times, fut_temp), use_container_width=True)
    with c2:
        st.plotly_chart(humid_chart(fut_times, fut_humid), use_container_width=True)

    # ── Forecast table ──
    st.markdown('<div class="section-title">Hourly Breakdown</div>', unsafe_allow_html=True)
    forecast_df = pd.DataFrame({
        'Time': fut_times,
        'Temperature (°C)': [round(t, 1) for t in fut_temp],
        'Humidity (%)':     [round(h, 1) for h in fut_humid],
    })
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)

elif search and not city_input:
    st.warning("Please type a city name first.")