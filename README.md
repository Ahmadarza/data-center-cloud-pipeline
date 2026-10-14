# Data Center & Cloud

## Project Overview

Data Center & Cloud Pipeline merupakan pipeline pengumpulan dan pengolahan berita terkait sektor Data Center & Cloud dari berbagai sumber berita online. Pipeline ini digunakan untuk menghasilkan business insight yang ditampilkan melalui dashboard untuk mendukung analisis bisnis dan pemasaran.

Pipeline menggunakan Apache Airflow untuk mengatur jadwal dan menjalankan proses otomatis, Python untuk web scraping dan pengolahan data, CSV sebagai staging area, PostgreSQL sebagai database utama, serta Flask sebagai backend dashboard.

**Alur pipeline:**

Apache Airflow → Web Scraping → Cleaning & Filtering → Business Insight Extraction → CSV Staging → PostgreSQL → Flask Dashboard → Business Intelligence Output

## 1. Apache Airflow

Apache Airflow digunakan untuk mengorkestrasi dan mengotomatisasi proses pipeline secara terjadwal.

Fungsi utama:
- Menjalankan pipeline secara otomatis menggunakan jadwal mingguan (`@weekly`).
- Mengatur urutan eksekusi setiap task.
- Memantau status dan hasil eksekusi pipeline.
- Mengelola proses scraping, pengolahan data, dan penyimpanan data.

DAG yang digunakan: `data_center_pipeline`.

## 2. Data Sources

Pipeline mengumpulkan berita dari beberapa sumber online yang membahas sektor Data Center & Cloud.

Sumber data:
- ANTARA News
- Katadata
- KOMPAS

Data yang dikumpulkan mencakup informasi terkait infrastruktur data center, investasi, energi, perusahaan, regulasi, dan perkembangan teknologi cloud.

## 3. Web Scraping

Web scraping digunakan untuk mengambil informasi berita dari setiap sumber secara otomatis menggunakan Python.

Teknologi yang digunakan:
- **Requests** untuk mengirim HTTP request.
- **BeautifulSoup** untuk parsing dan ekstraksi elemen HTML.
- **Selenium** untuk menangani halaman dinamis dan navigasi pagination.

Data yang dikumpulkan meliputi judul berita, tanggal publikasi, tautan artikel, gambar, dan isi artikel.

## 4. Data Processing

### 4.1 Cleaning & Filtering

Tahap ini dilakukan untuk membersihkan dan menyaring data berita sebelum disimpan ke database.

Proses meliputi:
- Membersihkan data hasil scraping.
- Menghapus atau menangani data duplikat.
- Memfilter artikel berdasarkan periode 12 bulan terakhir.
- Mengklasifikasikan relevansi artikel terhadap sektor Data Center & Cloud.

### 4.2 Business Insight Extraction

Tahap ini digunakan untuk mengekstraksi informasi penting dari artikel agar dapat dimanfaatkan untuk analisis bisnis.

Informasi yang diekstraksi meliputi:
- Technology
- Investment
- Capacity
- Company
- Organization
- Project Location
- Insight Type

Hasil ekstraksi digunakan sebagai dasar penyajian informasi dan business insight pada dashboard.

## 5. CSV Staging

CSV digunakan sebagai staging area atau tempat penyimpanan sementara sebelum data dimasukkan ke PostgreSQL.

Fungsi CSV staging:
- Menyimpan hasil scraping dan pengolahan sementara.
- Memudahkan validasi dan pemeriksaan data.
- Membantu proses debugging dan pemrosesan ulang apabila terjadi kesalahan.
- Memisahkan proses pengolahan data dari proses penyimpanan ke database utama.

CSV tidak digunakan sebagai penyimpanan historis utama. Data utama dikelola di PostgreSQL.

## 6. PostgreSQL

PostgreSQL digunakan sebagai database utama untuk menyimpan data artikel yang telah melalui proses cleaning, filtering, dan business insight extraction.

Data yang disimpan meliputi:
- Informasi artikel dan sumber berita.
- Tanggal publikasi dan tautan artikel.
- Kategori relevansi dan topik.
- Informasi teknologi dan investasi.
- Kapasitas, perusahaan, organisasi, dan lokasi proyek.
- Informasi pendukung dashboard.

Proses penyimpanan menggunakan mekanisme insert atau upsert berdasarkan URL artikel untuk membantu mencegah duplikasi data.

## 7. Flask Dashboard Backend

Flask digunakan sebagai backend yang menghubungkan PostgreSQL dengan dashboard.

Fungsi utama:
- Mengambil data dari PostgreSQL.
- Menyediakan data untuk ditampilkan pada dashboard.
- Menangani filter dan permintaan data dari pengguna.
- Menghubungkan fitur AI Executive Summary dengan Google Gemini API.

## 8. Dashboard

Dashboard digunakan untuk menampilkan hasil pengolahan data berita dalam bentuk visualisasi dan informasi yang mudah dipahami.

Fitur dashboard meliputi:
- Menampilkan daftar artikel berita.
- Menampilkan judul, tanggal, gambar, dan tautan artikel.
- Memfilter data berdasarkan sumber, topik, dan teknologi.
- Menampilkan tren dan distribusi data.
- Menyajikan informasi terkait investasi dan business insight.

## 9. AI Executive Summary

AI Executive Summary menggunakan Google Gemini API untuk membantu merangkum informasi dan insight dari data yang tersedia.

Fitur ini terintegrasi melalui Flask backend dan ditampilkan pada dashboard untuk membantu pengguna memahami perkembangan sektor Data Center & Cloud secara lebih ringkas.

## 10. Business Intelligence Output

Hasil akhir pipeline berupa informasi dan visualisasi yang dapat digunakan untuk mendukung analisis bisnis dan pemasaran.

Output meliputi:
- Tren berita Data Center & Cloud.
- Distribusi topik dan teknologi.
- Informasi investasi dan kapasitas.
- Informasi perusahaan, organisasi, dan lokasi proyek.
- Ringkasan insight untuk mendukung pengambilan keputusan.

## 11. Workflow

```text
Apache Airflow (@weekly)
          |
          v
     Data Sources
 ANTARA | Katadata | KOMPAS
          |
          v
     Web Scraping
          |
          v
 Cleaning & Filtering
          |
          v
Business Insight Extraction
          |
          v
     CSV Staging
          |
          v
      PostgreSQL
          |
          v
Flask Dashboard Backend
          |
          v
       Dashboard
          |
          v
Business Intelligence Output
```

**Catatan:**
- Apache Airflow mengatur jadwal dan eksekusi pipeline.
- CSV berfungsi sebagai penyimpanan sementara (*staging area*).
- PostgreSQL berfungsi sebagai database utama.
- Flask menghubungkan database, dashboard, dan layanan AI Executive Summary.
