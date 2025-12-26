# Schedule DB query - Development Specification

## Project Overview
A Python-based automation tool that executes SQL queries against a remote database on a scheduled basis, exports results to CSV files, and delivers them via email. Features intelligent file naming, automatic log rotation, and comprehensive schedule time tracking.

## Features

### 1. Database Query Execution
- **Python script** to connect to remote database
- Execute configurable SQL queries from external SQL files
- **SQLAlchemy integration** for better pandas compatibility
- Support for multiple database types (MySQL, PostgreSQL, SQL Server)
- Error handling and logging for database operations
- Connection pooling with health checks (`pool_pre_ping=True`)
- Configurable connection timeouts and pool recycling

### 2. Configuration Management
- **All sensitive data stored in `.env` file**:
  - Database credentials (host, port, username, password, database name)
  - Email service credentials (SMTP server, port, username, password)
  - Recipient email addresses
  - File paths and storage locations
  - **SQL query file path** (configurable)
  - **Log rotation settings**
- Use `python-dotenv` package to load environment variables
- `.env.example` template file for reference
- **Never commit `.env` to version control** (add to `.gitignore`)
- **Multi-database support**: MySQL, PostgreSQL, SQL Server
- **Optional email delivery**: Can be disabled via `EMAIL_ENABLED=false`
- **Flexible SQL query files**: Specify custom query file paths

### 3. Scheduled Execution
- **Configurable schedule** for automatic script execution using `schedule` Python library ✅ **Implemented**
- **24-hour time format** (HH:MM) for SCHEDULE_TIME
- **Multiple schedule times** supported (comma-separated: `08:00,12:00,18:00`)
- **Timezone support** with SCHEDULE_TIMEZONE setting
- **Flexible day selection**: Any combination of MON-SUN
- **Schedule time tracking**: Each execution logs which schedule time triggered it
- **Smart next run calculation**: Automatically skips past times, shows only future executions
- **Automatic cleanup**: Removes jobs with past execution times at startup
- **Duplicate execution prevention**: Built-in deduplication mechanism prevents the same task from running twice within the same minute
  - Tracks last execution minute
  - Prevents concurrent execution
  - Logs warnings when duplicates are detected
- Support for schedule patterns:
  - Daily at specific times
  - Weekly on specific days
  - Custom combinations

### 4. CSV Export
- Export SQL query results to **CSV format**
- **Smart file naming**: Output files automatically named after SQL query file
  - Example: `sales_report.sql` → `sales_report_2025-12-25_080005.csv`
- Features:
  - Query file name-based prefixes (no generic prefixes)
  - Automatic timestamp in format `YYYY-MM-DD_HHMMSS`
  - Configurable output directory
  - CSV formatting options (delimiter, quoting, encoding)
  - Header row with column names
  - Handle special characters and NULL values
- File management:
  - **Automatic cleanup** of old files (configurable retention period)
  - Cleanup applies per query file (different queries maintain separate file sets)
  - File size validation
  - Self-documenting file names (shows which query generated the output)

### 5. Email Delivery
- **Send CSV files as email attachments** (optional - can be disabled)
- **EMAIL_ENABLED** setting to enable/disable email delivery
  - When disabled: CSV files are still saved to output directory
  - When enabled: CSV files are saved AND sent via email
- **Multiple email provider support**:
  - Gmail (smtp.gmail.com) - Requires app-specific password
  - Office365 (smtp.office365.com) - Standard password
  - Outlook.com (smtp.office365.com) - Standard password
  - Custom SMTP servers
- Email features:
  - Support for SMTP/SMTP SSL/TLS
  - Multiple recipients (To, CC, BCC)
  - Customizable email subject and body
  - HTML and plain text email support
  - Attachment size validation
  - Retry mechanism for failed deliveries
- Email templates with dynamic content:
  - Query execution summary
  - Row count
  - Execution timestamp
  - Error notifications (only if email enabled)
- **Smart error handling**: No email attempts when EMAIL_ENABLED=false

### 6. Logging & Monitoring
- **Automatic log rotation** to prevent disk space issues
  - Size-based rotation (default: 10MB per file)
  - Configurable backup count (default: 5 backups)
  - Rotated files: `app.log`, `app.log.1`, `app.log.2`, etc.
