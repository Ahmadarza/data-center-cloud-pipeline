from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator


PIPELINE_DIR = "/opt/airflow/data-center-pipeline"


with DAG(
    dag_id="data_center_pipeline",
    start_date=datetime(2026, 9, 21),
    schedule_interval="@weekly",
    catchup=False,
    tags=["data-center", "multi-source"],
) as dag:

    # ==========================================
    # ANTARA
    # ==========================================

    scrape_antara = BashOperator(
        task_id="scrape_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python antaranews_scraping.py",
    )

    content_antara = BashOperator(
        task_id="content_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python antaranews_article_scraping.py",
    )

    clean_antara = BashOperator(
        task_id="clean_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python clean_filter_antaranews.py",
    )

    filter_antara = BashOperator(
        task_id="filter_current_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python filter_current_antaranews.py",
    )

    insight_antara = BashOperator(
        task_id="insight_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python extract_business_insight.py",
    )

    load_antara = BashOperator(
        task_id="load_antaranews",
        bash_command=f"cd {PIPELINE_DIR} && python load_postgresql.py",
    )


    # ==========================================
    # KATADATA
    # ==========================================

    scrape_katadata = BashOperator(
        task_id="scrape_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python katadata_scraping.py",
    )

    content_katadata = BashOperator(
        task_id="content_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python katadata_article_scraping.py",
    )

    clean_katadata = BashOperator(
        task_id="clean_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python clean_filter_katadata.py",
    )

    filter_katadata = BashOperator(
        task_id="filter_current_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python filter_current_katadata.py",
    )

    insight_katadata = BashOperator(
        task_id="insight_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python extract_business_insight_katadata.py",
    )

    load_katadata = BashOperator(
        task_id="load_katadata",
        bash_command=f"cd {PIPELINE_DIR} && python load_katadata_postgresql.py",
    )

# ==========================================
# KOMPAS
# ==========================================

scrape_kompas = BashOperator(
    task_id="scrape_kompas",
    bash_command=f"cd {PIPELINE_DIR} && python kompas_scraping.py",
)

clean_kompas = BashOperator(
    task_id="clean_kompas",
    bash_command=f"cd {PIPELINE_DIR} && python clean_filter_kompas.py",
)

filter_kompas = BashOperator(
    task_id="filter_current_kompas",
    bash_command=f"cd {PIPELINE_DIR} && python filter_current_kompas.py",
)

insight_kompas = BashOperator(
    task_id="insight_kompas",
    bash_command=f"cd {PIPELINE_DIR} && python extract_business_insight_kompas.py",
)

load_kompas = BashOperator(
    task_id="load_kompas",
    bash_command=f"cd {PIPELINE_DIR} && python load_kompas_postgresql.py",
)


# ==========================================
# DEPENDENCY KOMPAS
# ==========================================

(
    scrape_kompas
    >> clean_kompas
    >> filter_kompas
    >> insight_kompas
    >> load_kompas
)