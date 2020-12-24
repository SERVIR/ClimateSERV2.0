#!/usr/bin/env bash

# Activate the virtual python environment
source /cserv2/python_environments/environments/py36_climateserv_2_env/bin/activate

cd /cserv2/django_app/ClimateSERV-2.0-Server

# Back fill old data - Set specific date range targets
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2019 --START_MONTH_MM 12  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2019 --END_MONTH_MM 11  --END_DAY_DD 16 --END_30MININCREMENT_NN 22
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2020 --START_MONTH_MM 02  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2020 --END_MONTH_MM 02  --END_DAY_DD 01 --END_30MININCREMENT_NN 10
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2017 --START_MONTH_MM 01  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2020 --END_MONTH_MM 11  --END_DAY_DD 16 --END_30MININCREMENT_NN 22
python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2019 --START_MONTH_MM 06  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2020 --END_MONTH_MM 01  --END_DAY_DD 01 --END_30MININCREMENT_NN 01
