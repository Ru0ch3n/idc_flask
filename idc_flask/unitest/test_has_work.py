import sqlite3

conn = sqlite3.connect('../db/idc_sqlite.db', check_same_thread=False)
cursor = conn.cursor()


def has_worker(phone):
    cursor.execute("SELECT * FROM worker_info WHERE phone_num=?", (phone,))
    ls = []
    for row in cursor:
        ls.append(row)
    return len(ls) > 0


print(has_worker('15529490982'))
