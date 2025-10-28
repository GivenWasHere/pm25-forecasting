import streamlit as st

st.title("Tentang")
st.markdown("Cari tahu lebih lanjut mengenai aplikasi")
st.divider()

st.markdown("Aplikasi ini merupakan sebuah purwarupa dari sistem yang berfungsi untuk menghasilkan prediksi konsentrasi PM2.5 secara jangka pendek. Metode yang digunakan untuk melakukan prediksi adalah arsitektur *gated recurrent unit* (GRU) yang dilatih menggunakan data historis PM2.5 dan meteorologi. Tata cara pengoperasian dari aplikasi dapat diakses dari buku manual di bawah ini.")

file_path = r"C:\Users\given\Downloads\Buku Manual Aplikasi Prediksi PM2.5.pdf" 

try:
    with open(file_path, "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(
        label="**Unduh Buku Manual**",
        data=PDFbyte,
        file_name="Buku Manual.pdf",
        mime="application/pdf"
    )

except FileNotFoundError:
    st.error(f"Error: File tidak ditemukan di path: {file_path}")
except Exception as e:
    st.error(f"Terjadi error saat membaca file: {e}")