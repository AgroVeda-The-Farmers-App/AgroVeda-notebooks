import streamlit as st
import pandas as pd
import requests

df = pd.read_csv("niti_ayog_crop_data.csv", encoding="utf-8-sig")
df.columns = df.columns.str.strip()

state = st.selectbox("State", sorted(df["State"].unique()))
crops = df[df["State"] == state]["Crop Name"].unique()
crop  = st.selectbox("Crop", sorted(crops))

if st.button("Generate Calendar"):
    row = df[(df["State"] == state) & (df["Crop Name"] == crop)].iloc[0]
    st.write(f"Season: **{row['Season']}**  |  Category: **{row['Crop Category']}**")

    # OpenFarm API call — safely handled
    try:
        res = requests.get(
            f"https://openfarm.cc/api/v1/crops?filter={crop}",
            timeout=5,
            headers={"Accept": "application/json"}
        )
        res.raise_for_status()
        payload = res.json()
        data = payload.get("data", [])
    except Exception:
        data = []
        

    if data:
        attrs = data[0]["attributes"]
        st.subheader(f"Growth Guide: {crop}")
        st.write(f"**Sowing method:** {attrs.get('sowing_method') or 'N/A'}")
        st.write(f"**Sun requirements:** {attrs.get('sun_requirements') or 'N/A'}")
        st.write(f"**Plant spacing:** {attrs.get('spread') or 'N/A'} cm")
        st.write(f"**Row spacing:** {attrs.get('row_spacing') or 'N/A'} cm")
        description = attrs.get('description') or ''
        st.write(f"**Description:** {description[:300]}")
    else:
        st.info(
            f"No detailed guide found on OpenFarm for **'{crop}'**. "
            f"OpenFarm works best with specific crop names like *Rice*, *Wheat*, *Tomato* — "
            f"not category names like *Cereals* or *Foodgrains*."
        )