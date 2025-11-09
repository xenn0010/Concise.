# Database Strategy

Production-grade database management, migrations, and backup strategy for Concise SDK.

## Overview

The Concise SDK uses:
- **PostgreSQL 16**: Primary database for persistent storage
- **Redis 7**: High-speed cache for compression results and rate limiting
- **Alembic**: Database migration management

---

## Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### api_keys
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 60,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    INDEX idx_key (key),
    INDEX idx_user_id (user_id)
);
```

#### usage_records
```sql
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    original_tokens INTEGER NOT NULL,
    compressed_tokens INTEGER NOT NULL,
    tokens_saved INTEGER NOT NULL,
    compression_ratio FLOAT NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    compression_time_ms FLOAT NOT NULL,
    request_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_strategy (strategy)
);
```

---

## Migrations

### Setup Alembic

Alembic is already configured in the project.

```bash
cd backend
alembic init alembic  # Already done
```

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for custom changes
alembic revision -m "Description"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Show current version
alembic current

# Show migration history
alembic history
```

### Example Migration

```python
"""Add indexes for performance

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Add index for faster queries
    op.create_index(
        'idx_usage_records_created_at',
        'usage_records',
        ['created_at'],
        postgresql_using='btree'
    )

def downgrade():
    op.drop_index('idx_usage_records_created_at')
```

---

## Backup Strategy

### Automated Backups

#### Daily Full Backup

```bash
#!/bin/bash
# backup_daily.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
DB_NAME="concise"
DB_USER="concise"

# Create backup directory
mkdir -p $BACKUP_DIR

# Full database backup
pg_dump -U $DB_USER -F c -b -v -f "$BACKUP_DIR/concise_$DATE.backup" $DB_NAME

# Compress backup
gzip "$BACKUP_DIR/concise_$DATE.backup"

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.backup.gz" -mtime +30 -delete

echo "Backup completed: concise_$DATE.backup.gz"
```

#### Hourly Incremental Backup

```bash
#!/bin/bash
# backup_incremental.sh

# Use WAL archiving for point-in-time recovery
# Configure postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /backups/postgresql/wal/%f'

# WAL files are automatically archived
```

### Setup Automated Backups

#### Using Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_daily.sh >> /var/log/concise_backup.log 2>&1

# Add hourly incremental (WAL archiving is automatic)
```

#### Using Systemd Timer

```ini
# /etc/systemd/system/concise-backup.timer
[Unit]
Description=Daily Concise Database Backup

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/concise-backup.service
[Unit]
Description=Concise Database Backup Service

[Service]
Type=oneshot
ExecStart=/path/to/backup_daily.sh
User=postgres
```

```bash
# Enable timer
sudo systemctl enable concise-backup.timer
sudo systemctl start concise-backup.timer
```

---

## Restore Procedures

### Full Database Restore

```bash
# Stop application
docker-compose down

# Restore from backup
gunzip -c /backups/postgresql/concise_20250115.backup.gz > /tmp/restore.backup
pg_restore -U concise -d concise -v /tmp/restore.backup

# Start application
docker-compose up -d
```

### Point-in-Time Recovery (PITR)

```bash
# 1. Restore base backup
pg_restore -U concise -d concise /backups/postgresql/base_backup.backup

# 2. Configure recovery
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /backups/postgresql/wal/%f %p'
recovery_target_time = '2025-01-15 14:30:00'
EOF

# 3. Restart PostgreSQL
pg_ctl restart

# PostgreSQL will replay WAL files up to target time
```

### Table-Level Restore

```bash
# Restore specific table
pg_restore -U concise -d concise -t usage_records /backups/postgresql/concise_20250115.backup
```

---

## Redis Backup

### Manual Backup

```bash
# Trigger background save
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backups/redis/dump_$(date +%Y%m%d).rdb
```

### Automated Redis Backup

```bash
#!/bin/bash
# backup_redis.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/redis"

mkdir -p $BACKUP_DIR

# Trigger save
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) -le $(date +%s) ]; do
    sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/dump_$DATE.rdb"

# Compress
gzip "$BACKUP_DIR/dump_$DATE.rdb"

# Delete old backups
find $BACKUP_DIR -name "*.rdb.gz" -mtime +7 -delete

echo "Redis backup completed: dump_$DATE.rdb.gz"
```

### Redis Restore

```bash
# Stop Redis
redis-cli SHUTDOWN

# Replace RDB file
cp /backups/redis/dump_20250115.rdb /var/lib/redis/dump.rdb

# Start Redis
redis-server
```

---

## Disaster Recovery

### RTO (Recovery Time Objective)

- **Target**: 15 minutes
- **Process**:
  1. Detect failure (2 min)
  2. Restore latest backup (8 min)
  3. Validate data (3 min)
  4. Restart services (2 min)

### RPO (Recovery Point Objective)

- **Target**: 5 minutes of data loss maximum
- **Method**: Continuous WAL archiving to remote storage

### DR Testing

```bash
#!/bin/bash
# test_disaster_recovery.sh

