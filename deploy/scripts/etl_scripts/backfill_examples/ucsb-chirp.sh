#!/usr/bin/env bash

# Dataset ID and Path
DATASET_ID="aMTRBtVEexKmYvkD3u6n"   # PROD
cd /cserv2/django_app/ClimateSERV-2.0-Server
#DATASET_ID="Q3ky2Ud55wuWdu2f3BGc"   # DEV

COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_ID --START_YEAR_YYYY 2020 --START_MONTH_MM 01 --START_DAY_DD 01  --END_YEAR_YYYY 2020 --END_MONTH_MM 12 --END_DAY_DD 01"


# Execute the Script
echo "Running $COMMAND now"
$COMMAND