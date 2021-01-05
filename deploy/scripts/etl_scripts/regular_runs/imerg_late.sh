#!/usr/bin/env bash

# Description:
# # Script to update the THREDDS server with the IMERG Late product data on a regular basis.
#


# Dataset ID and Path
DATASET_ID="ggmNzrqfavjRPgyU2N2W"   # PROD
cd /cserv2/django_app/ClimateSERV-2.0-Server
#DATASET_ID="uGG9pqNfU4nk7FGZJpGj"   # DEV

# Date Variables and Calculations
#i=1
i=1
#MULTIPLE=10
MULTIPLE=1
j=`expr $i - 1`
EARLIEST_DAY_SUBTRACTOR=`expr $i \* $MULTIPLE`
LATEST_DAY_SUBTRACTOR=`expr $j \* $MULTIPLE`
#
# Debug
#echo " EARLIEST_DAY_SUBTRACTOR: $EARLIEST_DAY_SUBTRACTOR"
#echo " LATEST_DAY_SUBTRACTOR: $LATEST_DAY_SUBTRACTOR"
#
CURRENT_DATE=`date`
#
# Linux Version (PROD)
EARLIEST_YEAR=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%Y`
EARLIEST_MONTH=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%m`
EARLIEST_DAY=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%d`
LATEST_YEAR=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%Y`
LATEST_MONTH=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%m`
LATEST_DAY=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%d`

# Mac Version (DEV) - There is some difference between Mac Shell and Linux Server Shell which requires this to be different
#EARLIEST_YEAR=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%Y"`
#EARLIEST_MONTH=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%m"`
#EARLIEST_DAY=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%d"`
#LATEST_YEAR=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%Y"`
#LATEST_MONTH=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%m"`
#LATEST_DAY=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%d"`

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN 01 --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN 48"

echo ""
echo "i=$i, j=$j"
echo " EARLIEST DATE:   year, month, day: $EARLIEST_YEAR - $EARLIEST_MONTH - $EARLIEST_DAY "
echo " LATEST DATE:     year, month, day: $LATEST_YEAR - $LATEST_MONTH - $LATEST_DAY "
echo " ABOUT TO RUN COMMAND:  $COMMAND"
echo ""

$COMMAND


# Cron Setup
# Daily (Imerg Early: 17:45 Servertime (est)) (Imerg Late: 18:35 Servertime (est))
# # 45 17 * * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/imerg_early.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)_etl__regular_runs__imerg_early.log 2>&1
# # 35 18 * * * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/imerg_late.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)_etl__regular_runs__imerg_late.log 2>&1


