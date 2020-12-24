from django.db import models
from common_utils import utils as common_utils
import json
import sys


# Import This Model - Usage Example
# # from api_v2.app_models.model_WorkerProcess import WorkerProcess



class WorkerProcess(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")

    # Additional Columns Here
    is_worker_processing_a_job      = models.BooleanField(  default=False, help_text="Is this Instance currently processing a job?  When a worker starts processing a job, this should be set to True, when a worker finishes processing a job, this should be set to False")
    should_worker_be_stopped        = models.BooleanField(  default=False, help_text="This allows us to disable a worker from the database level.  When we disable a worker from the database level, this gets set to True, when a worker starts / initializes, this should be set to False")
    current_run_idle_check_counter  = models.IntegerField('Current Run Idle Check Counter', blank=False, default=0, help_text="How many times has this worker done it's idle checkpoint since the last time it has been turned on?  When a worker is first started/initialized, this gets reset to 0.  Each time a worker checks for a job, this value gets incremented.")

    class_name_string = "WorkerProcess"

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
        retObj["is_worker_processing_a_job"] = str(self.is_test_object).strip()
        retObj["should_worker_be_stopped"] = str(self.is_test_object).strip()
        retObj["current_run_idle_check_counter"] = str(self.is_test_object).strip()

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





    # This is the start_worker command
    # Returns the database id for this worker
    @staticmethod
    def restart_idle_worker_or_create_and_start_new_worker():
        ready_worker_id     = ""
        is_error            = False
        error_message       = ""

        try:
            worker_process = None
            try:
                # Get an existing worker that is 'idle' (set to stopped)
                worker_process = WorkerProcess.objects.filter(should_worker_be_stopped=True)[0]
                pass
            except:
                # Create new worker
                worker_process = WorkerProcess()

            # At this point we have a worker, either it is an existing 'idle' worker or a new worker
            # # Initialize the worker.
            worker_process.current_run_idle_check_counter   =   0
            worker_process.should_worker_be_stopped         =   False
            worker_process.is_worker_processing_a_job       =   False
            worker_process.save()

            # Set the id to return.
            ready_worker_id = str(worker_process.uuid).strip()

        except:
            is_error = True
            sysErrorData = str(sys.exc_info())
            error_message = "Unable to restart existing worker or create new worker.  System Error Message: " + str(sysErrorData)

        return ready_worker_id, is_error, error_message

    @staticmethod
    def increment_worker_idle_count(worker_uuid):
        try:
            worker_process = WorkerProcess.objects.filter(uuid=str(worker_uuid))[0]
            current_run_idle_check_counter                  = worker_process.current_run_idle_check_counter
            current_run_idle_check_counter                  = current_run_idle_check_counter + 1
            worker_process.current_run_idle_check_counter   = current_run_idle_check_counter
            worker_process.save()
        except:
            sysErrorData = str(sys.exc_info())
            print("increment_worker_idle_count: Unexpected Error.  System Error Message: " + str(sysErrorData))
            pass

    @staticmethod
    def stop_worker(worker_uuid):
        did_succeed = False
        error_message = ""
        is_processing_job = False
        try:
            worker_process = WorkerProcess.objects.filter(uuid=str(worker_uuid))[0]
            worker_process.should_worker_be_stopped = True
            is_processing_job = worker_process.is_worker_processing_a_job
            worker_process.save()
            did_succeed = True
        except:
            sysErrorData = str(sys.exc_info())
            error_message = "stop_worker: Unexpected Error.  System Error Message: " + str(sysErrorData)
            print(error_message)
            did_succeed = False

        return did_succeed, error_message, is_processing_job

    @staticmethod
    def stop_all_workers():
        did_succeed = False
        error_message = ""
        try:
            WorkerProcess.objects.all().update(should_worker_be_stopped=True)
            did_succeed = True
        except:
            sysErrorData = str(sys.exc_info())
            error_message = "stop_all_workers: Unable to set all workers to their stopped state.  System Error Message: " + str(sysErrorData)
            print(error_message)
            did_succeed = False

        return did_succeed, error_message


    @staticmethod
    def is_worker_still_running(worker_uuid, stop_worker_on_fail=False):
        ret_bool = True
        try:
            worker_process = WorkerProcess.objects.filter(uuid=str(worker_uuid))[0]
            should_worker_be_stopped = worker_process.should_worker_be_stopped
            if(should_worker_be_stopped == True):
                ret_bool = False
        except:
            sysErrorData = str(sys.exc_info())
            error_message = "is_worker_still_running: There was an unexpected error when checking to see if worker: "+str(worker_uuid)+" should still be running.  System Error Message: " + str(sysErrorData)
            print(error_message)

            # If we want this error to cause the worker to actually stop running,
            if(stop_worker_on_fail == True):
                ret_bool = False

        return ret_bool

    @staticmethod
    def set_is_processing_job(worker_uuid, is_processing_job_value):
        try:
            worker_process = WorkerProcess.objects.filter(uuid=str(worker_uuid))[0]
            worker_process.is_worker_processing_a_job = is_processing_job_value
            worker_process.save()
        except:
            pass

    @staticmethod
    def get_all_active_worker_uuids():
        ret_uuids = []
        try:
            active_workers = WorkerProcess.objects.filter(should_worker_be_stopped=False)
            for active_worker_process in active_workers:
                ret_uuids.append(str(active_worker_process.uuid))
        except:
            pass
        return ret_uuids


# MAKE MIGRATIONS
# # python manage.py makemigrations api_v2
# # python manage.py migrate


# Migrations for 'api_v2':
#   api_v2/migrations/0015_workerprocess.py
#     - Create model WorkerProcess
#
# Running migrations:
#   Applying api_v2.0015_workerprocess... OK




# END OF FILE!