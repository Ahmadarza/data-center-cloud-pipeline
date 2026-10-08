import pandas as pd

INPUT_FILE = "data_center_kompas_all.csv"
OUTPUT_FILE = "data_center_kompas_content.csv"

print("====================================")
print("CONTENT SCRAPING KOMPAS")
print("====================================")

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("Total data:", len(df))

# Content sudah tersedia dari tahap scraping utama
# Tahap ini memastikan kolom content tersedia
if "content" not in df.columns:
    raise Exception("Kolom content tidak ditemukan!")

df["content"] = df["content"].fillna("").astype(str)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("File berhasil dibuat:", OUTPUT_FILE)
print("Total:", len(df))
print("PROSES CONTENT SELESAI")