- **Schedule time tracking**: Each execution logs which schedule time triggered it
  - Format: `⏰ Scheduled execution triggered at HH:MM`
  - Helps identify which schedule caused each execution
  - Useful for auditing and troubleshooting
- **Execution timestamps**: Both schedule time and actual execution time logged
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation configuration:
  - `LOG_MAX_BYTES`: Maximum log file size before rotation
  - `LOG_BACKUP_COUNT`: Number of backup files to keep
- Include in logs:
  - Query execution time
  - Row count
  - File paths (including SQL query file)
  - Schedule time that triggered execution
  - Email delivery status
  - Errors and stack traces
  - Job cleanup (past execution times removed)

## Technical Stack

### Core Dependencies
```
python >= 3.8
python-dotenv >= 0.19.0
pandas >= 1.3.0
SQLAlchemy >= 1.4.0 (moved from optional to core)
pymysql >= 1.0.0 (for MySQL)
psycopg2-binary (for PostgreSQL - optional)
pyodbc (for SQL Server - optional)
schedule >= 1.1.0
smtplib (built-in)
logging (built-in)
logging.handlers (built-in - for RotatingFileHandler)
pathlib (built-in)
```

### Optional Dependencies
```
APScheduler >= 3.9.0 (for advanced scheduling - not currently used)
jinja2 >= 3.0.0 (for email templates - not currently used)
```

### Key Library Choices
- **SQLAlchemy**: Provides better pandas integration, eliminates DBAPI2 warnings
- **schedule**: Simple, reliable scheduling without external dependencies
- **RotatingFileHandler**: Built-in log rotation without external tools
- **pathlib**: Modern file path handling

## Project Structure
```
schedule-db-query/
├── .env                    # Environment variables (not in git)
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── README.md               # Project documentation
├── SPEC.md                 # This specification
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuration loader
│   └── queries.sql         # SQL query templates
├── src/
│   ├── __init__.py
│   ├── main.py             # Main entry point
│   ├── database.py         # Database connection and query execution
│   ├── exporter.py         # CSV export functionality
│   ├── emailer.py          # Email sending functionality
│   └── scheduler.py        # Scheduling logic
├── logs/
│   └── app.log             # Application logs
├── output/
│   └── snapshots/          # Generated CSV files
└── tests/
    ├── __init__.py
    ├── test_database.py
    ├── test_exporter.py
    └── test_emailer.py
```

## Environment Variables (.env)

```env
# Database Configuration
# Supported DB_TYPE: mysql, postgresql, sqlserver
DB_TYPE=mysql
DB_HOST=your-database-host.com
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Email Configuration (optional - can be disabled)
EMAIL_ENABLED=true                      # Set to false to disable email sending
# Supported SMTP servers: Gmail, Office365, Outlook, custom SMTP
SMTP_HOST=smtp.office365.com            # smtp.gmail.com for Gmail, smtp.office365.com for Office365
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@yourdomain.com # Full email address
SMTP_PASSWORD=your-password             # App password for Gmail, regular password for Office365
EMAIL_FROM=your-email@yourdomain.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
EMAIL_CC=
EMAIL_BCC=

# Schedule Configuration
SCHEDULE_ENABLED=true
SCHEDULE_TIME=08:00,12:00,18:00         # Multiple times supported (comma-separated)
SCHEDULE_TIMEZONE=Asia/Bangkok          # Timezone for scheduling
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI      # Days to run

# Query Configuration
SQL_QUERY_FILE=./config/queries.sql     # Path to SQL query file (relative or absolute)

# Export Configuration
OUTPUT_DIR=./output/snapshots
FILE_PREFIX=member_snapshot              # Deprecated: now uses query file name
FILE_RETENTION_DAYS=30
CSV_ENCODING=utf-8

# Logging Configuration
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/app.log
LOG_MAX_BYTES=10485760                  # Max log file size (10MB default)
LOG_BACKUP_COUNT=5                      # Number of backup log files to keep
```
# DB_TYPE=postgresql
# DB_HOST=postgres.example.com
# DB_PORT=5432
# DB_NAME=members_db
# DB_USER=postgres_user
# DB_PASSWORD=postgres_password

