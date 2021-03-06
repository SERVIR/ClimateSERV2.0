#!/usr/bin/env bash

# Dataset ID and Path
#
cd /cserv2/django_app/ClimateSERV-2.0-Server
#
# IMERG EARLY
#DATASET_ID="WJzA2uQHJHhEwXHvTYiv"   # PROD
#DATASET_ID="aZ9wbLzbE7efN2NSSAXn"   # DEV
#
# IMERG LATE
DATASET_ID="ggmNzrqfavjRPgyU2N2W"   # PROD
#DATASET_ID="uGG9pqNfU4nk7FGZJpGj"   # DEV

# Time Vars
EARLIEST_YEAR="2020"
EARLIEST_MONTH="12"
EARLIEST_DAY="31"
EARLIEST_30MIN_INCREMENT="01"

LATEST_YEAR="2021"
LATEST_MONTH="01"
LATEST_DAY="03"
LATEST_30MIN_INCREMENT="48"

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN $EARLIEST_30MIN_INCREMENT --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN $LATEST_30MIN_INCREMENT"



# Execute the Script
echo "Running $COMMAND now"
$COMMAND
