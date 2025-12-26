# Schedule Time Logging Feature

## Overview

Each scheduled snapshot execution now logs the specific schedule time that triggered it. This makes it easy to track which scheduled time caused each execution, especially useful when you have multiple schedule times configured.

## Log Format

### When Scheduled Execution Triggers

When a scheduled time triggers an execution, you'll see logs like this:

```
================================================================================
⏰ Scheduled execution triggered at 08:00
================================================================================
================================================================================
Starting Member Snapshot Execution
Execution Time: 2025-12-25 08:00:05
================================================================================
```

### When Manual Execution (--run-once)

When you run manually with `--run-once`, the schedule time log won't appear:

```
================================================================================
Starting Member Snapshot Execution
Execution Time: 2025-12-25 14:30:15
================================================================================
```

## Configuration Example

### Multiple Schedule Times

```env
SCHEDULE_TIME=08:00,12:00,18:00
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI
```

### Log Output Examples

#### Execution at 08:00
```
2025-12-25 08:00:05 - INFO - ================================================================================
2025-12-25 08:00:05 - INFO - ⏰ Scheduled execution triggered at 08:00
2025-12-25 08:00:05 - INFO - ================================================================================
2025-12-25 08:00:05 - INFO - ================================================================================
2025-12-25 08:00:05 - INFO - Starting Member Snapshot Execution
2025-12-25 08:00:05 - INFO - Execution Time: 2025-12-25 08:00:05
2025-12-25 08:00:05 - INFO - ================================================================================
2025-12-25 08:00:05 - INFO - Loading SQL query from: /app/config/queries.sql
2025-12-25 08:00:05 - INFO - Step 1: Executing database query...
...
2025-12-25 08:00:12 - INFO - ================================================================================
2025-12-25 08:00:12 - INFO - Snapshot Execution Completed Successfully
2025-12-25 08:00:12 - INFO -   Total rows: 1,234
2025-12-25 08:00:12 - INFO -   CSV file: member_snapshot_20251225_080005.csv
2025-12-25 08:00:12 - INFO -   Execution time: 7.23 seconds
...
```

#### Execution at 12:00
```
2025-12-25 12:00:03 - INFO - ================================================================================
2025-12-25 12:00:03 - INFO - ⏰ Scheduled execution triggered at 12:00
2025-12-25 12:00:03 - INFO - ================================================================================
2025-12-25 12:00:03 - INFO - ================================================================================
2025-12-25 12:00:03 - INFO - Starting Member Snapshot Execution
2025-12-25 12:00:03 - INFO - Execution Time: 2025-12-25 12:00:03
2025-12-25 12:00:03 - INFO - ================================================================================
...
```

#### Execution at 18:00
```
2025-12-25 18:00:02 - INFO - ================================================================================
2025-12-25 18:00:02 - INFO - ⏰ Scheduled execution triggered at 18:00
2025-12-25 18:00:02 - INFO - ================================================================================
2025-12-25 18:00:02 - INFO - ================================================================================
2025-12-25 18:00:02 - INFO - Starting Member Snapshot Execution
2025-12-25 18:00:02 - INFO - Execution Time: 2025-12-25 18:00:02
2025-12-25 18:00:02 - INFO - ================================================================================
...
```

## Benefits

1. **Easy Tracking**: Quickly identify which scheduled time triggered each execution
2. **Audit Trail**: Complete record of when and why each snapshot was created
3. **Debugging**: Easier to troubleshoot schedule-related issues
4. **Compliance**: Better logging for audit and compliance requirements
5. **Monitoring**: Easier to verify all scheduled times are executing correctly

## Use Cases

### Verify All Schedule Times Execute

Check your logs to ensure all configured schedule times are actually executing:

```bash
# View all scheduled executions
grep "⏰ Scheduled execution triggered" logs/app.log

# Count executions per schedule time
grep "⏰ Scheduled execution triggered" logs/app.log | sort | uniq -c
```

### Debug Missing Executions

If a schedule time isn't executing, check if it appears in the logs:

```bash
# Check if 08:00 execution ran today
grep "⏰ Scheduled execution triggered at 08:00" logs/app.log | grep "2025-12-25"
```

### Track Execution Patterns

Analyze execution patterns over time:

