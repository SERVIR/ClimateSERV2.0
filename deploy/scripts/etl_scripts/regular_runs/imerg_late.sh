#!/usr/bin/env bash

# Description:
# # Script to update the THREDDS server with the IMERG Late product data on a regular basis.
#


# Dataset ID and Path
DATASET_ID="ggmNzrqfavjRPgyU2N2W"
cd /cserv2/django_app/ClimateSERV-2.0-Server || exit


CURRENT=$(date)

EARLIEST_YEAR=$(date -d "$CURRENT - 1 days" +%Y)
EARLIEST_MONTH=$(date -d "$CURRENT - 1 days" +%m)
EARLIEST_DAY=$(date -d "$CURRENT - 1 days" +%d)
LATEST_YEAR=$(date -d "$CURRENT" +%Y)
LATEST_MONTH=$(date -d "$CURRENT" +%m)
LATEST_DAY=$(date -d "$CURRENT" +%d)


COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN 01 --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN 48"

echo ""
echo " ABOUT TO RUN COMMAND:  $COMMAND"
echo ""

$COMMAND


# Cron Setup
# Daily (Imerg Early: 17:45 Servertime (est)) (Imerg Late: 18:35 Servertime (est))
# # 45 17 * * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/imerg_early.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)_etl__regular_runs__imerg_early.log 2>&1
# # 35 18 * * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/imerg_late.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)_etl__regular_runs__imerg_late.log 2>&1


