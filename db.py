import psycopg2
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# PostgreSQL 資料庫連接
DB_CONFIG = {
    "dbname": os.getenv("DB_dbname"),  
    "user": os.getenv("DB_user"),  
    "password": os.getenv("DB_password"),  
    "host": os.getenv("DB_host"),  
    "port": os.getenv("DB_port") 
}

def get_connection():
    """建立與 PostgreSQL 的連線"""
    return psycopg2.connect(**DB_CONFIG)

# def add_word_group(words):
    # """ 新增單字組 """
    # conn = get_connection()  # 連線
    # cursor = conn.cursor()  # 查詢 cursor
# 
    # created_at = datetime.now().isoformat()
    # next_review_at = created_at  # 創建時立即可複習
# 
    # cursor.execute("INSERT INTO word_groups (words, created_at, next_review_at) VALUES (%s, %s, %s)", 
                #    (",".join(words), created_at, next_review_at))
# 
    # conn.commit()
    # conn.close()

def get_due_groups():
    #auto select group
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    #select group
    cursor.execute("SELECT id, next_review_at, stage FROM word_groups WHERE next_review_at <= %s AND stage != 4", (now,))
    groups = cursor.fetchall()
    print(groups)
    result = []
    #[(id,next_time,stage)]
    for group_id, next_review_at, stage in groups:
        cursor.execute("SELECT word, definition, example FROM word_items WHERE group_id = %s", (group_id,))
        #id 
        words = cursor.fetchall()
        result.append({
            "id": group_id,
            "next_review_at": next_review_at,
            "stage": stage,
            "words": [{"word": w, "definition": d, "example": e} for w, d, e in words]
        })
    #result id reviewtime stage word 
    conn.close()
    return result

def check_review():
    """檢查所有 word_groups 是否需要複習並進入下一階段"""
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    # 查詢所有 'next_review_at' 小於當前時間的 word_groups
    cursor.execute("SELECT id, next_review_at, stage FROM word_groups WHERE next_review_at <= %s", (now,))
    groups = cursor.fetchall()

    for group_id, next_review_at, stage in groups:
        # 根據 stage 進行階段更新 (例如將 stage + 1)
        new_stage = stage - 1
        if new_stage<0:
            new_stage=0
        cursor.execute("UPDATE word_groups SET stage = %s WHERE id = %s", (new_stage, group_id))
    conn.commit()
    cursor.close()
    conn.close()

def review_word_group(group_id):
    #手動更新
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, next_review_at, stage FROM word_groups WHERE id = %s", (group_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return "單字組不存在"

    group_id, next_review_at, stage = row
    now = datetime.now()
    next_review_time = datetime.fromisoformat(next_review_at)

    margin = timedelta(minutes=30)  # +-容錯

    if next_review_time - margin <= now <= next_review_time + margin:
        intervals = [timedelta(minutes=30), timedelta(hours=12), timedelta(days=1), timedelta(days=3)]        
        #stage start -1?
        next_review_time = now + intervals[stage]
        stage=stage+1
        cursor.execute("UPDATE word_groups SET next_review_at = %s, stage = stage + 1 WHERE id = %s", 
            (next_review_time.isoformat(), group_id))
        conn.commit()
        result = f"下一次時間：{next_review_time}"
    else:
        result = "未在允許時間內複習"

    conn.close()
    return result

def create_word_group():
    """從 word_items 取 10 未有 group_id 創建新的 word_group"""
    conn = get_connection()
    cursor = conn.cursor()

    # 選擇最多 10 個單字
    cursor.execute("SELECT id, word, definition, example FROM word_items WHERE group_id IS NULL LIMIT 10")
    words_to_add = cursor.fetchall()

    if not words_to_add:
        conn.close()
        return "沒有未分配 group_id "

    # 單字建立新 word_group
    now = datetime.now().isoformat()
    next_review_time=(datetime.now()+timedelta(minutes=30))
    cursor.execute("INSERT INTO word_groups (created_at, next_review_at, stage) VALUES (%s, %s, %s) RETURNING id", 
                   (now, next_review_time, 0))  # 初始狀態為 0，第一次複習時間是現在
    group_id = cursor.fetchone()[0]

    # 更新 word_items 表中 group_id
    for word_id, word, definition, example in words_to_add:
        cursor.execute("UPDATE word_items SET group_id = %s WHERE id = %s", (group_id, word_id))

    conn.commit()
    cursor.close()
    conn.close()

    return f"成功創建新單字組並分配給 {len(words_to_add)} 個單字，新的 group_id: {group_id}"


