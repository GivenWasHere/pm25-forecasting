import streamlit as st
import pandas as pd
import joblib
import numpy as np
from aplikasi import load_dataframes

FEATURES = ['pm25', 'tem', 'hum', 'pre', 'ap', 'ws', 'wd', 'pbl', 'sr']

# --- FUNGSI KRITIS: PREPROCESSING ---
# Anda HARUS mengganti isi fungsi ini dengan langkah-langkah
# preprocessing yang Anda gunakan di 'Eksperimen_Skripsi.ipynb'
def preprocess_raw_data(raw_df):
    """
    Mengubah data mentah (dari file CSV yang baru diunggah) 
    menjadi format 'processed_data.csv', sesuai dengan notebook.
    """
    
    try:
        processed_df = raw_df.copy()
        
        # 1. Konversi 'time' dan set sebagai index (dari Notebook Cell 4)
        processed_df['time'] = pd.to_datetime(processed_df['time'])
        processed_df = processed_df.set_index('time')
        
        # 2. Cek missing values (dari Notebook Cell 28)
        null_count = processed_df.isnull().sum().sum()
        if null_count > 0:
            st.warning(f"Data mentah mengandung {null_count} nilai null. Melakukan interpolasi linier...")
            # Lakukan interpolasi linier
            processed_df = processed_df.interpolate(method='linear')
            st.success("Interpolasi selesai.")
        else:
            st.write("")
        
        # Cek apakah semua kolom yang diperlukan ada
        missing_cols = [col for col in FEATURES if col not in processed_df.columns]
        if missing_cols:
            st.error(f"Data mentah kekurangan kolom: {', '.join(missing_cols)}")
            return None
            
        # Susun ulang kolom agar sesuai dengan urutan saat training
        processed_df = processed_df[FEATURES]
        
        return processed_df
        
    except Exception as e:
        st.error(f"Error saat preprocessing: {e}")
        st.exception(e)
        return None

# --- HALAMAN STREAMLIT ---
st.title("Unggah Data")
st.markdown("Unggah data pada aplikasi")
st.warning("**PERHATIAN**: Berkas baru berisi data historis dan tambahannya akan menimpa berkas sebelumnya. Pastikan Anda memiliki cadangan berkas sebelum melanjutkan. Perhatikan syarat untuk mengunggah data!", icon="⚠️")

_, _, start_time, end_time = load_dataframes()     
st.write(f"""Rentang waktu data saat ini mulai dari **{start_time.strftime('%d-%m-%Y %H:%M')}** hingga **{end_time.strftime('%d-%m-%Y %H:%M')}**.""")
''
''

st.markdown(
    '''
    **Syarat:**
    1. Berkas harus dalam format *comma-separated values* (CSV).
    2. Berkas harus memiliki 10 kolom, yaitu: time, pm25, tem, hum, pre, ap, ws, wd, pbl, dan sr.
    3. Urutan dan penamaan kolom harus sesuai seperti di atas.
    4. Kolom 'time' harus dengan format 'yyyy-mm-ddThh:mm', contohnya: '2020-12-25T15:00'.
    5. Kolom 'time' harus berisi waktu yang berurutan tanpa ada pukul yang terlewat.
    ''')
''
''
st.write("Sebagai gambaran awal, Anda dapat mengunduh contoh data di bawah ini.")

dummy_data_path = "Contoh Data.csv"

with open(dummy_data_path, "rb") as csv_file:
    csv_bytes = csv_file.read()

st.download_button(
    label="**Unduh Contoh Data**",
    data=csv_bytes,
    file_name="Contoh Data.csv",
    mime="text/csv"
)
''
''

# 1. Widget Pengunggah File
uploaded_file = st.file_uploader("Unggah berkas di sini", type=["csv"])

if uploaded_file:
    
    # 2. Tombol Aksi
    if st.button("**Mulai**", type='primary'):
        with st.spinner("Memproses..."):
            try:
                df_new_raw = pd.read_csv(uploaded_file)
                
                df_existing_processed = pd.read_csv('processed_data.csv', parse_dates=['time'], index_col='time')
                df_existing_scaled = pd.read_csv('scaled_data.csv', parse_dates=['time'], index_col='time')
                
                scaler = joblib.load('scaler.pkl')

                # --- Langkah B: Preprocessing Data Baru ---
                # Ini adalah bagian yang harus Anda kustomisasi
                df_new_processed = preprocess_raw_data(df_new_raw)
                
                if df_new_processed is not None:
                    
                    # --- Langkah C: Scaling Data Baru ---
                    # Pastikan urutan kolom sesuai dengan 'FEATURES'
                    df_new_processed_ordered = df_new_processed[FEATURES]
                    
                    # Gunakan .transform(), JANGAN .fit_transform()
                    new_scaled_values = scaler.transform(df_new_processed_ordered)
                    
                    df_new_scaled = pd.DataFrame(new_scaled_values, 
                                                 columns=FEATURES, 
                                                 index=df_new_processed.index)

                    # --- Langkah D: Gabungkan Data ---
                    df_combined_processed = pd.concat([df_existing_processed, df_new_processed])
                    df_combined_scaled = pd.concat([df_existing_scaled, df_new_scaled])
                    
                    # Hapus duplikat (jika ada data tumpang tindih), ambil yang terakhir
                    df_combined_processed = df_combined_processed[~df_combined_processed.index.duplicated(keep='last')].sort_index()
                    df_combined_scaled = df_combined_scaled[~df_combined_scaled.index.duplicated(keep='last')].sort_index()

                    # --- Langkah E: Simpan File ---
                    df_combined_processed.to_csv('processed_data.csv')
                    df_combined_scaled.to_csv('scaled_data.csv')

                    # --- Langkah F: Hapus Cache ---
                    st.cache_data.clear()
                    st.cache_resource.clear()

                    st.success("Selesai! Data telah berhasil diperbarui. Silakan muat ulang halaman aplikasi.")
                    st.balloons()

            except Exception as e:
                st.error(f"Terjadi kesalahan saat proses update: {e}")
                st.exception(e)