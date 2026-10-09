from flask import Flask, render_template, jsonify, request
import psycopg
import re

app = Flask(__name__)

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "data_center_insight",
    "user": "postgres",
    "password": "12345"
}


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return psycopg.connect(**DB_CONFIG)


def get_source_filter():
    """
    ALL = semua sumber.
    ANTARA / Katadata = filter berdasarkan source.
    """
    source = request.args.get("source", "ALL").strip()

    if source.upper() == "ALL":
        return None

    if source in ("ANTARA", "Katadata", "KOMPAS"):
        return source

    return None


def build_where(base_condition=None):
    """
    Membuat WHERE condition + parameter secara aman.
    """
    conditions = []
    params = []

    if base_condition:
        conditions.append(base_condition)

    source = get_source_filter()

    if source:
        conditions.append("source = %s")
        params.append(source)

    if conditions:
        return "WHERE " + " AND ".join(conditions), params

    return "", params


# ==========================================
# HOME
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# DASHBOARD SUMMARY
# ==========================================

@app.route("/api/summary")
def summary():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            where, params = build_where()
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM data_center_news
                {where};
                """,
                params
            )
            total_articles = cur.fetchone()[0]

            where, params = build_where(
                "investment_value IS NOT NULL AND investment_value <> ''"
            )
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM data_center_news
                {where};
                """,
                params
            )
            total_investment = cur.fetchone()[0]

            where, params = build_where(
                "capacity IS NOT NULL AND capacity <> ''"
            )
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM data_center_news
                {where};
                """,
                params
            )
            total_capacity = cur.fetchone()[0]

            where, params = build_where(
                "technology IS NOT NULL AND technology <> ''"
            )
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM data_center_news
                {where};
                """,
                params
            )
            total_technology = cur.fetchone()[0]

        return jsonify({
            "total_articles": total_articles,
            "total_investment": total_investment,
            "total_capacity": total_capacity,
            "total_technology": total_technology
        })

    finally:
        conn.close()


# ==========================================
# NEWS DATA
# ==========================================

@app.route("/api/news")
def news():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            where, params = build_where()

            cur.execute(
                f"""
                SELECT
                    id,
                    title,
                    published_date,
                    summary,
                    content,
                    article_url,
                    image_url,
                    source,
                    topic,
                    technology,
                    investment_value,
                    investment_type,
                    capacity,
                    capacity_type,
                    company,
                    organization,
                    project_location,
                    insight_type
                FROM data_center_news
                {where}
                ORDER BY published_date DESC, id DESC;
                """,
                params
            )

            rows = cur.fetchall()

        news_data = []

        for row in rows:

            # ==========================================
            # SUMMARY FALLBACK
            # ==========================================

            summary_value = row[3]
            content_value = row[4]

            # Kalau summary kosong / None / NaN,
            # gunakan potongan content sebagai summary
            if (
                summary_value is None
                or str(summary_value).strip() == ""
                or str(summary_value).strip().lower() == "nan"
            ):

                if content_value:
                    summary_value = str(content_value).strip()

                    # Batasi panjang summary
                    if len(summary_value) > 250:
                        summary_value = summary_value[:250] + "..."
                else:
                    summary_value = ""

            else:
                summary_value = str(summary_value).strip()

            news_data.append({
                "id": row[0],

                "title": row[1] or "",

                "published_date":
                    str(row[2])
                    if row[2]
                    else "",

                "summary":
                    summary_value,

                "content":
                    str(row[4])
                    if row[4]
                    else "",

                "article_url":
                    row[5] or "",

                "image_url":
                    row[6] or "",

                "source":
                    row[7] or "",

                "topic":
                    row[8] or "",

                "technology":
                    row[9] or "",

                "investment_value":
                    row[10] or "",

                "investment_type":
                    row[11] or "",

                "capacity":
                    row[12] or "",

                "capacity_type":
                    row[13] or "",

                "company":
                    row[14] or "",

                "organization":
                    row[15] or "",

                "project_location":
                    row[16] or "",

                "insight_type":
                    row[17] or ""
            })

        return jsonify(news_data)
    finally:
        conn.close()

# ==========================================
# BUSINESS INSIGHTS
# ==========================================

