import pandas as pd
import re


# =========================================================
# CONFIGURATION
# =========================================================

INPUT_FILE = "data_center_kompas_all.csv"
OUTPUT_FILE = "data_center_kompas_business_insight.csv"


# =========================================================
# HELPER
# =========================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def unique_join(items):

    result = []

    for item in items:

        item = clean_text(item)

        if item and item not in result:
            result.append(item)

    return "; ".join(result)


def get_context(text, position, window=250):

    start = max(0, position - window)
    end = min(len(text), position + window)

    return text[start:end]


# =========================================================
# TECHNOLOGY
# =========================================================

def extract_technology(text):

    text = clean_text(text)
    text_lower = text.lower()

    technologies = []

    technology_keywords = {

        "Data Center": [
            "data center",
            "data centre",
            "pusat data"
        ],

        "AI": [
            "artificial intelligence",
            "kecerdasan buatan",
            " ai ",
            "ai,"
        ],

        "Cloud": [
            "cloud computing",
            "cloud"
        ],

        "Server": [
            "server",
            "servers"
        ],

        "GPU": [
            "gpu",
            "graphics processing unit"
        ],

        "Storage": [
            "storage",
            "penyimpanan data"
        ],

        "Green Data Center": [
            "green data center",
            "green data centre",
            "data center hijau"
        ],

        "AI Data Center": [
            "ai data center",
            "ai data centre",
            "pusat data berbasis ai",
            "data center berbasis ai"
        ],

        "Renewable Energy": [
            "renewable energy",
            "energi terbarukan",
            "energi baru terbarukan",
            "ebt"
        ],

        "Geothermal": [
            "geothermal",
            "panas bumi"
        ],

        "Liquid Cooling": [
            "liquid cooling",
            "pendingin cair",
            "direct to chip"
        ],

        "Fiber Optic": [
            "fiber optik",
            "serat optik",
            "fiber optic"
        ],

        "5G": [
            "5g"
        ],

        "Cybersecurity": [
            "cybersecurity",
            "keamanan siber"
        ]
    }


    # -----------------------------------------------------
    # Konteks digital
    # -----------------------------------------------------

    digital_context = [

        "data center",
        "data centre",
        "pusat data",
        "digital",
        "komputasi",
        "artificial intelligence",
        "kecerdasan buatan",
        "cloud",
        "gpu",
        "server"
    ]


    has_digital_context = any(
        keyword in text_lower
        for keyword in digital_context
    )


    if not has_digital_context:
        return ""


    # -----------------------------------------------------
    # Deteksi teknologi
    # -----------------------------------------------------

    for technology, keywords in technology_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:

                technologies.append(
                    technology
                )

                break


    return unique_join(technologies)


# =========================================================
# INVESTMENT
# =========================================================

def extract_investment(text):

    text = clean_text(text)
    text_lower = text.lower()


    # -----------------------------------------------------
    # Pola nilai uang
    # -----------------------------------------------------

    money_pattern = r"""
        (?:
            us\$|usd|\$
        )
        \s*
        [\d.,]+
        (?:
            \s*-\s*
            [\d.,]+
        )?
        \s*
        (?:
            juta|
            miliar|
            triliun|
            million|
            billion|
            trillion
        )

        |

        (?:
            rp|idr
        )
        \s*
        [\d.,]+
        (?:
            \s*-\s*
            [\d.,]+
        )?
        \s*
        (?:
            juta|
            miliar|
            triliun
        )
    """


    matches = list(
        re.finditer(
            money_pattern,
            text_lower,
            flags=re.IGNORECASE | re.VERBOSE
        )
    )


    investment_values = []
    investment_types = []
    investment_contexts = []


    # -----------------------------------------------------
    # Keyword investasi
    # -----------------------------------------------------

    investment_keywords = [

        "investasi",
        "investor",
        "investment",
        "pendanaan",
        "funding",
        "financing",
        "nilai proyek",
        "nilai investasi",
        "investment pipeline",
        "pipeline investasi",
        "dana",
        "mendanai",
        "mengucurkan"
    ]


    data_center_keywords = [

        "data center",
        "data centre",
        "pusat data"
    ]


    market_keywords = [

        "pasar",
        "market",
        "ukuran pasar",
        "market size",
        "nilai pasar"
    ]


    for match in matches:

        value = match.group(0).strip()

        position = match.start()


        context = get_context(
            text_lower,
            position,
            window=300
        )


        # -------------------------------------------------
        # Harus berhubungan dengan Data Center
        # -------------------------------------------------

        has_data_center = any(
            keyword in context
            for keyword in data_center_keywords
        )


        if not has_data_center:
            continue


        # -------------------------------------------------
        # Harus berhubungan dengan investasi/pasar
        # -------------------------------------------------

        has_investment = any(
            keyword in context
            for keyword in investment_keywords
        )


        has_market = any(
            keyword in context
            for keyword in market_keywords
        )


        if not has_investment and not has_market:
            continue


        # -------------------------------------------------
        # Tentukan tipe
        # -------------------------------------------------

        if has_market:

            investment_type = "Market Value"

        elif (
            "pipeline" in context
        ):

            investment_type = "Investment Pipeline"

        elif (
            "pendanaan" in context
            or "funding" in context
            or "financing" in context
        ):

            investment_type = "Funding"

        elif (
            "akuisisi" in context
            or "acquisition" in context
            or "membeli" in context
            or "beli perusahaan" in context
        ):

            investment_type = "Acquisition"

        else:

            investment_type = "Project Investment"


        # -------------------------------------------------
        # Ambil konteks
        # -------------------------------------------------

        context_clean = re.sub(
            r"\s+",
            " ",
            text[
                max(0, position - 150):
                min(len(text), position + 220)
            ]
        ).strip()


        investment_values.append(value)

        investment_types.append(
            investment_type
        )

        investment_contexts.append(
            context_clean
        )


    return (

        unique_join(
            investment_values
        ),

        unique_join(
            investment_types
        ),

        unique_join(
            investment_contexts
        )
    )


