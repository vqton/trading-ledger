# Deployment Guide

## Prerequisites

- Python 3.12+
- Nginx
- Gunicorn
- SQLite (or PostgreSQL for production)

## Development Setup

```bash
cd /mnt/e/acct/accounting_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
flask run
```

## Production Deployment

### 1. Install Dependencies

```bash
pip install gunicorn
```

### 2. Configure Environment

```bash
export SECRET_KEY="your-secure-secret-key"
export LOG_LEVEL="warning"
```

### 3. Start Gunicorn

```bash
gunicorn -c gunicorn_config.py app:app
```

Or with systemd:

```ini
# /etc/systemd/system/accounting.service
[Unit]
Description=VAS Accounting App

[Service]
User=www-data
Group=www-data
WorkingDirectory=/mnt/e/acct/accounting_app
Environment="PATH=/mnt/e/acct/accounting_app/venv/bin"
ExecStart=/mnt/e/acct/accounting_app/venv/bin/gunicorn -c /mnt/e/acct/accounting_app/gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Configure Nginx

```bash
sudo cp nginx.conf /etc/nginx/sites-available/accounting
sudo ln -s /etc/nginx/sites-available/accounting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Setup Backup (Cron)

```bash
chmod +x /mnt/e/acct/accounting_app/backup/daily_backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /mnt/e/acct/accounting_app/backup/daily_backup.sh
```

## Testing

```bash
pytest
```

## File Structure

```
accounting_app/
├── app.py                 # Flask application
├── config.py              # Configuration
├── gunicorn_config.py     # Gunicorn config
├── nginx.conf             # Nginx config
├── requirements.txt        # Dependencies
├── backup/
│   └── daily_backup.sh    # Daily backup script
└── ...
```
