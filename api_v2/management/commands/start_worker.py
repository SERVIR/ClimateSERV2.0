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
    help = 'Create a new worker thread that watches for and processes incoming jobs on an endless loop'

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
        print("start_worker.handle():  (placeholder_arg): " + str(placeholder_arg))

        #Select_From_Netcdf.test__CanReadFromDjangoDB()


        # This test only reads from a single specific nc4 file and returns the data
        # (Worked Locally)
        #test_return_data = Select_From_Netcdf.test_select_data__From_SubmitDataRequest_Call()
        #print("start_worker.handle(): - test_return_data = Select_From_Netcdf.test_select_data__From_SubmitDataRequest_Call() - (test_return_data): " + str(test_return_data))

        # # TEST RESULT - Core functioning as expected (locally)
        #
        # This test preforms most of the core operations
        # # reads dataset info (handles legacy ids), gets the variable to select, reads the lat reversal order flag, creates a datetime range, finds all the nc4 files, selects data from each one, writes tifs, outputs download data
        # # Note: Jobs Ids on this test all start with '11111111' to make it easier to identify the output test results data
        # (??? Locally)
        #test_return_data = Select_From_Netcdf.test_Process_Job_Test_1()
        #print("start_worker.handle(): - test_return_data = Select_From_Netcdf.test_Process_Job_Test_1() - (test_return_data): " + str(test_return_data))

        # # TEST RESULT - Creating a task functions as expected (locally)
        # Now let's test and make sure we can create Tasks (jobs) in the Task_Log datamodel
        #Select_From_Netcdf.test__Create_New_TaskLog__and_Modify_TaskLog()
        #print("start_worker.handle(): - Select_From_Netcdf.test__Create_New_TaskLog__and_Modify_TaskLog() was called.  To see results, look for new Task_Log entries in the Database")


        # # TEST RESULT - The endless loop pulled in tasks from the database, processed them and then updated the results as expected (locally)
        # # Now testing to make sure we can have a worker loop.  This loop should get tasks and execute / process them.  Essentially loading tasks from the Task_Log that are waiting to be processed and then call the core functions to actually do the processing.
        # Select_From_Netcdf.test__almostEndlessLoop_for_worker()
        # print("start_worker.handle(): - Select_From_Netcdf.test__almostEndlessLoop_for_worker() was called.  To see results, look at console output to see print statements where the loop runs")



        # The production version right here.
        ready_worker_id, is_error, error_message = WorkerProcess.restart_idle_worker_or_create_and_start_new_worker()
        if(is_error == False):
            print("start_worker.handle(): - about to call: Select_From_Netcdf.worker_process_endless_loop().  This is the real endless loop.  To stop the worker(s), set the database flag, or call 'stop_worker' with a uuid, or call 'stop_all_workers'")
            Select_From_Netcdf.worker_process_endless_loop(worker_db_uuid=ready_worker_id)
        else:
            print("start_worker.handle(): - There was an error when trying to get a ready worker id.  More Details: " + str(error_message))


