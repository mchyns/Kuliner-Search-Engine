from flask import Flask, render_template, request, jsonify
from search import search_kuliner, tfidf_engine
import os

app = Flask(__name__)

# Initialize TF-IDF engine saat aplikasi dimulai
def initialize_tfidf():
    """Initialize TF-IDF index saat aplikasi pertama kali dijalankan"""
    print("Initializing TF-IDF search engine...")
    try:
        tfidf_engine.build_index()
        print("TF-IDF index built successfully!")
    except Exception as e:
        print(f"Error building TF-IDF index: {e}")

# Initialize saat modul dimuat
initialize_tfidf()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_method = request.args.get('method', 'tfidf')  # Default ke TF-IDF
    
    if not query:
        return render_template('index.html')
    
    # Pilih metode pencarian
    use_tfidf = search_method.lower() == 'tfidf'
    results = search_kuliner(query, use_tfidf=use_tfidf)
    
    return render_template('results.html', 
                         query=query, 
                         results=results, 
                         search_method=search_method)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    search_method = request.args.get('method', 'tfidf')
    max_results = int(request.args.get('max_results', 10))
    
    if not query:
        return jsonify({'error': 'Query tidak boleh kosong'}), 400
    
    use_tfidf = search_method.lower() == 'tfidf'
    results = search_kuliner(query, max_results=max_results, use_tfidf=use_tfidf)
    
    return jsonify({
        'query': query,
        'search_method': search_method,
        'results_count': len(results),
        'results': results
    })

@app.route('/api/rebuild_index')
def rebuild_index():
    """API endpoint untuk rebuild TF-IDF index"""
    try:
        tfidf_engine.build_index()
        return jsonify({
            'success': True, 
            'message': 'TF-IDF index rebuilt successfully',
            'documents_count': len(tfidf_engine.documents),
            'vocabulary_size': len(tfidf_engine.vocabulary)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)