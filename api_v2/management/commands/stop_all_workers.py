# start_worker.py
# Command function for starting a worker (workers watch for jobs to process and then process them).


# Call this custom command using
# # # python manage.py start_worker
# # # python manage.py start_worker --placeholder_arg some_arg_value

# Includes
from django.core.management.base import BaseCommand, CommandError
#from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
#from api_v2.processing_objects.etl_pipeline.etl_pipeline import ETL_Pipeline

from api_v2.app_models.model_WorkerProcess import WorkerProcess
from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf

# Improvements - Create a uuid for this worker, and set up a database trigger for stopping these workers.

class Command(BaseCommand):
    help = 'Stop all workers.  (Sends a stop signal to the database for all workers to stop.  If any workers are currently processing jobs, the workers will not be stopped until current jobs have completed processing.'

    # Parsing params
    def add_arguments(self, parser):
        # parser.add_argument('etl_dataset_uuid', type=str)
        # https://stackoverflow.com/questions/43331376/multiple-arguments-with-values-to-custom-management-command
        parser.add_argument('--placeholder_arg', type=str)

    # Function Handler
    def handle(self, *args, **options):
        # Do something with params
        #
        # REQUIRED PARAMS (Returns with error if getting the param fails)
        placeholder_arg = ""
        try:
            placeholder_arg = options['placeholder_arg']
        except:
            ## Required Param would have this
            #self.stdout.write(self.style.ERROR('start_worker.handle(): Could not read required input param: <placeholder_arg>'))
            #return

            # Optional param would have this
            placeholder_arg = "default_value"

        # Debug
        #print("start_worker.handle():  (placeholder_arg): " + str(placeholder_arg))

        did_succeed, error_message = WorkerProcess.stop_all_workers()
        if (did_succeed == True):
            print("stop_all_workers.handle(): - All Workers have been stopped.  Note: If any workers are currently processing jobs, those workers will not be stopped until current jobs have completed processing.")
        else:
            # print("stop_worker.handle(): - There was an error when trying to stop this worker.  Error Detail: " + str(error_message))
            self.stdout.write(self.style.ERROR("stop_all_workers.handle(): - There was an error when trying to stop all workers.  Error Detail: " + str(error_message)))