# SQL Server:
# DB_TYPE=sqlserver
# DB_HOST=sqlserver.example.com
# DB_PORT=1433
# DB_NAME=members_db
# DB_USER=sqlserver_user
# DB_PASSWORD=sqlserver_password

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
EMAIL_CC=
EMAIL_BCC=

# Office365/Outlook Configuration:
# SMTP_HOST=smtp.office365.com
# SMTP_PORT=587
# SMTP_USE_TLS=true
# SMTP_USERNAME=your-email@yourdomain.com
# SMTP_PASSWORD=your-password
# EMAIL_FROM=your-email@yourdomain.com

# Schedule Configuration
SCHEDULE_ENABLED=true
SCHEDULE_TIME=08:00
SCHEDULE_TIMEZONE=Asia/Shanghai
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI

# Export Configuration
OUTPUT_DIR=./output/snapshots
FILE_PREFIX=member_snapshot
FILE_RETENTION_DAYS=30
CSV_ENCODING=utf-8

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### New Environment Variables (Recent Additions)

#### SQL_QUERY_FILE
- **Purpose**: Specify custom SQL query file path
- **Default**: `./config/queries.sql`
- **Supports**: Relative and absolute paths
- **Examples**:
  - `./config/schedule_db_query.sql`
  - `./queries/custom_report.sql`
  - `/app/config/production_query.sql`
- **Benefit**: Use different query files for different environments or purposes

#### LOG_MAX_BYTES
- **Purpose**: Maximum log file size before rotation
- **Default**: `10485760` (10MB)
- **Common Values**:
  - 5MB: `5242880`
  - 10MB: `10485760`
  - 50MB: `52428800`
  - 100MB: `104857600`

#### LOG_BACKUP_COUNT
- **Purpose**: Number of rotated log files to keep
- **Default**: `5`
- **Behavior**: Keeps `app.log`, `app.log.1`, `app.log.2`, ... `app.log.{N}`
- **Total Space**: `LOG_MAX_BYTES × (LOG_BACKUP_COUNT + 1)`

#### SCHEDULE_TIME (Enhanced)
- **Old**: Single time only (`08:00`)
- **New**: Multiple times supported (`08:00,12:00,18:00`)
- **Format**: Comma-separated HH:MM values
- **Benefit**: Run multiple times per day without multiple containers

## Core Functionality

### 1. Database Module (`database.py`)
- Establish secure database connections using **SQLAlchemy**
- Execute parameterized SQL queries
- Return results as pandas DataFrame
- Handle connection errors and timeouts
- **Connection pooling** with health checks:
  - `pool_pre_ping=True`: Validates connections before use
  - `pool_recycle=3600`: Recycles connections hourly
  - `connect_timeout=30`: 30-second connection timeout
- **Multi-database support**:
  - ✅ MySQL (pymysql) - Fully implemented
  - ✅ PostgreSQL (psycopg2-binary) - Fully implemented
  - ✅ SQL Server (pyodbc) - Code ready, requires pyodbc installation
- **Load queries from external files**: `load_query_from_file()` function
- Easy switching via `DB_TYPE` environment variable

### 2. Exporter Module (`exporter.py`)
- Convert DataFrame to CSV
- **Smart filename generation**:
  - Uses SQL query file name as prefix (e.g., `sales_report_`)
  - Adds timestamp: `YYYY-MM-DD_HHMMSS`
  - Result: `sales_report_2025-12-25_080005.csv`
- Save files to configured directory
- **Automatic file cleanup**:
  - Based on `FILE_RETENTION_DAYS` setting
  - Only cleans files matching the current query file prefix
  - Different queries maintain separate file sets
- Validate export success
- Custom prefix support (passed from main)

### 3. Emailer Module (`emailer.py`)
- Compose email with attachments
- Send via SMTP
- Handle authentication
- Implement retry logic
- Support for HTML templates
- **Optional email delivery**: Controlled by EMAIL_ENABLED setting
- Only executes if EMAIL_ENABLED=true
- Credentials not required when email is disabled
- **Smart error notifications**: Only sent when email is enabled

### 4. Scheduler Module (`scheduler.py`)
- Parse schedule configuration
- **Multiple schedule times**: Support comma-separated times
- Run tasks at specified intervals
- Handle timezone conversions
- **Schedule time tracking**: Each execution logs which time triggered it
- **Smart next run calculation**:
  - `_cleanup_past_jobs()`: Removes jobs with past execution times
  - Only shows future times as "next run"
  - Handles service startup at or after scheduled time