# =========================================================
# CAPACITY
# =========================================================

def extract_capacity(text):

    text = clean_text(text)
    text_lower = text.lower()


    capacity_pattern = r"""
        \b
        \d+(?:[.,]\d+)?
        (?:
            \s*-\s*
            \d+(?:[.,]\d+)?
        )?
        \s*
        (?:
            mw|
            megawatt|
            megawatts|
            gw|
            gigawatt|
            gigawatts|
            mva|
            kva
        )
        \b
    """


    matches = list(
        re.finditer(
            capacity_pattern,
            text_lower,
            flags=re.IGNORECASE | re.VERBOSE
        )
    )


    capacity_values = []
    capacity_types = []
    capacity_contexts = []


    capacity_keywords = [

        "data center",
        "data centre",
        "pusat data",
        "kapasitas data center",
        "kapasitas pusat data",
        "proyek data center",
        "pembangunan data center",
        "listrik untuk data center"
    ]


    for match in matches:

        value = match.group(0).strip()

        position = match.start()


        context = get_context(
            text_lower,
            position,
            window=300
        )


        # -------------------------------------------------
        # Harus berhubungan dengan Data Center
        # -------------------------------------------------

        has_data_center = any(
            keyword in context
            for keyword in capacity_keywords
        )


        if not has_data_center:
            continue


        # -------------------------------------------------
        # Tentukan tipe kapasitas
        # -------------------------------------------------

        if any(
            keyword in context
            for keyword in [

                "tambahan",
                "additional",
                "akan dibangun",
                "rencana",
                "rencananya",
                "pipeline",
                "minat investor",
                "investor berminat",
                "direncanakan"
            ]
        ):

            capacity_type = (
                "Planned / Additional"
            )


        elif any(
            keyword in context
            for keyword in [

                "telah beroperasi",
                "sudah beroperasi",
                "operasional",
                "existing",
                "terpasang",
                "beroperasi"
            ]
        ):

            capacity_type = "Existing"


        elif any(
            keyword in context
            for keyword in [

                "pasok listrik",
                "suplai listrik",
                "menyuplai listrik",
                "supply listrik",
                "daya listrik"
            ]
        ):

            capacity_type = "Power Supply"


        else:

            capacity_type = "Capacity"


        # -------------------------------------------------
        # Context
        # -------------------------------------------------

        context_clean = re.sub(
            r"\s+",
            " ",
            text[
                max(0, position - 150):
                min(len(text), position + 220)
            ]
        ).strip()


        capacity_values.append(
            value
        )

        capacity_types.append(
            capacity_type
        )

        capacity_contexts.append(
            context_clean
        )


    return (

        unique_join(
            capacity_values
        ),

        unique_join(
            capacity_types
        ),

        unique_join(
            capacity_contexts
        )
    )


# =========================================================
# COMPANY
# =========================================================

