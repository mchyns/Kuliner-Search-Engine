import requests
from bs4 import BeautifulSoup
import json
import os
import time
from database import save_to_database
import re

# Daftar situs resep yang akan di-crawl
sites = [
    # Website resep populer Indonesia
    'https://cookpad.com/id/masakan-indonesia',
    'https://cookpad.com/id/cari/masakan%20nusantara',
    'https://resepkoki.id/resep/resep-masakan-indonesia/',
    'https://www.masakapahariini.com/resep/',
    'https://sajianredaksi.com/tag/resep-masakan-indonesia/',
    'https://www.briliofood.net/resep/',
    'https://resep.web.id/masakan-indonesia.htm',
    'https://www.tokomesin.com/resep/',
    'https://dapur.web.id/resep-masakan-indonesia/',
    'https://aneka-resep-masakan.blogspot.com/',
    
    # Website resep khusus
    'https://resepmasakanpraktis.com/category/masakan-indonesia/',
    'https://resepmasakan.id/resep-masakan-indonesia/',
    'https://www.fimela.com/food/recipe',
    'https://lifestyle.okezone.com/food-travel/resep',
    'https://food.detik.com/resep',
    
    # Blog dan komunitas masak
    'https://yummy.co.id/resep',
    'https://endeus.tv/resep',
    'https://www.pegipegi.com/travel/kuliner-nusantara/',
    'https://www.idntimes.com/food/recipe',
    
    # Website khusus makanan tradisional
    'https://www.indonesia.travel/id/id/ide-liburan/makanan-tradisional-indonesia',
    'https://bobo.grid.id/tag/resep-masakan-indonesia',
    'https://www.haibunda.com/food'
]

def extract_recipe(soup):
    """Ekstrak informasi resep dari halaman"""
    recipe = {}
    
    # Coba ekstrak nama resep
    recipe_name = ''
    possible_title_tags = soup.find_all(['h1', 'h2'])
    for tag in possible_title_tags[:2]:  # Ambil 2 heading pertama saja
        if len(tag.text.strip()) > 5 and len(tag.text.strip()) < 100:
            recipe_name = tag.text.strip()
            break
    
    recipe['name'] = recipe_name
    
    # Ekstrak bahan-bahan
    ingredients = []
    ingredient_patterns = [
        re.compile(r'bahan', re.IGNORECASE),
        re.compile(r'ingredient', re.IGNORECASE)
    ]
    
    # Cari heading yang mengandung kata "bahan"
    ingredient_section = None
    for pattern in ingredient_patterns:
        for heading in soup.find_all(['h2', 'h3', 'h4', 'strong']):
            if pattern.search(heading.text):
                ingredient_section = heading
                break
        if ingredient_section:
            break
    
    # Jika menemukan bagian bahan, cari list item setelahnya
    if ingredient_section:
        # Cari list item terdekat
        ul_tag = ingredient_section.find_next('ul')
        if ul_tag:
            for li in ul_tag.find_all('li'):
                ingredients.append(li.text.strip())
        else:
            # Jika tidak ada list, coba cari paragraf atau div dengan bahan
            next_elements = ingredient_section.find_next_siblings(['p', 'div'])
            for i, element in enumerate(next_elements):
                if i > 10:  # Batasi pencarian
                    break
                text = element.text.strip()
                if text and len(text) < 200:  # Bahan biasanya pendek
                    ingredients.append(text)
    
    # Jika masih belum menemukan bahan, cari paragraf yang mungkin berisi bahan
    if not ingredients:
        for p in soup.find_all('p'):
            text = p.text.strip().lower()
            if ('bahan:' in text or 'bahan-bahan:' in text) and len(text) < 500:
                # Pisahkan baris
                lines = text.split('\n')
                for line in lines:
                    if line.strip() and not line.lower().startswith('cara'):
                        ingredients.append(line.strip())
    
    recipe['ingredients'] = ingredients
    
    # Ekstrak cara memasak
    instructions = []
    instruction_patterns = [
        re.compile(r'cara', re.IGNORECASE),
        re.compile(r'langkah', re.IGNORECASE),
        re.compile(r'step', re.IGNORECASE),
        re.compile(r'instruction', re.IGNORECASE)
    ]
    
    # Cari heading yang mengandung kata "cara" atau "langkah"
    instruction_section = None
    for pattern in instruction_patterns:
        for heading in soup.find_all(['h2', 'h3', 'h4', 'strong']):
            if pattern.search(heading.text):
                instruction_section = heading
                break
        if instruction_section:
            break
    
    # Jika menemukan bagian cara memasak, cari list item setelahnya
    if instruction_section:
        # Cari list item terdekat
        ol_tag = instruction_section.find_next('ol')
        if ol_tag:
            for li in ol_tag.find_all('li'):
                instructions.append(li.text.strip())
        else:
            # Jika tidak ada list, coba cari paragraf
            next_elements = instruction_section.find_next_siblings(['p', 'div'])
            for i, element in enumerate(next_elements):
                if i > 15:  # Batasi pencarian
                    break
                text = element.text.strip()
                if text and len(text) > 10:  # Instruksi biasanya lebih panjang
                    instructions.append(text)
    
    # Jika masih belum menemukan cara memasak, cari paragraf yang mungkin berisi instruksi
    if not instructions:
        for p in soup.find_all('p'):
            text = p.text.strip().lower()
            if ('cara:' in text or 'langkah:' in text) and len(text) < 1000:
                # Pisahkan baris
                lines = text.split('\n')
                for line in lines:
                    if line.strip() and not line.lower().startswith('bahan'):
                        instructions.append(line.strip())
    
    recipe['instructions'] = instructions
    
    return recipe

