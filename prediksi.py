import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from aplikasi import(
    load_model_scaler
)

n_past = 24       
n_features = 9    
features = ['pm25', 'tem', 'hum', 'pre', 'ap', 'ws', 'wd', 'pbl', 'sr']
pm25_index = features.index('pm25') 
horizons = [1, 3, 6] 

model, scaler = load_model_scaler()

def get_pm25_label_html(pm25_value):
    base_style = (
        "padding: 3px 9px;"
        "border-radius: 0.55rem;"
        "color: white;"
        "font-weight: bold;"
        "display: inline-block;"
    )

    if pd.isna(pm25_value):
        style = f"{base_style} background-color: gray;"
        return "Tidak teridentifikasi", style, "gray"
    
    pm25_value = round(pm25_value) 
    
    if 0 <= pm25_value <= 30:
        color = "green"
        label = "Baik"
    elif 31 <= pm25_value <= 60:
        color = "#ffcc00"
        label = "Sedang"
    elif 61 <= pm25_value <= 90:
        color = "orange"
        label = "Waspada"
    elif 91 <= pm25_value <= 120:
        color = "red"
        label = "Tidak sehat"
    elif 121 <= pm25_value <= 250:
        color = "purple"
        label = "Buruk"
    elif pm25_value >= 251:
        color = "black"
        label = "Beracun"
    else:
        color = "gray"
        label = "Tidak teridentifikasi"
    
    style = f"{base_style} background-color: {color};"
        
    return label, style, color

def get_recommendation(label):
    if label == "Baik":
        return "**Kualitas udara sangat baik. Masyarakat boleh berkegiatan di outdoor dengan bebas.**", "success"
    elif label == "Sedang":
        return "**Kualitas udara masih dapat diterima. Kelompok sensitif (anak-anak, lansia, penderita asma) disarankan mengurangi aktivitas fisik berat di luar ruangan.**", "info"
    elif label == "Waspada":
        return "**Kualitas udara mulai memburuk. Kelompok sensitif sebaiknya menghindari aktivitas di luar ruangan. Masyarakat umum disarankan menggunakan masker jika beraktivitas di luar.**", "warning"
    elif label == "Tidak Sehat":
        return "**Kualitas udara tidak sehat. Masyarakat umum disarankan mengurangi aktivitas di luar ruangan dan menggunakan masker. Kelompok sensitif harus tetap berada di dalam ruangan.**", "error"
    elif label == "Buruk":
        return "**Sangat tidak sehat! Hindari semua aktivitas di luar ruangan. Gunakan masker N95 jika terpaksa keluar. Nyalakan pembersih udara (air purifier) jika ada.**", "error"
    elif label == "Beracun":
        return "**BERBAHAYA! Dilarang beraktivitas di luar ruangan. Tutup semua jendela dan ventilasi. Nyalakan pembersih udara (air purifier)**.", "error"
    else:
        return "**Tidak ada himbauan untuk kategori ini.**", "info"

def prediction_postprocessing(prediction_scaled, scaler):
    y_pred_flat = prediction_scaled.flatten() 
    y_pred_real = []
    for pred_val in y_pred_flat:
        dummy_array = np.zeros((1, n_features))
        dummy_array[0, pm25_index] = pred_val
        inv_pred = scaler.inverse_transform(dummy_array)
        y_pred_real.append(inv_pred[0, pm25_index])
    return y_pred_real 

def calculate_percentage_error(actual, predicted):
    if pd.isna(actual) or actual == 0:
        return None
    error = np.abs(actual - predicted) / actual * 100
    return error

def preprocess_input(data_dict, scaler):
    list_input = [data_dict[feature] for feature in features]
    array_input = np.array(list_input).reshape(1, -1) 
    scaled_input = scaler.transform(array_input) 
    sequence_input = np.repeat(scaled_input, n_past, axis=0) 
    model_input = sequence_input.reshape((1, n_past, n_features))
    return model_input


st.title("Prediksi PM2.5")
st.markdown("Jalan Hang Jebat, Kelurahan Gunung, Kecamatan Kebayoran Baru, Kota Administrasi Jakarta Selatan")
''
''

data_input = {}
col1, col2 = st.columns(2)