def extract_company(text):

    text = clean_text(text)
    text_lower = text.lower()


    company_keywords = {

        "PLN": [
            "pt pln",
            "pln (persero)",
            "pln"
        ],

        "Telkom": [
            "telkom",
            "pt telkom"
        ],

        "TelkomGroup": [
            "telkomgroup",
            "telkom group"
        ],

        "AMD": [
            "amd",
            "advanced micro devices"
        ],

        "Intel": [
            "intel",
            "intel corporation"
        ],

        "Nvidia": [
            "nvidia"
        ],

        "Microsoft": [
            "microsoft"
        ],

        "Google": [
            "google",
            "alphabet"
        ],

        "Amazon": [
            "amazon",
            "aws",
            "amazon web services"
        ],

        "Meta": [
            "meta platforms",
            "meta"
        ],

        "Apple": [
            "apple"
        ],

        "Oracle": [
            "oracle"
        ],

        "IBM": [
            "ibm"
        ],

        "Indosat": [
            "indosat"
        ],

        "Schneider Electric": [
            "schneider electric"
        ],

        "Digital Edge": [
            "digital edge",
            "edge dc"
        ],

        "Digital Realty": [
            "digital realty"
        ],

        "BDx": [
            "bdx data centers",
            "bdx"
        ],

        "DTC Netconnect": [
            "dtc netconnect"
        ]
    }


    companies = []


    for company, keywords in company_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:

                companies.append(
                    company
                )

                break


    return unique_join(companies)


# =========================================================
# ORGANIZATION
# =========================================================

def extract_organization(text):

    text = clean_text(text)
    text_lower = text.lower()


    organization_keywords = {

        "Pemerintah": [
            "pemerintah indonesia",
            "pemerintah"
        ],

        "Kementerian ESDM": [
            "kementerian energi dan sumber daya mineral",
            "kementerian esdm",
            "esdm"
        ],

        "Kementerian Investasi / BKPM": [
            "kementerian investasi",
            "bkpm",
            "badan koordinasi penanaman modal"
        ],

        "Kementerian Komunikasi dan Digital": [
            "kementerian komunikasi dan digital",
            "komdigi"
        ],

        "Kementerian Koordinator Bidang Perekonomian": [
            "kementerian koordinator bidang perekonomian",
            "menko perekonomian"
        ],

        "BP Batam": [
            "bp batam",
            "badan pengusahaan batam"
        ],

        "IDPRO": [
            "idpro",
            "indonesia data center provider organization"
        ],

        "Forbes": [
            "forbes"
        ]
    }


    organizations = []


    for organization, keywords in organization_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:

                organizations.append(
                    organization
                )

                break


    return unique_join(
        organizations
    )


# =========================================================
# PROJECT LOCATION
# =========================================================

def extract_project_location(text):

    text = clean_text(text)
    text_lower = text.lower()


    locations = {

        "Jakarta": [
            "jakarta"
        ],

        "Batam": [
            "batam",
            "nongsa"
        ],

        "Jatiluhur, Jawa Barat": [
            "jatiluhur"
        ],

        "Cikarang": [
            "cikarang"
        ],

        "Bekasi": [
            "bekasi"
        ],

        "Karawang": [
            "karawang"
        ],

        "Bandung": [
            "bandung"
        ],

        "Jawa Barat": [
            "jawa barat"
        ],

        "Kepulauan Riau": [
            "kepulauan riau"
        ],

        "Surabaya": [
            "surabaya"
        ],

        "Papua": [
            "papua"
        ],

        "Jayapura": [
            "jayapura"
        ],

        "Indonesia": [
            "indonesia"
        ]
    }


    project_locations = []


    project_keywords = [

        "data center",
        "data centre",
        "pusat data",
        "proyek",
        "pembangunan",
        "investor",
        "investasi",
        "ekspansi",
        "dibangun",
        "mengembangkan",
        "beroperasi",
        "kampus data center"
    ]


    for location, keywords in locations.items():

        for keyword in keywords:

            for match in re.finditer(
                re.escape(keyword),
                text_lower
            ):

                context = get_context(
                    text_lower,
                    match.start(),
                    window=250
                )


                has_project_context = any(
                    project_keyword in context
                    for project_keyword
                    in project_keywords
                )


                if has_project_context:

                    project_locations.append(
                        location
                    )

                    break


            if location in project_locations:
                break


    # -----------------------------------------------------
    # Hilangkan duplikat
    # -----------------------------------------------------

    project_locations = list(
        dict.fromkeys(
            project_locations
        )
    )


    # -----------------------------------------------------
    # Jika ada lokasi spesifik,
    # tidak perlu Indonesia
    # -----------------------------------------------------

    specific_locations = [

        location

        for location
        in project_locations

        if location != "Indonesia"
    ]


    if specific_locations:

        return unique_join(
            specific_locations
        )


    if "Indonesia" in project_locations:

        return "Indonesia"


    return ""


# =========================================================
# INSIGHT TYPE
# =========================================================

