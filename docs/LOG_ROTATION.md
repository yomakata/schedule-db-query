# Log Rotation Configuration

## Overview

The application uses automatic log rotation to prevent log files from growing indefinitely. When the log file reaches a specified size, it's automatically rotated, and old log files are kept as backups.

## How Log Rotation Works

The application uses Python's `RotatingFileHandler` which provides size-based log rotation:

1. **Current Log File**: All new logs are written to `logs/app.log`
2. **Size Check**: When `app.log` reaches `LOG_MAX_BYTES` size, rotation occurs
3. **Rotation Process**:
   - `app.log` → `app.log.1` (current file renamed)
   - `app.log.1` → `app.log.2` (previous backup renamed)
   - `app.log.2` → `app.log.3` (and so on...)
   - New `app.log` file created for fresh logs
4. **Cleanup**: Only `LOG_BACKUP_COUNT` backup files are kept, oldest are deleted

## Configuration

### Environment Variables

```env
# Logging Configuration
LOG_LEVEL=INFO                          # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=./logs/app.log                 # Log file path
LOG_MAX_BYTES=10485760                  # Maximum log file size (10MB = 10485760 bytes)
LOG_BACKUP_COUNT=5                      # Number of backup files to keep
```

### Default Values

| Setting | Default | Description |
|---------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Minimum log level to record |
| `LOG_FILE` | `./logs/app.log` | Path to log file |
| `LOG_MAX_BYTES` | `10485760` (10MB) | Maximum size before rotation |
| `LOG_BACKUP_COUNT` | `5` | Number of backup files to retain |

## Log File Sizes

Common size configurations in bytes:

| Size | Bytes | Environment Variable |
|------|-------|---------------------|
| 1 MB | 1048576 | `LOG_MAX_BYTES=1048576` |
| 5 MB | 5242880 | `LOG_MAX_BYTES=5242880` |
| 10 MB | 10485760 | `LOG_MAX_BYTES=10485760` (default) |
| 20 MB | 20971520 | `LOG_MAX_BYTES=20971520` |
| 50 MB | 52428800 | `LOG_MAX_BYTES=52428800` |
| 100 MB | 104857600 | `LOG_MAX_BYTES=104857600` |

## Example Scenarios

### Scenario 1: Default Configuration (10MB, 5 backups)

**Configuration:**
```env
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

**Files Created:**
```
logs/
├── app.log           # Current log file (up to 10MB)
├── app.log.1         # First backup (10MB)
├── app.log.2         # Second backup (10MB)
├── app.log.3         # Third backup (10MB)
├── app.log.4         # Fourth backup (10MB)
└── app.log.5         # Fifth backup (10MB)
```

**Total Space Used:** Up to 60MB (6 files × 10MB)

### Scenario 2: High Volume (50MB, 10 backups)

For high-volume logging or long retention:

**Configuration:**
```env
LOG_MAX_BYTES=52428800
LOG_BACKUP_COUNT=10
```

**Total Space Used:** Up to 550MB (11 files × 50MB)

### Scenario 3: Low Space (5MB, 3 backups)

For environments with limited disk space:

**Configuration:**
```env
LOG_MAX_BYTES=5242880
LOG_BACKUP_COUNT=3
```

**Total Space Used:** Up to 20MB (4 files × 5MB)

### Scenario 4: Debug Mode (Larger files)

For development/debugging with verbose logging:

**Configuration:**
```env
LOG_LEVEL=DEBUG
LOG_MAX_BYTES=20971520
LOG_BACKUP_COUNT=7
```

**Total Space Used:** Up to 160MB (8 files × 20MB)

## Best Practices

### 1. Size Selection

**Recommended:** 10-50MB per file
- **Too Small** (< 5MB): Frequent rotations, harder to find logs
- **Too Large** (> 100MB): Difficult to open/search, slower rotation
- **Just Right** (10-50MB): Good balance between usability and retention

### 2. Backup Count

**Recommended:** 5-10 backups
- **Calculation**: `total_retention = LOG_MAX_BYTES × (LOG_BACKUP_COUNT + 1)`
- **Example**: 10MB × 6 files = 60MB total
- **Consider**: How much history you need vs available disk space

### 3. Environment-Specific Settings

#### Development
```env
LOG_LEVEL=DEBUG
LOG_MAX_BYTES=10485760    # 10MB
LOG_BACKUP_COUNT=3        # Keep 3 backups (40MB total)
```

#### Production
```env
LOG_LEVEL=INFO
LOG_MAX_BYTES=52428800    # 50MB
LOG_BACKUP_COUNT=7        # Keep 7 backups (400MB total)
```

#### Docker Container
```env
LOG_LEVEL=INFO
LOG_MAX_BYTES=20971520    # 20MB
LOG_BACKUP_COUNT=5        # Keep 5 backups (120MB total)
```

### 4. Monitoring Disk Space

Calculate total log space usage:
```bash
# Linux/Mac
du -sh logs/

# Docker container
docker exec schedule-db-query du -sh /app/logs/
```

### 5. Log Retention vs CSV Retention

**Separate Settings:**
- `FILE_RETENTION_DAYS`: How long to keep CSV snapshot files (default: 30 days)
- `LOG_BACKUP_COUNT`: How many log file rotations to keep (not time-based)

**Note:** Log rotation is size-based, not time-based. In high-volume scenarios, all backups could be from the same day.

## File Structure

### After Multiple Rotations

```
logs/
├── app.log           # Current (5.2MB)
├── app.log.1         # Most recent backup (10MB)
├── app.log.2         # Older backup (10MB)
├── app.log.3         # Older backup (10MB)
├── app.log.4         # Older backup (10MB)
└── app.log.5         # Oldest backup (10MB)
```

### Reading Rotated Logs

#### All logs (newest to oldest)
```bash
# Linux/Mac
cat logs/app.log logs/app.log.{1..5}

