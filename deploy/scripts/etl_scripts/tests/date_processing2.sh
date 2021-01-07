#!/usr/bin/env bash


echo date "+%Y_%m_%d_%H%M_%S"
echo date "+%Y"
echo date "+%m"

echo `date "+%Y_%m_%d_%H%M_%S"`
echo `date "+%Y"`
echo `date "+%m"`

# Current and Previous
CURRENT_YEAR=`date "+%Y"`
CURRENT_MONTH=`date "+%m"`
CURRENT_DAY=`date "+%d"`
PREVIOUS_YEAR=`date -v-1d "+%Y"`
PREVIOUS_MONTH=`date -v-1d "+%m"`
PREVIOUS_DAY=`date -v-1d "+%d"`
START_YEAR_EXAMPLE=$CURRENT_YEAR
echo ""
echo "Variables: "
echo "  CURRENT_YEAR: $CURRENT_YEAR"
echo "  CURRENT_MONTH: $CURRENT_MONTH"
echo "  CURRENT_DAY: $CURRENT_DAY"
echo "  PREVIOUS_YEAR: $PREVIOUS_YEAR"
echo "  PREVIOUS_MONTH: $PREVIOUS_MONTH"
echo "  PREVIOUS_DAY: $PREVIOUS_DAY"
echo "  START_YEAR_EXAMPLE: $START_YEAR_EXAMPLE"
echo ""



COMMAND_STRING="some_command_with_varibles -start_year $PREVIOUS_YEAR -start_month $PREVIOUS_MONTH -end_year $CURRENT_YEAR -start_year $CURRENT_MONTH"
echo "  COMMAND_STRING: $COMMAND_STRING"


echo ""
echo "For loop for XYZ days before today"
for i in {0..5}
do
    MULTIPLE=20
    CURRENT_DATE_SUBTRACTOR=`expr $i \* $MULTIPLE`
    echo "CURRENT_DATE_SUBTRACTOR: $CURRENT_DATE_SUBTRACTOR"
    # date -v-1000d "+%Y-%m-%d"
    # Subtract 'i' days from the current date (get the year, month and day of that subtracted date)
    #    LOOP_YEAR=`date -v-$i'd' "+%Y"`
    #    LOOP_MONTH=`date -v-$i'd' "+%m"`
    #    LOOP_DAY=`date -v-$i'd' "+%d"`

    LOOP_YEAR=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%Y"`
    LOOP_MONTH=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%m"`
    LOOP_DAY=`date -v-$CURRENT_DATE_SUBTRACTOR'd' "+%d"`

    #echo date -v-$i'd' "+%Y-%m-%d"
    echo " year, month, day: $LOOP_YEAR - $LOOP_MONTH - $LOOP_DAY "
done
