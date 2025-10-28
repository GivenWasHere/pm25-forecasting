import streamlit as st
from tensorflow.keras.models import load_model
import pandas as pd
import joblib
from cards import (
    validasi_card,
    tentang_card
)

n_past = 24       
n_features = 9    
features = ['pm25', 'tem', 'hum', 'pre', 'ap', 'ws', 'wd', 'pbl', 'sr']
pm25_index = features.index('pm25') 
horizons = [1, 3, 6] 

st.set_page_config(page_icon="💨", layout="wide")

@st.cache_resource
def load_model_scaler():
    model = load_model('model.keras') 
    scaler = joblib.load('scaler.pkl')

    return model, scaler

@st.cache_data
def load_dataframes():
    df_processed = pd.read_csv('processed_data.csv', parse_dates=['time'], index_col='time')
    df_scaled = pd.read_csv('scaled_data.csv', parse_dates=['time'], index_col='time')

    start_time = df_processed.index[n_past]
    end_time = df_processed.index[-max(horizons) - 1]

    return df_processed, df_scaled, start_time, end_time

pages = [
    st.Page(
        "prediksi.py",
        title="Prediksi"
    ),
    st.Page(
        "validasi.py",
        title="Validasi"
    ),
    st.Page(
        "tentang.py",
        title="Tentang"
    )
]

page = st.navigation(pages)
page.run()

with st.sidebar.container(height=310):
    if page.title == "Validasi":
        validasi_card()
    elif page.title == "Tentang":
        tentang_card()
    else:
        st.page_link("prediksi.py", label="Prediksi")
        st.write("Halaman ini berfungsi untuk menghasilkan prediksi PM2.5 secara jangka pendek. Coba dengan memasukkan variabel yang diperlukan dan lihat hasilnya.")