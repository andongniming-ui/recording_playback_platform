#!/usr/bin/env bash
set -euo pipefail

database="${MYSQL_DATABASE:-arex_recorder}"
user="${MYSQL_USER:-arex}"
password="${MYSQL_PASSWORD:?MYSQL_PASSWORD is required}"

mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" <<SQL
CREATE DATABASE IF NOT EXISTS \`${database}\`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${user}'@'%' IDENTIFIED BY '${password}';
GRANT ALL PRIVILEGES ON \`${database}\`.* TO '${user}'@'%';
FLUSH PRIVILEGES;
SQL
