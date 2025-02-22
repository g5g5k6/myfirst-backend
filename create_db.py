import psycopg2

DB_CONFIG = {
    "dbname": "vocab",  # 資料庫名稱
    "user": "postgres",  # 用戶名稱
    "password": "12345",  # 密碼
    "host": "localhost",  # 資料庫主機
    "port": 5432  # PostgreSQL 端口
}

def create_db():
    """建立資料庫並創建 word_groups 表格"""
    print("連接...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 創建 word_groups 
    cursor.execute("""
    CREATE TABLE word_groups (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP,
        next_review_at TIMESTAMP,
        stage INTEGER
    )
    """)

    # 創建 word_items 
    cursor.execute("""
    CREATE TABLE word_items (
        id SERIAL PRIMARY KEY,
        group_id INTEGER REFERENCES word_groups(id) ON DELETE CASCADE,
        word TEXT NOT NULL,
        definition TEXT,
        example TEXT
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("新表格成功")

if __name__ == "__main__":
    create_db()