- **Duplicate execution prevention**:
  - `task_executing` flag prevents concurrent execution
  - `last_execution_minute` tracking prevents duplicate runs in same minute
  - Logs warnings when duplicates are detected: "Skipping duplicate execution"
  - Resolves issues with multiple jobs scheduled for the same time
- **Improved logging**:
  - Shows which schedule time triggered execution
  - Displays remaining runs for today
  - Debug mode shows job timestamps
- Graceful shutdown on errors
- **Same-day execution**: Ensures today's scheduled times run today (not tomorrow)

### 5. Main Script (`main.py`)
- Orchestrate all modules
- **Enhanced logging setup**:
  - Uses `RotatingFileHandler` for automatic log rotation
  - Configurable size and backup count
- **Smart query file handling**:
  - Loads SQL from `SQL_QUERY_FILE` setting
  - Supports relative and absolute paths
  - Extracts query file name for output file prefix
- Command-line interface options:
  - `--run-once`: Execute immediately (no scheduling)
  - `--test-email`: Send test email (warns if EMAIL_ENABLED=false)
  - `--test-db`: Test database connection
  - `--schedule`: Run with scheduler (default)
- **Always saves CSV files** to output directory
- **Conditionally sends email** based on EMAIL_ENABLED setting
- Comprehensive execution summary with:
  - SQL query file path
  - Execution timestamp
  - Schedule time that triggered it (if scheduled)
  - File path and size
- Error notifications only sent if email is enabled

## Logging Strategy
- **Automatic log rotation** using `RotatingFileHandler`
  - Size-based rotation (configurable via `LOG_MAX_BYTES`)
  - Maintains multiple backup files (`LOG_BACKUP_COUNT`)
  - Files: `app.log`, `app.log.1`, `app.log.2`, etc.
  - Prevents disk space exhaustion
- **Schedule time tracking** in logs:
  - `⏰ Scheduled execution triggered at HH:MM`
  - Shows which schedule time caused each execution
  - Helps with auditing and troubleshooting
- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include in logs:
  - **SQL query file path** being executed
  - **Schedule time** that triggered execution
  - Query execution time
  - Row count
  - **Output file path** (with smart naming)
  - Email delivery status
  - **Past job cleanup** (removed jobs)
  - Errors and stack traces
- **Debug mode enhancements**:
  - Current time and future scheduled times
  - Job next_run timestamps
  - Individual job scheduling details

## Error Handling
- **Try-catch blocks around**:
  - **SQL query file loading** (file not found, invalid SQL)
  - Database connections (with SQLAlchemy engine)
  - Query execution
  - File operations (read/write permissions, disk space)
  - Email delivery (SMTP errors)
  - **Schedule setup and job cleanup**
- **Conditional email notifications**:
  - Only sent when `EMAIL_ENABLED=true`
  - Respects user configuration to prevent unwanted notifications
  - Error emails include context and stack traces
- **Database error recovery**:
  - SQLAlchemy connection pooling with `pool_pre_ping=True`
  - Automatic connection recovery on stale connections
  - Connection recycling every hour (`pool_recycle=3600`)
- Graceful degradation:
  - Log errors comprehensively
  - Continue operation where possible
  - Clean shutdown on critical failures
- Detailed error messages with:
  - Timestamp and context
  - Stack traces
  - Affected configuration/files
  - Suggested remediation

## Security Considerations
- **Never hardcode credentials**
- Use `.env` for all sensitive data
- Add `.env` to `.gitignore`
- Use environment-specific configurations
- Secure SMTP authentication (app passwords, OAuth)
- Validate file paths to prevent directory traversal
- SQL injection prevention (parameterized queries)

## Testing Strategy
- **Unit tests for each module**:
  - `database.py`: SQLAlchemy engine creation, connection pooling
  - `exporter.py`: CSV generation, file prefix customization, cleanup
  - `emailer.py`: EMAIL_ENABLED check, SMTP sending (mocked)
  - `scheduler.py`: Multiple time parsing, past job cleanup, next run calculation
  - `main.py`: Query file loading, log rotation setup
