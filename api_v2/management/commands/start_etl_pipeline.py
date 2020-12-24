# start_etl_pipeline.py
# Command function for starting the ETL Pipeline for a specific dataset uuid


# Call this custom command using
# # # python manage.py start_etl_pipeline <etl_dataset_uuid>.

# Includes
from django.core.management.base import BaseCommand, CommandError
from api_v2.app_models.model_ETL_Dataset import ETL_Dataset

from api_v2.processing_objects.etl_pipeline.etl_pipeline import ETL_Pipeline


class Command(BaseCommand):
    help = 'Create a new Dataset from an input name with default parameters.'

    # Parsing params
    def add_arguments(self, parser):
        #parser.add_argument('etl_dataset_uuid', type=str)
        # https://stackoverflow.com/questions/43331376/multiple-arguments-with-values-to-custom-management-command
        parser.add_argument('--etl_dataset_uuid', type=str)

        # optional additional params
        # # Year
        parser.add_argument('--START_YEAR_YYYY', nargs='+', type=int)
        parser.add_argument('--END_YEAR_YYYY', nargs='+', type=int)
        # # Month (Range from 01 to 12)
        parser.add_argument('--START_MONTH_MM', nargs='+', type=int)
        parser.add_argument('--END_MONTH_MM', nargs='+', type=int)
        # # Day (Range from 01 to 31)
        parser.add_argument('--START_DAY_DD', nargs='+', type=int)
        parser.add_argument('--END_DAY_DD', nargs='+', type=int)
        # # 30Min Increment (Range from 00 to 48)
        parser.add_argument('--START_30MININCREMENT_NN', nargs='+', type=int)
        parser.add_argument('--END_30MININCREMENT_NN', nargs='+', type=int)
        # # Region Code (FOR EMODIS: 'ea', 'wa', 'sa', 'cta' .... 'ea' is the default down in the subclass)
        parser.add_argument('--REGION_CODE', nargs='+', type=str)
        # # Weekly Julian Offset (for ESI, number from 0 to 6 -- 0 means, use Jan 1st, 6 means, use Jan 7th as first Julian Date)
        parser.add_argument('--WEEKLY_JULIAN_START_OFFSET', nargs='+', type=int)

        # Experimenting (TODO REMOVE ME)
        # python manage.py start_etl_pipeline --etl_dataset_uuid fRjduT9v4jHyazGBMEJe --str_arg1 someYear --int_arg2 abc
        # python manage.py start_etl_pipeline --etl_dataset_uuid fRjduT9v4jHyazGBMEJe --int_arg2 123 --str_arg1 someYear --START_YEAR_YYYY 2018
        parser.add_argument('--str_arg1', nargs='+', type=str)  # example Optional params
        parser.add_argument('--int_arg2', nargs='+', type=int)  # Nice, we have built in validation

    # Function Handler
    def handle(self, *args, **options):
        # Get the dataset uuid input params
        #
        # REQUIRED PARAMS (Returns with error if getting the param fails)
        etl_dataset_uuid = ""
        try:
            etl_dataset_uuid = options['etl_dataset_uuid']
        except:
            self.stdout.write(self.style.ERROR('start_etl_pipeline.handle(): Could not read required input param: <etl_dataset_uuid>'))
            return

        # OPTIONAL PARAMS (Just uses default of blank string if not passed in)
        START_YEAR_YYYY = ""
        try:
            START_YEAR_YYYY = str(options['START_YEAR_YYYY'][0])
        except:
            START_YEAR_YYYY = ""
        END_YEAR_YYYY = ""
        try:
            END_YEAR_YYYY = str(options['END_YEAR_YYYY'][0])
        except:
            END_YEAR_YYYY = ""

        START_MONTH_MM = ""
        try:
            START_MONTH_MM = str(options['START_MONTH_MM'][0])
        except:
            START_MONTH_MM = ""
        END_MONTH_MM = ""
        try:
            END_MONTH_MM = str(options['END_MONTH_MM'][0])
        except:
            END_MONTH_MM = ""

        START_DAY_DD = ""
        try:
            START_DAY_DD = str(options['START_DAY_DD'][0])
        except:
            START_DAY_DD = ""
        END_DAY_DD = ""
        try:
            END_DAY_DD = str(options['END_DAY_DD'][0])
        except:
            END_DAY_DD = ""

        START_30MININCREMENT_NN = ""
        try:
            START_30MININCREMENT_NN = str(options['START_30MININCREMENT_NN'][0])
        except:
            START_30MININCREMENT_NN = ""
        END_30MININCREMENT_NN = ""
        try:
            END_30MININCREMENT_NN = str(options['END_30MININCREMENT_NN'][0])
        except:
            END_30MININCREMENT_NN = ""

        REGION_CODE = ""
        try:
            REGION_CODE = str(options['REGION_CODE'][0])
        except:
            REGION_CODE = ""

        WEEKLY_JULIAN_START_OFFSET = ""
        try:
            WEEKLY_JULIAN_START_OFFSET = str(options['WEEKLY_JULIAN_START_OFFSET'][0])
        except:
            WEEKLY_JULIAN_START_OFFSET = ""


        # Filter down to a forced string that is not empty.
        etl_dataset_uuid = str(etl_dataset_uuid).strip()

        # Debug
        self.stdout.write(self.style.SUCCESS('start_etl_pipeline.py: Successfully called handle(): with param: (etl_dataset_uuid) ' + str(etl_dataset_uuid)))

        # Verify that this uuid does exist
        does_etl_dataset_exist = ETL_Dataset.does_etl_dataset_exist__by_uuid(input__uuid=etl_dataset_uuid)

        if(does_etl_dataset_exist == False):
            self.stdout.write(self.style.ERROR('start_etl_pipeline.handle(): Dataset with UUID: ' + str() + 'does not exist.  Try using "python manage.py list_etl_dataset_uuids" to see a list of all datasets and their uuids.'))
            return

        # DEBUG
        self.stdout.write(self.style.SUCCESS('start_etl_pipeline.py: (does_etl_dataset_exist) ' + str(does_etl_dataset_exist)))


        # Get the other input params
        # TODO - Additional Possible Inputs here.


        # Create an instance of the pipeline
        etl_pipeline = ETL_Pipeline()

        # Set input params as configuration options on the ETL Pipeline
        etl_pipeline.etl_dataset_uuid   = etl_dataset_uuid
        etl_pipeline.START_YEAR_YYYY    = START_YEAR_YYYY
        etl_pipeline.END_YEAR_YYYY      = END_YEAR_YYYY
        etl_pipeline.START_MONTH_MM     = START_MONTH_MM
        etl_pipeline.END_MONTH_MM       = END_MONTH_MM
        etl_pipeline.START_DAY_DD       = START_DAY_DD
        etl_pipeline.END_DAY_DD         = END_DAY_DD
        etl_pipeline.START_30MININCREMENT_NN    = START_30MININCREMENT_NN
        etl_pipeline.END_30MININCREMENT_NN      = END_30MININCREMENT_NN
        etl_pipeline.REGION_CODE        = REGION_CODE
        etl_pipeline.WEEKLY_JULIAN_START_OFFSET     = WEEKLY_JULIAN_START_OFFSET


        #print(str(etl_pipeline))

        # Call the actual function to start the pipeline
        etl_pipeline.execute_pipeline_control_function()

        # DEBUG
        #print("ETL_Pipeline.test_function_call: Reached the End")
        #ETL_Pipeline.test_function_call()




        return



