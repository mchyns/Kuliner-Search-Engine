import json
import os
import re
import math
from collections import Counter, defaultdict
from database import get_all_kuliner

def preprocess_text(text):
    # Ubah ke lowercase dan hapus karakter khusus
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def is_main_ingredient(ingredient_list, query_terms):
    """Memeriksa apakah query adalah bahan utama dalam resep"""
    if not ingredient_list or not query_terms:
        return False
    
    # Ambil 3 bahan pertama sebagai bahan utama
    main_ingredients = [preprocess_text(ing) for ing in ingredient_list[:3]]
    main_ingredients_text = ' '.join(main_ingredients)
    
    # Periksa apakah query ada di bahan utama
    for term in query_terms:
        if any(term in ingredient.split() for ingredient in main_ingredients):
            return True
    return False

def is_specific_recipe(name, query_terms):
    """Memeriksa apakah query adalah nama resep spesifik"""
    if not name or not query_terms:
        return False
    
    name_processed = preprocess_text(name)
    # Jika semua kata dalam query ada dalam nama resep dan panjang query minimal 2 kata
    # maka ini dianggap pencarian resep spesifik
    if len(query_terms) >= 2 and all(term in name_processed for term in query_terms):
        return True
    return False

def search_kuliner(query, max_results=10, use_tfidf=True):
    """
    Pencarian kuliner dengan opsi menggunakan TF-IDF atau metode tradisional
    """
    if use_tfidf:
        # Gunakan TF-IDF search
        return tfidf_engine.search_tfidf(query, max_results)
    else:
        # Gunakan metode pencarian tradisional
        return _traditional_search(query, max_results)

def _traditional_search(query, max_results=10):
    """Metode pencarian tradisional (algoritma lama)"""
    query = preprocess_text(query)
    query_terms = query.split()
    
    # Dapatkan semua data kuliner dari database
    all_kuliner = get_all_kuliner()
    
    # Hitung skor relevansi untuk setiap dokumen
    results = []
    specific_recipe_results = []
    main_ingredient_results = []
    other_results = []
    
    for kuliner in all_kuliner:
        # Periksa apakah ini adalah format resep baru
        is_recipe = 'name' in kuliner and 'ingredients' in kuliner and 'instructions' in kuliner
        
        if is_recipe:
            # Format resep baru
            name = preprocess_text(kuliner.get('name', ''))
            ingredients = kuliner.get('ingredients', [])
            ingredients_text = ' '.join([preprocess_text(ingredient) for ingredient in ingredients])
            instructions_text = ' '.join([preprocess_text(instruction) for instruction in kuliner.get('instructions', [])])
            
            # Hitung skor berdasarkan kemunculan kata kunci
            score = 0
            for term in query_terms:
                # Bobot lebih tinggi jika kata kunci muncul di nama resep
                name_count = name.count(term) * 5
                # Bobot tinggi jika kata kunci muncul di bahan
                ingredients_count = ingredients_text.count(term) * 3
                # Bobot normal jika kata kunci muncul di instruksi
                instructions_count = instructions_text.count(term)
                
                score += name_count + ingredients_count + instructions_count
            
            if score > 0:
                result = {
                    'title': kuliner.get('name', ''),
                    'url': kuliner.get('url', ''),
                    'ingredients': kuliner.get('ingredients', []),
                    'instructions': kuliner.get('instructions', []),
                    'images': kuliner.get('images', [])[:1],  # Ambil 1 gambar saja
                    'score': score,
                    'is_recipe': True
                }
                
                # Kategorikan hasil pencarian
                if is_specific_recipe(name, query_terms):
                    specific_recipe_results.append(result)
                elif is_main_ingredient(ingredients, query_terms):
                    main_ingredient_results.append(result)
                else:
                    other_results.append(result)
        else:
            # Format artikel lama
            title = preprocess_text(kuliner.get('title', ''))
            content = preprocess_text(kuliner.get('content', ''))
            
            # Hitung skor berdasarkan kemunculan kata kunci
            score = 0
            for term in query_terms:
                # Bobot lebih tinggi jika kata kunci muncul di judul
                title_count = title.count(term) * 3
                content_count = content.count(term)
                
                score += title_count + content_count
            
            if score > 0:
                other_results.append({
                    'title': kuliner.get('title', ''),
                    'url': kuliner.get('url', ''),
                    'content': kuliner.get('content', '')[:200] + '...',  # Preview konten
                    'images': kuliner.get('images', [])[:1],  # Ambil 1 gambar saja
                    'score': score,
                    'is_recipe': False
                })
    
    # Prioritaskan hasil berdasarkan kategori
    if specific_recipe_results:
        # Jika ada resep spesifik yang cocok, hanya tampilkan itu
        results = specific_recipe_results
    elif main_ingredient_results:
        # Jika tidak ada resep spesifik tapi ada resep dengan bahan utama yang cocok
        results = main_ingredient_results
    else:
        # Jika tidak ada keduanya, tampilkan hasil lainnya
        results = other_results
    
    # Urutkan hasil berdasarkan skor (dari tertinggi ke terendah)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:max_results]

