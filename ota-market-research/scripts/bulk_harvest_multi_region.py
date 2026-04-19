import sys
import os

# Add the root directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.collectors.agoda import AgodaCollector
from app.collectors.booking import BookingCollector

def run_multi_region_harvest():
    regions = [
        {"name": "Hongdae", "keywords": ["Hongdae", "Yeonnam"]},
        {"name": "Myeongdong", "keywords": ["Myeongdong", "Jung-gu"]},
        {"name": "Jongno", "keywords": ["Jongno", "Ikseon-dong"]},
        {"name": "Sinchon", "keywords": ["Sinchon", "Ewha"]}
    ]
    
    collectors = [AgodaCollector(), BookingCollector()]
    
    print("=== [Track B] Multi-Region Harvest Start ===")
    
    for region in regions:
        print(f"\n> Region: {region['name']}")
        for kw in region['keywords']:
            for collector in collectors:
                try:
                    # Harvest 2 pages for each keyword/collector
                    count = collector.collect_by_area(
                        area_name=region['name'], 
                        keyword=kw, 
                        pages=2
                    )
                    print(f"  - {collector.source_name} ({kw}): {count} items collected.")
                except Exception as e:
                    print(f"  - Error in {collector.source_name} for {kw}: {e}")

    print("\n=== Harvest Task Completed ===")

if __name__ == "__main__":
    run_multi_region_harvest()
