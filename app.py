import streamlit as st
import joblib
import numpy as np

# Load models
model = joblib.load("saved/xgb_yield_model.pkl")
le_state = joblib.load("saved/state_encode.pkl")
le_district = joblib.load("saved/district_encode.pkl")
le_season = joblib.load("saved/season_encode.pkl")
le_crop = joblib.load("saved/crop_encode.pkl")

st.set_page_config(page_title="AgroVeda", layout="centered")

st.title(" AgroVeda - Smart Yield Predictor")

# Inputs
state = st.selectbox("Select State", le_state.classes_)
district = st.selectbox("Select District", le_district.classes_)
season = st.selectbox("Select Season", le_season.classes_)
crop = st.selectbox("Select Crop", le_crop.classes_)
area = st.number_input("Enter Area (in hectares)", min_value=0.1)

# Predict
if st.button("Predict Yield"):

    try:
        # Encode
        state_enc = le_state.transform([state])[0]
        district_enc = le_district.transform([district])[0]
        season_enc = le_season.transform([season])[0]
        crop_enc = le_crop.transform([crop])[0]

        # Input array
        input_data = np.array([[state_enc, district_enc, 2020, season_enc, crop_enc, area]])

        # Prediction
        yield_pred = model.predict(input_data)[0]
        production = yield_pred * area

        # Output
        st.success(f" Predicted Yield: {yield_pred:.2f} t/ha")
        st.success(f" Expected Production: {production:.2f} tonnes")

    except Exception as e:
        st.error(f"Error: {e}")
    