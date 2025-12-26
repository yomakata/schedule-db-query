# Pre-Commit Security Checklist

Before pushing to git, ensure the following sensitive data is NOT included:

## ✅ Files Properly Ignored (Verified)

### Environment Files
- ✅ `.env` - Contains real database credentials and API keys
- ✅ `.env.local`, `.env.production`, `.env.staging` - Environment-specific configs
- ✅ `.env.example` - Safe to commit (contains placeholders only)

### SQL Query Files
- ✅ `config/*.sql` - May contain sensitive queries or database structure
- ✅ `config/sales_report.sql` - Production query (IGNORED)
- ✅ `config/local_directus.sql` - Local dev query (IGNORED)
- ✅ `config/queries.sql.example` - Safe template (COMMITTED)

### Log Files
- ✅ `logs/` directory - May contain sensitive data, errors with details
- ✅ `*.log` files - Application logs
- ✅ `*.log.*` files - Rotated log backups (app.log.1, app.log.2, etc.)

### Output Files
- ✅ `output/` directory - Contains exported data
- ✅ `*.csv` files - CSV exports with member data

### Python Cache
- ✅ `__pycache__/` directories
- ✅ `*.pyc` bytecode files

### Virtual Environment
- ✅ `venv/`, `env/`, `ENV/` - Virtual environment directories

## 🔍 Manual Verification Steps

### 1. Check for Hardcoded Credentials
```bash
# Search for potential hardcoded secrets
grep -r "password" --include="*.py" --include="*.yml" src/
grep -r "api_key" --include="*.py" --include="*.yml" src/
grep -r "secret" --include="*.py" --include="*.yml" src/
```

### 2. Review .env.example
- ✅ Contains only placeholder values (no real credentials)
- ✅ Includes clear comments and examples
- ✅ Documents all required environment variables

### 3. Verify Git Status
```bash
# Check what will be committed
git status

# Check ignored files
git status --ignored

# Dry run of git add
git add -n .
```

### 4. Review Staged Files
```bash
# List files to be committed
git diff --cached --name-only

# Review content of staged files
git diff --cached
```

## 📋 Safe to Commit

The following files/directories are safe to commit:

### Configuration Templates
- ✅ `.env.example` - Template with placeholders
- ✅ `config/queries.sql.example` - Example SQL query
- ✅ `config/settings.py` - Configuration loader (no secrets)
- ✅ `config/__init__.py` - Python package marker

### Source Code
- ✅ `src/*.py` - Application source code
- ✅ `tests/*.py` - Unit tests

### Documentation
- ✅ `README.md` - Main documentation
- ✅ `SPEC.md` - Technical specification
- ✅ `IMPLEMENTATION.md` - Implementation notes
- ✅ `docs/*.md` - Feature documentation

### Docker Configuration
- ✅ `Dockerfile` - Container image definition
- ✅ `docker-compose.yml` - Docker Compose configuration
- ✅ `.dockerignore` - Docker build ignore rules

### Project Files
- ✅ `.gitignore` - Git ignore rules
- ✅ `requirements.txt` - Python dependencies

## ⚠️ NEVER Commit

### Sensitive Data
- ❌ `.env` - Real credentials
- ❌ `config/*.sql` (except .example files) - Real queries
- ❌ `logs/` - Application logs with sensitive data
- ❌ `output/*.csv` - Exported data files

### Generated Files
- ❌ `__pycache__/` - Python bytecode
- ❌ `*.pyc`, `*.pyo` - Compiled Python files
- ❌ `.pytest_cache/` - Test cache

### Local Environment
- ❌ `venv/`, `env/` - Virtual environment
- ❌ `.vscode/`, `.idea/` - IDE settings (may contain local paths)

## 🚀 Ready to Commit

If all checks pass, you can safely commit:

```bash
# Stage all safe files
git add .

# Verify what's staged
git status

# Create commit
git commit -m "Initial commit: Schedule DB Query Tool"

# Push to remote
git push origin main
```

## 🔒 Additional Security Measures

### 1. Add Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Pre-commit hook to prevent committing sensitive files

if git diff --cached --name-only | grep -E "(\.env$|config/.*\.sql$)"; then
    echo "Error: Attempting to commit sensitive files!"
    echo "Blocked files:"
    git diff --cached --name-only | grep -E "(\.env$|config/.*\.sql$)"
    exit 1
fi

exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 2. Use Git Secrets Tool
```bash
# Install git-secrets
git secrets --install
git secrets --register-aws
```

### 3. Regular Audits
- Review committed files periodically
- Check for accidentally committed secrets
- Use tools like `truffleHog` or `GitGuardian`

## 📝 Commit Message Template

```
<type>: <short summary>

<detailed description>

Breaking Changes: <if any>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat: Add log rotation and smart file naming

- Implemented RotatingFileHandler for automatic log rotation
- Output files now named after SQL query file
- Added schedule time tracking in logs
- Fixed next run calculation for past times

Breaking Changes: None
```
