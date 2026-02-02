import pandas as pd
import time
from geopy.geocoders import ArcGIS

file_path = 'data/data_sekolah_clean.json'
df = pd.read_json(file_path)

geolocator = ArcGIS(user_agent="lokasi_sekolah")
df['alamat_lengkap'] = df['nama_sekolah'] + ", " + df['alamat'] + ", " + df['wilayah']

def geocode(alamat):
    try:
        location = geolocator.geocode(alamat)
        if location:
            print(f"Found: {alamat[:30]}...")
            time.sleep(0.3)
            return location.latitude, location.longitude
    except:
        pass
    return None, None

mask = (df['latitude'] == 0.0) | (df['latitude'].isna())

if mask.any():
    results = df.loc[mask, 'alamat_lengkap'].apply(geocode)
    df.loc[mask, ['latitude', 'longitude']] = pd.DataFrame(results.tolist(), index=df.index[mask]).values

df = df.drop(columns=['alamat_lengkap'])
df.to_json(file_path, orient='records', indent=4)

print("Update selesai!")