class TFIDFSearchEngine:
    def __init__(self):
        self.documents = []
        self.vocabulary = set()
        self.tf_matrix = []
        self.idf_scores = {}
        self.tfidf_matrix = []
        self.doc_index = {}  # Mapping index ke data kuliner
    
    def preprocess_document(self, kuliner):
        """Preprocessing dokumen kuliner untuk TF-IDF"""
        # Ambil teks dari berbagai field
        texts = []
        
        if 'name' in kuliner:
            # Format resep baru
            texts.append(kuliner.get('name', ''))
            texts.extend(kuliner.get('ingredients', []))
            texts.extend(kuliner.get('instructions', []))
        else:
            # Format artikel lama
            texts.append(kuliner.get('title', ''))
            texts.append(kuliner.get('content', ''))
        
        # Gabung semua teks dan preprocessing
        full_text = ' '.join(texts)
        processed_text = preprocess_text(full_text)
        tokens = processed_text.split()
        
        return tokens
    
    def build_index(self):
        """Membangun index TF-IDF dari database"""
        print("Building TF-IDF index...")
        
        # Reset index
        self.documents = []
        self.vocabulary = set()
        self.doc_index = {}
        
        # Dapatkan semua data kuliner
        all_kuliner = get_all_kuliner()
        
        for i, kuliner in enumerate(all_kuliner):
            tokens = self.preprocess_document(kuliner)
            self.documents.append(tokens)
            self.vocabulary.update(tokens)
            self.doc_index[i] = kuliner
        
        # Hitung TF-IDF
        self._calculate_tf()
        self._calculate_idf()
        self._calculate_tfidf()
        
        print(f"TF-IDF index built: {len(self.documents)} documents, {len(self.vocabulary)} terms")
    
    def _calculate_tf(self):
        """Menghitung Term Frequency"""
        self.tf_matrix = []
        
        for doc_tokens in self.documents:
            token_count = Counter(doc_tokens)
            total_tokens = len(doc_tokens)
            
            tf_scores = {}
            for term in self.vocabulary:
                tf_scores[term] = token_count[term] / total_tokens if total_tokens > 0 else 0
            
            self.tf_matrix.append(tf_scores)
    
    def _calculate_idf(self):
        """Menghitung Inverse Document Frequency"""
        total_docs = len(self.documents)
        
        for term in self.vocabulary:
            doc_count = sum(1 for doc_tokens in self.documents if term in doc_tokens)
            self.idf_scores[term] = math.log(total_docs / doc_count) if doc_count > 0 else 0
    
    def _calculate_tfidf(self):
        """Menghitung TF-IDF matrix"""
        self.tfidf_matrix = []
        
        for tf_scores in self.tf_matrix:
            tfidf_scores = {}
            for term in self.vocabulary:
                tfidf_scores[term] = tf_scores[term] * self.idf_scores[term]
            self.tfidf_matrix.append(tfidf_scores)
    
    def search_tfidf(self, query, max_results=10):
        """Pencarian menggunakan TF-IDF similarity"""
        if not self.tfidf_matrix:
            self.build_index()
        
        # Preprocessing query
        query_tokens = preprocess_text(query).split()
        
        # Hitung TF untuk query
        query_tf = Counter(query_tokens)
        total_query_tokens = len(query_tokens)
        
        # Hitung TF-IDF untuk query
        query_tfidf = {}
        for term in query_tokens:
            if term in self.vocabulary:
                tf_score = query_tf[term] / total_query_tokens
                query_tfidf[term] = tf_score * self.idf_scores[term]
            else:
                query_tfidf[term] = 0
        
        # Hitung cosine similarity dengan setiap dokumen
        similarities = []
        
        for i, doc_tfidf in enumerate(self.tfidf_matrix):
            similarity = self._cosine_similarity(query_tfidf, doc_tfidf)
            if similarity > 0:
                similarities.append((i, similarity))
        
        # Sort berdasarkan similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Konversi ke format hasil
        results = []
        for doc_index, similarity in similarities[:max_results]:
            kuliner = self.doc_index[doc_index]
            
            # Format hasil berdasarkan jenis data
            if 'name' in kuliner:
                # Format resep
                result = {
                    'title': kuliner.get('name', ''),
                    'url': kuliner.get('url', ''),
                    'ingredients': kuliner.get('ingredients', []),
                    'instructions': kuliner.get('instructions', []),
                    'images': kuliner.get('images', [])[:1],
                    'score': similarity,
                    'is_recipe': True,
                    'tfidf_score': similarity
                }
            else:
                # Format artikel
                result = {
                    'title': kuliner.get('title', ''),
                    'url': kuliner.get('url', ''),
                    'content': kuliner.get('content', '')[:200] + '...',
                    'images': kuliner.get('images', [])[:1],
                    'score': similarity,
                    'is_recipe': False,
                    'tfidf_score': similarity
                }
            
            results.append(result)
        
        return results
    
    def _cosine_similarity(self, vec1, vec2):
        """Menghitung cosine similarity antara dua vektor"""
        # Ambil terms yang ada di kedua vektor
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0
        
        # Hitung dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Hitung magnitude
        magnitude1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        magnitude2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)

# Inisialisasi TF-IDF Search Engine
tfidf_engine = TFIDFSearchEngine()