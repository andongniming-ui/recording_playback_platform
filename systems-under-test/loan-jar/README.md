# loan-jar

This directory wraps the external `loan.jar` as a runnable system-under-test for the recording playback platform.

## What It Is

- Spring Boot application: `pers.marco.LoanApplication`
- Default HTTP port: `4623`
- Main API: `/loan/query`
- Supported transaction code: `RP54KH01`
- Request parameters: `code`, `idcard`
- Database table: `cust_info`

Example request:

```bash
curl 'http://127.0.0.1:4623/loan/query?code=RP54KH01&idcard=110101199001011234'
```

## Initialize Database

The original jar does not include schema or seed data. Initialize the local MySQL used by this project:

```bash
mysql -h127.0.0.1 -P3307 -uroot -proot123 < init_db.sql
```

## Start

Start with AREX agent, after confirming `AREX_AGENT_JAR_PATH` points to a valid agent jar:

```bash
./start.sh
```

For local smoke testing without AREX agent:

```bash
LOAN_ENABLE_AREX=0 ./start.sh
```

Useful overrides:

```bash
LOAN_SERVER_PORT=4623
LOAN_DB_HOST=127.0.0.1
LOAN_DB_PORT=3307
LOAN_DB_NAME=loan_jar
LOAN_DB_USERNAME=root
LOAN_DB_PASSWORD=root123
AREX_SERVICE_NAME=loan-jar
AREX_STORAGE_URL=127.0.0.1:8000
AREX_AGENT_JAR_PATH=/path/to/arex-agent.jar
```

## Send Samples

```bash
./send_samples.sh
```

Or send one specific id card:

```bash
./send_samples.sh 110101199001011234
```

The script sleeps 2 seconds between requests by default to give the AREX agent enough time to flush each request reliably. Override it when needed:

```bash
LOAN_SAMPLE_INTERVAL=5 ./send_samples.sh
LOAN_SAMPLE_INTERVAL=0 ./send_samples.sh
```

## Platform Application

Register an application in the platform with:

- Name: `loan-jar`
- Service port: `4623`
- AREX app id: `loan-jar`

The jar mainly performs an HTTP entry request and a MySQL query. HTTP sub-calls are not expected unless the jar is changed to call another HTTP service.
