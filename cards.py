import streamlit as st

def validasi_card():
    st.page_link("validasi.py", label="Validasi")
    st.write("Halaman ini berfungsi untuk menguji keakuratan hasil prediksi. Coba dengan memasukkan tanggal dan waktu yang diinginkan dan lihat hasilnya.")

def tentang_card():
    st.page_link("tentang.py", label="Tentang")
    st.write("Halaman ini berfungsi untuk menyimpan informasi tambahan mengenai aplikasi yang dapat diakses.")