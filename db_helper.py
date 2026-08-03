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

    # 로그인 검증
    def verify_user(self, username, password):
        sql = "SELECT id FROM users WHERE username = %s AND password = %s AND deleted_at IS NULL"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (username, password))
                row = cur.fetchone()
                return row[0] if row else None

    # 삭제되지 않은 상품 전체 조회
    def fetch_items(self, user_id):
        sql = "SELECT id, name, price, stock FROM items WHERE user_id = %s AND deleted_at IS NULL ORDER BY id"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id,))
                return cur.fetchall()  # [(id, name, price, stock), ...]

    # 휴지통 상품 전체 조회
    def fetch_deleted_items(self, user_id):
        sql = "SELECT id, name, price, stock, deleted_at FROM items WHERE user_id = %s AND deleted_at IS NOT NULL ORDER BY deleted_at DESC, id DESC"
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id,))
                return cur.fetchall()

    # 상품 추가
    def insert_item(self, user_id, name, price, stock):
        sql = "INSERT INTO items (name, price, stock, user_id) VALUES (%s, %s, %s, %s)"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (name, price, stock, user_id))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 상품 수정
    def update_item(self, user_id, item_id, name, price, stock):
        sql = "UPDATE items SET name = %s, price = %s, stock = %s WHERE user_id = %s AND id = %s AND deleted_at IS NULL"
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (name, price, stock, user_id, item_id))
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False

    # 선택한 상품을 휴지통으로 이동
    def soft_delete_items(self, user_id, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"UPDATE items SET deleted_at = NOW() WHERE user_id = %s AND id IN ({placeholders}) AND deleted_at IS NULL"
        params = (user_id, *item_ids)
        return self._execute_item_ids(sql, params)

    # 휴지통에서 선택한 상품 복원
    def restore_items(self, user_id, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"UPDATE items SET deleted_at = NULL WHERE user_id = %s AND id IN ({placeholders}) AND deleted_at IS NOT NULL"
        params = (user_id, *item_ids)
        return self._execute_item_ids(sql, params)

    # 휴지통에서 선택한 상품 영구 삭제
    def permanently_delete_items(self, user_id, item_ids):
        if not item_ids:
            return False

        placeholders = ", ".join(["%s"] * len(item_ids))
        sql = f"DELETE FROM items WHERE user_id = %s AND id IN ({placeholders}) AND deleted_at IS NOT NULL"
        params = (user_id, *item_ids)
        return self._execute_item_ids(sql, params)

    def _execute_item_ids(self, sql, params):
        with self.connect() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                conn.commit()
                return True
            except Exception:
                conn.rollback()
                return False