echo "Testing disaster recovery procedure..."

# 1. Create test backup
echo "Creating backup..."
pg_dump -U concise -F c -f /tmp/dr_test.backup concise

# 2. Drop test database
echo "Simulating disaster..."
dropdb -U concise concise_dr_test

# 3. Restore
echo "Restoring from backup..."
createdb -U concise concise_dr_test
pg_restore -U concise -d concise_dr_test /tmp/dr_test.backup

# 4. Verify
echo "Verifying data..."
psql -U concise -d concise_dr_test -c "SELECT COUNT(*) FROM users;"

echo "DR test completed successfully"
```

---

## Monitoring

### Database Health Checks

```bash
# Check database size
psql -U concise -c "SELECT pg_size_pretty(pg_database_size('concise'));"

# Check table sizes
psql -U concise -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass)) FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(tablename::regclass) DESC;"

# Check active connections
psql -U concise -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
psql -U concise -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Automated Monitoring

```python
# monitoring_script.py
import psycopg2
from datetime import datetime

def check_database_health():
    conn = psycopg2.connect(
        dbname="concise",
        user="concise",
        password="password",
        host="localhost"
    )

    cursor = conn.cursor()

    # Check database size
    cursor.execute("SELECT pg_database_size('concise');")
    size = cursor.fetchone()[0]

    # Check connection count
    cursor.execute("SELECT count(*) FROM pg_stat_activity;")
    connections = cursor.fetchone()[0]

    # Check last backup
    cursor.execute("SELECT MAX(created_at) FROM backup_log;")
    last_backup = cursor.fetchone()[0]

    health = {
        'timestamp': datetime.now().isoformat(),
        'database_size_mb': size / (1024 * 1024),
        'active_connections': connections,
        'last_backup': str(last_backup),
        'healthy': connections < 100 and size < 10_000_000_000  # 10GB limit
    }

    return health

if __name__ == "__main__":
    health = check_database_health()
    print(f"Database Health: {'✓ HEALTHY' if health['healthy'] else '✗ UNHEALTHY'}")
    print(f"  Size: {health['database_size_mb']:.2f} MB")
    print(f"  Connections: {health['active_connections']}")
    print(f"  Last Backup: {health['last_backup']}")
```

---

## Performance Optimization

### Indexes

```sql
-- Most frequently queried columns
CREATE INDEX idx_usage_records_user_id ON usage_records(user_id);
CREATE INDEX idx_usage_records_created_at ON usage_records(created_at);
CREATE INDEX idx_usage_records_strategy ON usage_records(strategy);
CREATE INDEX idx_api_keys_key ON api_keys(key);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);

-- Composite indexes for common queries
CREATE INDEX idx_usage_records_user_date ON usage_records(user_id, created_at DESC);
```

### Partitioning

```sql
-- Partition usage_records by month for better performance
CREATE TABLE usage_records_2025_01 PARTITION OF usage_records
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE usage_records_2025_02 PARTITION OF usage_records
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### Vacuuming

```bash
# Manual vacuum
psql -U concise -c "VACUUM ANALYZE;"

# Configure autovacuum in postgresql.conf
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
```

---

## Security

### Encryption at Rest

```bash
# Enable transparent data encryption (TDE)
# PostgreSQL with pgcrypto extension
psql -U concise -c "CREATE EXTENSION pgcrypto;"
```

### SSL/TLS

```bash
# Configure postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

### Access Control

```sql
-- Create read-only user
CREATE USER concise_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE concise TO concise_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO concise_readonly;

-- Create application user with limited permissions
CREATE USER concise_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE concise TO concise_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO concise_app;
```

---

## Best Practices

1. **Backups**:
   - Daily full backups
   - Continuous WAL archiving
   - Test restores monthly

2. **Monitoring**:
   - Database size
   - Query performance
   - Connection pool usage
   - Backup success/failure

3. **Maintenance**:
   - Regular VACUUM ANALYZE
   - Index maintenance
   - Partition management
   - Log rotation

4. **Security**:
   - Encrypted connections (SSL)
   - Encrypted backups
   - Strong passwords
   - Principle of least privilege

5. **Scaling**:
   - Read replicas for scaling reads
   - Connection pooling (PgBouncer)
   - Partitioning large tables
   - Archiving old data

---

## Troubleshooting

### Connection Issues

```bash
# Check PostgreSQL status
systemctl status postgresql

# Check connections
psql -U concise -c "SELECT * FROM pg_stat_activity;"

# Check logs
tail -f /var/log/postgresql/postgresql-16-main.log
```

### Performance Issues

```bash
# Find slow queries
psql -U concise -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check table bloat
psql -U concise -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Backup Failures

```bash
# Check disk space
df -h

# Check backup logs
tail -f /var/log/concise_backup.log

# Test backup manually
pg_dump -U concise -F c -v -f /tmp/test.backup concise
```

---

## Contact

For database-related support:
- GitHub Issues: https://github.com/yourusername/Concise/issues
- Email: database-admin@concise-sdk.com
