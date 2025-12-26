# Schedule DB Query

A robust Python-based automation tool that executes SQL queries against remote databases on a scheduled basis, exports results to CSV files, and delivers them via email. Features intelligent file naming, automatic log rotation, comprehensive schedule tracking, and duplicate execution prevention.

## ✨ Key Features

- 🗄️ **Multi-Database Support**: Connect to MySQL, PostgreSQL, or SQL Server with SQLAlchemy
- 🔐 **Secure Configuration**: All sensitive data stored in `.env` file (never committed)
- ⏰ **Flexible Scheduling**: Multiple times per day, custom days, timezone support
- �️ **Duplicate Prevention**: Built-in deduplication prevents double execution
- 📊 **Smart CSV Export**: Auto-named files based on query file with timestamp
- 📧 **Multi-Provider Email**: Support for Gmail, Office365, and custom SMTP (optional)
- 🔄 **Automatic Log Rotation**: Size-based rotation prevents disk space issues
- 🐳 **Docker Ready**: Full Docker and Docker Compose support
- 📝 **Comprehensive Logging**: Track execution with schedule time tracking and debug info
- 🔧 **Command Line Tools**: Test database, email, or run once without scheduling

## 🎯 Use Cases

- Daily/weekly database snapshots
- Automated reporting to stakeholders
- Scheduled data exports for analytics
- Regular backup of critical data
- Compliance and audit trail generation

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **Git** for cloning the repository
- **Database Access**: MySQL, PostgreSQL, or SQL Server with read permissions
- **SMTP Account** (optional): Gmail, Office365, or custom SMTP server
- **Docker & Docker Compose** (optional, for containerized deployment)

### Installation

#### Method 1: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yomakata/schedule-db-query.git
   cd schedule-db-query
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual credentials
   # Windows: notepad .env
   # Linux/Mac: nano .env
   ```

5. **Create your SQL query file**
   ```bash
   # Edit the default query file
   # Or create a new one and update SQL_QUERY_FILE in .env
   nano config/queries.sql
   ```

6. **Test your configuration**
   ```bash
   # Test database connection
   python src/main.py --test-db
   
   # Test email configuration (if enabled)
   python src/main.py --test-email
   
   # Run once to verify everything works
   python src/main.py --run-once
   ```

#### Method 2: Docker Deployment (Recommended for Production)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yomakata/schedule-db-query.git
   cd schedule-db-query
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your credentials
   ```

3. **Build and run**
   ```bash
   # Build the Docker image
   docker compose build
   
   # Start the container in detached mode
   docker compose up -d
   
   # View logs
   docker compose logs -f
   ```

4. **Verify it's running**
   ```bash
   # Check container status
   docker compose ps
   
   # View recent logs
   docker compose logs --tail=50
   ```

## 📖 Usage

### Command Line Options

The application supports several command-line modes:

#### Run Once (Immediate Execution)
Execute the query immediately without scheduling:
```bash
python src/main.py --run-once
```
**Use case**: Testing, manual execution, one-time reports

#### Run with Scheduler (Default)
Start the scheduler and run at configured times:
```bash
python src/main.py --schedule
# or simply
python src/main.py
```
**Use case**: Production automated scheduling

#### Test Database Connection
Verify database configuration and connectivity:
```bash
python src/main.py --test-db
```
**Output**: Connection status, database info, sample query execution

#### Test Email Configuration
Test email settings and send a test email:
```bash
python src/main.py --test-email
```
**Note**: Only works when `EMAIL_ENABLED=true` in `.env`

### Docker Commands

#### Start the Service
```bash
# Start in background
docker compose up -d

# Start with logs visible
docker compose up
```

#### View Logs
```bash
# Follow logs in real-time
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Filter for specific patterns
docker compose logs -f | grep "⏰ Scheduled execution"
docker compose logs -f | grep ERROR
```

#### Stop the Service
```bash
# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

#### Restart After Config Changes
```bash
# If you only changed .env (Docker Compose auto-loads it)
docker compose restart

