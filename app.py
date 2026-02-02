import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Sistem Analisis Sekolah Bandung Raya dan Sumedang",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Keren
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3498db;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 Dashboard Analisis & Sebaran Sekolah Menengah Atas di Bandung Raya dan Sumedang")
st.markdown("---")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "data", "data_sekolah_clean.json"),
        "data_sekolah_clean.json"
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
            
    if file_path is None:
        st.error("⚠️ File data tidak ditemukan. Cek folder data.")
        st.stop()

    try:
        df = pd.read_json(file_path)
        
        # Bersihkan Data
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0)
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0)
        df['status'] = df['status'].astype(str).str.upper().str.strip()
        
        if 'akreditasi' not in df.columns: df['akreditasi'] = "Tidak Terdata"
        else: df['akreditasi'] = df['akreditasi'].fillna("Tidak Terdata")
            
        if 'alamat' not in df.columns: df['alamat'] = "-"
        else: df['alamat'] = df['alamat'].fillna("-")
        
        if 'nama_sekolah' in df.columns:
            df['nama_sekolah'] = df['nama_sekolah'].astype(str).str.replace('"', '').str.replace("'", "")
            
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 3. SISTEM LAPORAN
# ==========================================
base_dir = os.path.dirname(os.path.abspath(__file__))
folder_data = os.path.join(base_dir, "data")
if not os.path.exists(folder_data):
    os.makedirs(folder_data)

# Path file harus konsisten
PATH_LAPORAN = os.path.join(folder_data, "laporan_warga.csv")

# Fungsi untuk memuat data dari CSV ke Session State
def load_laporan_dari_csv():
    if os.path.exists(PATH_LAPORAN):
        try:
            return pd.read_csv(PATH_LAPORAN).to_dict('records')
        except:
            return []
    return []

# Inisialisasi Session State
if 'laporan_db' not in st.session_state:
    st.session_state['laporan_db'] = load_laporan_dari_csv()

def save_laporan():
    if st.session_state['laporan_db']:
        df_save = pd.DataFrame(st.session_state['laporan_db'])
        df_save.to_csv(PATH_LAPORAN, index=False)
    else:
        # Jika list kosong, hapus filenya atau buat file kosong
        if os.path.exists(PATH_LAPORAN):
            pd.DataFrame(columns=["Pelapor", "Sekolah", "Ket", "Status"]).to_csv(PATH_LAPORAN, index=False)

# ==========================================
# 4. SIDEBAR FILTER & BANTUAN
# ==========================================
st.sidebar.header("🎛️ Panel Kontrol")
mode_tampilan = st.sidebar.radio("Menu:", ["📊 Dashboard Utama", "📂 Data Lengkap", "🗣️ Forum Warga"])
st.sidebar.markdown("---")

if not df.empty:
    st.sidebar.subheader("Filter Data")
    
    opt_wilayah = sorted(df['wilayah'].astype(str).unique())
    opt_jenjang = sorted(df['bentuk_pendidikan'].astype(str).unique())
    opt_status = sorted(df['status'].astype(str).unique())
    opt_akr = sorted(df['akreditasi'].astype(str).unique())
    
    sel_wilayah = st.sidebar.multiselect("Wilayah:", opt_wilayah, default=opt_wilayah)
    sel_jenjang = st.sidebar.multiselect("Jenjang:", opt_jenjang, default=opt_jenjang)
    sel_status = st.sidebar.multiselect("Status:", opt_status, default=opt_status)
    sel_akr = st.sidebar.multiselect("Akreditasi:", opt_akr, default=opt_akr)
    
    df_filtered = df[
        (df['wilayah'].isin(sel_wilayah)) & 
        (df['bentuk_pendidikan'].isin(sel_jenjang)) & 
        (df['status'].isin(sel_status)) &
        (df['akreditasi'].isin(sel_akr))
    ]
else:
    df_filtered = pd.DataFrame()

st.sidebar.success(f"Data Terpilih: {len(df_filtered)}")

