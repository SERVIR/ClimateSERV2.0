#!/usr/bin/env bash

# Description:
# # Script to update the THREDDS server with the chirp_global_0_05deg_1dy product data on a regular basis.
#
# Data Range:
# # This script takes whatever current month we are in and gets data it can find from the previous month and the current month.
# # So if we are in November, the month range will be from months 10 to 11.
#


# Dataset ID and Path
DATASET_ID="aMTRBtVEexKmYvkD3u6n"   # PROD
cd /cserv2/django_app/ClimateSERV-2.0-Server
#DATASET_ID="Q3ky2Ud55wuWdu2f3BGc"   # DEV

# Date Variables
CURRENT_YEAR=`date "+%Y"`
CURRENT_MONTH=`date "+%m"`
CURRENT_DAY=`date "+%d"`
PREVIOUS_YEAR=`expr $CURRENT_YEAR - 1`
PREVIOUS_MONTH=`expr $CURRENT_MONTH - 1`
PREVIOUS_MONTH_DAY=1

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

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $START_YEAR --START_MONTH_MM $START_MONTH --START_DAY_DD $PREVIOUS_MONTH_DAY  --END_YEAR_YYYY $END_YEAR --END_MONTH_MM $END_MONTH --END_DAY_DD $CURRENT_DAY"
#COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $START_YEAR --START_MONTH_MM $START_MONTH --END_YEAR_YYYY $END_YEAR --END_MONTH_MM $END_MONTH --WEEKLY_JULIAN_START_OFFSET 0"


# Check Variables for this run
echo ""
echo "Debug Variables (after checking and adjusting for the condition that the current month is Jan (1)): "
echo "  START_YEAR: $START_YEAR"
echo "  START_MONTH: $START_MONTH"
echo "  PREVIOUS_MONTH_DAY: $PREVIOUS_MONTH_DAY"
echo "  END_YEAR: $END_YEAR"
echo "  END_MONTH: $END_MONTH"
echo "  CURRENT_DAY: $CURRENT_DAY"
echo "  DATASET_ID: $DATASET_ID"
echo "  COMMAND: $COMMAND"
echo ""

# Execute the Script
echo "Running $COMMAND now"
$COMMAND

# Cron Setup
# Weekly (1:30am on Mondays)
# # 30 1 * * 1 /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/regular_runs/ucsb_chirp.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__regular_runs__ucsb_chirp.log 2>&1