def determine_insight_type(row):

    insight_types = []


    if clean_text(
        row["investment_value"]
    ):

        insight_types.append(
            "Investment"
        )


    if clean_text(
        row["capacity"]
    ):

        insight_types.append(
            "Capacity"
        )


    if clean_text(
        row["technology"]
    ):

        insight_types.append(
            "Technology"
        )


    if clean_text(
        row["company"]
    ):

        insight_types.append(
            "Company"
        )


    if clean_text(
        row["organization"]
    ):

        insight_types.append(
            "Organization"
        )


    if clean_text(
        row["project_location"]
    ):

        insight_types.append(
            "Location"
        )


    return unique_join(
        insight_types
    )


# =========================================================
# MAIN
# =========================================================

print(
    "===================================="
)

print(
    "KOMPAS BUSINESS INSIGHT EXTRACTION"
)

print(
    "===================================="
)


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig",
    keep_default_na=False
)


print(
    f"Total artikel: {len(df)}"
)


# =========================================================
# PASTIKAN KOLOM TIDAK MENJADI NaN
# =========================================================

for column in df.columns:

    df[column] = df[column].apply(
        clean_text
    )


# =========================================================
# GABUNGKAN TEKS
# =========================================================

df["text_analysis"] = (

    df["title"]
    + " "

    + df["summary"]
    + " "

    + df["content"]
)


# =========================================================
# TECHNOLOGY
# =========================================================

df["technology"] = (

    df["text_analysis"]
    .apply(
        extract_technology
    )
)


# =========================================================
# INVESTMENT
# =========================================================

investment_result = (

    df["text_analysis"]
    .apply(
        extract_investment
    )
)


df["investment_value"] = (

    investment_result
    .apply(
        lambda x: x[0]
    )
)


df["investment_type"] = (

    investment_result
    .apply(
        lambda x: x[1]
    )
)


df["investment_context"] = (

    investment_result
    .apply(
        lambda x: x[2]
    )
)


# =========================================================
# CAPACITY
# =========================================================

capacity_result = (

    df["text_analysis"]
    .apply(
        extract_capacity
    )
)


df["capacity"] = (

    capacity_result
    .apply(
        lambda x: x[0]
    )
)


df["capacity_type"] = (

    capacity_result
    .apply(
        lambda x: x[1]
    )
)


df["capacity_context"] = (

    capacity_result
    .apply(
        lambda x: x[2]
    )
)


# =========================================================
# COMPANY
# =========================================================

df["company"] = (

    df["text_analysis"]
    .apply(
        extract_company
    )
)


# =========================================================
# ORGANIZATION
# =========================================================

df["organization"] = (

    df["text_analysis"]
    .apply(
        extract_organization
    )
)


# =========================================================
# PROJECT LOCATION
# =========================================================

df["project_location"] = (

    df["text_analysis"]
    .apply(
        extract_project_location
    )
)


# =========================================================
# SECTOR
# =========================================================

df["sector"] = (
    "Data Center & Cloud"
)


# =========================================================
# INSIGHT TYPE
# =========================================================

df["insight_type"] = (

    df.apply(
        determine_insight_type,
        axis=1
    )
)


# =========================================================
# HAPUS LOCATION LAMA
# =========================================================

if "location" in df.columns:

    df.drop(
        columns=["location"],
        inplace=True
    )


# =========================================================
# FINAL CLEANING
# =========================================================

df = df.fillna("")


for column in df.columns:

    df[column] = df[column].apply(
        clean_text
    )


# =========================================================
# URUTKAN KOLOM
# =========================================================

preferred_columns = [

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
    "investment_context",

    "capacity",
    "capacity_type",
    "capacity_context",

    "company",
    "organization",
    "project_location",

    "insight_type",

    "content",
    "scraped_at",

    "text_analysis"
]


existing_columns = [

    column

    for column
    in preferred_columns

    if column in df.columns
]


df = df[
    existing_columns
]


# =========================================================
# SAVE
# =========================================================

df.to_csv(

    OUTPUT_FILE,

    index=False,

    encoding="utf-8-sig"
)


# =========================================================
# SUMMARY
# =========================================================

print()

print(
    "===================================="
)

print(
    "EXTRACTION SELESAI"
)

print(
    "===================================="
)


print(
    f"Total artikel    : {len(df)}"
)


print(
    "Technology       :",
    (
        df["technology"] != ""
    ).sum()
)


print(
    "Investment       :",
    (
        df["investment_value"] != ""
    ).sum()
)


print(
    "Capacity         :",
    (
        df["capacity"] != ""
    ).sum()
)


print(
    "Company          :",
    (
        df["company"] != ""
    ).sum()
)


print(
    "Organization     :",
    (
        df["organization"] != ""
    ).sum()
)


print(
    "Project Location :",
    (
        df["project_location"] != ""
    ).sum()
)


print()

print(
    "===================================="
)

print(
    "FILE OUTPUT"
)

print(
    OUTPUT_FILE
)

print(
    "===================================="
)