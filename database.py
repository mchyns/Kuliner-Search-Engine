import json
import os

# File untuk menyimpan data kuliner
DATA_FILE = 'kuliner_data.json'

def save_to_database(kuliner_data):
    """Simpan data kuliner ke database (file JSON)"""
    try:
        # Baca data yang sudah ada
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Tambahkan data baru
        data.append(kuliner_data)
        
        # Simpan kembali ke file
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        return False

def get_all_kuliner():
    """Ambil semua data kuliner dari database"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error reading from database: {str(e)}")
        return []