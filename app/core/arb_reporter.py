
import sqlite3
import os
from datetime import datetime
from app.core.db import get_db_connection, OUTPUT_DIR
from config.settings import STRATEGY_CONFIG

def fetch_daily_data(table_name, date_str, columns="*"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {columns} FROM {table_name} WHERE date = ?", (date_str,))
        rows = cursor.fetchall()
        # Get column names
        col_names = [description[0] for description in cursor.description]
        return rows, col_names
    except sqlite3.Error as e:
        print(f"Error reading {table_name}: {e}")
        return [], []
    finally:
        conn.close()

def format_liq(val):
    """Formats liquidity value (assumes units are in 'Wan')."""
    if val >= 10000:
        return f"{val/10000:.2f}Y" # 亿 (100 Million)
    return f"{val:.1f}W" # 万 (10 Thousand)

def format_table(rows, headers, alignments=None):
    if not rows:
        return "*No data available for today.*"
        
    header_line = "| " + " | ".join(headers) + " |"
    
    align_map = {'left': ':---', 'right': '---:', 'center': ':---:'}
    if not alignments:
        alignments = ['left'] * len(headers)
    
    separator_line = "| " + " | ".join([align_map.get(a, ':---') for a in alignments]) + " |"
    
    body = ""
    for row in rows:
        row_str = [str(x).replace('|', '\\|') for x in row]
        body += "| " + " | ".join(row_str) + " |\n"
        
    return f"{header_line}\n{separator_line}\n{body}"
