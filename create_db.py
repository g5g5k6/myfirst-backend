import psycopg2
import os

DB_CONFIG = {
    "dbname": os.getenv("DB_dbname"),  
    "user": os.getenv("DB_user"),  
    "password": os.getenv("DB_password"),  
    "host": os.getenv("DB_host"),  
    "port": os.getenv("DB_port") 
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