#!/usr/bin/env python3
"""
Script untuk menjalankan crawler dengan link resep terbaik
"""

import os
import sys
import time
from datetime import datetime

# Tambah path untuk import module lokal
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import start_crawling, test_website_accessibility, get_best_recipe_sites

def main():
    print("=" * 60)
    print("🍽️  KULINER SEARCH ENGINE CRAWLER")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Jalankan crawler
        start_crawling()
        
        print("\n" + "=" * 60)
        print("✅ Crawling completed successfully!")
        print("📊 Check kuliner_data.json for crawled recipes")
        print("📋 Check crawl_summary.json for crawling statistics")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Crawling interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during crawling: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
