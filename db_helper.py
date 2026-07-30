# db_helper.py
import pymysql

DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="1234",
    database="chipmunkdb",
    charset="utf8"
)

class DB:
    def __init__(self, **config):
        self.config = config

    def connect(self):
        return pymysql.connect(**self.config)

    # 상품 전체 조회
    def fetch_items(self):
        sql = "SELECT id, name, price, stock FROM items ORDER BY id"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()  # [(id, name, price, stock), ...]

    # 상품 추가
    def insert_item(self, name, price, stock):
        sql = "INSERT INTO items (name, price, stock) VALUES (%s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (name, price, stock))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False