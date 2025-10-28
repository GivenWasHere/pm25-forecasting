# import streamlit as st
# import pandas as pd
# import numpy as np
# import altair as alt
# from aplikasi import(
#     load_dataframes,
#     load_model_scaler
# )
# from prediksi import(
#     prediction_postprocessing,
#     get_pm25_label_html,
#     calculate_percentage_error
# )

# n_past = 24       
# n_features = 9    
# features = ['pm25', 'tem', 'hum', 'pre', 'ap', 'ws', 'wd', 'pbl', 'sr']
# pm25_index = features.index('pm25') 
# horizons = [1, 3, 6] 

# df_processed, df_scaled, start_time, end_time = load_dataframes()
# model, scaler = load_model_scaler()

# def get_model_historic_input(selected_time, df_scaled):
#     loc = df_scaled.index.get_loc(selected_time)
#     sequence_input = df_scaled.iloc[loc - n_past : loc][features].values
#     model_input = sequence_input.reshape((1, n_past, n_features))
#     return model_input

# st.title("Validasi")
# st.markdown("Uji akurasi prediksi yang dihasilkan")
# ''
# ''

# col1, col2 = st.columns([1, 2])

# with col1:
#     selected_date = st.date_input(
#         "Tanggal",
#         min_value=start_time.date(),
#         max_value=end_time.date(),
#         value=end_time.date() 
#     )

# with col2:
#     selected_hour = st.slider(
#         "Waktu (00.00 - 23.00)",
#         min_value=0,
#         max_value=23,
#         value=end_time.hour 
#     )

# selected_time_str = f"{selected_date.strftime('%Y-%m-%d')} {selected_hour:02d}:00"
# selected_time = pd.to_datetime(selected_time_str)

# if not (start_time <= selected_time <= end_time):
#     st.error(f"Waktu yang dipilih di luar rentang data yang valid, silahkan pilih waktu antara **{start_time.strftime('%Y-%m-%d %H:00')}** hingga **{end_time.strftime('%Y-%m-%d %H:00')}**.")
#     valid_selection = False
# else:
#     st.write(f"Waktu dipilih untuk analisis adalah **{selected_time.strftime('%Y-%m-%d %H:%M')}**.")
#     valid_selection = True

# if st.button("**Prediksi**", type="primary", disabled=(not valid_selection)):
#         with st.spinner("Memproses..."):
            
#             model_input = get_model_historic_input(selected_time, df_scaled)
            
#             if model_input is not None:
#                 pred_scaled = model.predict(model_input) 
#                 predictions_real = prediction_postprocessing(pred_scaled, scaler) 
                
#                 if np.isnan(predictions_real).any():
#                     st.error("ERROR: Model menghasilkan 'NaN'. Jalankan ulang `preprocess.py` dan clear cache.")
#                 else:
#                     st.success("Prediksi berhasil!")
#                     ''
#                     ''
#                     st.title(f"Hasil Prediksi")
#                     ''
#                     ''

#                     current_pm25 = df_processed.loc[selected_time, 'pm25']
#                     actual_label, actual_style, _ = get_pm25_label_html(current_pm25)

#                     with st.container(border=True):
#                         st.metric("PM2.5 saat ini", f"{current_pm25:.2f} µg/m³")
#                         st.markdown(f'<span style="{actual_style}">{actual_label}</span>', unsafe_allow_html=True)
                    
#                     pred_times = [selected_time + pd.Timedelta(hours=h) for h in horizons]
#                     actual_future_values = []
#                     for t in pred_times:
#                         try:
#                             actual_future_values.append(df_processed.loc[t, 'pm25'])
#                         except KeyError:
#                             actual_future_values.append(np.nan)
#                     ''
#                     ''
#                     leg_col1, leg_col2, leg_col3 = st.columns(3)

#                     with leg_col1:
#                         st.write("**1 jam ke depan**")
                    
#                     with leg_col2:
#                         st.write("**3 jam ke depan**")

#                     with leg_col3:
#                         st.write("**6 jam ke depan**")

#                     p_col1, p_col2, p_col3 = st.columns(3, border=True)
                    
#                     for i, col in enumerate([p_col1, p_col2, p_col3]):
#                         with col:
#                             horizon = horizons[i]

#                             val_pred = predictions_real[i]
#                             val_act = actual_future_values[i]
                            
