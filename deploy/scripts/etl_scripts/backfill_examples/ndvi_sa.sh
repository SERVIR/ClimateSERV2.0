#!/usr/bin/env bash


cd /cserv2/django_app/ClimateSERV-2.0-Server




# Yearly run - see how long it takes ~ roughly 40 minutes per year (1 minute per file and there are 36 files per year)

# See if I can make a sequential, to do one year, then another, then another, or even in monthly batches (see if it can be 2 pipeline runs?)
echo "===== Running Multiple Items in Sequence: Starting now. ====="

#echo ""
#echo "About to Run: python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2019 --START_MONTH_MM 7 --END_YEAR_YYYY 2019 --END_MONTH_MM 10 --REGION_CODE sa"
#echo ""
#python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2019 --START_MONTH_MM 7 --END_YEAR_YYYY 2019 --END_MONTH_MM 10 --REGION_CODE sa
#
#
#echo ""
#echo "About to Run: python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2019 --START_MONTH_MM 11 --END_YEAR_YYYY 2019 --END_MONTH_MM 12 --REGION_CODE sa"
#echo ""
#python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2019 --START_MONTH_MM 11 --END_YEAR_YYYY 2019 --END_MONTH_MM 12 --REGION_CODE sa
#


#echo ""
#echo "About to Run: python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2018 --START_MONTH_MM 1 --END_YEAR_YYYY 2018 --END_MONTH_MM 6 --REGION_CODE sa"
#echo ""
#python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2018 --START_MONTH_MM 1 --END_YEAR_YYYY 2018 --END_MONTH_MM 6 --REGION_CODE sa
#
#echo ""
#echo "About to Run: python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2018 --START_MONTH_MM 7 --END_YEAR_YYYY 2018 --END_MONTH_MM 12 --REGION_CODE sa"
#echo ""
#python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY 2018 --START_MONTH_MM 7 --END_YEAR_YYYY 2018 --END_MONTH_MM 12 --REGION_CODE sa



echo ""
echo "Running 4 Months of data between 1 minute sleeps."
echo ""

for YEAR in 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018
do
    echo ""
    echo "This script is now on year: $YEAR"
    echo ""
    echo "About to Run Year $YEAR, Months 1 - 4"
    python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY $YEAR --START_MONTH_MM 1 --END_YEAR_YYYY $YEAR --END_MONTH_MM 4 --REGION_CODE sa
    sleep 3m
    echo "About to Run Year $YEAR, Months 5 - 8"
    python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY $YEAR --START_MONTH_MM 5 --END_YEAR_YYYY $YEAR --END_MONTH_MM 8 --REGION_CODE sa
    sleep 3m
    echo "About to Run Year $YEAR, Months 9 - 12"
    python3 manage.py start_etl_pipeline --etl_dataset_uuid 8QEhfrTe73VeudjFyeAw --START_YEAR_YYYY $YEAR --START_MONTH_MM 9 --END_YEAR_YYYY $YEAR --END_MONTH_MM 12 --REGION_CODE sa
    sleep 3m
done


echo ""
echo "Script Ended."






echo ""
echo "===== Running Multiple Items in Sequence: Ending now. ====="




# Cron to call this file
# 02 17 24 11 * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/backfill_examples/ndvi_sa.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__backfills__ndvi_sa.log 2>&1