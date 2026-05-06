# MySQL Initialization and Migration

## Initialization

For a new intranet environment, let the MySQL container mount `mysql/initdb` through `docker-compose.intranet.yml`. The init script reads `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_ROOT_PASSWORD` from `.env.production`.

Script:

```text
mysql/initdb/00-create-platform-database.sh
```

If you use an existing external MySQL instance instead of the Compose `db` service, create the database and user manually with equivalent SQL before starting the backend.

## Schema Creation and Migration

The backend currently creates missing tables and applies additive column migrations during startup:

1. `database.init_db()` creates missing tables from SQLAlchemy models.
2. `main._migrate_db()` applies versioned additive migrations from `platform/backend/migrations.py` and records them in `schema_migration`.
3. `main._verify_db_schema()` fails startup if required tables or columns are missing.

This means the production deployment flow is:

1. Create database and user.
2. Configure `AR_DB_TYPE=mysql`.
3. Configure `AR_DB_URL=mysql+aiomysql://arex:<password>@db:3306/arex_recorder`.
4. Start backend once and check logs for migration errors.
5. Back up MySQL before every future application upgrade.

## Manual Health Checks

```bash
mysql -h127.0.0.1 -P3307 -uarex -p arex_recorder -e "SHOW TABLES;"
curl http://127.0.0.1:8000/api/health
```