- **Integration tests for end-to-end flow**:
  - Load query from custom file → Execute → Export with custom prefix → Optional email
  - Schedule setup → Past job cleanup → Correct next run display
  - Log rotation: File size monitoring → Backup creation
- **Mock external dependencies**:
  - Database connections (use SQLAlchemy in-memory or test DB)
  - SMTP server (mock email sending)
  - File system (tempfile for testing)
- **Command-line testing**:
  - `--run-once`: Immediate execution test
  - `--test-email`: Email configuration validation
  - `--test-db`: Database connectivity test
  - `--schedule`: Scheduler behavior test
- **Configuration testing**:
  - Various SCHEDULE_TIME formats (single, multiple, day-specific)
  - SQL_QUERY_FILE paths (relative, absolute, nonexistent)
  - LOG_MAX_BYTES and LOG_BACKUP_COUNT variations
  - EMAIL_ENABLED true/false behavior
- **Edge case testing**:
  - Service start after scheduled time (past job cleanup)
  - Multiple times on same day
  - Schedule across midnight
  - Log rotation during active execution
  - Query file name extraction for various path formats
- Test error scenarios
- Validate CSV output format
- Test scheduling logic

## Deployment Options

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/output/snapshots

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "src/main.py", "--schedule"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  schedule-db-query:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: schedule-db-query
    restart: unless-stopped
    # Docker Compose automatically loads .env file from the same directory
    env_file:
      - .env
    volumes:
      # Persist logs and output files
      - ./logs:/app/logs
      - ./output:/app/output
      # Optional: Mount config for easy updates
      - ./config/queries.sql:/app/config/queries.sql:ro    # Optional: Add health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

networks:
  default:
    external: true
    name: reverse-proxy
```

**Note:** Docker Compose automatically reads the `.env` file in the same directory and makes all variables available to the container. You can also use `env_file` to explicitly specify the environment file, or use multiple environment files if needed:
```yaml
env_file:
  - .env
  - .env.local  # Optional: for local overrides
```

#### .dockerignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/

# Environment files
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Output and logs
logs/
output/
*.log

# Git
.git/
.gitignore

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# Documentation
README.md
SPEC.md
*.md

# Tests
tests/
*.pytest_cache/
.coverage
htmlcov/
```

#### Docker Usage

**Build and Run with Docker Compose:**
```bash
# Build the image
docker-compose build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Restart the container
docker-compose restart
```

**Run One-Time Execution:**
```bash
docker-compose run --rm schedule-db-query python src/main.py --run-once
```

**Test Database Connection:**
```bash
docker-compose run --rm schedule-db-query python src/main.py --test-db
```

**Test Email Sending:**
```bash
docker-compose run --rm schedule-db-query python src/main.py --test-email
```

### Local Development
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python src/main.py --run-once
```

### Production Deployment

#### Option 1: Docker Compose (Recommended)
```bash
# On production server
cd /opt/schedule-db-query
cp .env.example .env
# Edit .env with production credentials
nano .env

# Pull and run with docker-compose
docker-compose pull
docker-compose up -d

