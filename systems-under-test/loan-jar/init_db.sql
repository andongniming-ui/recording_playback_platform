CREATE DATABASE IF NOT EXISTS loan_jar DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE loan_jar;

CREATE TABLE IF NOT EXISTS cust_info (
  id BIGINT NOT NULL AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  gender VARCHAR(16) NOT NULL,
  birth DATE NOT NULL,
  age INT NOT NULL,
  idcard VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  cretime DATE DEFAULT NULL,
  modtime DATE DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_cust_info_idcard (idcard)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO cust_info (name, gender, birth, age, idcard, status, cretime, modtime)
VALUES
  ('Alice Zhang', 'F', '1990-01-01', 36, '110101199001011234', 'NORMAL', CURRENT_DATE, CURRENT_DATE),
  ('Bob Li', 'M', '1988-05-20', 37, '310101198805201111', 'NORMAL', CURRENT_DATE, CURRENT_DATE),
  ('Carol Wang', 'F', '1995-09-09', 30, '440101199509092222', 'FROZEN', CURRENT_DATE, CURRENT_DATE)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  gender = VALUES(gender),
  birth = VALUES(birth),
  age = VALUES(age),
  status = VALUES(status),
  modtime = CURRENT_DATE;