#                             label_pred, style_pred, _ = get_pm25_label_html(val_pred)
#                             label_act, style_act, _ = get_pm25_label_html(val_act)
                            
#                             st.metric(f"Prediksi", f"{val_pred:.2f} µg/m³")
#                             st.markdown(f'<span style="{style_pred}">{label_pred}</span>', unsafe_allow_html=True)
#                             ''
#                             ''
#                             st.metric(f"Nilai sebenarnya", f"{val_act:.2f} µg/m³" if not pd.isna(val_act) else "N/A")
#                             st.markdown(f'<span style="{style_act}">{label_act}</span>', unsafe_allow_html=True)
#                             ''
#                             ''
#                             error = calculate_percentage_error(val_act, val_pred)
#                             if error is not None:
#                                 st.metric("Persentase kesalahan", f"{error:.2f} %")
#                             else:
#                                 st.text("Error: N/A")

#                     ''
#                     ''
#                     st.write("**PM2.5 24 jam terakhir**")
                    
#                     loc = df_processed.index.get_loc(selected_time)
#                     historic_data_slice = df_processed.iloc[loc - n_past : loc]
                    
#                     chart_data = historic_data_slice[['pm25']]
                    
#                     chart_data_altair = chart_data.reset_index()

#                     original_time_col_name = chart_data_altair.columns[0]
                    
#                     chart_data_altair = chart_data_altair.rename(columns={original_time_col_name: 'Waktu'})

#                     chart_data_altair['Waktu'] = pd.to_datetime(chart_data_altair['Waktu'])
#                     chart_data_altair['pm25'] = pd.to_numeric(chart_data_altair['pm25'], errors='coerce')

#                     if not chart_data_altair['pm25'].isna().all() and not chart_data_altair.empty:
                        
#                         base = alt.Chart(chart_data_altair).encode(
#                             x=alt.X('Waktu:T', title='Waktu', scale=alt.Scale()), 
#                             y=alt.Y('pm25:Q', title='PM2.5 (µg/m³)', scale=alt.Scale(zero=False)), 
#                             tooltip=[
#                                 alt.Tooltip('Waktu:T', format='%Y-%m-%d %H:%M', title='Waktu'), 
#                                 alt.Tooltip('pm25', title='PM2.5', format='.2f')
#                             ]
#                         )

#                         # Layer 1: Garis (TANPA point=True)
#                         line = base.mark_line(
#                             color='#60b5ff'  # Warna garis
#                         ).transform_filter(
#                             "isValid(datum.pm25)"
#                         )

#                         # Layer 2: Titik (dibuat terpisah agar warnanya bisa diatur)
#                         points = base.mark_point(
#                             color='#60b5ff', # Warna titik, disamakan dengan garis
#                             filled=True   # Opsional: membuat titiknya terisi penuh
#                         ).transform_filter(
#                             "isValid(datum.pm25)"
#                         )

#                         # Layer 3: Teks
#                         text = base.mark_text(
#                             align='center',
#                             dy=-10,
#                             color='white',
#                             fontSize=14  # <-- TAMBAHKAN UKURAN FONT DI SINI (misal 14)
#                         ).encode(
#                             text=alt.Text('pm25:Q', format='.2f')
#                         ).transform_filter(
#                             "isValid(datum.pm25)"
#                         )
#                         # --- AKHIR PERUBAHAN ---

#                         final_chart = (line + points + text).interactive()
                        
#                         st.altair_chart(final_chart, use_container_width=True)

#                     else:
#                         st.warning("Tidak ada data 'pm25' yang valid untuk digambar.")
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from aplikasi import(
    load_dataframes,
    load_model_scaler
)
from prediksi import(
    prediction_postprocessing,
    get_pm25_label_html,
    calculate_percentage_error
)

n_past = 24      
n_features = 9    
features = ['pm25', 'tem', 'hum', 'pre', 'ap', 'ws', 'wd', 'pbl', 'sr']
pm25_index = features.index('pm25') 
horizons = [1, 3, 6] 

df_processed, df_scaled, start_time, end_time = load_dataframes()
model, scaler = load_model_scaler()

def get_model_historic_input(selected_time, df_scaled):
    loc = df_scaled.index.get_loc(selected_time)
    sequence_input = df_scaled.iloc[loc - n_past : loc][features].values
    model_input = sequence_input.reshape((1, n_past, n_features))
    return model_input