def crawl_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"Crawling: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ekstrak judul dan URL
        title = soup.find('title').text if soup.find('title') else ''
        
        # Cari semua link yang mungkin mengarah ke halaman resep dengan pola yang lebih spesifik
        recipe_links = set()  # Gunakan set untuk menghindari duplikasi
        
        # Pola-pola link resep yang lebih spesifik
        recipe_patterns = [
            r'resep[-_/]',
            r'recipe[-_/]',
            r'masak[-_/]',
            r'kuliner[-_/]',
            r'food[-_/]',
            r'/\d+/', # URL dengan ID numerik
        ]
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.text.strip().lower()
            
            # Filter link yang kemungkinan mengarah ke resep
            is_recipe_link = False
            
            # Cek berdasarkan href
            for pattern in recipe_patterns:
                if re.search(pattern, href.lower()):
                    is_recipe_link = True
                    break
            
            # Cek berdasarkan teks link
            recipe_keywords = ['resep', 'masak', 'recipe', 'kuliner', 'makanan', 'menu']
            if any(keyword in link_text for keyword in recipe_keywords):
                is_recipe_link = True
            
            if is_recipe_link:
                # Pastikan ini adalah URL lengkap
                if href.startswith('http'):
                    recipe_links.add(href)
                elif href.startswith('/'):
                    # Relatif URL, tambahkan domain
                    from urllib.parse import urljoin
                    full_url = urljoin(url, href)
                    recipe_links.add(full_url)
        
        # Konversi set ke list dan batasi
        recipe_links = list(recipe_links)[:8]  # Ambil 8 link resep
        
        recipes = []
        for i, link in enumerate(recipe_links):
            try:
                print(f"  [{i+1}/{len(recipe_links)}] Crawling resep dari: {link}")
                recipe_response = requests.get(link, headers=headers, timeout=15)
                recipe_response.raise_for_status()
                
                recipe_soup = BeautifulSoup(recipe_response.text, 'html.parser')
                
                # Ekstrak informasi resep
                recipe = extract_recipe(recipe_soup)
                
                # Tambahkan informasi tambahan
                recipe['url'] = link
                recipe['source_title'] = title
                recipe['source_domain'] = url.split('/')[2] if '/' in url else url
                
                # Cari gambar-gambar makanan
                images = []
                for img in recipe_soup.find_all('img'):
                    if img.get('src'):
                        img_url = img.get('src')
                        if img_url.startswith('/'):
                            from urllib.parse import urljoin
                            img_url = urljoin(link, img_url)
                        elif not img_url.startswith('http'):
                            continue
                        
                        # Filter gambar yang kemungkinan makanan
                        img_keywords = ['food', 'resep', 'masak', 'menu', 'dish', 'cook']
                        img_alt = img.get('alt', '').lower()
                        img_src_lower = img_url.lower()
                        
                        if any(keyword in img_alt or keyword in img_src_lower for keyword in img_keywords):
                            images.append(img_url)
                
                recipe['images'] = images[:3]  # Ambil 3 gambar saja
                recipe['timestamp'] = time.time()
                
                # Hanya simpan resep yang memiliki nama, bahan, dan cara memasak
                if (recipe['name'] and len(recipe['name']) > 3 and 
                    recipe['ingredients'] and len(recipe['ingredients']) > 0 and 
                    recipe['instructions'] and len(recipe['instructions']) > 0):
                    
                    recipes.append(recipe)
                    # Simpan ke database
                    save_to_database(recipe)
                    print(f"    ✓ Berhasil: {recipe['name']}")
                else:
                    print(f"    ✗ Resep tidak lengkap: {recipe['name'] or 'Tanpa nama'}")
                
                time.sleep(2)  # Delay untuk menghindari overloading server
                
            except Exception as e:
                print(f"    ✗ Error crawling recipe {link}: {str(e)}")
        
        print(f"Berhasil crawl {len(recipes)} resep dari {url}")
        return recipes
    
    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")
        return []

