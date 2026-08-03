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

    # 삭제되지 않은 상품 전체 조회
    def fetch_items(self):
        sql = "SELECT id, name, price, stock FROM items WHERE deleted_at IS NULL ORDER BY id"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()  # [(id, name, price, stock), ...]

    # 휴지통 상품 전체 조회
    def fetch_deleted_items(self):
        sql = "SELECT id, name, price, stock, deleted_at FROM items WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC, id DESC"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

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

    # 상품 수정
    def update_item(self, item_id, name, price, stock):
        sql = "UPDATE items SET name = %s, price = %s, stock = %s WHERE id = %s AND deleted_at IS NULL"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (name, price, stock, item_id))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 선택한 상품을 휴지통으로 이동
    def soft_delete_items(self, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"UPDATE items SET deleted_at = NOW() WHERE id IN ({placeholders}) AND deleted_at IS NULL"
        return self._execute_item_ids(sql, item_ids)

    # 휴지통에서 선택한 상품 복원
    def restore_items(self, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"UPDATE items SET deleted_at = NULL WHERE id IN ({placeholders}) AND deleted_at IS NOT NULL"
        return self._execute_item_ids(sql, item_ids)

    # 휴지통에서 선택한 상품 영구 삭제
    def permanently_delete_items(self, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"DELETE FROM items WHERE id IN ({placeholders}) AND deleted_at IS NOT NULL"
        return self._execute_item_ids(sql, item_ids)

    def _execute_item_ids(self, sql, item_ids):
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(item_ids))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False