# If you changed Python code (rebuild required)
docker compose down
docker compose build --no-cache
docker compose up -d
```

#### Run One-Time Execution in Docker
```bash
docker compose run --rm schedule-db-query python src/main.py --run-once
```

#### Test Configuration in Docker
```bash
# Test database
docker compose run --rm schedule-db-query python src/main.py --test-db

# Test email
docker compose run --rm schedule-db-query python src/main.py --test-email
```

#### Access Container Shell
```bash
docker compose exec schedule-db-query /bin/bash

# View files inside container
docker compose exec schedule-db-query ls -la /app/output/snapshots/
docker compose exec schedule-db-query ls -la /app/logs/
```

## ⚙️ Configuration

### Environment Variables (.env)

All configuration is managed through the `.env` file. **Never commit this file to version control!**

#### Database Configuration

```env
# Database Type (mysql, postgresql, sqlserver)
DB_TYPE=mysql
DB_HOST=your-database-host.com
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

**Supported Database Types:**
- `mysql` - Requires `pymysql` (included in requirements.txt)
- `postgresql` - Requires `psycopg2-binary` (included in requirements.txt)
- `sqlserver` - Requires `pyodbc` (optional, install separately if needed)

#### Email Configuration

**Option 1: Gmail SMTP**
```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password        # Use app-specific password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
EMAIL_CC=
EMAIL_BCC=
```

**Option 2: Office365/Outlook SMTP**
```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@yourdomain.com
SMTP_PASSWORD=your-regular-password    # Use regular password
EMAIL_FROM=your-email@yourdomain.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
EMAIL_CC=
EMAIL_BCC=
```

**Option 3: Disable Email**
```env
EMAIL_ENABLED=false
# No need to configure SMTP settings
# CSV files will still be saved to output directory
```

#### Schedule Configuration

```env
SCHEDULE_ENABLED=true

# Single time
SCHEDULE_TIME=08:00

# Multiple times per day (comma-separated)
SCHEDULE_TIME=08:00,12:00,18:00

# Timezone (important for accurate scheduling)
SCHEDULE_TIMEZONE=Asia/Bangkok         # Use your timezone

# Days to run (any combination)
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI      # Weekdays only
# SCHEDULE_DAYS=MON,TUE,WED,THU,FRI,SAT,SUN  # Every day
# SCHEDULE_DAYS=MON,WED,FRI             # Specific days
```

**Time Format:** 24-hour format `HH:MM` (e.g., `08:00`, `14:30`, `23:45`)

