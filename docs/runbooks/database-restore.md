# Point-in-Time Database Restore Procedure

## Context
In the event of accidental data deletion (e.g., dropped tables) or severe corruption, we must restore the PostgreSQL database using Write-Ahead Logs (WAL) and base backups (via `pgBackRest` or `wal-g`).

## Procedure

### 1. Halt Application Traffic
Prevent further writes and inconsistent states.
```bash
# Scale down backend services
docker-compose stop backend
```

### 2. Identify Target Restoration Point
Determine the exact timestamp (UTC) or Transaction ID (XID) just before the corruption occurred.

### 3. Restore the Database
Assuming `pgBackRest` is configured:
1. Stop the PostgreSQL service.
2. Run the restore command specifying the target time:
   ```bash
   pgbackrest --stanza=talentdb --type=time --target="2026-09-29 12:00:00+00" restore
   ```
3. Start the PostgreSQL service. The server will enter recovery mode, replay the WAL up to the specified target, and then promote itself.

### 4. Verification
1. Connect via `psql` and verify data integrity (e.g., check resume tables, pgvector indices).
2. Run sanity queries on candidate matches.

### 5. Resume Operations
Once verified, restart the backend and frontend services.
```bash
docker-compose start backend
```
