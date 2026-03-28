import streamlit as st
import pandas as pd
import json
import re
import os
from dotenv import load_dotenv
from groq import Groq

# --- Load API key ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found. Please add it to your .env file.")
    st.code("GROQ_API_KEY=your_key_here", language="bash")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="AgroVeda Smart Calendar", page_icon="🌾", layout="wide")
st.title("🌾 AgroVeda Smart Calendar")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("niti_ayog_crop_data.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Selectors ---
col1, col2 = st.columns(2)
with col1:
    state = st.selectbox("Select State", sorted(df["State"].unique()))
with col2:
    crops = sorted(df[df["State"] == state]["Crop Name"].unique())
    crop = st.selectbox("Select Crop", crops)

# --- Show regional info ---
matches = df[(df["State"] == state) & (df["Crop Name"] == crop)]
if not matches.empty:
    row = matches.iloc[0]
    season   = row["Season"]
    category = row["Crop Category"]

    i1, i2, i3 = st.columns(3)
    i1.metric("State", state)
    i2.metric("Season", season)
    i3.metric("Category", category)

# --- Groq/Llama API call ---
def get_crop_guide(crop_name, season, state):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are an expert agricultural advisor for Indian farmers.
Give a detailed practical farming guide for {crop_name} grown in {state}, India during the {season} season.

Return ONLY a valid JSON object with exactly these keys, no extra text, no markdown, no explanation:
{{
  "sowing_method": "how to sow/plant this crop",
  "best_sowing_months": "e.g. June-July",
  "harvest_months": "e.g. October-November",
  "harvest_duration": "e.g. 90-120 days",
  "sun_requirements": "Full Sun / Partial Shade etc",
  "soil_type": "best soil type",
  "water_needs": "irrigation frequency and amount",
  "plant_spacing_cm": "spacing between plants in cm",
  "row_spacing_cm": "spacing between rows in cm",
  "fertilizer": "recommended fertilizer and schedule",
  "common_pests": "2-3 common pests and basic control",
  "yield_per_hectare": "expected yield",
  "market_tip": "one market or storage tip relevant to {state}",
  "pro_tip": "one expert tip specific to {season} season in {state}"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # best free Llama model on Groq
        messages=[
            {
                "role": "system",
                "content": "You are an agricultural expert. Always respond with valid JSON only. No markdown, no explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()
    return json.loads(raw)

# --- Generate Button ---
st.divider()
if st.button(" Generate Growth Calendar", use_container_width=True):
    if matches.empty:
        st.error("No data found for this state/crop combination.")
        st.stop()

    with st.spinner(f"Generating crop guide for {crop} in {state}..."):
        try:
            guide = get_crop_guide(crop, season, state)

            st.success(f"✅ Growth Guide Generated for {crop}")

            st.subheader("📅 Crop Calendar")
            st.write(f"🟢 **Sow:** {guide.get('best_sowing_months', '')}  →  🟡 **Grow**  →  🟠 **Harvest:** {guide.get('harvest_months', '')}")
            st.divider()

            st.subheader("📋 Complete Farming Guide")
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("**🌱 Sowing**")
                st.write(f"- Method: {guide.get('sowing_method', 'N/A')}")
                st.write(f"- Best months: {guide.get('best_sowing_months', 'N/A')}")
                st.write(f"- Plant spacing: {guide.get('plant_spacing_cm', 'N/A')} cm")
                st.write(f"- Row spacing: {guide.get('row_spacing_cm', 'N/A')} cm")
                st.markdown("**☀️ Growing Conditions**")
                st.write(f"- Sun: {guide.get('sun_requirements', 'N/A')}")
                st.write(f"- Soil: {guide.get('soil_type', 'N/A')}")
                st.write(f"- Water: {guide.get('water_needs', 'N/A')}")

            with c2:
                st.markdown("**🌾 Harvest**")
                st.write(f"- Harvest months: {guide.get('harvest_months', 'N/A')}")
                st.write(f"- Duration: {guide.get('harvest_duration', 'N/A')}")
                st.write(f"- Expected yield: {guide.get('yield_per_hectare', 'N/A')}")
                st.markdown("**🧪 Inputs**")
                st.write(f"- Fertilizer: {guide.get('fertilizer', 'N/A')}")
                st.write(f"- Pests: {guide.get('common_pests', 'N/A')}")

            st.divider()
            st.info(f"**Pro Tip ({season} in {state}):** {guide.get('pro_tip', '')}")
            st.success(f"**Market Tip:** {guide.get('market_tip', '')}")
            

        except json.JSONDecodeError:
            st.error("Model returned unexpected format. Please try again.")
        except Exception as e:
            st.error(f"Error: {e}")