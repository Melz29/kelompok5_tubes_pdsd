import requests
import time
import pandas as pd
import os

url ="https://sekolah.data.kemendikdasmen.go.id/v1/sekolah-service/sekolah/cari-sekolah"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://sekolah.data.kemendikdasmen.go.id",
    "Referer": "https://sekolah.data.kemendikdasmen.go.id/sekolah?keyword=&bentuk_pendidikan=SMA&kabupaten_kota=Kota%20Bandung&status_sekolah=&page=0&size=12",
    "sec-ch-ua": '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-platform": '"Windows"',
}

cookies = {
    "TSc78de468027": "0837bd474fab2000843db62a874f83328a8bc9f7437b887869405ddf7d75b86ae574f34ae984059d0808fc6b2d1130008c39c9dc522f8c0983a7e0199f23dd7a96bf23fe6c0a612fcc5a018d1d2790aae90feb4f9efc72688e7f768cc09226e8"
}

daftar_kota = ["Kota Bandung", "Kota Cimahi", "Kab. Bandung", "Kab. Sumedang","Kab. Bandung Barat"]
daftar_bentuk = ["SMA", "SMK", "SMAK", "MA"]
semua_data_sekolah = []

for kota in daftar_kota:
    for bentuk in daftar_bentuk:
        halaman = 0
        jumlah_data = 0
        print(f"\nMengambil {bentuk} di {kota}...")

        while True:
            payload = {
                "page": halaman,
                "size": 48,
                "keyword": "",
                "kabupaten_kota": kota,
                "bentuk_pendidikan": bentuk,
                "status_sekolah": ""
            }

            try:
                response = requests.post(url, json=payload, headers=headers, cookies=cookies)

                if response.status_code != 200:
                    print(f"Server error {response.status_code}. Berhenti di halaman {halaman}")
                    break

                data_json = response.json()
                daftar_sekolah = data_json.get('data', [])

                if not daftar_sekolah:
                    break

                for sekolah in daftar_sekolah:
                    semua_data_sekolah.append({
                       "nama_sekolah": sekolah.get('nama'),
                        "npsn": sekolah.get('npsn'),
                        "status": sekolah.get('status_sekolah'),
                        "akreditasi": sekolah.get('akreditasi'),
                        "latitude": sekolah.get('lintang'),
                        "longitude": sekolah.get('bujur'),
                        "alamat": sekolah.get('alamat_jalan'),
                        "wilayah": kota,
                        "bentuk_pendidikan": bentuk 
                    })
                    jumlah_data += 1

                halaman += 1
                time.sleep(0.2)

            except Exception as e:
                print(f"Terjadi error: {e}")
                break

        print(f"Data yang didapatkan adalah {jumlah_data} data")

if semua_data_sekolah:
    df = pd.DataFrame(semua_data_sekolah)

    file = "data"
    if not os.path.exists(file):
        os.makedirs(file)
        print(f"folder {file} berhasil dibuat")

    file_path = os.path.join(file, "data_sekolah.json")
    df.to_json(file_path, orient="records", indent=4)

print(f"\nTotal seluruh data: {len(semua_data_sekolah)} disimpan ke data_sekolah.json")

