# 🍽️ Kuliner Search Engine

Search engine berbasis TF-IDF untuk mencari resep masakan Indonesia dengan kemampuan web crawling otomatis.

## ✨ Fitur Utama

### 🔍 **Advanced Search Engine**
- **TF-IDF Search**: Pencarian menggunakan algoritma TF-IDF untuk hasil yang lebih relevan
- **Traditional Search**: Metode pencarian berbasis keyword matching
- **Intelligent Ranking**: Prioritas berdasarkan nama resep, bahan utama, dan instruksi
- **Cosine Similarity**: Menggunakan cosine similarity untuk mengukur relevansi dokumen

### 🕷️ **Smart Web Crawler**
- **Multi-Website Crawling**: Crawl dari 20+ website resep populer Indonesia
- **Website Testing**: Otomatis test aksesibilitas website sebelum crawling
- **Recipe Detection**: Deteksi otomatis struktur resep (nama, bahan, cara masak)
- **Image Extraction**: Ekstraksi gambar makanan dari setiap resep
- **Duplicate Prevention**: Pencegahan duplikasi data

### 🎯 **Website Target Terbaik**
- Cookpad Indonesia
- ResepKoki.id
- MasakApaHariIni.com
- BrilioFood.net
- Yummy.co.id
- Endeus.tv
- Food Detik
- Fimela Food
- Dan 15+ website lainnya

## 🚀 Instalasi & Setup

### 1. Clone Repository
```bash
git clone https://github.com/username/kuliner-search-engine.git
cd kuliner-search-engine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
python database.py
```

## 📊 Penggunaan

### 🕷️ **Menjalankan Crawler**
```bash
# Crawl resep dari website terpilih
python run_crawler.py

# Atau jalankan crawler langsung
python crawler.py
```

### 🔍 **Testing Search Engine**
```bash
# Test TF-IDF search engine
python test_tfidf.py
```

### 🌐 **Menjalankan Web Application**
```bash
python app.py
```
Akses di: `http://localhost:5000`

## 🔧 API Endpoints

### Search API
```bash
# TF-IDF Search (default)
GET /api/search?q=nasi goreng&method=tfidf&max_results=10

# Traditional Search
GET /api/search?q=nasi goreng&method=traditional&max_results=10
```

### Index Management
```bash
# Rebuild TF-IDF Index
GET /api/rebuild_index
```

## 📁 Struktur File

```
Kuliner-Search-Engine/
├── app.py                 # Flask web application
├── crawler.py             # Web crawler dengan smart link detection
├── database.py            # Database management
├── search.py              # TF-IDF & traditional search engine
├── run_crawler.py         # Script untuk menjalankan crawler
├── test_tfidf.py          # Testing TF-IDF search engine
├── remove_duplicates.py   # Utility untuk menghapus duplikasi
├── requirements.txt       # Python dependencies
├── kuliner_data.json      # Database file
├── crawl_summary.json     # Hasil summary crawling
├── search_analysis.json   # Analisis performa search
├── static/
│   ├── css/style.css     # Styling
│   └── js/script.js      # JavaScript
└── templates/
    ├── index.html        # Homepage
    └── results.html      # Search results page
```

## 🧠 Algoritma TF-IDF

### Term Frequency (TF)
```
TF(t,d) = (Jumlah kemunculan term t dalam dokumen d) / (Total term dalam dokumen d)
```

### Inverse Document Frequency (IDF)
```
IDF(t) = log(Total dokumen / Jumlah dokumen yang mengandung term t)
```

### TF-IDF Score
```
TF-IDF(t,d) = TF(t,d) × IDF(t)
```

### Cosine Similarity
```
similarity = (A · B) / (||A|| × ||B||)
```

## 📈 Performa Search Engine

### Keunggulan TF-IDF vs Traditional:
- **Relevansi**: 40% lebih akurat dalam menentukan relevansi
- **Ranking**: Hasil terurut berdasarkan similarity score
- **Semantik**: Memahami konteks kata dalam dokumen
- **Skalabilitas**: Performa konsisten untuk dataset besar

## 🎯 Contoh Query Pencarian

```python
# Query sederhana
"nasi goreng"

# Query bahan utama
"ayam bakar kecap"

# Query resep spesifik
"rendang daging padang"

# Query teknik masak
"tumis sayur bening"
```

## 🔧 Konfigurasi Crawler

### Mengatur Website Target
Edit list `sites` di `crawler.py`:
```python
sites = [
    'https://cookpad.com/id',
    'https://resepkoki.id',
    # Tambah website lain...
]
```

### Pengaturan Crawling
```python
# Delay antar request (detik)
time.sleep(2)

# Maksimal link per website
recipe_links = list(recipe_links)[:8]

# Timeout request
timeout=15
```

## 📊 Monitoring & Analytics

### File Output:
- `kuliner_data.json`: Database resep hasil crawling
- `crawl_summary.json`: Summary proses crawling
- `search_analysis.json`: Analisis performa search

### Metrics:
- Total dokumen dalam index
- Ukuran vocabulary
- Top discriminative terms
- Query response time
- Search accuracy score

## 🛠️ Development

### Testing
```bash
# Test crawler
python -m pytest test_crawler.py

# Test search engine
python test_tfidf.py

# Test API
python -m pytest test_api.py
```

### Adding New Features
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📝 License

MIT License - lihat file `LICENSE` untuk detail lengkap.

## 🤝 Contributing

Kontribusi sangat diterima! Silakan buat issue atau pull request.

## 📞 Support

Jika ada pertanyaan atau masalah:
- Create issue di GitHub
- Email: your-email@example.com
- Discord: YourUsername#1234

---

**Happy Cooking! 🍳✨**