def test_website_accessibility():
    """Tes aksesibilitas website untuk memilih yang terbaik"""
    print("Testing website accessibility...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    accessible_sites = []
    
    for site in sites:
        try:
            print(f"Testing: {site}")
            response = requests.get(site, headers=headers, timeout=10)
            if response.status_code == 200:
                # Cek apakah ada konten resep
                soup = BeautifulSoup(response.text, 'html.parser')
                recipe_indicators = ['resep', 'recipe', 'bahan', 'ingredient', 'cara', 'langkah']
                
                page_text = soup.get_text().lower()
                recipe_score = sum(1 for indicator in recipe_indicators if indicator in page_text)
                
                if recipe_score >= 3:  # Minimal ada 3 indikator resep
                    accessible_sites.append({
                        'url': site,
                        'score': recipe_score,
                        'response_time': response.elapsed.total_seconds()
                    })
                    print(f"  ✓ Accessible (score: {recipe_score})")
                else:
                    print(f"  ✗ Low recipe content (score: {recipe_score})")
            else:
                print(f"  ✗ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
    
    # Sort berdasarkan skor dan response time
    accessible_sites.sort(key=lambda x: (x['score'], -x['response_time']), reverse=True)
    
    print(f"\nFound {len(accessible_sites)} accessible sites:")
    for site in accessible_sites[:10]:  # Tampilkan 10 terbaik
        print(f"  {site['url']} (score: {site['score']}, time: {site['response_time']:.2f}s)")
    
    return [site['url'] for site in accessible_sites]

def get_best_recipe_sites():
    """Dapatkan list website resep terbaik yang mudah diakses"""
    return [
        'https://cookpad.com/id',
        'https://resepkoki.id',
        'https://www.masakapahariini.com',
        'https://www.briliofood.net',
        'https://yummy.co.id',
        'https://endeus.tv',
        'https://food.detik.com',
        'https://www.fimela.com/food',
        'https://lifestyle.okezone.com/food-travel',
        'https://sajianredaksi.com'
    ]

def start_crawling():
    print("=== KULINER SEARCH ENGINE CRAWLER ===")
    print("Memulai crawling resep makanan Indonesia...\n")
    
    # Test aksesibilitas website
    accessible_sites = test_website_accessibility()
    
    if not accessible_sites:
        print("Tidak ada website yang dapat diakses. Menggunakan backup sites...")
        accessible_sites = get_best_recipe_sites()
    
    # Gunakan hanya website yang dapat diakses
    global sites
    sites = accessible_sites[:10]  # Ambil 10 terbaik
    
    print(f"\nMulai crawling dari {len(sites)} website...")
    
    all_recipes = []
    for i, site in enumerate(sites):
        print(f"\n[{i+1}/{len(sites)}] Processing: {site}")
        recipes = crawl_website(site)
        if recipes:
            all_recipes.extend(recipes)
        time.sleep(3)  # Delay untuk menghindari overloading server
    
    print(f"\n=== CRAWLING SELESAI ===")
    print(f"Total {len(all_recipes)} resep berhasil di-crawl dari {len(sites)} website.")
    
    # Simpan summary
    summary = {
        'total_recipes': len(all_recipes),
        'websites_crawled': len(sites),
        'timestamp': time.time(),
        'successful_sites': [site for site in sites if any(r['url'].startswith(site) for r in all_recipes)]
    }
    
    with open('crawl_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return all_recipes

if __name__ == "__main__":
    start_crawling()