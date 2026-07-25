import os
import sys
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from pathlib import Path

# Add the project root to sys.path to allow importing from src
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

DATABASE_URL = os.environ.get("DATABASE_URL")
SAMPLE_DIR = root_dir / "src" / "backtester" / "data" / "sample"

def seed_db():
    if not DATABASE_URL:
        print("DATABASE_URL not set. Skipping seed.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        with conn.cursor() as cur:
            # Create the schema
            with open(Path(__file__).parent / "schema.sql", "r") as f:
                cur.execute(f.read())
            
            print("Schema created/verified.")
            
            # Load samples
            if not SAMPLE_DIR.exists():
                print(f"Sample directory not found: {SAMPLE_DIR}")
                return
                
            for csv_file in SAMPLE_DIR.glob("*.csv"):
                ticker = csv_file.stem.upper()
                print(f"Loading {ticker}...")
                
                df = pd.read_csv(csv_file)
                # Ensure correct columns
                records = []
                for _, row in df.iterrows():
                    # Parse date from string or assume ISO
                    records.append((
                        ticker,
                        row['Date'],
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        row['Volume'],
                        'sample'
                    ))
                    
                query = """
                    INSERT INTO price_cache (ticker, date, open, high, low, close, volume, source)
                    VALUES %s
                    ON CONFLICT (ticker, date) DO NOTHING
                """
                execute_values(cur, query, records)
                
            conn.commit()
            print("Seed complete.")
            
    except Exception as e:
        print(f"Error seeding DB: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_db()
