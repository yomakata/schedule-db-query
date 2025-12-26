# SQL Query File Configuration

## Overview

The `SQL_QUERY_FILE` environment variable allows you to specify a custom path to your SQL query file, providing flexibility in organizing and managing multiple query files.

## Configuration

### In `.env` file:

```env
SQL_QUERY_FILE=./config/queries.sql     # Path to SQL query file
```

## Supported Path Types

### 1. Relative Path (Recommended)
Relative to the project root directory:

```env
SQL_QUERY_FILE=./config/queries.sql
SQL_QUERY_FILE=./queries/member_report.sql
SQL_QUERY_FILE=./sql/custom_query.sql
```

### 2. Absolute Path
Full system path:

```env
# Windows
SQL_QUERY_FILE=C:/Projects/schedule-db-query/config/queries.sql

# Linux/Mac
SQL_QUERY_FILE=/app/config/queries.sql
```

## Use Cases

### Multiple Query Files

You can maintain different query files for different purposes:

```
config/
├── queries.sql                 # Default member snapshot query
├── queries_detailed.sql        # Detailed member report
├── queries_summary.sql         # Summary report
└── queries_custom.sql          # Custom query for special cases
```

Switch between them by updating the `.env` file:

```env
# Use detailed report
SQL_QUERY_FILE=./config/queries_detailed.sql

# Use summary report
SQL_QUERY_FILE=./config/queries_summary.sql
```

### Environment-Specific Queries

Different queries for different environments:

```
config/
├── queries_dev.sql             # Development environment
├── queries_uat.sql             # UAT environment
└── queries_prod.sql            # Production environment
```

Configuration:

```env
# Development
SQL_QUERY_FILE=./config/queries_dev.sql

# Production
SQL_QUERY_FILE=./config/queries_prod.sql
```

## Default Behavior

If `SQL_QUERY_FILE` is not specified, the system defaults to:

```
./config/queries.sql
```

## Error Handling

If the specified file doesn't exist, the application will:
1. Log an error message
2. Raise a `FileNotFoundError` with the full path
3. Exit gracefully

Example error message:
```
ERROR - Query file not found: /app/config/queries_missing.sql
FileNotFoundError: Query file not found: /app/config/queries_missing.sql
```

## Best Practices

1. **Use Relative Paths**: Easier to maintain across different environments
2. **Version Control**: Keep query files in version control
3. **Naming Convention**: Use descriptive names (e.g., `queries_member_snapshot.sql`)
4. **Documentation**: Add comments in SQL files explaining the query purpose
5. **Testing**: Always test query files before deployment

## Examples

### Example 1: Default Configuration

```env
# Uses default: ./config/queries.sql
# SQL_QUERY_FILE=./config/queries.sql
```

### Example 2: Custom Query File

```env
SQL_QUERY_FILE=./config/queries_detailed_member_report.sql
```

### Example 3: Shared Query Directory

```env
# Shared queries directory
SQL_QUERY_FILE=./shared/queries/member_snapshot.sql
```

## Docker Configuration

When using Docker, ensure the query file is accessible inside the container.

### docker-compose.yml:
```yaml
services:
  schedule-db-query:
    volumes:
      - ./config:/app/config  # Mount config directory
      - ./queries:/app/queries  # Mount custom queries directory
```

### .env:
```env
SQL_QUERY_FILE=./queries/custom_member_report.sql
```

## Verification

To verify the correct query file is being loaded, check the application logs:

```
INFO - Loading SQL query from: /app/config/queries_detailed.sql
INFO - Loaded query from /app/config/queries_detailed.sql
```

## Troubleshooting

### Issue: File Not Found

**Problem**: `FileNotFoundError: Query file not found: ...`

**Solutions**:
1. Check the file path is correct
2. Verify the file exists
3. Check file permissions
4. If using Docker, ensure the file is mounted correctly

### Issue: Wrong Query Executed

**Problem**: The application runs but uses the wrong query

**Solutions**:
1. Verify `.env` has the correct `SQL_QUERY_FILE` value
2. Restart the application after changing `.env`
3. Check logs for "Loading SQL query from: ..." message
4. If using Docker, rebuild the container: `docker-compose up --build -d`

## Related Configuration

- `OUTPUT_DIR`: Where CSV files are saved
- `FILE_PREFIX`: Prefix for output files
- `LOG_FILE`: Where application logs are written

See [README.md](../README.md) for full configuration options.
