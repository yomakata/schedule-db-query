# Log Rotation Quick Reference

## Quick Configuration

```env
# .env file
LOG_FILE=./logs/app.log
LOG_MAX_BYTES=10485760      # 10MB (default)
LOG_BACKUP_COUNT=5          # Keep 5 backups (default)
```

## Common Sizes

| Size | Bytes |
|------|-------|
| 5 MB | 5242880 |
| 10 MB | 10485760 |
| 20 MB | 20971520 |
| 50 MB | 52428800 |
| 100 MB | 104857600 |

## File Structure

```
logs/
├── app.log       # Current log (active)
├── app.log.1     # Most recent backup
├── app.log.2     # 
├── app.log.3     # 
├── app.log.4     # 
└── app.log.5     # Oldest backup
```

## Quick Commands

### View Current Logs
```bash
# Last 50 lines
tail -n 50 logs/app.log

# Follow live logs
tail -f logs/app.log

# Docker container
docker-compose logs -f schedule-db-query
```

### Search Logs
```bash
# Search all log files
grep "ERROR" logs/app.log*

# Search specific backup
grep "ERROR" logs/app.log.1

# Count errors
grep -c "ERROR" logs/app.log*
```

### Check Disk Usage
```bash
# Log directory size
du -sh logs/

# Docker container
docker exec schedule-db-query du -sh /app/logs/
```

### Clean Old Logs
```bash
# Keep only current + 2 backups
rm logs/app.log.{3..10}

# Remove all backups (keep current only)
rm logs/app.log.[1-9]*
```

## Environment Recommendations

| Environment | LOG_MAX_BYTES | LOG_BACKUP_COUNT | Total Space |
|-------------|---------------|------------------|-------------|
| Development | 10485760 (10MB) | 3 | 40MB |
| Testing | 10485760 (10MB) | 5 | 60MB |
| Production | 52428800 (50MB) | 7 | 400MB |
| Docker | 20971520 (20MB) | 5 | 120MB |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Logs not rotating | Check permissions, restart container |
| Too many rotations | Increase LOG_MAX_BYTES or reduce LOG_LEVEL |
| Disk full | Delete old backups, reduce LOG_BACKUP_COUNT |
| Can't open logs | Use `tail`/`grep`, reduce LOG_MAX_BYTES |

## See Full Documentation

[docs/LOG_ROTATION.md](./LOG_ROTATION.md)