# Monitor logs
docker-compose logs -f --tail=100
```

#### Option 2: Linux Server with Cron
   ```bash
   0 8 * * * cd /path/to/project && ./venv/bin/python src/main.py --run-once
   ```

#### Option 3: Docker Swarm
   ```bash
   # Initialize swarm
   docker swarm init
   
   # Deploy stack
   docker stack deploy -c docker-compose.yml db-snapshot
   
   # View services
   docker service ls
   
   # View logs
   docker service logs db-snapshot_schedule-db-query
   ```

#### Option 4: Cloud Functions (AWS Lambda, Azure Functions)
   - Use CloudWatch Events or Azure Timer trigger
   - Store secrets in cloud secret manager

#### Option 5: Windows Task Scheduler
   - Create scheduled task
   - Point to Python executable and script

## Monitoring and Alerts

### Application-Level Monitoring
- **Log rotation monitoring**:
  - Track log file sizes (logs/app.log)
  - Monitor backup file creation (app.log.1, app.log.2, etc.)
  - Alert if LOG_MAX_BYTES threshold exceeded frequently
  - Verify old logs are properly archived
- **Execution tracking**:
  - Log successful executions with timestamps
  - Track which schedule time triggered each execution
  - Monitor execution duration and performance
  - Alert on failures (via email if enabled)
- **Database health**:
  - Connection pool status
  - Query execution times
  - Failed connection attempts
- **File system monitoring**:
  - Output directory disk space
  - CSV file generation success rate
  - File naming correctness (query file prefix)
  - Old file cleanup operations

### Docker Container Monitoring
- **Health Checks**: Docker healthcheck in docker-compose.yml
- **Log Aggregation**: 
  ```bash
  docker-compose logs -f --tail=100
  # Filter for specific patterns
  docker-compose logs -f | grep "⏰ Scheduled execution"
  docker-compose logs -f | grep ERROR
  ```
- **Resource Monitoring**:
  ```bash
  docker stats schedule-db-query
  ```
- **Auto-restart**: Set `restart: unless-stopped` in docker-compose.yml

### Docker Volume Management
- **Monitor log rotation in volumes**:
  ```bash
  # Check log sizes
  docker exec schedule-db-query ls -lh /app/logs/
  
  # Verify rotation is working
  docker exec schedule-db-query find /app/logs/ -name "app.log*" -ls
  ```
- **Regularly backup persistent volumes**:
  ```bash
  docker run --rm -v schedule-db-query_logs:/logs -v $(pwd)/backup:/backup \
    alpine tar czf /backup/logs-$(date +%Y%m%d).tar.gz /logs
  ```
- **Monitor volume size**:
  ```bash
  docker system df -v
  ```
- **Output file management**:
  ```bash
  # Check output directory size
  docker exec schedule-db-query du -sh /app/output/snapshots/
  
  # List recent snapshots
  docker exec schedule-db-query ls -lht /app/output/snapshots/ | head -10
  ```

### Alerting Strategy
- **Email alerts** (when EMAIL_ENABLED=true):
  - Critical failures during execution
  - Database connection failures
  - File system errors
- **Log-based monitoring**:
  - Set up log aggregation tools (ELK, Splunk, CloudWatch)
  - Create alerts for ERROR and CRITICAL log levels
  - Monitor for missing scheduled executions
  - Track log rotation events

## Future Enhancements
- **Web dashboard for monitoring**:
  - View execution history and logs
  - Manage schedules via UI
  - Real-time status monitoring
- **Multiple query configurations**:
  - Support multiple SQL query files
  - Different schedules for different queries
  - Query-specific email recipients
- **Export format enhancements**:
  - Support for Excel (.xlsx) with formatting
  - JSON export option
  - Compressed archives (ZIP) for large datasets
- **Advanced scheduling**:
  - Calendar-based scheduling (skip holidays)
  - Dynamic schedules based on data changes
  - Manual trigger via API or webhook
- **Database enhancements**:
  - Query result caching for performance
  - Support for stored procedures
  - Multi-database query support (join across databases)
- **Notification improvements**:
  - Webhook notifications (Slack, Microsoft Teams)
  - SMS alerts for critical failures
  - Success/failure summary reports
- **Data quality features**:
  - Data validation rules before export
  - Anomaly detection (unexpected row count changes)
  - Data profiling and statistics
- **Security enhancements**:
  - Encryption for sensitive data in CSV
  - PGP encryption for email attachments
  - Audit log for all operations
- **Performance optimizations**:
  - Parallel execution for multiple queries
  - Incremental snapshots (only changed data)
  - Streaming large result sets

## Development Timeline

### Phase 1: Core Functionality (Week 1)
- Set up project structure
- Implement database connection
- Basic SQL query execution
- CSV export functionality

### Phase 2: Email Integration (Week 1)
- SMTP configuration
- Email composition with attachments
- Error handling and retry logic

### Phase 3: Scheduling (Week 2)
- Implement scheduler
- Configuration management
- Logging and monitoring

### Phase 4: Testing & Documentation (Week 2)
- Write unit tests
- Integration testing
- Complete README
- Deployment guides

### Phase 5: Production Deployment (Week 3)
- Choose deployment method
- Set up monitoring
- Production testing
- Go live

## Success Criteria
- ✅ Successfully connects to remote database (MySQL, PostgreSQL, SQL Server) with SQLAlchemy
- ✅ Executes SQL queries without errors from configurable query files
- ✅ Generates valid CSV files with timestamps and smart naming
- ✅ Sends emails with attachments (optional - can be disabled)
- ✅ Supports multiple email providers (Gmail, Office365, custom SMTP)
- ✅ CSV files always saved to output directory regardless of email setting
- ✅ Runs on schedule without manual intervention with multiple times per day
- ✅ **Prevents duplicate executions** within the same minute
- ✅ All sensitive data in .env file
- ✅ Comprehensive error logging with automatic rotation
- ✅ Handles failures gracefully with connection pooling
- ✅ Documentation complete with feature-specific guides
- ✅ Docker support with docker-compose
- ✅ Multiple database type support via SQLAlchemy
- ✅ 24-hour time format for scheduling
- ✅ Timezone support (Asia/Bangkok)
- ✅ Optional email delivery with conditional validation
- ✅ Configurable SQL query file path
- ✅ Schedule time tracking in logs
- ✅ Automatic log rotation (size-based)
- ✅ Smart output file naming (query file prefix)
- ✅ Correct next run calculation (skips past times)

## Key Features Implemented

### Recent Bug Fixes (December 2025)
- ✅ **Duplicate Execution Prevention** - Fixed issue where scheduled tasks were executing twice
  - Added `task_executing` flag to prevent concurrent execution
  - Added `last_execution_minute` tracking to prevent duplicate runs
  - Logs warning messages when duplicate execution is attempted
  - Root cause: Multiple scheduler jobs being created for the same time slot
- ✅ **Office365 Email Support** - Updated email configuration to support Office365/Outlook
  - Changed SMTP_HOST to `smtp.office365.com`
  - Updated documentation for email provider setup
  - Supports both Gmail and Office365 SMTP servers
- ✅ **Fixed Email Module Syntax Error** - Resolved duplicate docstring issue
  - Cleaned up emailer.py module initialization
  - Removed conflicting docstring declarations

### Database Support
- ✅ **SQLAlchemy-based connections** - Professional database abstraction
  - Connection pooling with health checks (`pool_pre_ping=True`)
  - Automatic connection recycling (`pool_recycle=3600`)
  - Multi-database support (MySQL, PostgreSQL, SQL Server)
- ✅ **MySQL** - Fully implemented with pymysql
- ⚠️ **PostgreSQL** - Code ready, requires `psycopg2-binary` package
- ⚠️ **SQL Server** - Code ready, requires `pyodbc` package
- Easy switching via `DB_TYPE` environment variable

### Configuration Flexibility
- ✅ **Configurable SQL query files** - `SQL_QUERY_FILE` setting
  - Support for relative and absolute paths
  - Default: `./config/queries.sql`
  - Query file name used for output file prefix
- ✅ **Environment-based configuration** - All settings via `.env`
- ✅ **Conditional feature enablement** - EMAIL_ENABLED, etc.

### Email Flexibility
- ✅ **Optional Email Delivery** - Control via `EMAIL_ENABLED` setting
  - `true`: Save CSV + Send Email (requires credentials)
  - `false`: Save CSV only (no credentials needed)
- ✅ **Conditional validation** - Email credentials only checked when enabled
- ✅ **Smart error notifications** - Only sent when email is enabled

### Scheduling Features
- ✅ **Multiple schedule times per day** - Comma-separated format (08:00,12:00,18:00)
- ✅ **Schedule time tracking** - Logs which time triggered each execution
- ✅ **Smart next run calculation**:
  - Removes past job times at startup
  - Only displays future execution times
  - Handles service restart gracefully
- ✅ **24-hour time format** for precise scheduling
- ✅ **Timezone support** for global deployments (Asia/Bangkok)
- ✅ **Flexible day selection** (any combination of days)
- ✅ **Same-day execution** - Ensures today's scheduled times run today
- ✅ Run-once mode for testing

### File Management
- ✅ **Smart file naming** - Uses query file name as prefix
  - Format: `{query_filename}_{timestamp}.csv`
  - Example: `schedule_db_query_20240115_083000.csv`
- ✅ **Timestamped filenames** for easy tracking
- ✅ **Automatic cleanup** of old files
- ✅ **Configurable retention period**
- ✅ **Always saves files** regardless of email setting

### Logging & Monitoring
- ✅ **Automatic log rotation**:
  - Size-based rotation via `RotatingFileHandler`
  - Configurable max size (`LOG_MAX_BYTES`, default 10MB)
  - Configurable backup count (`LOG_BACKUP_COUNT`, default 5)
  - Prevents disk space exhaustion
- ✅ **Schedule time tracking** in logs:
  - Shows which schedule time triggered each execution
  - Format: `⏰ Scheduled execution triggered at HH:MM`
- ✅ **Comprehensive execution logging**:
  - Query file path
  - Execution timestamp
  - Row count and file size
  - Past job cleanup operations
- ✅ **Debug mode** with enhanced logging

### Deployment Options
- ✅ **Docker & Docker Compose** support
- ✅ **Environment-based configuration**
- ✅ **Health checks** for containers
- ✅ **Volume persistence** for logs and outputs

## Maintenance
- **Regular dependency updates**
  - Update SQLAlchemy and other core packages
  - Review security advisories
- **Monitor log files**
  - Check log rotation is functioning (app.log, app.log.1, etc.)
  - Review ERROR and WARNING entries
  - Verify schedule time tracking logs
- **Monitor disk space**
  - Output directory (`/app/output/snapshots/`)
  - Log directory (`/app/logs/`)
  - Ensure log rotation prevents disk exhaustion
- **Clean up old CSV files**
  - Review retention period (`RETENTION_DAYS`)
  - Verify cleanup job is running
  - Archive important historical snapshots
- **Review and optimize SQL queries**
  - Update query files (`SQL_QUERY_FILE`)
  - Monitor query execution times
  - Optimize for performance
- **Validate scheduling**
  - Verify correct next run times displayed
  - Check multiple schedule times working
  - Review past job cleanup at startup
- **Email configuration**
  - Test email delivery periodically (when enabled)
  - Update credentials if needed
  - Verify EMAIL_ENABLED setting
- **Backup critical files**
  - `.env` configuration (store securely)
  - SQL query files
  - docker-compose.yml
  - Custom configuration files
- **Monitor container health**
  - Check Docker container status
  - Review resource usage
  - Verify volume mounts

## Known Issues & Troubleshooting

### Duplicate Execution Issue (RESOLVED)
**Issue**: Tasks were executing twice at the scheduled time
**Symptoms**: 
- Two CSV files generated with timestamps seconds apart
- Two email notifications sent for the same scheduled time
- Logs showing duplicate "⏰ Scheduled execution triggered" messages

**Root Cause**: The scheduler was creating multiple jobs for the same time slot when using day-specific scheduling (MON-FRI)

**Solution**: Implemented deduplication mechanism in `scheduler.py`:
- Added `task_executing` flag to prevent concurrent execution
- Added `last_execution_minute` tracking to prevent duplicate runs in the same minute
- Logs warning: "Skipping duplicate execution" when duplicate is detected

**How to Verify Fix**:
```bash
# Rebuild Docker image to pick up code changes
docker compose down
docker compose build --no-cache
docker compose up