# Windows
type logs\app.log logs\app.log.1 logs\app.log.2 logs\app.log.3 logs\app.log.4 logs\app.log.5
```

#### Search across all log files
```bash
# Linux/Mac
grep "ERROR" logs/app.log*

# Docker
docker exec schedule-db-query grep "ERROR" /app/logs/app.log*
```

#### View specific backup
```bash
# Second most recent log
cat logs/app.log.1

# Docker
docker exec schedule-db-query cat /app/logs/app.log.1
```

## Docker Considerations

### Volume Mounting

Ensure logs directory is mounted to persist across container restarts:

**docker-compose.yml:**
```yaml
services:
  schedule-db-query:
    volumes:
      - ./logs:/app/logs         # Persist logs
      - ./output:/app/output     # Persist CSV files
```

### Disk Space Monitoring

Monitor container disk usage:
```bash
# Check container disk usage
docker exec schedule-db-query df -h /app/logs

# Check log directory size
docker exec schedule-db-query du -sh /app/logs
```

### Log Cleanup in Docker

If logs grow too large:
```bash
# Stop container
docker-compose down

# Clean old backups (keep only last 2)
rm logs/app.log.{3..10}

# Restart
docker-compose up -d
```

## Troubleshooting

### Issue: Logs Not Rotating

**Symptoms:**
- `app.log` grows beyond `LOG_MAX_BYTES`
- No `.1`, `.2`, etc. backup files created

**Possible Causes:**
1. Write permissions issue on logs directory
2. Configuration not loaded correctly
3. Multiple processes writing to same log file

**Solutions:**
```bash
# Check file permissions
ls -la logs/

# Verify configuration is loaded
docker-compose logs schedule-db-query | head -20

# Check disk space
df -h

# Restart container
docker-compose restart schedule-db-query
```

### Issue: Too Many Rotations

**Symptoms:**
- Log files rotate very frequently
- Hard to find recent logs

**Solutions:**
1. Increase `LOG_MAX_BYTES`
2. Reduce `LOG_LEVEL` from DEBUG to INFO
3. Check for excessive logging in code

### Issue: Disk Full

**Symptoms:**
- "No space left on device" error
- Application crashes

**Solutions:**
```bash
# Immediate: Delete old backups
rm logs/app.log.{3..10}

# Long-term: Adjust retention settings
# Reduce LOG_BACKUP_COUNT or LOG_MAX_BYTES in .env

# Add disk space monitoring
docker exec schedule-db-query df -h
```

### Issue: Cannot Open Log Files

**Symptoms:**
- Log files are huge (> 100MB)
- Text editor freezes when opening

**Solutions:**
1. Use command-line tools instead:
   ```bash
   # View last 100 lines
   tail -n 100 logs/app.log
   
   # Search for errors
   grep "ERROR" logs/app.log | tail -n 50
   
   # View specific time range
   grep "2025-12-25 08:" logs/app.log
   ```

2. Reduce `LOG_MAX_BYTES` for future rotations

3. Use log analysis tools:
   ```bash
   # Count log levels
   grep -o "INFO\|WARNING\|ERROR" logs/app.log | sort | uniq -c
   
   # Find errors only
   grep "ERROR" logs/app.log > errors.txt
   ```

## Advanced Configuration

### Time-Based Rotation (Alternative)

If you need time-based rotation (daily, weekly) instead of size-based, you would need to use `TimedRotatingFileHandler` instead. This requires code changes in `src/main.py`.

**Example (not implemented by default):**
```python
from logging.handlers import TimedRotatingFileHandler

# Rotate daily at midnight, keep 30 days
handler = TimedRotatingFileHandler(
    settings.LOG_FILE,
    when='midnight',
    interval=1,
    backupCount=30
)
```

### Combined Size and Time Rotation

For production systems, consider implementing both:
1. Size-based: Prevent any single file from being too large
2. Time-based: Keep logs for specific number of days

This would require custom log handler implementation.

## Monitoring and Alerts

### Check Log Rotation Status

Create a script to monitor log rotation:

```bash
#!/bin/bash
# check-logs.sh

LOG_DIR="./logs"
MAX_SIZE_MB=10

echo "Log Rotation Status:"
echo "===================="

for file in $LOG_DIR/app.log*; do
    if [ -f "$file" ]; then
        size=$(du -m "$file" | cut -f1)
        echo "$file: ${size}MB"
        
        if [ "$size" -gt "$MAX_SIZE_MB" ]; then
            echo "  ⚠️  WARNING: File exceeds ${MAX_SIZE_MB}MB"
        fi
    fi
done

echo ""
echo "Total log space used:"
du -sh $LOG_DIR
```

### Alerting

Set up monitoring to alert when:
- Total log size exceeds threshold
- Disk space is low
- Log rotation stops working

## Related Documentation

- [README.md](../README.md) - Main documentation
- [SCHEDULE_TIME_LOGGING.md](./SCHEDULE_TIME_LOGGING.md) - Schedule time logging
- [SQL_QUERY_FILE_CONFIGURATION.md](./SQL_QUERY_FILE_CONFIGURATION.md) - Query file configuration

## Summary

Log rotation is automatically configured with sensible defaults:
- **10MB** per log file
- **5 backup files** retained
- **60MB total** maximum log space

Adjust `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT` in `.env` based on your needs and available disk space.
