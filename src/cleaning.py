import pandas as pd

df = pd.read_json("data/data_sekolah.json")

df['akreditasi'] = df['akreditasi'].fillna('Tidak Terdata').replace(['', '-', ' '], 'Tidak Terdata')

df['nama_sekolah'] = df['nama_sekolah'].str.upper().str.strip()

df['latitude'] = df['latitude'].fillna(0.0)
df['longitude'] = df['longitude'].fillna(0.0)

df = df.drop_duplicates(subset=['npsn'])

df.to_json("data/data_sekolah_clean.json", orient="records", indent=4)

print("Cleaning selesai!")