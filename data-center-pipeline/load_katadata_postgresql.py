import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


CSV_FILE = "data_center_katadata_business_insight.csv"

DB_CONFIG = {
    "host": "host.docker.internal",
    "port": 5432,
    "dbname": "data_center_insight",
    "user": "postgres",
    "password": "12345"
}


TARGET_COLUMNS = [
    "title",
    "published_date",
    "summary",
    "article_url",
    "image_url",
    "source",
    "tag",
    "sector",
    "topic",
    "relevance",
    "relevance_score",
    "technology",
    "investment_value",
    "investment_type",
    "capacity",
    "capacity_type",
    "company",
    "organization",
    "project_location",
    "insight_type",
    "content"
]


# ==========================================
# LOAD CSV
# ==========================================

df = pd.read_csv(
    CSV_FILE,
    encoding="utf-8-sig"
)

print("Data Katadata dari CSV:", len(df), "artikel")


# ==========================================
# TAMBAH KOLOM YANG BELUM ADA
# ==========================================

for column in TARGET_COLUMNS:

    if column not in df.columns:
        df[column] = None


# ==========================================
# NILAI TAMBAHAN
# ==========================================

df["source"] = "Katadata"

df["tag"] = "Data Center"

df["sector"] = "Data Center & Cloud"

df["topic"] = "Data Center"

# ==========================================
# KONVERSI TANGGAL INDONESIA
# ==========================================

bulan = {
    "Januari": "01",
    "Februari": "02",
    "Maret": "03",
    "April": "04",
    "Mei": "05",
    "Juni": "06",
    "Juli": "07",
    "Agustus": "08",
    "September": "09",
    "Oktober": "10",
    "November": "11",
    "Desember": "12"
}


def parse_tanggal(tanggal):
    if pd.isna(tanggal):
        return None

    tanggal = str(tanggal).strip()

    bagian = tanggal.split()

    if len(bagian) != 3:
        return None

    hari = bagian[0]
    nama_bulan = bagian[1]
    tahun = bagian[2]

    nomor_bulan = bulan.get(nama_bulan)

    if not nomor_bulan:
        return None

    return f"{tahun}-{nomor_bulan}-{hari.zfill(2)}"


df["published_date"] = df["published_date"].apply(
    parse_tanggal
)

# Relevant diberi score 1
df["relevance_score"] = df[
    "relevance"
].apply(
    lambda x: 1 if str(x).lower() == "relevant" else 0
)


# ==========================================
# BERSIHKAN NaN
# ==========================================

df = df.replace(
    {pd.NA: None}
)

df = df.where(
    pd.notnull(df),
    None
)


# ==========================================
# UNIQUE INDEX
# ==========================================

conn = psycopg2.connect(
    **DB_CONFIG
)

cursor = conn.cursor()


cursor.execute(
    """
    CREATE UNIQUE INDEX IF NOT EXISTS
    data_center_news_article_url_unique
    ON data_center_news(article_url);
    """
)

conn.commit()


# ==========================================
# INSERT / UPSERT
# ==========================================

columns_sql = ", ".join(
    TARGET_COLUMNS
)

placeholders = ", ".join(
    ["%s"] * len(TARGET_COLUMNS)
)


update_columns = [
    column
    for column in TARGET_COLUMNS
    if column != "article_url"
]


update_sql = ", ".join(
    f"{column} = EXCLUDED.{column}"
    for column in update_columns
)


query = f"""
INSERT INTO data_center_news (
    {columns_sql}
)
VALUES ({placeholders})
ON CONFLICT (article_url)
DO UPDATE SET
    {update_sql};
"""


values = []

for _, row in df.iterrows():

    values.append(
        tuple(
            row[column]
            for column in TARGET_COLUMNS
        )
    )


cursor.executemany(
    query,
    values
)

conn.commit()


print()
print("=" * 50)
print("LOAD KATADATA KE POSTGRESQL SELESAI")
print("=" * 50)
print(
    "Data dari CSV:",
    len(df),
    "artikel"
)
print(
    "Data berhasil di-load:",
    len(values),
    "artikel"
)
print(
    "Mode: INSERT / UPDATE berdasarkan article_url"
)


cursor.close()
conn.close()

print("LOAD POSTGRESQL SELESAI")