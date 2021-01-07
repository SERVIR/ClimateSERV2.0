#!/usr/bin/env bash

# Activate the virtual python environment
source /cserv2/python_environments/environments/py36_climateserv_2_env/bin/activate

cd /cserv2/django_app/ClimateSERV-2.0-Server

# NDVI - East Africa
python3 manage.py start_etl_pipeline --etl_dataset_uuid QqyPayzNjrFuqXBRMg8G --START_YEAR_YYYY 2020 --START_MONTH_MM 09 --END_YEAR_YYYY 2020 --END_MONTH_MM 11 --REGION_CODE ea


# Cron tab setup (Specific Date and time)
# # 00 16 18 11 * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/test_etl_ndvi_ea_1.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)test_etl_ndvi_ea_1.log 2>&1
