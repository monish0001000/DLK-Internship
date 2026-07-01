import sqlite3
import time

conn = sqlite3.connect('sentinelx.db')
for _ in range(30):
    alerts = conn.execute('SELECT title FROM alerts').fetchall()
    if alerts:
        print(f"ALERTS FOUND: {alerts}")
        break
    time.sleep(2)
else:
    print("NO ALERTS FOUND AFTER 60 SECONDS")
