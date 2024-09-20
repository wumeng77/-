import sqlite3
def create_tables():
    try:
        conn = sqlite3.connect('hosts.db')
        cur = conn.cursor()
        sql_create_table='''CREATE TABLE IF NOT EXISTS hosts (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                IPADDR TEXT NOT NULL UNIQUE,
                                USERNAME TEXT NOT NULL,
                                PASSWORD TEXT NOT NULL)'''
        cur.execute(sql_create_table)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False

def insert_host(info):
    if create_tables():
        conn = sqlite3.connect('hosts.db')
        cur = conn.cursor()
    else:return False

    try:
        sql_insert='''INSERT OR IGNORE INTO hosts (IPADDR,USERNAME,PASSWORD) VALUES (?,?,?)'''
        cur.execute(sql_insert,info)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_hosts():
    conn = sqlite3.connect('hosts.db')  # 替换为你实际的数据库文件
    cur = conn.cursor()
    cur.execute("SELECT IPADDR, USERNAME FROM hosts")  # 假设数据库中有 IP 和用户名
    hosts = cur.fetchall()
    conn.close()
    return hosts








