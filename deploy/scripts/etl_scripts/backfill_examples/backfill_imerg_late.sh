#!/usr/bin/env bash

# Activate the virtual python environment
source /cserv2/python_environments/environments/py36_climateserv_2_env/bin/activate

cd /cserv2/django_app/ClimateSERV-2.0-Server

# Back fill old data - Set specific date range targets  
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2019 --START_MONTH_MM 12  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2019 --END_MONTH_MM 11  --END_DAY_DD 16 --END_30MININCREMENT_NN 22
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2020 --START_MONTH_MM 02  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2020 --END_MONTH_MM 02  --END_DAY_DD 01 --END_30MININCREMENT_NN 10
#python3 manage.py start_etl_pipeline --etl_dataset_uuid WJzA2uQHJHhEwXHvTYiv --START_YEAR_YYYY 2017 --START_MONTH_MM 01  --START_DAY_DD 01 --START_30MININCREMENT_NN 01 --END_YEAR_YYYY 2020 --END_MONTH_MM 11  --END_DAY_DD 16 --END_30MININCREMENT_NN 22

DATE=2020-12-12

for i in {1..47..2}
do
	NEXT_DATE=$(date -d "$DATE + $i day")
	#j=$(expr $i + 1)
	echo "Starting $NEXT_DATE"
	EARLIEST_YEAR=$(date -d "$NEXT_DATE" +%Y)
	EARLIEST_MONTH=$(date -d "$NEXT_DATE" +%m)
	EARLIEST_DAY=$(date -d "$NEXT_DATE" +%d)
	LATEST_YEAR=$(date -d "$NEXT_DATE + 1 day" +%Y)
	LATEST_MONTH=$(date -d "$NEXT_DATE + 1 day" +%m)
	LATEST_DAY=$(date -d "$NEXT_DATE + 1 day" +%d)
	python3 manage.py start_etl_pipeline --etl_dataset_uuid ggmNzrqfavjRPgyU2N2W --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN 01 --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN 48

	echo "Completed $(date -d "$NEXT_DATE + 1 day")"
done

echo "Finished, thanx!"
