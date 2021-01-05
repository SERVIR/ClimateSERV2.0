#!/usr/bin/env bash

# Dataset ID and Path
DATASET_ID="ZfyAm5a8swYqjVXxxGPQ"   # PROD
cd /cserv2/django_app/ClimateSERV-2.0-Server
#DATASET_ID="J2dbgY5Mb7cf6c7CJ5x8"   # DEV

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY 2020 --START_MONTH_MM 07 --START_DAY_DD 01  --END_YEAR_YYYY 2020 --END_MONTH_MM 12 --END_DAY_DD 01"


# Execute the Script
echo "Running $COMMAND now"
$COMMAND