@app.route("/api/insights")
def insights():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            # TOTAL ARTICLES
            where, params = build_where()

            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM data_center_news
                {where};
                """,
                params
            )

            total_articles = cur.fetchone()[0]

            # TOPIC
            where, params = build_where(
                "topic IS NOT NULL AND TRIM(topic) <> ''"
            )

            cur.execute(
                f"""
                SELECT
                    TRIM(topic) AS topic,
                    COUNT(*) AS total
                FROM data_center_news
                {where}
                GROUP BY TRIM(topic)
                ORDER BY total DESC;
                """,
                params
            )

            topics = [
                {"name": row[0], "count": row[1]}
                for row in cur.fetchall()
            ]


            # TECHNOLOGY
            where, params = build_where()

            extra = "TRIM(value) <> ''"

            if where:
                where = f"{where} AND {extra}"
            else:
                where = f"WHERE {extra}"

            cur.execute(
                f"""
                SELECT
                    TRIM(value) AS technology,
                    COUNT(*) AS total
                FROM data_center_news,
                regexp_split_to_table(
                    COALESCE(technology, ''),
                    '\\s*;\\s*|\\s*,\\s*'
                ) AS value
                {where}
                GROUP BY TRIM(value)
                ORDER BY total DESC;
                """,
                params
            )

            technologies = [
                {"name": row[0], "count": row[1]}
                for row in cur.fetchall()
            ]


            # COMPANY
            where, params = build_where()

            if where:
                where = f"{where} AND {extra}"
            else:
                where = f"WHERE {extra}"

            cur.execute(
                f"""
                SELECT
                    TRIM(value) AS company,
                    COUNT(*) AS total
                FROM data_center_news,
                regexp_split_to_table(
                    COALESCE(company, ''),
                    '\\s*;\\s*|\\s*,\\s*'
                ) AS value
                {where}
                GROUP BY TRIM(value)
                ORDER BY total DESC
                LIMIT 10;
                """,
                params
            )

            companies = [
                {"name": row[0], "count": row[1]}
                for row in cur.fetchall()
            ]


            # ORGANIZATION
            where, params = build_where()

            if where:
                where = f"{where} AND {extra}"
            else:
                where = f"WHERE {extra}"

            cur.execute(
                f"""
                SELECT
                    TRIM(value) AS organization,
                    COUNT(*) AS total
                FROM data_center_news,
                regexp_split_to_table(
                    COALESCE(organization, ''),
                    '\\s*;\\s*|\\s*,\\s*'
                ) AS value
                {where}
                GROUP BY TRIM(value)
                ORDER BY total DESC
                LIMIT 10;
                """,
                params
            )

            organizations = [
                {"name": row[0], "count": row[1]}
                for row in cur.fetchall()
            ]


            # ==========================================
            # PROJECT LOCATIONS
            # ==========================================

            where, params = build_where(
                "project_location IS NOT NULL "
                "AND TRIM(project_location) <> ''"
            )

            cur.execute(
                f"""
                SELECT id, project_location
                FROM data_center_news
                {where};
                """,
                params
            )

            location_rows = cur.fetchall()


            from collections import defaultdict
            import re

            location_articles = defaultdict(set)


            def normalize_location(value):

                if not value:
                    return []

                value = value.strip()

                # --------------------------------------
                # Lokasi yang terdiri dari 2 bagian
                # dan harus tetap dianggap satu lokasi
                # --------------------------------------

                compound_locations = [
                    "Jatiluhur, Jawa Barat",
                    "Bandung, Jawa Barat",
                    "Jawa Barat",
                    "Jawa Timur",
                    "Jawa Tengah",
                    "Kepulauan Riau",
                    "Jakarta Selatan",
                    "Jakarta Barat",
                    "Jakarta Timur",
                    "Jakarta Utara",
                    "Jakarta Pusat"
                ]

                # --------------------------------------
                # Lokasi yang dapat berdiri sendiri
                # --------------------------------------

                simple_locations = [
                    "Jakarta",
                    "Batam",
                    "Cikarang",
                    "Bandung",
                    "Surabaya",
                    "Semarang",
                    "Medan",
                    "Bekasi",
                    "Bogor",
                    "Tangerang",
                    "Depok",
                    "Jatiluhur",
                    "Singapura",
                    "Malaysia",
                    "Indonesia"
                ]

                locations = []

                # --------------------------------------
                # 1. Pisahkan berdasarkan ;
                # --------------------------------------

                raw_parts = [
                    part.strip()
                    for part in value.split(";")
                    if part.strip()
                ]

                # --------------------------------------
                # 2. Proses setiap bagian
                # --------------------------------------

                for part in raw_parts:

                    found = []

                    # ----------------------------------
                    # Cari compound location terlebih dahulu
                    # ----------------------------------

                    for location in compound_locations:

                        if location.lower() in part.lower():

                            if location not in found:
                                found.append(location)

                            # Hapus lokasi yang sudah ditemukan
                            part = re.sub(
                                re.escape(location),
                                "",
                                part,
                                flags=re.IGNORECASE
                            )

                    # ----------------------------------
                    # Cari lokasi sederhana
                    # ----------------------------------

                    for location in simple_locations:

                        pattern = r"\b" + re.escape(location) + r"\b"

                        if re.search(
                            pattern,
                            part,
                            flags=re.IGNORECASE
                        ):

                            if location not in found:
                                found.append(location)

                    # ----------------------------------
                    # Jika berhasil menemukan lokasi
                    # ----------------------------------

                    if found:

                        locations.extend(found)

                    else:

                        # ----------------------------------
                        # Fallback:
                        # gunakan data asli
                        # ----------------------------------

                        cleaned = part.strip(" ,")

                        if cleaned:
                            locations.append(cleaned)

                # --------------------------------------
                # Hilangkan duplikasi
                # --------------------------------------

                unique_locations = []

                for location in locations:

                    if location not in unique_locations:
                        unique_locations.append(location)

                return unique_locations


            # ==========================================
            # HITUNG PER ARTIKEL
            # ==========================================

            for article_id, location_value in location_rows:

                normalized_locations = normalize_location(
                    location_value
                )

                # Satu artikel hanya dihitung satu kali
                # untuk lokasi yang sama
                normalized_locations = set(
                    normalized_locations
                )

                for location in normalized_locations:

                    location_articles[location].add(
                        article_id
                    )


            # ==========================================
            # HASIL LOCATIONS
            # ==========================================

            locations = [
                {
                    "name": location,
                    "count": len(article_ids)
                }
                for location, article_ids
                in location_articles.items()
            ]


            # ==========================================
            # SORT
            # ==========================================

            locations.sort(
                key=lambda x: x["count"],
                reverse=True
            )


            # ==========================================
            # TOP 10 LOCATIONS
            # ==========================================

            locations = locations[:10]

            # ==========================================
            # INVESTMENT SIGNAL
            # ==========================================

            where, params = build_where(
                "investment_value IS NOT NULL "
                "AND TRIM(investment_value) <> ''"
            )

            cur.execute(
                f"""
                SELECT id, investment_value
                FROM data_center_news
                {where};
                """,
                params
            )

            investment_rows = cur.fetchall()


            # ==========================================
            # INVESTMENT RANGE
            # ==========================================

            investment_ranges = [
                ("0 – 1 juta", 0, 1_000_000),
                ("1 – 10 juta", 1_000_000, 10_000_000),
                ("10 – 100 juta", 10_000_000, 100_000_000),
                ("100 juta – 1 miliar", 100_000_000, 1_000_000_000),
                ("1 – 10 miliar", 1_000_000_000, 10_000_000_000),
                ("10 – 100 miliar", 10_000_000_000, 100_000_000_000),
                ("100 miliar – 1 triliun", 100_000_000_000, 1_000_000_000_000),
                ("1 – 10 triliun", 1_000_000_000_000, 10_000_000_000_000),
                ("10 triliun+", 10_000_000_000_000, float("inf"))
            ]


            investment_articles = {
                name: set()
                for name, _, _ in investment_ranges
            }


            # ==========================================
            # PARSE SEMUA NILAI INVESTASI
            # ==========================================

            def parse_investment_values(value):

                if not value:
                    return []

                value = str(value).lower().strip()

                results = []

                # ==========================================
                # KURS USD → IDR
                # ==========================================
                # Dibuat sebagai konfigurasi agar mudah diubah
                USD_TO_IDR = 16_500

                # ==========================================
                # CARI NOMINAL
                # Mendukung:
                # Rp 5 triliun
                # Rp 5,7 triliun
                # US$ 100 miliar
                # $ 200 juta
                # USD 1 billion
                # ==========================================

                pattern = re.findall(
                    r'(rp|us\$|usd|\$)\s*([\d.,]+)\s*'
                    r'(triliun|miliar|juta|ribu|trillion|billion|million|thousand)?',
                    value,
                    re.IGNORECASE
                )

                for currency, number_text, unit in pattern:

                    # ==========================================
                    # NORMALISASI ANGKA
                    # ==========================================

                    if "," in number_text and "." in number_text:

                        # Contoh:
                        # 1.768,7 → 1768.7
                        number_text = (
                            number_text
                            .replace(".", "")
                            .replace(",", ".")
                        )

                    elif "," in number_text:

                        # Contoh:
                        # 2,54 → 2.54
                        number_text = number_text.replace(",", ".")

                    elif "." in number_text:

                        # Contoh:
                        # 1.700 → 1700
                        parts = number_text.split(".")

                        if (
                            len(parts) > 1
                            and all(len(x) == 3 for x in parts[1:])
                        ):
                            number_text = number_text.replace(".", "")

                    try:
                        number = float(number_text)

                    except ValueError:
                        continue

                    # ==========================================
                    # KONVERSI SATUAN
                    # ==========================================

                    unit = unit.lower().strip()

                    if unit in ["triliun", "trillion"]:
                        number *= 1_000_000_000_000

                    elif unit in ["miliar", "billion"]:
                        number *= 1_000_000_000

                    elif unit in ["juta", "million"]:
                        number *= 1_000_000

                    elif unit in ["ribu", "thousand"]:
                        number *= 1_000


                    # ==========================================
                    # KONVERSI USD → IDR
                    # ==========================================

                    currency = currency.lower().strip()

                    if currency in ["us$", "usd", "$"]:

                        number *= USD_TO_IDR


                    results.append(number)

                return results


            # ==========================================
            # MASUKKAN ARTIKEL KE RANGE
            # ==========================================

            for article_id, investment_value in investment_rows:

                values = parse_investment_values(
                    investment_value
                )

                if not values:
                    continue

                # Satu artikel hanya dihitung
                # berdasarkan nilai investasi TERBESAR
                max_amount = max(values)

                for range_name, minimum, maximum in investment_ranges:

                    if minimum <= max_amount < maximum:

                        investment_articles[
                            range_name
                        ].add(article_id)

                        break


            # ==========================================
            # HASIL INVESTMENT SIGNAL
            # ==========================================

            investments = [
                {
                    "range": range_name,
                    "count": len(
                        investment_articles[range_name]
                    )
                }

                for range_name, _, _
                in investment_ranges
            ]


            # Jumlah artikel yang memiliki
            # investment signal
            investment_count = sum(
                item["count"]
                for item in investments
            )

            # ==========================================
            # CAPACITY SIGNAL
            # ==========================================

            where, params = build_where(
                "capacity IS NOT NULL "
                "AND TRIM(capacity) <> ''"
            )

            cur.execute(
                f"""
                SELECT id, capacity
                FROM data_center_news
                {where};
                """,
                params
            )

            capacity_rows = cur.fetchall()


            # ------------------------------------------
            # RANGE CAPACITY
            # Semua nilai dikonversi ke MW
            # ------------------------------------------

            capacity_ranges = [
                ("0 – 100 MW", 0, 100),
                ("100 – 500 MW", 100, 500),
                ("500 MW – 1 GW", 500, 1_000),
                ("1 – 5 GW", 1_000, 5_000),
                ("5 – 10 GW", 5_000, 10_000),
                ("10 GW+", 10_000, float("inf"))
            ]


            # ------------------------------------------
            # SIMPAN ID ARTIKEL PER RANGE
            # ------------------------------------------

            capacity_articles = {
                range_name: set()
                for range_name, _, _ in capacity_ranges
            }


            # ------------------------------------------
            # PARSE CAPACITY
            # ------------------------------------------

            def parse_capacity(value):

                if not value:
                    return []

                value = str(value).strip().lower()

                # Cari semua angka yang mempunyai
                # satuan MW atau GW
                matches = re.findall(
                    r'(\d+(?:[.,]\d+)?)\s*(mw|gw)\b',
                    value,
                    re.IGNORECASE
                )

                if not matches:
                    return []

                result = []

                for number_text, unit in matches:

                    # Format desimal Indonesia
                    # contoh: 1,3 GW → 1.3 GW
                    number_text = number_text.replace(",", ".")

                    try:
                        number = float(number_text)
                    except ValueError:
                        continue

                    # Konversi GW → MW
                    if unit.lower() == "gw":
                        number *= 1_000

                    result.append(number)

                return result


            # ------------------------------------------
            # HITUNG ARTIKEL PER RANGE
            # ------------------------------------------

            for article_id, capacity_value in capacity_rows:

                parsed_capacities = parse_capacity(
                    capacity_value
                )

                if not parsed_capacities:
                    continue

                # Supaya satu artikel tidak dihitung
                # berkali-kali dalam range yang sama
                article_ranges = set()

                for amount in parsed_capacities:

                    for range_name, minimum, maximum in capacity_ranges:

                        if minimum <= amount < maximum:

                            article_ranges.add(
                                range_name
                            )

                            break

                # Masukkan ID artikel ke range
                for range_name in article_ranges:

                    capacity_articles[
                        range_name
                    ].add(article_id)


            # ------------------------------------------
            # HASIL CAPACITY SIGNAL
            # ------------------------------------------

            capacities = [
                {
                    "range": range_name,
                    "count": len(
                        capacity_articles[range_name]
                    )
                }

                for range_name, _, _
                in capacity_ranges
            ]


            # ------------------------------------------
            # TOTAL ARTIKEL YANG MEMILIKI CAPACITY
            # ------------------------------------------

            capacity_count = sum(
                item["count"]
                for item in capacities
            )


            # ==========================================
            # INVESTMENT COUNT
            # ==========================================

            investment_count = sum(
                item["count"]
                for item in investments
            )
            capacity_count = len(capacities)

        top_topic = (
            topics[0]
            if topics
            else {"name": "-", "count": 0}
        )

        top_technology = (
            technologies[0]
            if technologies
            else {"name": "-", "count": 0}
        )

        top_company = (
            companies[0]
            if companies
            else {"name": "-", "count": 0}
        )

        top_location = (
            locations[0]
            if locations
            else {"name": "-", "count": 0}
        )


        return jsonify({

            "summary": {
                "top_topic": top_topic["name"],
                "top_topic_count": top_topic["count"],

                "top_technology": top_technology["name"],
                "top_technology_count": top_technology["count"],

                "top_company": top_company["name"],
                "top_company_count": top_company["count"],

                "top_location": top_location["name"],
                "top_location_count": top_location["count"]
            },

            "total_articles": total_articles,

            "topics": topics,
            "technologies": technologies,
            "companies": companies,
            "organizations": organizations,
            "locations": locations,
            "investment_count": investment_count,
            "investments": investments,
            "capacity_count": capacity_count,
            "capacities": capacities
        })

    finally:
        conn.close()


# ==========================================
# MONTHLY NEWS TREND
# ==========================================

@app.route("/api/trends")
def trends():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            where, params = build_where(
                "published_date IS NOT NULL"
            )

            cur.execute(
                f"""
                SELECT
                    TO_CHAR(
                        DATE_TRUNC('month', published_date),
                        'YYYY-MM'
                    ) AS month,
                    COUNT(*) AS total
                FROM data_center_news
                {where}
                GROUP BY DATE_TRUNC(
                    'month',
                    published_date
                )
                ORDER BY month;
                """,
                params
            )

            rows = cur.fetchall()

            return jsonify([
                {
                    "month": row[0],
                    "total": row[1]
                }
                for row in rows
            ])

    finally:
        conn.close()
        
# ==========================================
# AI EXECUTIVE SUMMARY
# ==========================================

@app.route("/api/ai-summary")
def ai_summary():

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # ==========================================
            # BUAT TABEL CACHE JIKA BELUM ADA
            # ==========================================

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_summary_cache (
                    source VARCHAR(50) PRIMARY KEY,
                    total_articles INTEGER NOT NULL,
                    latest_article_date DATE,
                    summary TEXT NOT NULL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # ==========================================
            # AMBIL DATA SESUAI FILTER SOURCE
            # ==========================================

            where, params = build_where()

            cur.execute(
                f"""
                SELECT
                    COUNT(*),
                    MAX(published_date)
                FROM data_center_news
                {where};
                """,
                params
            )

            result = cur.fetchone()

            total_articles = result[0]
            latest_article_date = result[1]

            if total_articles == 0:

                return jsonify({
                    "success": False,
                    "message": "Tidak ada artikel untuk dianalisis."
                }), 404

            # ==========================================
            # TENTUKAN SOURCE CACHE
            # ==========================================

            source = get_source_filter()

            if source is None:
                cache_source = "ALL"
            else:
                cache_source = source.upper()

            # ==========================================
            # CEK CACHE
            # ==========================================

            cur.execute(
                """
                SELECT
                    total_articles,
                    latest_article_date,
                    summary,
                    generated_at
                FROM ai_summary_cache
                WHERE source = %s;
                """,
                (cache_source,)
            )

            cached = cur.fetchone()

            if cached:

                cached_total = cached[0]
                cached_latest_date = cached[1]
                cached_summary = cached[2]
                cached_generated_at = cached[3]

                # Jika data database masih sama,
                # gunakan hasil AI yang sudah tersimpan.

                if (
                    cached_total == total_articles
                    and cached_latest_date == latest_article_date
                ):

                    return jsonify({
                        "success": True,
                        "total_articles": total_articles,
                        "summary": cached_summary,
                        "cached": True,
                        "generated_at": str(
                            cached_generated_at
                        )
                    })

            # ==========================================
            # AMBIL DATA ARTIKEL
            # ==========================================

            cur.execute(
                f"""
                SELECT
                    title,
                    published_date,
                    summary,
                    source,
                    technology,
                    investment_value,
                    capacity,
                    company,
                    organization,
                    project_location,
                    insight_type
                FROM data_center_news
                {where}
                ORDER BY published_date DESC, id DESC;
                """,
                params
            )

            rows = cur.fetchall()

        # ==========================================
        # SIAPKAN DATA UNTUK GEMINI
        # ==========================================

        articles = []

        for row in rows:

            articles.append({
                "title": row[0] or "",
                "published_date": (
                    str(row[1])
                    if row[1]
                    else ""
                ),
                "summary": row[2] or "",
                "source": row[3] or "",
                "technology": row[4] or "",
                "investment": row[5] or "",
                "capacity": row[6] or "",
                "company": row[7] or "",
                "organization": row[8] or "",
                "location": row[9] or "",
                "insight_type": row[10] or ""
            })

        # ==========================================
        # GEMINI
        # ==========================================

        from google import genai

        client = genai.Client()

        prompt = f"""
