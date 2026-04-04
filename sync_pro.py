import os
import sqlalchemy as sa
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from pathlib import Path
import json
from decimal import Decimal
from datetime import datetime

load_dotenv()

# Cấu hình các bảng chính của dự án
TABLES_TO_SYNC = [
    'entries_marisinput',
]

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / 'db.sqlite3'

pg_url = URL.create(
    drivername="postgresql",
    username="postgres",
    password=os.getenv('DB_PASSWORD'),
    host="maglev.proxy.rlwy.net",
    port=45153,
    database="railway"
)


def format_value(v):
    """Xử lý các kiểu dữ liệu Postgres mà SQLite không hiểu"""
    if isinstance(v, (dict, list)): return json.dumps(v)
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, datetime): return v.isoformat()
    return v


def run_sync_pro():
    pg_engine = sa.create_engine(pg_url)
    sl_engine = sa.create_engine(f"sqlite:///{SQLITE_PATH}")
    metadata = sa.MetaData()

    print(f"🚀 Đang kéo dữ liệu từ Railway về Local...")

    try:
        metadata.reflect(bind=pg_engine, only=TABLES_TO_SYNC)
        metadata.create_all(bind=sl_engine)

        with pg_engine.connect() as pg_conn, sl_engine.connect() as sl_conn:
            # Tắt check khóa ngoại để sync mượt mà
            sl_conn.execute(sa.text("PRAGMA foreign_keys = OFF;"))

            for table_name in TABLES_TO_SYNC:
                table = metadata.tables[table_name]
                result = pg_conn.execute(table.select()).fetchall()

                if result:
                    # Chuẩn bị dữ liệu sạch
                    clean_data = [
                        {k: format_value(v) for k, v in row._mapping.items()}
                        for row in result
                    ]

                    # Dùng Bulk Insert (INSERT OR REPLACE) để đạt tốc độ tối đa
                    cols = ", ".join(clean_data[0].keys())
                    placeholders = ", ".join([f":{k}" for k in clean_data[0].keys()])
                    stmt = sa.text(f"INSERT OR REPLACE INTO {table_name} ({cols}) VALUES ({placeholders})")

                    sl_conn.execute(stmt, clean_data)
                    sl_conn.commit()
                    print(f" ✅ Đã xong bảng: {table_name} ({len(clean_data)} dòng)")

            sl_conn.execute(sa.text("PRAGMA foreign_keys = ON;"))

        print("\n✨ Hoàn tất! Dữ liệu local đã sẵn sàng để Debug.")

    except Exception as e:
        print(f"\n❌ Lỗi hệ thống: {e}")
    finally:
        pg_engine.dispose()
        sl_engine.dispose()


if __name__ == "__main__":
    run_sync_pro()
