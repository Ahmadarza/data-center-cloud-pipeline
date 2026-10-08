# Data Center & Cloud Pipeline

Data pipeline dan Business Intelligence dashboard untuk mengolah dan menganalisis data berita terkait sektor **Data Center & Cloud di Indonesia**.

## Project Overview

Project ini bertujuan untuk mengumpulkan data berita dari beberapa sumber publik, melakukan pengolahan dan ekstraksi business insight, menyimpan data ke PostgreSQL, serta menyajikan hasil analisis melalui dashboard.

Pipeline yang digunakan terdiri dari beberapa tahap:

**Web Scraping → Cleaning & Filtering → Business Insight → CSV Staging → PostgreSQL → Flask → Dashboard**

Selain itu, dashboard dilengkapi dengan fitur **AI Executive Summary** menggunakan Google Gemini API.

---

## 1. Data Sources

Data dikumpulkan dari beberapa sumber berita publik:

- ANTARA
- Katadata
- Kompas

Fokus data adalah berita yang berkaitan dengan sektor **Data Center & Cloud di Indonesia**.

---

## 2. Web Scraping

Proses pengumpulan data dilakukan menggunakan beberapa library Python:

- **Selenium** → digunakan untuk halaman yang membutuhkan interaksi browser atau pemuatan data secara dinamis.
- **BeautifulSoup** → digunakan untuk membaca dan memproses struktur HTML.
- **Requests** → digunakan untuk melakukan HTTP request pada halaman yang dapat diakses secara langsung.

---

## 3. Data Processing

Data hasil scraping tidak langsung digunakan untuk analisis. Data terlebih dahulu melalui beberapa tahap pengolahan.

### 3.1 Cleaning & Filtering

Tahap ini digunakan untuk membersihkan dan menyaring data berdasarkan:

- Relevansi berita
- Topik Data Center & Cloud
- Periode data 12 bulan
- Informasi yang dibutuhkan untuk analisis

Tujuannya adalah mendapatkan data yang lebih relevan sebelum masuk ke tahap berikutnya.

### 3.2 Business Insight Extraction

Informasi penting dari artikel diekstraksi menjadi beberapa kategori:

- Technology
- Investment
- Capacity
- Company
- Organization
- Project Location
- Insight Type

Tahap ini bertujuan mengubah data berita menjadi informasi yang lebih terstruktur untuk kebutuhan Business Intelligence.

---

## 4. CSV Staging

CSV digunakan sebagai **staging area** atau penyimpanan sementara sebelum data dimasukkan ke PostgreSQL.

CSV digunakan untuk membantu:

- Validasi data
- Pemeriksaan hasil scraping
- Debugging
- Reprocessing data

CSV bukan merupakan penyimpanan utama. Data utama yang digunakan oleh dashboard disimpan di PostgreSQL.

---

## 5. PostgreSQL

PostgreSQL digunakan sebagai **database utama** untuk menyimpan data yang telah diproses.

Data yang disimpan mencakup informasi artikel dan business insight seperti:

- Title
- Published Date
- Summary
- Article URL
- Image URL
- Source
- Topic
- Relevance
- Technology
- Investment Value
- Investment Type
- Capacity
- Capacity Type
- Company
- Organization
- Project Location
- Insight Type
- Content

Proses load data menggunakan mekanisme **upsert berdasarkan URL artikel** untuk membantu mencegah duplikasi data.

---

## 6. Flask Dashboard

Dashboard dikembangkan menggunakan **Flask**.

Flask berfungsi sebagai backend yang menghubungkan PostgreSQL dengan tampilan dashboard.

Flask mengambil data dari PostgreSQL dan menyediakan data yang dibutuhkan oleh dashboard seperti:

- Total artikel
- Investment Signal
- Capacity Signal
- Technology
- News Trends
- Business Insights
- Latest News
- Filter berdasarkan source

---

## 7. Dashboard

Dashboard digunakan untuk menyajikan hasil pengolahan data dalam bentuk **Business Intelligence**.

Informasi yang ditampilkan meliputi:

- Total Artikel
- Investment Signal
- Capacity Signal
- Technology
- News Trend
- Trend Insight
- Business Insight
- Latest News
- Source Filter
- AI Executive Summary

Dashboard membantu pengguna melihat perkembangan dan informasi penting terkait sektor Data Center & Cloud.

---

## 8. AI Executive Summary

Dashboard dilengkapi fitur **AI Executive Summary** menggunakan Google Gemini API.

Gemini digunakan untuk menganalisis data artikel yang tersedia dan menghasilkan ringkasan bisnis.

Analisis AI mencakup:

1. **Ringkasan Utama**  
   Memberikan gambaran umum mengenai informasi yang paling banyak dibahas dalam kumpulan artikel.

2. **Tren yang Terlihat**  
   Mengidentifikasi pola atau tren yang muncul berdasarkan data artikel.

3. **Investment & Capacity**  
   Menganalisis informasi terkait investasi dan kapasitas data center yang terdapat dalam data.

4. **Teknologi dan Perusahaan**  
   Mengidentifikasi teknologi, perusahaan, dan organisasi yang sering muncul dalam data.

5. **Business Insight**  
   Memberikan rangkuman insight bisnis berdasarkan informasi yang tersedia.

AI diarahkan untuk menggunakan informasi yang tersedia pada data dan tidak mengarang angka atau fakta.

---

##9. 10. Business Intelligence Output
Hasil akhir dari pipeline adalah Business Intelligence Dashboard yang menyajikan informasi terkait sektor Data Center & Cloud.
Dashboard digunakan untuk melihat:
- Tren pemberitaan
- Investment Signal
- Capacity Signal
- Teknologi
- Perusahaan dan organisasi
- Lokasi proyek
- Berita terbaru
- AI Executive Summary

## 10. Workflow

```text
Data Source
ANTARA | Katadata | Kompas
        ↓
Web Scraping
        ↓
Cleaning & Filtering
        ↓
Business Insight Extraction
        ↓
CSV Staging
        ↓
PostgreSQL
        ↓
Flask
        ↓
Dashboard
        ↓
Business Intelligence Output
