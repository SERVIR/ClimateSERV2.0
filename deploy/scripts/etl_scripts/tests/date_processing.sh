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
PREVIOUS_YEAR=`expr $CURRENT_YEAR - 1`
PREVIOUS_MONTH=`expr $CURRENT_MONTH - 1`
START_YEAR_EXAMPLE=$CURRENT_YEAR
echo ""
echo "Variables: "
echo "  CURRENT_YEAR: $CURRENT_YEAR"
echo "  CURRENT_MONTH: $CURRENT_MONTH"
echo "  CURRENT_DAY: $CURRENT_DAY"
echo "  PREVIOUS_YEAR: $PREVIOUS_YEAR"
echo "  PREVIOUS_MONTH: $PREVIOUS_MONTH"
echo "  START_YEAR_EXAMPLE: $START_YEAR_EXAMPLE"
echo ""

# check for condition of equal to 1
if [[ "$CURRENT_MONTH" == 1 ]]; then
echo "The Current Month is 1 (Jan), so the previous month needs to be set to 12"
PREVIOUS_MONTH=12
else
echo "The Current Month is NOT 1 (Not Jan) - No change to the above variable assignment"
fi


echo ""
echo "Variables (after checking and adjusting for the condition that the current month is Jan (1)): "
echo "  CURRENT_YEAR: $CURRENT_YEAR"
echo "  CURRENT_MONTH: $CURRENT_MONTH"
echo "  PREVIOUS_YEAR: $PREVIOUS_YEAR"
echo "  PREVIOUS_MONTH: $PREVIOUS_MONTH"
echo ""


COMMAND_STRING="some_command_with_varibles -start_year $PREVIOUS_YEAR -start_month $PREVIOUS_MONTH -end_year $CURRENT_YEAR -start_year $CURRENT_MONTH"
echo "  COMMAND_STRING: $COMMAND_STRING"

