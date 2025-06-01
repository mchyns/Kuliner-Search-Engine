#!/usr/bin/env python3
"""
Script untuk menguji TF-IDF Search Engine
"""

import os
import sys
import json
from datetime import datetime

# Tambah path untuk import module lokal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search import search_kuliner, tfidf_engine

def test_search_queries():
    """Test berbagai query pencarian"""
    test_queries = [
        "nasi goreng",
        "ayam bakar",
        "soto ayam",
        "rendang daging",
        "gado gado",
        "bakso malang",
        "gudeg jogja",
        "sambal terasi",
        "ikan bakar",
        "sayur asem",
        "es campur",
        "kue lapis",
        "masakan padang",
        "makanan tradisional",
        "resep mudah"
    ]
    
    print("🔍 Testing TF-IDF Search Engine")
    print("=" * 50)
    
    # Build index terlebih dahulu
    print("Building TF-IDF index...")
    tfidf_engine.build_index()
    print("Index built successfully!\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i:2d}] Query: '{query}'")
        
        try:
            # Test TF-IDF search
            tfidf_results = search_kuliner(query, max_results=3, use_tfidf=True)
            
            # Test traditional search
            traditional_results = search_kuliner(query, max_results=3, use_tfidf=False)
            
            print(f"     TF-IDF Results: {len(tfidf_results)} found")
            for j, result in enumerate(tfidf_results[:2], 1):
                title = result['title'][:40] + "..." if len(result['title']) > 40 else result['title']
                score = result.get('tfidf_score', result.get('score', 0))
                print(f"       {j}. {title} (score: {score:.4f})")
            
            print(f"     Traditional Results: {len(traditional_results)} found")
            for j, result in enumerate(traditional_results[:2], 1):
                title = result['title'][:40] + "..." if len(result['title']) > 40 else result['title']
                score = result.get('score', 0)
                print(f"       {j}. {title} (score: {score})")
            
            print()
            
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")
            print()

def compare_search_methods():
    """Bandingkan metode pencarian TF-IDF vs Traditional"""
    
    print("\n📊 Comparing Search Methods")
    print("=" * 50)
    
    comparison_queries = ["nasi goreng", "rendang", "ayam bakar"]
    
    for query in comparison_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 30)
        
        # TF-IDF Results
        tfidf_results = search_kuliner(query, max_results=5, use_tfidf=True)
        print(f"TF-IDF ({len(tfidf_results)} results):")
        for i, result in enumerate(tfidf_results, 1):
            score = result.get('tfidf_score', result.get('score', 0))
            print(f"  {i}. {result['title']} (score: {score:.4f})")
        
        # Traditional Results
        traditional_results = search_kuliner(query, max_results=5, use_tfidf=False)
        print(f"\nTraditional ({len(traditional_results)} results):")
        for i, result in enumerate(traditional_results, 1):
            score = result.get('score', 0)
            print(f"  {i}. {result['title']} (score: {score})")

def save_search_analysis():
    """Simpan analisis hasil pencarian ke file"""
    analysis_data = {
        'timestamp': datetime.now().isoformat(),
        'total_documents': len(tfidf_engine.documents),
        'vocabulary_size': len(tfidf_engine.vocabulary),
        'top_terms': [],
        'sample_queries': []
    }
    
    # Analisis vocabulary
    if tfidf_engine.idf_scores:
        # Ambil terms dengan IDF tertinggi (paling diskriminatif)
        top_idf_terms = sorted(tfidf_engine.idf_scores.items(), 
                              key=lambda x: x[1], reverse=True)[:20]
        analysis_data['top_discriminative_terms'] = top_idf_terms
    
    # Test sample queries
    sample_queries = ["nasi goreng", "rendang", "soto"]
    for query in sample_queries:
        results = search_kuliner(query, max_results=3, use_tfidf=True)
        analysis_data['sample_queries'].append({
            'query': query,
            'results_count': len(results),
            'top_results': [
                {
                    'title': r['title'],
                    'score': r.get('tfidf_score', r.get('score', 0))
                } for r in results[:3]
            ]
        })
    
    # Simpan ke file
    with open('search_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print("📋 Search analysis saved to search_analysis.json")

def main():
    print("🍽️  TF-IDF SEARCH ENGINE TESTER")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test search queries
        test_search_queries()
        
        # Compare methods
        compare_search_methods()
        
        # Save analysis
        save_search_analysis()
        
        print("\n✅ Testing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
