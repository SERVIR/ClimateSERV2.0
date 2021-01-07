#!/usr/bin/env bash

# Activate the virtual python environment
#source /cserv2/python_environments/environments/py36_climateserv_2_env/bin/activate

cd /cserv2/django_app/ClimateSERV-2.0-Server

# Backfill all available of 2020 ESI 4 week
python3 manage.py start_etl_pipeline --etl_dataset_uuid xnxTq8BwKiTuWW58KicU --START_YEAR_YYYY 2020 --START_MONTH_MM 1 --END_YEAR_YYYY 2020 --END_MONTH_MM 11 --WEEKLY_JULIAN_START_OFFSET 0

# Backfill all available of 2020 ESI 12 week
python3 manage.py start_etl_pipeline --etl_dataset_uuid xnxTq8BwKiTuWW58KicU --START_YEAR_YYYY 2020 --START_MONTH_MM 1 --END_YEAR_YYYY 2020 --END_MONTH_MM 11 --WEEKLY_JULIAN_START_OFFSET 0



# Backfill NDVI
# # Cron Setup
# # Monthly, on the 18th of Every month at 2:33 server time, with logging of output
# # 33 14 18 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/backup_database.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)__backup_database.log 2>&1