**Timezone Examples:**
- `Asia/Bangkok` - Bangkok, Thailand
- `Asia/Shanghai` - China
- `Asia/Tokyo` - Japan
- `America/New_York` - US Eastern
- `Europe/London` - UK
- [Full list of timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

#### Query Configuration

```env
# Path to your SQL query file (relative or absolute)
SQL_QUERY_FILE=./config/queries.sql

# Examples of other configurations:
# SQL_QUERY_FILE=./config/member_snapshot.sql
# SQL_QUERY_FILE=./queries/daily_report.sql
# SQL_QUERY_FILE=/app/config/production_query.sql
```

**Note:** The output CSV files will be automatically named based on your query file name.
- `queries.sql` → `queries_2025-12-26_140530.csv`
- `member_snapshot.sql` → `member_snapshot_2025-12-26_140530.csv`

#### Export Configuration

```env
OUTPUT_DIR=./output/snapshots
FILE_PREFIX=member_snapshot            # Deprecated: now uses query file name
FILE_RETENTION_DAYS=30                 # Delete files older than N days (0 = never delete)
CSV_ENCODING=utf-8                     # CSV encoding
```

#### Logging Configuration

```env
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/app.log
LOG_MAX_BYTES=10485760                 # 10MB per log file
LOG_BACKUP_COUNT=5                     # Keep 5 backup files (app.log.1 to app.log.5)
```

**Log Rotation Example:**
- Main log: `app.log` (up to 10MB)
- When full, rotates to: `app.log.1`
- Next rotation: `app.log.1` → `app.log.2`, etc.
- Keeps up to 5 backups, deletes oldest when limit reached

### Email Provider Setup

#### Gmail Setup

Gmail requires an **App Password** for security:

1. **Enable 2-Factor Authentication**
   - Go to Google Account → Security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other" as the device, name it "Schedule DB Query"
   - Copy the generated 16-character password

3. **Update .env**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # The 16-char app password
   ```

#### Office365/Outlook Setup

Office365 uses your regular email password:

1. **Verify SMTP is enabled**
   - Check with your IT admin if using corporate Office365
   - Personal Outlook.com accounts have SMTP enabled by default

2. **Update .env**
   ```env
   SMTP_HOST=smtp.office365.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   SMTP_USERNAME=your-email@yourdomain.com
   SMTP_PASSWORD=your-regular-password
   ```

#### Custom SMTP Server

For other email providers:
```env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587                          # or 465 for SSL
SMTP_USE_TLS=true                      # or false if using SSL
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Project Structure

```
schedule-db-query/
├── .env                    # Environment variables (not in git)
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── README.md               # This file
├── SPEC.md                 # Detailed specification
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuration loader
│   └── queries.sql         # SQL query templates
├── src/
│   ├── __init__.py
│   ├── main.py             # Main entry point
│   ├── database.py         # Database connection and query
│   ├── exporter.py         # CSV export functionality
│   ├── emailer.py          # Email sending functionality
│   └── scheduler.py        # Scheduling logic
├── logs/                   # Application logs
├── output/                 # Generated CSV files
└── tests/                  # Unit tests
```

## Example SQL Query

Edit `config/queries.sql` with your query:

```sql
SELECT 
    member_id,
    member_name,
    email,
    registration_date,
    status
FROM 
    members
WHERE 
    status = 'active'
ORDER BY 
    registration_date DESC;
```

## Testing

Run unit tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Scheduling

The application supports multiple scheduling patterns:

- **Daily**: Set `SCHEDULE_DAYS=MON,TUE,WED,THU,FRI,SAT,SUN`
- **Weekdays only**: Set `SCHEDULE_DAYS=MON,TUE,WED,THU,FRI`
- **Specific days**: Set `SCHEDULE_DAYS=MON,WED,FRI`
- **Custom time**: Set `SCHEDULE_TIME=14:30` for 2:30 PM

## Logging

Logs are stored in the directory specified by `LOG_FILE` (default: `./logs/app.log`)

Log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about execution
- **WARNING**: Warning messages
- **ERROR**: Error messages

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Duplicate Execution (Tasks Running Twice)

**Symptoms:**
- Two CSV files generated seconds apart
- Two emails received for the same scheduled time
- Logs show duplicate "⏰ Scheduled execution triggered" messages

**Solution:**
This issue has been fixed in recent versions. If you're experiencing this:

```bash
# Rebuild Docker image without cache
docker compose down
docker compose build --no-cache
docker compose up -d

# Check logs for "Skipping duplicate execution" warnings
docker compose logs -f | grep "duplicate"
```

The fix includes:
- Deduplication mechanism in scheduler
- `task_executing` flag prevents concurrent runs
- `last_execution_minute` tracking prevents same-minute duplicates

#### 2. Database Connection Issues

**Symptoms:**
- "Cannot connect to database" errors
- "Connection refused" errors
- Timeout errors

**Solutions:**

**Check database credentials:**
```bash
python src/main.py --test-db
```

**Common fixes:**
```env
# Ensure correct database type
DB_TYPE=mysql  # not MySQL or MYSQL

# Check host format
DB_HOST=192.168.1.100  # Not http://192.168.1.100
DB_HOST=db.example.com # Not db.example.com:3306

# Port must be a number
DB_PORT=3306  # Not "3306"

# For Docker, use host.docker.internal for localhost
DB_HOST=host.docker.internal  # Instead of localhost or 127.0.0.1
```

**Network/Firewall checks:**
```bash
# Test connectivity (outside container)
telnet your-db-host.com 3306
# or
nc -zv your-db-host.com 3306

# From Docker container
docker compose exec schedule-db-query telnet your-db-host.com 3306
```

#### 3. Email Sending Issues

**Symptoms:**
- "Authentication failed" errors
- "Connection refused" errors
- No emails being sent

**Solutions:**

**Test email configuration:**
```bash
python src/main.py --test-email
```

**Gmail specific:**
```env
# Make sure you're using App Password, not regular password
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-character app password

# Common Gmail settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

**Office365 specific:**
```env
# Use regular password (no app password needed)
SMTP_PASSWORD=your-regular-password

# Correct host
SMTP_HOST=smtp.office365.com  # Not smtp.outlook.com for Office365
SMTP_PORT=587
SMTP_USE_TLS=true

# Username must be full email
SMTP_USERNAME=user@yourdomain.com  # Not just 'user'
```

**Debug email issues:**
```env
# Enable debug logging
LOG_LEVEL=DEBUG

# Check if EMAIL_ENABLED is true
EMAIL_ENABLED=true

# Verify all email fields are set
EMAIL_FROM=your-email@domain.com
EMAIL_TO=recipient@example.com
```

#### 4. Scheduler Not Running

**Symptoms:**
- Application starts but doesn't execute at scheduled time
- No "Next scheduled run" message in logs

**Solutions:**

**Check configuration:**
```env
# Ensure scheduling is enabled
SCHEDULE_ENABLED=true

# Verify time format (24-hour, HH:MM)
SCHEDULE_TIME=08:00  # Correct
# SCHEDULE_TIME=8:00   # Incorrect (missing leading zero)
# SCHEDULE_TIME=8am    # Incorrect (not 24-hour format)

# Check timezone
SCHEDULE_TIMEZONE=Asia/Bangkok  # Must be valid timezone

# Verify days
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI  # Correct
# SCHEDULE_DAYS=Mon,Tue,Wed         # Incorrect (use uppercase)
```

**Check logs:**
```bash
# Look for schedule setup
docker compose logs | grep "Schedule times"
docker compose logs | grep "Next scheduled run"

# Check for errors
docker compose logs | grep ERROR
```

#### 5. Docker Container Not Picking Up Changes

**Symptoms:**
- Code changes not reflected in running container
- .env changes not applied

**Solutions:**

**For .env changes:**
```bash
# Docker Compose auto-loads .env, just restart
docker compose restart
```

**For code changes:**
```bash
# Must rebuild image
docker compose down
docker compose build --no-cache
docker compose up -d
```

**For Docker Compose configuration changes:**
```bash
docker compose down
docker compose up -d
```

#### 6. Permission Denied Errors

**Symptoms:**
- Cannot write to logs/
- Cannot write to output/
- File permission errors

**Solutions:**

**Local development:**
```bash
# Linux/Mac: Ensure directories exist and are writable
mkdir -p logs output/snapshots
chmod 755 logs output

# Windows: Run as administrator or check folder permissions
```

**Docker:**
```bash
# Create directories before starting
mkdir -p logs output/snapshots

# Check volume mounts in docker-compose.yml
volumes:
  - ./logs:/app/logs
  - ./output:/app/output
```

#### 7. Log Files Growing Too Large

**Solution:**

Configure log rotation in `.env`:
```env
LOG_MAX_BYTES=10485760    # 10MB per file
LOG_BACKUP_COUNT=5         # Keep 5 backups

# For more frequent rotation:
LOG_MAX_BYTES=5242880     # 5MB per file
LOG_BACKUP_COUNT=10        # Keep 10 backups
```

Verify rotation is working:
```bash
ls -lh logs/
# You should see: app.log, app.log.1, app.log.2, etc.
```

#### 8. CSV Files Not Being Generated

**Symptoms:**
- No files in output directory
- Query executes but no CSV created

**Solutions:**

**Check query file:**
```bash
# Verify query file exists
ls -la config/

# Check SQL_QUERY_FILE path in .env
SQL_QUERY_FILE=./config/queries.sql  # Must be correct path
```

**Check output directory:**
```env
OUTPUT_DIR=./output/snapshots  # Ensure directory exists
```

**Check logs for errors:**
```bash
docker compose logs | grep "Exporting"
docker compose logs | grep ERROR
```

**Test manually:**
```bash
python src/main.py --run-once
# Check output/snapshots/ for new file
```

### Getting Help

**Check logs:**
```bash
# Docker
docker compose logs -f --tail=100

# Local
tail -f logs/app.log
```

**Enable debug mode:**
```env
LOG_LEVEL=DEBUG
```

**Review documentation:**
- See [SPEC.md](SPEC.md) for detailed specifications
- Check [docs/](docs/) folder for specific guides

**Still having issues?**
1. Check logs at `./logs/app.log`
2. Run with `--test-db` and `--test-email` flags
3. Enable DEBUG logging
4. Review error messages in logs

## Production Deployment

### Option 1: Docker Compose (Recommended)

```bash
# On production server
cd /opt/schedule-db-query
cp .env.example .env
nano .env  # Edit with production credentials

docker-compose up -d
docker-compose logs -f --tail=100
```

### Option 2: Systemd Service (Linux)

**Advantages:**
- Native Linux service integration
- No Docker overhead
- Systemd management

**Setup:**

1. **Install application:**
   ```bash
   cd /opt
   git clone https://github.com/yomakata/schedule-db-query.git
   cd schedule-db-query
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   cp .env.example .env
   nano .env
   ```

2. **Create service file:**
   ```bash
   sudo nano /etc/systemd/system/schedule-db-query.service
   ```

3. **Service content:**
   ```ini
   [Unit]
   Description=Schedule DB Query Service
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   Group=your-group
   WorkingDirectory=/opt/schedule-db-query
   Environment="PATH=/opt/schedule-db-query/venv/bin"
   ExecStart=/opt/schedule-db-query/venv/bin/python src/main.py --schedule
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable schedule-db-query
   sudo systemctl start schedule-db-query
   sudo systemctl status schedule-db-query
   
   # View logs
   sudo journalctl -u schedule-db-query -f
   ```

## 🛠️ Maintenance

### Regular Tasks

**Daily:** Monitor logs, verify executions
**Weekly:** Check disk space, review log sizes
**Monthly:** Update dependencies, optimize queries

### Monitoring

```bash
# Check service status
docker compose ps

# Monitor logs
docker compose logs -f --tail=100

# Check disk usage
du -sh logs/ output/
```

### Backups

```bash
# Backup important files
cp .env .env.backup
tar czf config-backup.tar.gz config/
tar czf output-backup.tar.gz output/
```

## 👥 For Developers

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yomakata/schedule-db-query.git
cd schedule-db-query
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure for development
cp .env.example .env
nano .env

# Run tests
pytest tests/ -v
```

### Project Structure

```
schedule-db-query/
├── config/          # SQL queries and settings
├── src/             # Source code
├── tests/           # Unit tests
├── docs/            # Documentation
├── logs/            # Log files (gitignored)
└── output/          # CSV outputs (gitignored)
```

### Adding Features

1. Create feature branch
2. Make changes
3. Add tests
4. Update documentation
5. Submit pull request

See [SPEC.md](SPEC.md) for architecture details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

Copyright © 2025. All rights reserved.

## 📞 Support

- **Issues**: Check `./logs/app.log`
- **Documentation**: See [SPEC.md](SPEC.md) and [docs/](docs/)
- **Troubleshooting**: Review sections above

## 🔗 Additional Resources

- [SPEC.md](SPEC.md) - Technical specification
- [docs/LOG_ROTATION.md](docs/LOG_ROTATION.md) - Log rotation guide
- [docs/SQL_QUERY_FILE_CONFIGURATION.md](docs/SQL_QUERY_FILE_CONFIGURATION.md) - Query setup
- [docs/OUTPUT_FILE_NAMING.md](docs/OUTPUT_FILE_NAMING.md) - File naming

---

**Built with ❤️ for automated database reporting**
