import sqlite3

def check_table_structure():
    """Kiểm tra cấu trúc các bảng"""
    conn = sqlite3.connect('movielens.db')
    cursor = conn.cursor()
    
    tables = ['movies', 'ratings', 'tags', 'links']
    
    for table in tables:
        print(f"{table.upper()} table structure:")
        cursor.execute(f'PRAGMA table_info({table})')
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_table_structure() 