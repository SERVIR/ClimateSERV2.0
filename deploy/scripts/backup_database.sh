#!/usr/bin/env bash

echo "About to backup the django app sqlite database."
DATE_BASE_STRING=`date "+%Y_%m_%d_%H%M_%S"`
DB_BACKUP_FULL_FILE_PATH="/cserv2/db_backups/db_"${DATE_BASE_STRING}".sqlite3.bak"
sqlite3 /cserv2/django_app/ClimateSERV-2.0-Server/db/db.sqlite3 ".backup ${DB_BACKUP_FULL_FILE_PATH}"
echo "Database backed up to: ${DB_BACKUP_FULL_FILE_PATH}"

# # Cron Setup
# # Monthly, on the 18th of Every month at 2:33 server time, with logging of output
# # 33 14 18 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/backup_database.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)__backup_database.log 2>&1