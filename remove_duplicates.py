import json
import os

# Path ke file data
DATA_FILE = 'd:\\TKI UAS\\Kuliner-Search-Engine\\kuliner_data.json'

def remove_duplicates():
    """Menghapus entri duplikat dari file JSON"""
    try:
        # Baca data yang sudah ada
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Jumlah data sebelum penghapusan duplikat: {len(data)}")
            
            # Gunakan dictionary untuk melacak entri unik berdasarkan URL
            unique_entries = {}
            for entry in data:
                # Gunakan URL sebagai kunci unik
                key = entry.get('url', '')
                if key and key not in unique_entries:
                    unique_entries[key] = entry
            
            # Konversi kembali ke list
            unique_data = list(unique_entries.values())
            
            print(f"Jumlah data setelah penghapusan duplikat: {len(unique_data)}")
            print(f"Jumlah duplikat yang dihapus: {len(data) - len(unique_data)}")
            
            # Simpan kembali ke file
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(unique_data, f, ensure_ascii=False, indent=4)
            
            return True
        else:
            print(f"File {DATA_FILE} tidak ditemukan")
            return False
    except Exception as e:
        print(f"Error saat menghapus duplikat: {str(e)}")
        return False

if __name__ == "__main__":
    remove_duplicates()