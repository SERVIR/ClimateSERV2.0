# model_Task_Log.py

from django.db import models
from common_utils import utils as common_utils
import json
import os
import sys
import uuid
import zipfile

from api_v2.app_models.model_Config_Setting import Config_Setting

# Import This Model - Usage Example
# # from api_v2.app_models.model_Task_Log import Task_Log



class Task_Log(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")

    # job_uuid, is_errored, job_status, job_progress
    ip_address      = models.CharField('What was the IP Address', max_length=90, blank=False, default="UNKNOWN_IP", help_text="What was the IP address of the computer that requested this Task?")
    job_uuid        = models.CharField(default="00000000-0000-0000-0000-000000000000", max_length=40, blank=False)  # Job UUID
    is_errored      = models.BooleanField(default=False, help_text="When this task was processed, were there any errors?")
    job_status      = models.CharField('Job Status', max_length=30, blank=False, default="Default", help_text="What is the current status of this job.  Current Recognized Enum choices are: 'Waiting_To_Start', 'In_Progress', and 'Processing_Complete' ")
    job_progress    = models.IntegerField('Job Progress', blank=False, default=0, help_text="Job Process Progress.  Integer from 0 to 100")



    # Additional Columns Here
    # TODO - More Columns Here,
    #  TODO     -Dataset requested
    #  TODO 	-Area Geometry
    #  TODO 	-IP Address of Request
    #  TODO     -AND MORE FIELDS

    class_name_string = "Task_Log"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        return outString


    # Non Static, Serialize current element to JSON
    def to_JSONable_Object(self):
        retObj = {}
        retObj["id"]                            = str(self.id).strip()
        retObj["uuid"]                          = str(self.uuid).strip()
        retObj["created_at"]                    = str(self.created_at).strip()
        retObj["created_by"]                    = str(self.created_by).strip()
        retObj["is_test_object"]                = str(self.is_test_object).strip()
        retObj["additional_json"]               = json.loads(self.additional_json)

        # Add Custom Export to JSON Content Here - Fields/Columns Serialization (stringifying)

        # job_uuid, is_errored, job_status, job_progress

        retObj["ip_address"]    = str(self.ip_address).strip()
        retObj["job_uuid"]      = str(self.job_uuid).strip()
        retObj["is_errored"]    = str(self.is_errored).strip()
        retObj["job_status"]    = str(self.job_status).strip()
        retObj["job_progress"]  = str(self.job_progress).strip()

        return retObj


    # # Specialized JSONable functions for Client Side Usage

    # For a Detail View
    def to_JSONable_Object__For_ClientSide_Detail(self):
        retObj = {}
        retObj["uuid"]                          = str(self.uuid).strip()

        # Add Other Safe Fields here.

        return retObj

    # For a List View
    def to_JSONable_Object__For_ClientSide_PreviewList(self):
        retObj = {}
        retObj["uuid"]                          = str(self.uuid).strip()

        # Add Other Safe Fields here.

        return retObj


    #   retObj["job_uuid"]      = str(self.job_uuid).strip()
    #   retObj["is_errored"]    = str(self.is_errored).strip()
    #   retObj["job_status"]    = str(self.job_status).strip()
    #   retObj["job_progress"]  = str(self.job_progress).strip()
    #
    # function: Create new Task (With a specified job_uuid and default parameters)

    @staticmethod
    def create_new_task(job_uuid, request_params, ip_address):

        is_task_created = False
        error_message = ""

        try:
            additional_json = {}
            additional_json["request_params"] = request_params

            new_task = Task_Log()
            new_task.additional_json    = json.dumps(additional_json)
            new_task.ip_address         = str(ip_address).strip()
            new_task.job_uuid           = str(job_uuid).strip()
            new_task.is_errored         = False
            new_task.job_progress       = int(0)
            new_task.job_status         = "Waiting_To_Start"            # All Choices: "Waiting_To_Start", "In_Progress", "Processing_Complete"

            new_task.save()

            is_task_created = True
        except:
            is_task_created = False
            sysErrorData = str(sys.exc_info())
            error_message = "Unable to create new task.  System Error Message: " + str(sysErrorData)


        return is_task_created, error_message

    @staticmethod
    def set_JobStatus_To__In_Progress(job_uuid):
        try:
            current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            current_job.job_status = "In_Progress"
            current_job.save()
        except:
            pass

    @staticmethod
    def set_JobStatus_To__Processing_Complete(job_uuid, job_result_info):
        try:
            current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            current_job.job_status      = "Processing_Complete"
            current_job.job_progress    = int(100)

            additional_json = json.loads(current_job.additional_json)
            additional_json['job_result_info'] = job_result_info            # Inject new json property 'job_result_info'
            current_job.additional_json = json.dumps(additional_json)

            current_job.save()
        except:
            pass

    @staticmethod
    def set_JobProgress_To(job_uuid, current_progress_int):
        try:
            current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            current_job.job_progress    = int(current_progress_int)
            current_job.save()
        except:
            pass

    @staticmethod
    def flag_Job_As__Is_Errored(job_uuid):
        try:
            current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            current_job.is_errored = True
            current_job.job_progress    =   int(-1)             # Legacy Support - When a job errored in ClimateSERV 1, the Errors showed a job progress of -1
            current_job.save()
        except:
            pass

    # When a submit data request happens, a task_log (job) gets created and set to waiting, this function let's us select one of the jobs that is waiting.  If none are available, nothing is selected.
    @staticmethod
    def get_job_uuid_for_a_waiting_job():
        did_find_available_job = False
        job_uuid = ""
        total_jobs_available = 0

        try:
            available_jobs          = Task_Log.objects.filter(job_status="Waiting_To_Start")
            current_job             = available_jobs[0]
            total_jobs_available    = available_jobs.count()

            # Get the UUID, set the status to inprogress (so it can't be selected again in this process) and then return everything.
            job_uuid = current_job.job_uuid
            Task_Log.set_JobStatus_To__In_Progress(job_uuid=job_uuid)
            did_find_available_job = True
        except:
            # Hitting this block happens when the
            pass

        return did_find_available_job, job_uuid, total_jobs_available


    # Used by the API when a user is requesting the progress of a job that is in processing (or finished with processing)
    @staticmethod
    def get_job_progress(job_uuid):
        job_progress = 0.0
        try:
            current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            job_progress = float(current_job.job_progress)
        except:
            job_progress = -1.0
        return job_progress


    # Used by the API when user is requesting the data contained in the .json file from a job
    @staticmethod
    def get_job_data(job_uuid):
        job_data = {}
        try:
            # job_data = {"placeholder": "DONE: Load the JSON file, parse and then send back"}
            # pass

            # Load the JSON file, parse and then send back
            base_output_dir = Config_Setting.get_value(setting_name="PATH__BASE_DATA_OUTPUT_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/")  # Append   "<Job_UUID>/"
            job_output_dir = os.path.join(base_output_dir, str(job_uuid))
            output_base_file_name = str(job_uuid)
            json_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.json')

            with open(json_file_output_fullpath, 'r') as f:
                job_data = json.load(f)

            #current_job = Task_Log.objects.filter(job_uuid=str(job_uuid))[0]
            #job_progress = float(current_job.job_progress)
        except:
            #job_progress = -1.0
            job_data = {}
        return job_data

    # Gets 'expectedFileLocation' and 'expectedFileName' for any given job id.
    @staticmethod
    def get_job_file_info(job_uuid):

        expectedFileLocation = "UNSET"  # Full Path, including the name
        expectedFileName = "UNSET"
        try:
            base_output_dir = Config_Setting.get_value(setting_name="PATH__BASE_DATA_OUTPUT_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/")  # Append   "<Job_UUID>/"
            job_output_dir = os.path.join(base_output_dir, str(job_uuid))
            output_base_file_name = str(job_uuid)
            #json_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.json')
            zip_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.zip')

            expectedFileLocation = zip_file_output_fullpath                         # full/path/to/filename.zip
            expectedFileName = os.path.join(output_base_file_name + '.zip')         # Just a filename.zip
        except:
            expectedFileLocation = "ERROR_GETTING_EXPECTED_FILE_LOCATION"
            expectedFileName = "ERROR_GETTING_EXPECTED_FILENAME"

        return expectedFileLocation, expectedFileName


    @staticmethod
    def make_new_job_uuid():
        new_job_uuid = ""
        new_job_uuid = str(uuid.uuid4())      # '37928bc5-75a2-4142-acab-599af5e5854d'
        return new_job_uuid

    @staticmethod
    def create_dir_if_not_exist(dir_path):
        ret_IsError = False
        error_data = ""
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                ret_IsError = False
            except:
                # Log the Error (Unable to create a new directory)
                sysErrorData = str(sys.exc_info())
                error_description = "Unable to create new directory at: " + str(dir_path) + ".  Sys Error Message: " + str(sysErrorData)
                print(error_description)
                error_data = error_description
                ret_IsError = True

        # END OF        if not os.path.exists(dir_path):
        return ret_IsError, error_data

    # Problem with this method is that it COMPLETELY preserves the zip paths, we don't want the entire hierarchy.. just the directory that is being zipped.
    # @staticmethod
    # def zipdir(path, ziph):
    #     # ziph is zipfile handle
    #     for root, dirs, files in os.walk(path):
    #         for file in files:
    #             ziph.write(os.path.join(root, file))
    #
    # @staticmethod
    # def zip_all_files_in_dir(src_path, out_zip_file_name='zipfile.zip'):
    #     zipf = zipfile.ZipFile(out_zip_file_name, 'w', zipfile.ZIP_DEFLATED) #zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
    #     Task_Log.zipdir(path=str(src_path)+'/', ziph=zipf) #zipdir(path='tmp/', ziph=zipf)
    #     zipf.close()


    # Look up Operation Type (Legacy Support)   # min, max, mean, download
    @staticmethod
    def get_operation_type_from_legacy_operation_int(operation_int=0):
        operation_enum = "max"
        try:
            operation_int = int(operation_int)
            if(operation_int == 0):
                operation_enum = 'max'
            if (operation_int == 1):
                operation_enum = 'min'
            if (operation_int == 5):
                operation_enum = 'mean'
            if (operation_int == 6):
                operation_enum = 'download'
        except:
            pass

        return operation_enum


# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate

# Migrations for 'api_v2':
#   api_v2/migrations/0012_task_log.py
#     - Create model Task_Log
#
#   Applying api_v2.0012_task_log... OK







# END OF FILE!