st.title("Validasi")
st.markdown("Uji akurasi prediksi yang dihasilkan")
''
''

col1, col2 = st.columns([1, 2])

with col1:
    selected_date = st.date_input(
        "Tanggal",
        min_value=start_time.date(),
        max_value=end_time.date(),
        value=end_time.date() 
    )

with col2:
    selected_hour = st.slider(
        "Waktu (00.00 - 23.00)",
        min_value=0,
        max_value=23,
        value=end_time.hour 
    )

selected_time_str = f"{selected_date.strftime('%Y-%m-%d')} {selected_hour:02d}:00"
selected_time = pd.to_datetime(selected_time_str)

if not (start_time <= selected_time <= end_time):
    st.error(f"Waktu yang dipilih di luar rentang data yang valid, silahkan pilih waktu antara **{start_time.strftime('%Y-%m-%d %H:00')}** hingga **{end_time.strftime('%Y-%m-%d %H:00')}**.")
    valid_selection = False
else:
    st.write(f"Waktu dipilih untuk analisis adalah **{selected_time.strftime('%Y-%m-%d %H:%M')}**.")
    valid_selection = True

if st.button("**Prediksi**", type="primary", disabled=(not valid_selection)):
        with st.spinner("Memproses..."):
            
            model_input = get_model_historic_input(selected_time, df_scaled)
            
            if model_input is not None:
                pred_scaled = model.predict(model_input) 
                predictions_real = prediction_postprocessing(pred_scaled, scaler) 
                
                if np.isnan(predictions_real).any():
                    st.error("ERROR: Model menghasilkan 'NaN'. Jalankan ulang `preprocess.py` dan clear cache.")
                else:
                    st.success("Prediksi berhasil!")
                    ''
                    ''
                    st.title(f"Hasil Prediksi")
                    ''
                    ''

                    current_pm25 = df_processed.loc[selected_time, 'pm25']
                    actual_label, actual_style, _ = get_pm25_label_html(current_pm25)

                    with st.container(border=True):
                        st.metric("PM2.5 saat ini", f"{current_pm25:.2f} µg/m³")
                        st.markdown(f'<span style="{actual_style}">{actual_label}</span>', unsafe_allow_html=True)
                    
                    pred_times = [selected_time + pd.Timedelta(hours=h) for h in horizons]
                    actual_future_values = []
                    for t in pred_times:
                        try:
                            actual_future_values.append(df_processed.loc[t, 'pm25'])
                        except KeyError:
                            actual_future_values.append(np.nan)
                    ''
                    ''
                    leg_col1, leg_col2, leg_col3 = st.columns(3)

                    with leg_col1:
                        st.write("**1 jam ke depan**")
                    
                    with leg_col2:
                        st.write("**3 jam ke depan**")

                    with leg_col3:
                        st.write("**6 jam ke depan**")

                    # --- TAMBAHAN MAE/RMSE: Langkah 1. Inisialisasi lists ---
                    valid_predictions = []
                    valid_actuals = []
                    # ---------------------------------------------------

                    p_col1, p_col2, p_col3 = st.columns(3, border=True)
                    
                    for i, col in enumerate([p_col1, p_col2, p_col3]):
                        with col:
                            horizon = horizons[i]

                            val_pred = predictions_real[i]
                            val_act = actual_future_values[i]
                            
                            label_pred, style_pred, _ = get_pm25_label_html(val_pred)
                            label_act, style_act, _ = get_pm25_label_html(val_act)
                            
                            st.metric(f"Prediksi", f"{val_pred:.2f} µg/m³")
                            st.markdown(f'<span style="{style_pred}">{label_pred}</span>', unsafe_allow_html=True)
                            ''
                            ''
                            st.metric(f"Nilai sebenarnya", f"{val_act:.2f} µg/m³" if not pd.isna(val_act) else "N/A")
                            st.markdown(f'<span style="{style_act}">{label_act}</span>', unsafe_allow_html=True)
                            ''
                            ''
                            
                            # --- PERUBAHAN DI SINI ---
                            # --- TAMBAHAN MAE/RMSE: Langkah 2. Kumpulkan data valid ---
                            # Sekaligus hitung metrik per horizon jika data valid
                            if not pd.isna(val_act):
                                valid_predictions.append(val_pred)
                                valid_actuals.append(val_act)
                                
                                # 1. Persentase Kesalahan
                                percent_error = calculate_percentage_error(val_act, val_pred)
                                st.metric("Persentase kesalahan", f"{percent_error:.2f} %")
                                ''
                                ''
                                # 2. Kesalahan Absolut (Ini adalah MAE/RMSE untuk 1 titik)
                                absolute_error = np.abs(val_act - val_pred)
                                st.metric("Kesalahan absolut", f"{absolute_error:.2f} µg/m³")

                            else:
                                # val_act adalah NaN, jadi tidak bisa hitung error
                                st.text("Persentase Kesalahan: N/A")
                                st.text("Kesalahan Absolut: N/A")
                            # -------------------------------------------------------

                    ''
                    ''
                    st.write("**PM2.5 24 jam terakhir**")
                    
                    loc = df_processed.index.get_loc(selected_time)
                    historic_data_slice = df_processed.iloc[loc - n_past : loc]
                    
                    chart_data = historic_data_slice[['pm25']]
                    
                    chart_data_altair = chart_data.reset_index()

                    original_time_col_name = chart_data_altair.columns[0]
                    
                    chart_data_altair = chart_data_altair.rename(columns={original_time_col_name: 'Waktu'})

                    chart_data_altair['Waktu'] = pd.to_datetime(chart_data_altair['Waktu'])
                    chart_data_altair['pm25'] = pd.to_numeric(chart_data_altair['pm25'], errors='coerce')

                    if not chart_data_altair['pm25'].isna().all() and not chart_data_altair.empty:
                        
                        base = alt.Chart(chart_data_altair).encode(
                            x=alt.X('Waktu:T', title='Waktu', scale=alt.Scale()), 
                            y=alt.Y('pm25:Q', title='PM2.5 (µg/m³)', scale=alt.Scale(zero=False)), 
                            tooltip=[
                                alt.Tooltip('Waktu:T', format='%Y-%m-%d %H:%M', title='Waktu'), 
                                alt.Tooltip('pm25', title='PM2.5', format='.2f')
                            ]
                        )

                        # Layer 1: Garis (TANPA point=True)
                        line = base.mark_line(
                            color='#60b5ff'  # Warna garis
                        ).transform_filter(
                            "isValid(datum.pm25)"
                        )

                        # Layer 2: Titik (dibuat terpisah agar warnanya bisa diatur)
                        points = base.mark_point(
                            color='#60b5ff', # Warna titik, disamakan dengan garis
                            filled=True   # Opsional: membuat titiknya terisi penuh
                        ).transform_filter(
                            "isValid(datum.pm25)"
                        )

                        # Layer 3: Teks
                        text = base.mark_text(
                            align='center',
                            dy=-10,
                            color='white',
                            fontSize=14  # <-- TAMBAHKAN UKURAN FONT DI SINI (misal 14)
                        ).encode(
                            text=alt.Text('pm25:Q', format='.2f')
                        ).transform_filter(
                            "isValid(datum.pm25)"
                        )
                        # --- AKHIR PERUBAHAN ---

                        final_chart = (line + points + text).interactive()
                        
                        st.altair_chart(final_chart, use_container_width=True)

                    else:
                        st.warning("Tidak ada data 'pm25' yang valid untuk digambar.")

                    # --- TAMBAHAN MAE/RMSE: Langkah 3. Hitung dan Tampilkan ---
                    ''
                    st.write("**Metrik kesalahan gabungan**")
                    
                    # Cek apakah kita punya data valid untuk dihitung
                    if len(valid_actuals) > 0:
                        # Konversi ke array numpy untuk perhitungan
                        y_true = np.array(valid_actuals)
                        y_pred = np.array(valid_predictions)
                        
                        # Hitung MAE (Mean Absolute Error)
                        mae = np.mean(np.abs(y_true - y_pred))
                        
                        # Hitung RMSE (Root Mean Squared Error)
                        rmse = np.sqrt(np.mean(np.square(y_true - y_pred)))
                        
                        m_col1, m_col2 = st.columns(2, border=True)
                        with m_col1:
                            st.metric("Mean absolute error (MAE)", f"{mae:.2f} µg/m³")
                        with m_col2:
                            st.metric("Root mean squared error (RMSE)", f"{rmse:.2f} µg/m³")
                    
                    else:
                        st.warning("Tidak ada data aktual yang valid (semua N/A) untuk menghitung MAE/RMSE.")
                    # --- AKHIR TAMBAHAN MAE/RMSE ---