```bash
# All scheduled executions today
grep "⏰ Scheduled execution triggered" logs/app.log | grep "2025-12-25"

# Executions for specific schedule time
grep "⏰ Scheduled execution triggered at 12:00" logs/app.log
```

### Identify Performance Issues by Schedule Time

Compare execution times for different schedule times:

```bash
# Find all executions and their times for 08:00 schedule
grep -A 15 "⏰ Scheduled execution triggered at 08:00" logs/app.log | grep "Execution time:"

# Find all executions and their times for 18:00 schedule
grep -A 15 "⏰ Scheduled execution triggered at 18:00" logs/app.log | grep "Execution time:"
```

## Log File Analysis

### Example Log Search Commands

#### Docker Container Logs
```bash
# View recent scheduled executions
docker-compose logs schedule-db-query | grep "⏰ Scheduled execution"

# Follow logs and watch for scheduled executions
docker-compose logs -f schedule-db-query | grep "⏰ Scheduled execution"

# Count executions per schedule time today
docker-compose logs schedule-db-query | grep "2025-12-25" | grep "⏰ Scheduled execution" | sort | uniq -c
```

#### Local Log Files
```bash
# View all scheduled executions
cat logs/app.log | grep "⏰ Scheduled execution"

# Last 10 scheduled executions
grep "⏰ Scheduled execution" logs/app.log | tail -10

# Scheduled executions with timestamps
grep "⏰ Scheduled execution" logs/app.log | grep -o "[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}.*⏰.*"
```

## Technical Implementation

### How It Works

1. The `SnapshotScheduler` creates wrapper functions for each schedule time
2. Each wrapper function logs the schedule time before calling the main task function
3. The main task function logs the actual execution timestamp
4. Both logs are displayed in sequence, showing:
   - Which schedule time triggered the execution
   - When the execution actually started

### Code Changes

**src/scheduler.py:**
- Added `_create_task_wrapper()` method that creates a wrapper function for each schedule time
- The wrapper logs the schedule time before executing the task
- Each schedule time gets its own unique wrapper function

**src/main.py:**
- Added execution timestamp logging to `execute_snapshot()`
- Shows both the schedule time (from wrapper) and actual execution time

## Best Practices

1. **Regular Log Review**: Periodically check logs to ensure all schedule times are executing
2. **Monitor Execution Times**: Track if certain schedule times consistently take longer
3. **Audit Compliance**: Keep logs for audit trails showing when snapshots were created
4. **Alert on Missing Executions**: Set up monitoring to alert if a scheduled time doesn't execute
5. **Log Rotation**: Ensure log rotation is configured to prevent disk space issues

## Troubleshooting

### Issue: Schedule Time Not Appearing in Logs

**Problem**: The "⏰ Scheduled execution triggered at XX:XX" message doesn't appear

**Possible Causes**:
1. Running with `--run-once` flag (manual execution)
2. Schedule time hasn't occurred yet
3. Scheduler not running

**Solutions**:
1. Check if using `--run-once` - this is expected behavior for manual execution
2. Verify current time vs scheduled times in `.env`
3. Check scheduler is running: look for "Scheduler started" in logs

### Issue: Multiple Executions at Same Time

**Problem**: Same schedule time appears multiple times at once

**Possible Causes**:
1. Multiple day schedules configured (expected for MON, TUE, etc.)
2. Both daily and day-specific schedules configured

**Solutions**:
1. This is normal if you have specific days configured (e.g., MON,TUE,WED,THU,FRI)
2. Check your `SCHEDULE_DAYS` configuration

### Issue: Execution Time Doesn't Match Schedule Time

**Problem**: "Scheduled execution triggered at 08:00" but "Execution Time: 2025-12-25 08:00:05"

**Explanation**: This is normal! 
- The schedule time (08:00) is when the execution was supposed to start
- The execution time (08:00:05) is when the code actually ran (5 seconds later)
- Small delays (a few seconds) are normal and expected

## Related Configuration

- `SCHEDULE_TIME`: Comma-separated list of times (e.g., "08:00,12:00,18:00")
- `SCHEDULE_DAYS`: Days to run (e.g., "MON,TUE,WED,THU,FRI")
- `LOG_LEVEL`: Set to "INFO" or "DEBUG" to see schedule logs
- `LOG_FILE`: Where logs are written

See [README.md](../README.md) for full configuration documentation.
