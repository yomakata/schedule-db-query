# Schedule DB Query

A Python-based automation tool that executes SQL queries against a remote database on a scheduled basis, exports results to CSV files, and delivers them via email.

## Features

- 🗄️ **Database Query Execution**: Connect to MySQL/PostgreSQL/SQL Server and execute configurable SQL queries
- 🔐 **Secure Configuration**: All sensitive data stored in `.env` file
- ⏰ **Scheduled Execution**: Automated runs with flexible scheduling (daily, weekly, custom)
- 📊 **CSV Export**: Export query results with timestamps and automatic cleanup
- � **Smart File Naming**: Output files automatically named after the SQL query file
- �📧 **Email Delivery**: Send CSV files as attachments with detailed reports
- � **Log Rotation**: Automatic log file rotation to prevent disk space issues
- �🐳 **Docker Support**: Run in containers with Docker Compose
- 📝 **Comprehensive Logging**: Track execution with detailed logs and schedule time tracking

## Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL/PostgreSQL/SQL Server database access
- SMTP email account (Gmail, Outlook, etc.)

### Installation

1. **Clone the repository**
   ```bash
   cd c:\Projects\schedule-db-query
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

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and email credentials
   ```

5. **Update SQL query**
   - Edit `config/queries.sql` with your actual SQL query

### Usage

#### Run Once (No Scheduling)
```bash
python src/main.py --run-once
```

#### Test Database Connection
```bash
python src/main.py --test-db
```

#### Test Email Configuration
```bash
python src/main.py --test-email
```

#### Run with Scheduler
```bash
python src/main.py --schedule
```

### Docker Deployment

#### Using Docker Compose (Recommended)

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Build and run**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop container**
   ```bash
   docker-compose down
   ```

#### Run One-Time with Docker
```bash
docker-compose run --rm schedule-db-query python src/main.py --run-once
```

## Configuration

### Environment Variables (.env)

```env
# Database Configuration
DB_TYPE=mysql                           # Database type (mysql, postgresql, sqlserver)
DB_HOST=your-database-host.com          # Database host
DB_PORT=3306                            # Database port
DB_NAME=your_database_name              # Database name
DB_USER=your_username                   # Database username
DB_PASSWORD=your_password               # Database password

# Email Configuration
SMTP_HOST=smtp.gmail.com                # SMTP server host
SMTP_PORT=587                           # SMTP port
SMTP_USE_TLS=true                       # Use TLS (true/false)
SMTP_USERNAME=your-email@gmail.com      # SMTP username
SMTP_PASSWORD=your-app-password         # SMTP password or app password
EMAIL_FROM=your-email@gmail.com         # From address
EMAIL_TO=recipient@example.com          # To addresses (comma-separated)
EMAIL_CC=                               # CC addresses (optional)
EMAIL_BCC=                              # BCC addresses (optional)

# Schedule Configuration
SCHEDULE_ENABLED=true                   # Enable scheduling
SCHEDULE_TIME=08:00,12:00,18:00         # Times to run (comma-separated, HH:MM format)
SCHEDULE_TIMEZONE=Asia/Shanghai         # Timezone
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI      # Days to run

# Query Configuration
SQL_QUERY_FILE=./config/queries.sql     # Path to SQL query file (relative or absolute)

# Export Configuration
OUTPUT_DIR=./output/snapshots            # Output directory
FILE_PREFIX=member_snapshot              # File prefix (deprecated: now uses query file name)
FILE_RETENTION_DAYS=30                   # Keep files for N days
CSV_ENCODING=utf-8                       # CSV encoding

# Logging Configuration
LOG_LEVEL=INFO                          # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=./logs/app.log                 # Log file path
LOG_MAX_BYTES=10485760                  # Max log file size in bytes (10MB default)
LOG_BACKUP_COUNT=5                      # Number of backup log files to keep
```

### Gmail SMTP Setup

For Gmail, you need to use an **App Password**:

1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use the generated password in `SMTP_PASSWORD`

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

## Troubleshooting

### Database Connection Issues

1. Verify database credentials in `.env`
2. Check network connectivity
3. Ensure database port is accessible
4. Test connection: `python src/main.py --test-db`

### Email Sending Issues

1. Verify SMTP credentials
2. Check if using app password (for Gmail)
3. Verify SMTP port and TLS settings
4. Test email: `python src/main.py --test-email`

### Permission Issues

Ensure the application has write permissions for:
- `logs/` directory
- `output/` directory

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

Create `/etc/systemd/system/schedule-db-query.service`:

```ini
[Unit]
Description=Schedule DB Query
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/schedule-db-query
Environment="PATH=/opt/schedule-db-query/venv/bin"
ExecStart=/opt/schedule-db-query/venv/bin/python src/main.py --schedule
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable schedule-db-query
sudo systemctl start schedule-db-query
sudo systemctl status schedule-db-query
```

## Contributing

See [SPEC.md](SPEC.md) for detailed development specification.

## License

Copyright © 2025. All rights reserved.

## Support

For issues or questions, contact the system administrator or check the logs at `./logs/app.log`.
