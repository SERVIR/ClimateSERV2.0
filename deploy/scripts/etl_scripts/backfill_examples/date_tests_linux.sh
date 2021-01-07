#!/usr/bin/env bash

for i in {1..3}
do
    MULTIPLE=20
    j=`expr $i - 1`
    EARLIEST_DAY_SUBTRACTOR=`expr $i \* $MULTIPLE`
    LATEST_DAY_SUBTRACTOR=`expr $j \* $MULTIPLE`



    # This works in linux
    ONE=1
    dataset_date=`date`
    TODAY=`date -d "$dataset_date - $ONE days" +%d-%b-%G`
    echo $TODAY

    # This works in linux
    #ONE=1
    dataset_date=`date`
    EARLIEST_DATE=`date -d "$dataset_date - $EARLIEST_DAY_SUBTRACTOR days" +%d-%b-%G`
    echo $EARLIEST_DATE

    # Works on Mac, but not regular linux....
    #    EARLIEST_YEAR=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%Y"`
    #    EARLIEST_MONTH=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%m"`
    #    EARLIEST_DAY=`date -v-$EARLIEST_DAY_SUBTRACTOR'd' "+%d"`
    #
    #    LATEST_YEAR=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%Y"`
    #    LATEST_MONTH=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%m"`
    #    LATEST_DAY=`date -v-$LATEST_DAY_SUBTRACTOR'd' "+%d"`


#    COMMAND="python3 manage.py start_etl_pipeline --etl_dataset_uuid $DATASET_UUID --START_YEAR_YYYY $EARLIEST_YEAR --START_MONTH_MM $EARLIEST_MONTH  --START_DAY_DD $EARLIEST_DAY --START_30MININCREMENT_NN 01 --END_YEAR_YYYY $LATEST_YEAR --END_MONTH_MM $LATEST_MONTH  --END_DAY_DD $LATEST_DAY --END_30MININCREMENT_NN 01"
#
#    echo ""
#    echo "i=$i, j=$j"
#    echo " EARLIEST DATE:   year, month, day: $EARLIEST_YEAR - $EARLIEST_MONTH - $EARLIEST_DAY "
#    echo " LATEST DATE:     year, month, day: $LATEST_YEAR - $LATEST_MONTH - $LATEST_DAY "
#    echo " ABOUT TO RUN COMMAND:  $COMMAND"
#    echo ""

done
