CREATE DATABASE IF NOT EXISTS chipmunkdb DEFAULT CHARACTER SET utf8mb4;

USE chipmunkdb;

CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at DATETIME
);

-- username key가 중복일 경우 에러 대신 업데이트를 실행합니다.
INSERT INTO users (username, password)
VALUES ('admin', 'admin123'), ('manager', 'manager123')
ON DUPLICATE KEY UPDATE password=VALUES(password);

-- 화면 표시/추가용 데이터 테이블(상품 목록)
CREATE TABLE IF NOT EXISTS items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  price INT NOT NULL,
  stock INT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at DATETIME,
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO items (name, price, stock, user_id)
VALUES ('견과류', 3000, 100, 1), ('삼각김밥', 1700, 10, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);