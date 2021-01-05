#!/usr/bin/env bash


cd /cserv2/django_app/ClimateSERV-2.0-Server


# Choose which of these to comment/uncomment in order to run IMERG Early or IMERG Late
DATASET_UUID="WJzA2uQHJHhEwXHvTYiv"  # IMERG EARLY - PRODUCTION
#DATASET_UUID="ggmNzrqfavjRPgyU2N2W"  # IMERG LATE - PRODUCTION

DATASET_NAME="Imerg Early"  # WJzA2uQHJHhEwXHvTYiv
#DATASET_NAME="Imerg Late"   # ggmNzrqfavjRPgyU2N2W

echo ""
echo "About to Run Backfill script for $DATASET_NAME"
echo "Loop through the sequences of dates for each specific run (imerg disconnected after 1000 files, each day is 48 files, so we can do about 20 days worth per loop)"
#for i in {0..5}
#for i in {1..3}
#for i in {4..16}
#for i in {4..28}   # 28 goes to about 6 months back, also this process takes around 48 hours
for i in {0..28}
do
    #MULTIPLE=20   # Batches started failing after the first one.
    MULTIPLE=10
    j=`expr $i - 1`
    EARLIEST_DAY_SUBTRACTOR=`expr $i \* $MULTIPLE`
    LATEST_DAY_SUBTRACTOR=`expr $j \* $MULTIPLE`


    # Linux Version
    CURRENT_DATE=`date`
    EARLIEST_YEAR=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%Y`
    EARLIEST_MONTH=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%m`
    EARLIEST_DAY=`date -d "$CURRENT_DATE -$EARLIEST_DAY_SUBTRACTOR days" +%d`
    LATEST_YEAR=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%Y`
    LATEST_MONTH=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%m`
    LATEST_DAY=`date -d "$CURRENT_DATE -$LATEST_DAY_SUBTRACTOR days" +%d`

    # Mac Version
    #EARLIEST_YEAR=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%Y"`
    #EARLIEST_MONTH=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%m"`
    #EARLIEST_DAY=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%d"`
    #LATEST_YEAR=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%Y"`
    #LATEST_MONTH=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%m"`
    #LATEST_DAY=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%d"`


    #    EARLIEST_YEAR=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%Y"`
    #    EARLIEST_MONTH=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%m"`
    #    EARLIEST_DAY=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%d"`
    #
    #    LATEST_YEAR=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%Y"`
    #    LATEST_MONTH=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%m"`
    #    LATEST_DAY=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%d"`


    COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_UUID --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN 01 --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN 01"

    echo ""
    echo "i=$i, j=$j"
    echo " EARLIEST DATE:   year, month, day: $EARLIEST_YEAR - $EARLIEST_MONTH - $EARLIEST_DAY "
    echo " LATEST DATE:     year, month, day: $LATEST_YEAR - $LATEST_MONTH - $LATEST_DAY "
    echo " ABOUT TO RUN COMMAND:  $COMMAND"
    echo ""

    $COMMAND

    # sleep between runs so the ftp server lets us keep downloading
    echo ""
    echo "Sleeping for 20 minutes between runs...."
    echo ""
    echo ""
    sleep 20m


    #    MULTIPLE=20
    #    CURRENT_DATE_SUBTRACTOR=`expr $i \* $MULTIPLE`
    #    echo "CURRENT_DATE_SUBTRACTOR: $CURRENT_DATE_SUBTRACTOR"
    #    # date -v-1000d "+%Y-%m-%d"
    #    # Subtract 'i' days from the current date (get the year, month and day of that subtracted date)
    #    #    LOOP_YEAR=`date -v-$i'd' "+%Y"`
    #    #    LOOP_MONTH=`date -v-$i'd' "+%m"`
    #    #    LOOP_DAY=`date -v-$i'd' "+%d"`
    #    #
    #    LOOP_YEAR=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%Y"`
    #    LOOP_MONTH=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%m"`
    #    LOOP_DAY=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%d"`
    #    #
    #    #echo date -v-$i'd' "+%Y-%m-%d"
    #    echo " year, month, day: $LOOP_YEAR - $LOOP_MONTH - $LOOP_DAY "
done

echo ""
echo "Script run Now Completed"

# CRON Setup
# Cron to call this file
# 31 12 26 11 * /usr/bin/sh /cserv2/django_app/ClimateSERV-2.0-Server/deploy/scripts/etl_scripts/backfill_examples/imerg.sh >> /cserv2/cron_logs/$(date +\%Y_\%m_\%d_\%H\%M_\%S)etl__backfills__imerg.log 2>&1