import pandas as pd
import requests
import io

# Link Raw GitHub yang lu kasih (Valid 100%)
url = "https://raw.githubusercontent.com/LcLucifer/Web-Parawisata/refs/heads/main/data_wisata.html"

print(f"🚀 OTW Mengambil data dari: {url}")

try:
    # 1. Request Data
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Koneksi ke GitHub Sukses! Data ditangan.")
        
        # 2. Parsing HTML Table
        # Pandas otomatis nyari <table> di dalem HTML itu
        dfs = pd.read_html(io.StringIO(response.text))
        
        if dfs:
            # Ambil tabel pertama (biasanya data utama)
            df = dfs[0]
            
            print(f"\n🔥 BOOM! Berhasil dapet {len(df)} baris data.")
            print("👇 Nih sampel datanya:")
            print(df.head())
            
            print("\n📋 CEK KOLOM (Penting buat GIS nanti):")
            # Gue print list kolomnya biar lu gampang copy ke gue
            print(df.columns.tolist())
            
            # 3. Data Cleaning Dikit (Jaga-jaga)
            # Kadang nama kolom ada spasi aneh, kita bersihin
            df.columns = df.columns.str.strip()
            
            # Save ke CSV biar enak
            df.to_csv("data_wisata_final_banget.csv", index=False)
            print("\n💾 Data aman! Disave ke 'data_wisata_final_banget.csv'.")
            
        else:
            print("⚠️ HTML kebaca, tapi kok gak nemu tabel? Cek file HTML-nya isinya tabel beneran kan?")
            
    else:
        print(f"❌ Link error. Status Code: {response.status_code}")

except Exception as e:
    print(f"💀 Error: {e}")