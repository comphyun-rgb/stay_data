import pandas as pd
from pathlib import Path

class OTAManualImporter:
    """
    OTA(Agoda, Booking, Airbnb 등)에서 수동으로 추출한 CSV 데이터를 임포트합니다.
    """
    
    def import_csv(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}")
            return None
            
        try:
            df = pd.read_csv(file_path)
            print(f"Successfully loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return None

    def validate_ota_df(self, df):
        """
        필수 컬럼 존재 여부 확인
        """
        required_cols = ['ota_source', 'raw_name', 'price_per_night_krw', 'collected_at']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"Warning: Missing required columns: {missing}")
            return False
        return True
