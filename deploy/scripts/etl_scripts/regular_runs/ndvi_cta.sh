#!/usr/bin/env bash

# Description:
# # Script to update the THREDDS server with the NDVI Central Asia product data on a regular basis.
#
# Data Range:
# # This script takes whatever current month we are in and gets data it can find from the previous month and the current month.
# # So if we are in November, the month range will be from months 10 to 11.
#
# Schedule Notes:
# # This script is called by 3 different monthly crontab triggers so that each of the dekadal dates get pulled in.

# Dataset ID and Path
DATASET_ID="M55Fg5mJuEWJLYRFSmGA"   # PROD
cd /cserv2/django_app/ClimateSERV-2.0-Server
#DATASET_ID="M55Fg5mJuEWJLYRFSmGA"   # DEV

# Date Variables
CURRENT_YEAR=`date "+%Y"`
CURRENT_MONTH=`date "+%m"`
PREVIOUS_YEAR=`expr $CURRENT_YEAR - 1`
PREVIOUS_MONTH=`expr $CURRENT_MONTH - 1`

START_YEAR=$CURRENT_YEAR
START_MONTH=$PREVIOUS_MONTH
END_YEAR=$CURRENT_YEAR
END_MONTH=$CURRENT_MONTH

# check for condition of equal to 1
#if [[ "$CURRENT_MONTH" == 1 ]]; then
if [[ "$CURRENT_MONTH" == "01" ]]; then
echo "The Current Month is 1 (Jan), so the previous month needs to be set to 12"
PREVIOUS_MONTH=12
START_YEAR=$PREVIOUS_YEAR
START_MONTH=$PREVIOUS_MONTH
else
echo "The Current Month is NOT 1 (Not Jan) - No change to the above variable assignment"
fi

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $START_YEAR --START_MONTH_MM $START_MONTH --END_YEAR_YYYY $END_YEAR --END_MONTH_MM $END_MONTH --REGION_CODE cta"

# Check Variables for this run
echo ""
echo "Debug Variables (after checking and adjusting for the condition that the current month is Jan (1)): "
echo "  START_YEAR: $START_YEAR"
echo "  START_MONTH: $START_MONTH"
echo "  END_YEAR: $END_YEAR"
echo "  END_MONTH: $END_MONTH"
echo "  DATASET_ID: $DATASET_ID"
echo "  COMMAND: $COMMAND"
echo ""

# Execute the Script
echo "Running $COMMAND now"
$COMMAND

# Cron Setup
# Monthly (3 different schedules per NDVI Product to catch each of the dekadal chunks)
#
# wa - West Africa
# # 02 18 02 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_wa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_wa.log 2>&1
# # 02 18 12 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_wa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_wa.log 2>&1
# # 02 18 22 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_wa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_wa.log 2>&1
#
# ea - East Africa
# # 23 18 02 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_ea.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_ea.log 2>&1
# # 23 18 12 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_ea.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_ea.log 2>&1
# # 23 18 22 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_ea.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_ea.log 2>&1
#
# sa - Southern Africa
# # 54 18 02 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_sa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_sa.log 2>&1
# # 54 18 12 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_sa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_sa.log 2>&1
# # 54 18 22 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_sa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_sa.log 2>&1
#
# cta - Central Asia
# # 27 19 02 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_cta.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_cta.log 2>&1
# # 27 19 12 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_cta.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_cta.log 2>&1
# # 27 19 22 * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ndvi_cta.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ndvi_cta.log 2>&1
