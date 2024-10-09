import sqlite3
import os
#
# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'hosts.db')

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables():
    """创建 hosts 表（如果不存在）"""
    create_table_sql = '''CREATE TABLE IF NOT EXISTS hosts (
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            IPADDR TEXT NOT NULL UNIQUE,
                            USERNAME TEXT NOT NULL,
                            PASSWORD TEXT NOT NULL)'''
    try:
        with get_db_connection() as conn:
            if conn is not None:
                cur = conn.cursor()
                cur.execute(create_table_sql)
                conn.commit()
                print("Table created or already exists.")
                return True
            else:
                print("Failed to create table: no connection.")
                return False
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False

def insert_host(info):
    """插入主机信息，info 应为 (IPADDR, USERNAME, PASSWORD)"""
    if create_tables():
        insert_sql = '''INSERT OR IGNORE INTO hosts (IPADDR, USERNAME, PASSWORD) VALUES (?, ?, ?)'''
        try:
            with get_db_connection() as conn:
                if conn is not None:
                    cur = conn.cursor()
                    cur.execute(insert_sql, info)
                    conn.commit()
                    print("Host inserted successfully.")
                    return True
                else:
                    print("Failed to insert host: no connection.")
                    return False
        except sqlite3.Error as e:
            print(f"Error inserting host: {e}")
            return False
    else:
        return False

def get_hosts():
    """获取所有主机的 IP 和用户名"""
    select_sql = "SELECT IPADDR, USERNAME FROM hosts"
    try:
        with get_db_connection() as conn:
            if conn is not None:
                cur = conn.cursor()
                cur.execute(select_sql)
                hosts = cur.fetchall()
                return hosts
            else:
                print("Failed to fetch hosts: no connection.")
                return []
    except sqlite3.Error as e:
        print(f"Error fetching hosts: {e}")
        return []
