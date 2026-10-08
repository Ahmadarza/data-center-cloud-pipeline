import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


CSV_FILE = "/opt/airflow/data-center-pipeline/data_center_antaranews_business_insight.csv"

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


print("====================================")
print("LOAD DATA KE POSTGRESQL")
print("====================================")


# Baca CSV hasil business insight
df = pd.read_csv(CSV_FILE, encoding="utf-8")

print(f"Data dari CSV: {len(df)} artikel")


# Pastikan hanya kolom yang dibutuhkan
for column in TARGET_COLUMNS:
    if column not in df.columns:
        df[column] = None

df = df[TARGET_COLUMNS]


# Ubah NaN menjadi None agar cocok dengan PostgreSQL
df = df.where(pd.notnull(df), None)


# Koneksi PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()


# Pastikan article_url unik untuk kebutuhan UPSERT
cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    data_center_news_article_url_unique
    ON data_center_news(article_url);
""")


# UPSERT
columns = ", ".join(TARGET_COLUMNS)

update_columns = [
    column for column in TARGET_COLUMNS
    if column != "article_url"
]

update_clause = ", ".join(
    f"{column} = EXCLUDED.{column}"
    for column in update_columns
)


query = f"""
    INSERT INTO data_center_news ({columns})
    VALUES %s
    ON CONFLICT (article_url)
    DO UPDATE SET
        {update_clause};
"""


values = [
    tuple(row[column] for column in TARGET_COLUMNS)
    for _, row in df.iterrows()
]


execute_values(
    cursor,
    query,
    values
)


conn.commit()


print(f"Data berhasil di-load: {len(values)} artikel")
print("Mode: INSERT / UPDATE berdasarkan article_url")


cursor.close()
conn.close()


print("====================================")
print("LOAD POSTGRESQL SELESAI")
print("====================================")