# --- BANTUAN PERSONAL ---
st.sidebar.markdown("---")
with st.sidebar.expander("🆘 Butuh Bantuan Personal?", expanded=True):
    st.write("Hubungi Tim Helper kami jika menemukan kendala:")
    col_wa, col_tg = st.columns(2)
    with col_wa:
        st.link_button("WhatsApp (Ernest)", "https://wa.me/6282217849130") 
    with col_tg:
        st.link_button("WhatsApp (Faisal)", "https://wa.me/6281224017174")
    st.caption("Respon cepat(jam kerja): 08.00 - 16.00 WIB")

# ==========================================
# 5. FUNGSI GRAFIK
# ==========================================
def buat_donut_chart(data, kolom, judul):
    if data.empty: return None
    
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = data[kolom].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
    
    def my_fmt(x):
        return '{:.1f}%'.format(x) if x > 5 else ''

    wedges, texts, autotexts = ax.pie(
        counts, autopct=my_fmt, startangle=90, 
        colors=colors[:len(counts)], pctdistance=0.85,
        textprops={'color':"black", 'weight':'bold'}
    )
    
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    ax.legend(wedges, counts.index, title=kolom, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(judul)
    ax.axis('equal')
    return fig

# ==========================================
# 6. KONTEN UTAMA
# ==========================================

if mode_tampilan == "📊 Dashboard Utama":
    
    # === METRICS ===
    if not df_filtered.empty:
        total_sekolah = len(df_filtered)
        total_negeri = len(df_filtered[df_filtered['status'] == 'NEGERI'])
        total_swasta = len(df_filtered[df_filtered['status'] == 'SWASTA'])
        top_wilayah = df_filtered['wilayah'].mode()[0] if not df_filtered['wilayah'].empty else "-"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sekolah", f"{total_sekolah}", "Unit")
        m2.metric("Negeri", f"{total_negeri}", "Sekolah")
        m3.metric("Swasta", f"{total_swasta}", "Sekolah")
        m4.metric("Wilayah Terbanyak", f"{top_wilayah}")
    
    st.markdown("---")

    # === PETA ===
    st.subheader(f"🗺️ Peta Sebaran")
    
    if df_filtered.empty:
        st.warning("Data kosong.")
    else:
        m = folium.Map(location=[-6.9175, 107.6191], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        
        data_list = df_filtered.to_dict('records')
        count_map = 0
        
        for i in range(len(data_list)):
            row = data_list[i]
            lat = row['latitude']
            lon = row['longitude']

            if (lat >= -7.25 and lat <= -6.70) and (lon >= 107.30 and lon <= 108.350):
                count_map += 1
                warna = 'red' if row['status'] == 'SWASTA' else 'blue'
                
                # --- POPUP SULTAN ---
                alamat_clean = str(row['alamat'])
                if len(alamat_clean) > 50:
                    alamat_clean = alamat_clean[:50] + "..."
                
                popup_html = f"""
                <div style="font-family: 'Segoe UI', sans-serif; font-size: 13px; width: 240px;">
                    <div style="background-color: #ecf0f1; padding: 5px; border-radius: 5px; margin-bottom: 5px;">
                        <b style="color: #2c3e50; font-size: 14px;">{row['nama_sekolah']}</b>
                    </div>
                    <div style="margin-bottom: 5px;">
                        <span style="color: #7f8c8d;">Status:</span> <b>{row['status']}</b>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="color: #7f8c8d;">Akreditasi:</span> 
                        <span style="background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 15px; font-weight: bold; font-size: 11px;">{row['akreditasi']}</span>
                    </div>
                    <div style="border-top: 1px dashed #bdc3c7; padding-top: 5px; color: #555; font-style: italic;">
                        <span style="color: #e74c3c; font-style: normal;">📍</span> {alamat_clean}
                    </div>
                </div>
                """
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=260),
                    icon=folium.Icon(color=warna, icon='info-sign')
                ).add_to(marker_cluster)
        
        st_folium(m, use_container_width=True, height=500, returned_objects=[])
        st.caption(f"Menampilkan {count_map} sekolah di wilayah Bandung Raya & Sumedang.")

    st.markdown("---")

    # === GRAFIK ===
    st.subheader("📊 Statistik Ringkas")
    c1, c2 = st.columns(2)
    with c1:
        if not df_filtered.empty:
            st.pyplot(buat_donut_chart(df_filtered, 'status', 'Komposisi Status'))
    with c2:
        if not df_filtered.empty:
            st.pyplot(buat_donut_chart(df_filtered, 'akreditasi', 'Komposisi Akreditasi'))

    st.markdown("---")
    
    # === REKOMENDASI ===
    st.subheader("🚧 Rekomendasi Pembangunan")
    if not df_filtered.empty:
        df_wil = df_filtered['wilayah'].value_counts().reset_index()
        df_wil.columns = ['Wilayah', 'Jumlah']
        rata = df_wil['Jumlah'].mean()
        
        col_grafik, col_info = st.columns([2, 1])
        with col_grafik:
            st.bar_chart(df_wil.set_index('Wilayah'))
        with col_info:
            st.metric("Rata-rata Wilayah", f"{rata:.1f}")
            st.write("---")
            for index, row in df_wil.iterrows():
                if row['Jumlah'] < rata:
                    st.error(f"🚨 **{row['Wilayah']}** (Kurang)")
                else:
                    st.success(f"✅ **{row['Wilayah']}** (Cukup)")