# # Running Test:
#

# python manage.py start_etl_pipeline abcdefg
#
# # Output from Test:
# start_etl_pipeline.py: Successfully called handle(): with param: (etl_dataset_uuid) abcdefg
# start_etl_pipeline.py: (does_etl_dataset_exist) False


# # Deprecated this in favor of having all named parameters (better to be explicit with backend processes) # python manage.py start_etl_pipeline fRjduT9v4jHyazGBMEJe


# python manage.py start_etl_pipeline --etl_dataset_uuid fRjduT9v4jHyazGBMEJe
# python manage.py start_etl_pipeline --etl_dataset_uuid fRjduT9v4jHyazGBMEJe --str_arg1 someYear --int_arg2 abc        # TODO: Remove me and add the correct 'complete' example that uses ALL params.
#
# # Output from Test:
# start_etl_pipeline.py: Successfully called handle(): with param: (etl_dataset_uuid) fRjduT9v4jHyazGBMEJe
# start_etl_pipeline.py: (does_etl_dataset_exist) True


# TODO: WHEN FINISHED WRITING THIS COMMAND COMPLETELY
# python manage.py start_etl_pipeline fRjduT9v4jHyazGBMEJe
#
# # Output from Test:
# add_new_etl_dataset.py: Successfully created new dataset, CSERV-TEST_PIPELINE_DATASET, with UUID: fRjduT9v4jHyazGBMEJe