# Watch for duplicate warnings in logs
docker compose logs -f | grep "Skipping duplicate"
```

### Email Configuration Issues
**Gmail Authentication**:
- Requires app-specific password (not regular password)
- Enable 2-factor authentication first
- Generate app password from Google Account settings

**Office365 Authentication**:
- Use regular email password
- Ensure account has SMTP enabled
- Check organization's security policies

**Common SMTP Errors**:
- `535 Authentication failed`: Wrong username/password
- `Connection refused`: Wrong SMTP host or port
- `TLS required`: Set `SMTP_USE_TLS=true`

### Docker Issues
**Container Not Picking Up Code Changes**:
```bash
# Force rebuild without cache
docker compose down
docker compose build --no-cache
docker compose up
```

**Volume Permission Issues**:
```bash
# Ensure directories exist and have correct permissions
mkdir -p logs output/snapshots
chmod 755 logs output
```

### Schedule Not Running
**Check Configuration**:
- Verify `SCHEDULE_ENABLED=true`
- Ensure time format is `HH:MM` (24-hour)
- Check timezone is correct (`SCHEDULE_TIMEZONE`)
- Verify days are correct (`SCHEDULE_DAYS`)

**Check Logs**:
```bash
docker compose logs -f | grep "Next scheduled run"
```

