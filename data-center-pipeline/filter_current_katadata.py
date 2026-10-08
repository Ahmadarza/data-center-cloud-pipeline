import pandas as pd


INPUT_FILE = "data_center_katadata_curated.csv"

OUTPUT_FILE = "data_center_katadata_current.csv"

REVIEW_FILE = "data_center_katadata_review.csv"


# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("Total data curated:", len(df))


# ==========================================
# KONVERSI BULAN INDONESIA
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


# ==========================================
# FUNGSI PARSING TANGGAL
# ==========================================

def parse_date(date_text):

    if pd.isna(date_text):
        return pd.NaT

    date_text = str(date_text).strip()

    parts = date_text.split()

    if len(parts) < 3:
        return pd.NaT

    day = parts[0]
    month_name = parts[1]
    year = parts[2]

    month = bulan.get(month_name)

    if not month:
        return pd.NaT

    date_string = (
        f"{year}-{month}-{day.zfill(2)}"
    )

    return pd.to_datetime(
        date_string,
        errors="coerce"
    )


# ==========================================
# PARSE TANGGAL
# ==========================================

df["published_date_parsed"] = df[
    "published_date"
].apply(parse_date)


# ==========================================
# CEK HASIL PARSING
# ==========================================

print()
print("Hasil parsing tanggal:")

print(
    df[
        [
            "published_date",
            "published_date_parsed"
        ]
    ].to_string(index=False)
)


# ==========================================
# PERIODE 12 BULAN
# ==========================================

start_date = pd.Timestamp(
    "2025-09-22"
)

end_date = pd.Timestamp(
    "2026-09-22"
)


# ==========================================
# FILTER PERIODE
# ==========================================

df_current = df[
    (
        df["published_date_parsed"]
        >= start_date
    )
    &
    (
        df["published_date_parsed"]
        <= end_date
    )
].copy()


# ==========================================
# DATA DI LUAR PERIODE
# ==========================================

df_review = df[
    ~df["article_url"].isin(
        df_current["article_url"]
    )
].copy()


# ==========================================
# HAPUS KOLOM BANTU
# ==========================================

df_current.drop(
    columns=["published_date_parsed"],
    inplace=True
)

df_review.drop(
    columns=["published_date_parsed"],
    inplace=True
)


# ==========================================
# SIMPAN
# ==========================================

df_current.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

df_review.to_csv(
    REVIEW_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# HASIL
# ==========================================

print()
print("=" * 50)
print("FILTER 12 BULAN KATADATA SELESAI")
print("=" * 50)

print(
    "Periode:",
    start_date.strftime("%d-%m-%Y"),
    "sampai",
    end_date.strftime("%d-%m-%Y")
)

print(
    "Artikel dalam periode:",
    len(df_current)
)

print(
    "Artikel di luar periode:",
    len(df_review)
)

print()
print(
    "Output:",
    OUTPUT_FILE
)

print(
    "Review:",
    REVIEW_FILE
)