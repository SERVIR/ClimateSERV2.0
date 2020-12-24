#!/usr/bin/env bash

# Activate the virtual python environment
source /cserv2/python_environments/environments/py36_climateserv_2_env/bin/activate

cd /cserv2/django_app/ClimateSERV-2.0-Server

# Imerg - Early
python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2020 --START_MONTH_MM 11  --START_DAY_DD 15 --START_30MININCREMENT_NN 10 --END_YEAR_YYYY 2020 --END_MONTH_MM 11  --END_DAY_DD 19 --END_30MININCREMENT_NN 01


# Cron tab setup (Specific Date and time)
# # 00 16 18 11 * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/test_concurrent_etl_imerg_early_2.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)test_concurrent_etl_imerg_early_2.log 2>&1
