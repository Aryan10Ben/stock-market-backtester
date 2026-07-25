import os
import logging
from datetime import date

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger("api.db")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL)

def get_price_data(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    """Fetch price data from Neon DB price_cache."""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT date as "Date", open as "Open", high as "High", low as "Low", 
               close as "Close", volume as "Volume"
        FROM price_cache
        WHERE ticker = %s AND date >= %s AND date <= %s
        ORDER BY date ASC
    """
    try:
        df = pd.read_sql_query(query, conn, params=(ticker, start_date, end_date), index_col="Date")
        if not df.empty:
            df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        logger.error(f"Error reading from DB cache: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def save_price_data(ticker: str, df: pd.DataFrame, source: str):
    """Save newly fetched price data to Neon DB price_cache."""
    conn = get_connection()
    if not conn:
        return

    # Prepare records for insertion
    df_reset = df.reset_index()
    records = []
    for _, row in df_reset.iterrows():
        records.append((
            ticker,
            row['Date'].date(),
            row['Open'],
            row['High'],
            row['Low'],
            row['Close'],
            row['Volume'],
            source
        ))

    query = """
        INSERT INTO price_cache (ticker, date, open, high, low, close, volume, source)
        VALUES %s
        ON CONFLICT (ticker, date) DO NOTHING
    """

    try:
        with conn.cursor() as cur:
            execute_values(cur, query, records)
        conn.commit()
    except Exception as e:
        logger.error(f"Error writing to DB cache: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_run_to_db(req_dict: dict, metrics: dict):
    conn = get_connection()
    if not conn:
        return

    query = """
        INSERT INTO backtest_runs (ticker, start_date, end_date, params, metrics)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    import json
    try:
        with conn.cursor() as cur:
            cur.execute(query, (
                req_dict["ticker"],
                req_dict["start_date"],
                req_dict["end_date"],
                json.dumps(req_dict),
                json.dumps(metrics)
            ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving run to DB: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_history_runs() -> list:
    conn = get_connection()
    if not conn:
        return []
    
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM backtest_runs ORDER BY created_at DESC LIMIT 50")
            rows = cur.fetchall()
            for r in rows:
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                if r.get("start_date"):
                    r["start_date"] = r["start_date"].isoformat()
                if r.get("end_date"):
                    r["end_date"] = r["end_date"].isoformat()
            return rows
    except Exception as e:
        logger.error(f"DB Error fetching history: {e}")
        return []
    finally:
        if conn:
            conn.close()