with col1:
    data_input['pm25'] = st.slider("PM2.5 saat ini (µg/m³)", 0, 300, 0)
    data_input['tem'] = st.slider("Suhu (°C)", 20, 40, 20)
    data_input['hum'] = st.slider("Kelembapan (%)", 20, 100, 20)
    data_input['ws'] = st.slider("Kecepatan angin (m/s)", 0.0, 30.0, 0.0, step=0.1)
    data_input['sr'] = st.slider("Radiasi Matahari (W/m²)", 0, 1100, 0)

with col2:
    data_input['pbl'] = st.number_input("Tinggi lapisan batas planet (m)", min_value=0, max_value=300000, value=0, step=50)
    data_input['ap'] = st.slider("Tekanan udara (hPa)", 1000.0, 1015.0, 1000.0, step=0.1)
    data_input['pre'] = st.slider("Curah hujan (mm)", 0.0, 25.0, 0.0, step=0.1)
    data_input['wd'] = st.slider("Arah angin (°)", 0, 360, 0)

if st.button("**Prediksi**", type="primary"):
    with st.spinner("Memproses..."):
            
        model_input = preprocess_input(data_input, scaler)
            
        if model_input is not None:
            pred_scaled = model.predict(model_input)
            predictions_real = prediction_postprocessing(pred_scaled, scaler)
                
            if np.isnan(predictions_real).any():
                st.error("ERROR: Model menghasilkan 'NaN'. Cek file 'scaler.pkl' Anda.")
            else:
                st.success("Prediksi berhasil!")
                ''
                ''
                st.title("Hasil Prediksi")
                ''
                ''  
                current_pm25 = data_input['pm25']
                actual_label, actual_style, _ = get_pm25_label_html(current_pm25)

                with st.container(border=True):
                    st.metric("PM2.5 saat ini", f"{current_pm25:.2f} µg/m³")
                    st.markdown(f'<span style="{actual_style}">{actual_label}</span>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3, border=True)
                    
                label_1jam = "" 
                    
                with col1:
                    val = predictions_real[0]
                    label, style, _ = get_pm25_label_html(val)
                    label_1jam = label 
                    st.metric("1 jam ke depan", f"{val:.2f} µg/m³")
                    st.markdown(f'<span style="{style}">{label}</span>', unsafe_allow_html=True)
                with col2:
                    val = predictions_real[1]
                    label, style, _ = get_pm25_label_html(val)
                    st.metric("3 jam ke depan", f"{val:.2f} µg/m³")
                    st.markdown(f'<span style="{style}">{label}</span>', unsafe_allow_html=True)
                with col3:
                    val = predictions_real[2]
                    label, style, _ = get_pm25_label_html(val)
                    st.metric("6 jam ke depan", f"{val:.2f} µg/m³")
                    st.markdown(f'<span style="{style}">{label}</span>', unsafe_allow_html=True)
                ''
                ''

                leg_col1, leg_col2 = st.columns(2)

                with leg_col1:
                    style_baik = get_pm25_label_html(0)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_baik}">Baik</span> : 0 - 30 µg/m³', 
                        unsafe_allow_html=True
                    )
    
                    style_sedang = get_pm25_label_html(35)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_sedang}">Sedang</span> : 31 - 60 µg/m³', 
                        unsafe_allow_html=True
                    )
    
                    style_waspada = get_pm25_label_html(65)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_waspada}">Waspada</span> : 61 - 90 µg/m³', 
                        unsafe_allow_html=True
                    )

                with leg_col2:
                    style_tidak_sehat = get_pm25_label_html(95)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_tidak_sehat}">Tidak Sehat</span> : 91 - 120 µg/m³', 
                        unsafe_allow_html=True
                    )
    
                    style_buruk = get_pm25_label_html(125)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_buruk}">Buruk</span> : 121 - 250 µg/m³', 
                        unsafe_allow_html=True
                    )
    
                    style_beracun = get_pm25_label_html(255)[1].replace("display: inline-block;", "")
                    st.markdown(
                        f'<span style="{style_beracun}">Beracun</span> : 251+ µg/m³', 
                        unsafe_allow_html=True
                    )

                ''
                ''
                st.markdown("## Himbauan 1 Jam Selanjutnya")
                    
                himbauan_teks, himbauan_tipe = get_recommendation(label_1jam)
                    
                if himbauan_tipe == "success":
                    st.success(himbauan_teks, icon="✅")
                elif himbauan_tipe == "info":
                    st.info(himbauan_teks, icon="ℹ️")
                elif himbauan_tipe == "warning":
                    st.warning(himbauan_teks, icon="⚠️")
                elif himbauan_tipe == "error":
                    st.error(himbauan_teks, icon="🚨")