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
    help = 'Stop a worker by the worker uuid.  (Sends a stop signal to the database for the specified worker uuid)'

    # Parsing params
    def add_arguments(self, parser):
        # parser.add_argument('etl_dataset_uuid', type=str)
        # https://stackoverflow.com/questions/43331376/multiple-arguments-with-values-to-custom-management-command
        #parser.add_argument('--uuid', type=str)
        parser.add_argument('-uuid', type=str)

    # Function Handler
    def handle(self, *args, **options):
        # Do something with params
        #
        # REQUIRED PARAMS (Returns with error if getting the param fails)
        uuid = ""
        try:
            uuid = options['uuid']

            if(uuid == None):
                self.stdout.write(self.style.ERROR('stop_worker.handle(): Could not read required input param: <uuid>'))

                active_worker_uuids = WorkerProcess.get_all_active_worker_uuids()
                self.stdout.write(self.style.ERROR('stop_worker.handle(): Here is a full list of currently active worker uuids: ' + str(active_worker_uuids)))
                return
        except:
            ## Required Param would have this


            self.stdout.write(self.style.ERROR('stop_worker.handle(): Could not read required input param: <uuid>'))

            active_worker_uuids = WorkerProcess.get_all_active_worker_uuids()
            self.stdout.write(self.style.ERROR('stop_worker.handle(): Here is a full list of currently active worker uuids: ' + str(active_worker_uuids)))
            return

            # Optional param would have this
            #placeholder_arg = "default_value"

        # Debug
        #print("start_worker.handle():  (placeholder_arg): " + str(placeholder_arg))
        print("start_worker.handle():  (uuid): " + str(uuid))

        did_succeed, error_message, is_processing_job = WorkerProcess.stop_worker(worker_uuid=str(uuid))
        if(did_succeed == True):
            if(is_processing_job == True):
                print("stop_worker.handle(): - Worker " + str(uuid) + " is currently processing a job.  When the job processing is completed, this worker will stop.")
            else:
                print("stop_worker.handle(): - Worker " + str(uuid) + " was stopped.")
        else:
            # print("stop_worker.handle(): - There was an error when trying to stop this worker.  Error Detail: " + str(error_message))
            self.stdout.write(self.style.ERROR("stop_worker.handle(): - There was an error when trying to stop this worker.  Error Detail: " + str(error_message)))

