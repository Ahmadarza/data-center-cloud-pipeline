import pandas as pd
import psycopg2


# ==========================================
# CONFIGURATION
# ==========================================

CSV_FILE = "/opt/airflow/data-center-pipeline/data_center_kompas_business_insight.csv"

DB_CONFIG = {
    "host": "host.docker.internal",
    "port": 5432,
    "database": "data_center_insight",
    "user": "postgres",
    "password": "12345"
}


# ==========================================
# LOAD CSV
# ==========================================

print("====================================")
print("LOAD KOMPAS BUSINESS INSIGHT")
print("====================================")

df = pd.read_csv(
    CSV_FILE,
    encoding="utf-8-sig",
    keep_default_na=False
)

print(f"Total data CSV : {len(df)}")


# ==========================================
# CONNECT DATABASE
# ==========================================

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()


# ==========================================
# COUNTER
# ==========================================

updated = 0
inserted = 0
skipped = 0


# ==========================================
# PROCESS DATA
# ==========================================

for _, row in df.iterrows():

    article_url = row["article_url"]

    if not article_url:
        skipped += 1
        continue


    # ======================================
    # CEK ARTIKEL BERDASARKAN URL
    # ======================================

    cur.execute(
        """
        SELECT id
        FROM data_center_news
        WHERE article_url = %s
        LIMIT 1;
        """,
        (article_url,)
    )

    existing = cur.fetchone()


    # ======================================
    # UPDATE ARTIKEL YANG SUDAH ADA
    # ======================================

    if existing:

        cur.execute(
            """
            UPDATE data_center_news
            SET
                title = %s,
                published_date = %s,
                summary = %s,
                image_url = %s,
                source = %s,
                tag = %s,
                topic = %s,
                relevance = %s,
                technology = %s,
                investment_value = %s,
                investment_type = %s,
                capacity = %s,
                capacity_type = %s,
                company = %s,
                organization = %s,
                project_location = %s,
                insight_type = %s,
                content = %s
            WHERE article_url = %s;
            """,
            (
                row["title"],
                row["published_date"],
                row["summary"],
                row["image_url"],
                row["source"],
                row["tag"],
                row["topic"],
                row["relevance"],
                row["technology"],
                row["investment_value"],
                row["investment_type"],
                row["capacity"],
                row["capacity_type"],
                row["company"],
                row["organization"],
                row["project_location"],
                row["insight_type"],
                row["content"],
                article_url
            )
        )

        updated += 1

        continue


    # ======================================
    # INSERT ARTIKEL BARU
    # ======================================

    cur.execute(
        """
        INSERT INTO data_center_news (
            title,
            published_date,
            summary,
            article_url,
            image_url,
            source,
            tag,
            sector,
            topic,
            relevance,
            relevance_score,
            technology,
            investment_value,
            investment_type,
            capacity,
            capacity_type,
            company,
            organization,
            project_location,
            insight_type,
            content
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s
        );
        """,
        (
            row["title"],
            row["published_date"],
            row["summary"],
            row["article_url"],
            row["image_url"],
            row["source"],
            row["tag"],
            row["sector"],
            row["topic"],
            row["relevance"],
            row["relevance_score"],
            row["technology"],
            row["investment_value"],
            row["investment_type"],
            row["capacity"],
            row["capacity_type"],
            row["company"],
            row["organization"],
            row["project_location"],
            row["insight_type"],
            row["content"]
        )
    )

    inserted += 1


# ==========================================
# COMMIT
# ==========================================

conn.commit()

cur.close()
conn.close()


# ==========================================
# RESULT
# ==========================================

print("")
print("====================================")
print("HASIL LOAD KOMPAS")
print("====================================")
print(f"Total CSV     : {len(df)}")
print(f"Data di-update: {updated}")
print(f"Data baru     : {inserted}")
print(f"Data dilewati : {skipped}")
print("====================================")
print("PROSES SELESAI")
print("====================================")