Kamu adalah AI Business Intelligence Analyst
untuk sektor Data Center & Cloud di Indonesia.

Analisis kumpulan artikel berita berikut.

JUMLAH ARTIKEL YANG DIANALISIS: {len(articles)}

PENTING:
- Wajib menyebutkan jumlah artikel yang dianalisis.
- Pada bagian "1. Ringkasan Utama", kalimat pertama WAJIB menggunakan format:
  "Berdasarkan analisis terhadap {len(articles)} artikel..."
- Jangan menggunakan jumlah artikel lain.
- Jangan mengarang angka atau fakta.
- Gunakan hanya informasi yang tersedia dalam data.

Tujuan analisis:
- memahami tren pemberitaan,
- mengidentifikasi topik utama,
- melihat perkembangan investasi,
- melihat perkembangan kapasitas data center,
- mengidentifikasi teknologi yang sering muncul,
- melihat perusahaan atau organisasi yang sering disebut,
- melihat lokasi proyek,
- memberikan insight bisnis secara objektif.

Buat Executive Summary dalam bahasa Indonesia.

Gunakan format:

### 1. Ringkasan Utama

### 2. Tren yang Terlihat

### 3. Investment & Capacity

### 4. Teknologi dan Perusahaan

### 5. Business Insight

Data artikel:

{articles}
"""

        interaction = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt
        )

        generated_summary = interaction.output_text

        # ==========================================
        # SIMPAN HASIL GEMINI KE CACHE
        # ==========================================

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO ai_summary_cache (
                    source,
                    total_articles,
                    latest_article_date,
                    summary,
                    generated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (source)
                DO UPDATE SET
                    total_articles = EXCLUDED.total_articles,
                    latest_article_date = EXCLUDED.latest_article_date,
                    summary = EXCLUDED.summary,
                    generated_at = CURRENT_TIMESTAMP;
                """,
                (
                    cache_source,
                    total_articles,
                    latest_article_date,
                    generated_summary
                )
            )

            conn.commit()

        # ==========================================
        # RESPONSE
        # ==========================================

        return jsonify({
            "success": True,
            "total_articles": total_articles,
            "summary": generated_summary,
            "cached": False
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        conn.close()

# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