elif mode_tampilan == "📂 Data Lengkap":
    st.subheader("📂 Database Sekolah")
    if not df_filtered.empty:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "data_sekolah.csv", "text/csv")
        st.dataframe(df_filtered, use_container_width=True)
    else:
        st.warning("Data kosong.")

elif mode_tampilan == "🗣️ Forum Warga":
    st.subheader("🗣️ Forum Warga")
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.info("📝 **Tulis Laporan**")
        with st.form("form_lapor"):
            nama = st.text_input("Nama:")
            list_sekolah = sorted(df['nama_sekolah'].unique()) if not df.empty else []
            sekolah = st.selectbox("Sekolah:", list_sekolah)
            ket = st.text_area("Masalah:")
            if st.form_submit_button("Kirim"):
                if nama and ket:
                    st.session_state['laporan_db'].append({
                        "Pelapor": nama, "Sekolah": sekolah, "Ket": ket, "Status": "Baru"
                    })
                    save_laporan()
                    st.success("Terkirim!")
                    st.rerun()
                else:
                    st.error("Isi lengkap!")

    with c2:
        st.write("📋 **Daftar Laporan Masuk**")
        
        # Tampilkan tabel biasa (Read-only)
        if st.session_state['laporan_db']:
            st.dataframe(pd.DataFrame(st.session_state['laporan_db']), use_container_width=True)
        else:
            st.info("Belum ada laporan dari warga.")
            
        st.markdown("---")
        
        # === AREA KHUSUS ADMIN ===
        with st.expander("🔒 Admin Area (Kelola Laporan)"):
            password_input = st.text_input("Masukkan Password Admin:", type="password", key="admin_pass")
            
            if password_input == "fei~123":
                st.success("✅ Login Berhasil! Silakan kelola data di bawah ini.")
                
                if st.session_state['laporan_db']:
                    st.write("### Hapus Laporan Tertentu:")
                    
                    # Konversi ke DataFrame sementara agar mudah di-loop
                    df_lapor = pd.DataFrame(st.session_state['laporan_db'])
                    
                    # Loop untuk membuat baris per laporan dengan tombol hapus
                    for index, row in df_lapor.iterrows():
                        col_text, col_btn = st.columns([3, 1])
                        
                        with col_text:
                            st.markdown(f"**{row['Pelapor']}** - _{row['Sekolah']}_")
                            st.caption(f"Isi: {row['Ket']}")
                            st.divider()
                        
                        with col_btn:
                            # Tombol Hapus Unik per baris
                            if st.button("🗑️ Hapus", key=f"hapus_{index}"):
                                # Hapus item dari list session_state berdasarkan index
                                st.session_state['laporan_db'].pop(index)
                                # Simpan perubahan ke CSV
                                save_laporan()
                                # Rerun agar tampilan langsung update
                                st.rerun()
                else:
                    st.info("Tidak ada laporan yang perlu dihapus.")
            elif password_input:
                st.error("❌ Password salah!")