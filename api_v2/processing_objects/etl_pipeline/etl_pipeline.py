# etl_pipeline.py

# Example Import
# from api_v2.processing_objects.etl_pipeline.etl_pipeline import ETL_Pipeline

from api_v2.app_models.model_ETL_PipelineRun        import ETL_PipelineRun
from api_v2.app_models.model_ETL_Dataset            import ETL_Dataset
from api_v2.app_models.model_ETL_Log                import ETL_Log
from api_v2.app_models.model_ETL_Granule            import ETL_Granule
from api_v2.app_models.model_Available_Granule      import Available_Granule


from django.conf import settings
from api_v2.app_models.model_Config_Setting import Config_Setting

from common_utils import utils as common_utils

import os
import sys


# Importing SubTypes
from api_v2.processing_objects.etl_pipeline.custom_scripts.etl_type__emodis import emodis   as Subtype__emodis
from api_v2.processing_objects.etl_pipeline.custom_scripts.etl_type__imerg  import imerg    as Subtype__imerg
from api_v2.processing_objects.etl_pipeline.custom_scripts.etl_type__esi    import esi      as Subtype__esi
from api_v2.processing_objects.etl_pipeline.custom_scripts.etl_type__chirps import chirps   as Subtype__chirps
# TODO finish these scripts and import them here.




# emodis construction   START
from urllib import request as urllib_request
import re
import os.path as path
import gzip
import os
import sys
import zipfile
# emodis construction   END


# ETL Pipeline is used to manage various ETL Jobs on Datasets.
# The pipeline runs through a set of standardized functions for doing the following tasks.
# # Extracting data from a remote source
# # Transforming it according to script specific logic
# # Loading it into it's destination to be used on demand by the front end application.

# Test of the pipeline
# python manage.py start_etl_pipeline --etl_dataset_uuid fRjduT9v4jHyazGBMEJe

class ETL_Pipeline():

    # Pipeline Run - UUID - What is the Database UUID for this ETL Pipeline Run Instance
    ETL_PipelineRun__UUID = ""  # Set when a new Database object is created.

    # Pipeline Config Params - Set Externally (only the etl_dataset_uuid param is actually required.  The rest are optional)
    etl_dataset_uuid            = ""
    START_YEAR_YYYY             = ""
    END_YEAR_YYYY               = ""
    START_MONTH_MM              = ""
    END_MONTH_MM                = ""
    START_DAY_DD                = ""
    END_DAY_DD                  = ""
    START_30MININCREMENT_NN     = ""
    END_30MININCREMENT_NN       = ""
    REGION_CODE                 = ""
    WEEKLY_JULIAN_START_OFFSET  = ""
    # TODO: If there are more Params, they go here

    # Pipeline - Dataset Config Options - Set by Reading Dataset Item from the Database
    dataset_name = ""
    dataset_JSONable_Object = {}

    # Keeps a list of all the ETL Log IDs created during this run.
    new_etl_log_ids__EVENTS = []
    # Keeps a list of all the ETL Logs that are Errors created during this run.
    new_etl_log_ids__ERRORS = []
    # Keeps a list of all the new ETL Granules that were created during this run.
    new_etl_granule_ids = []
    # Keeps a list of all Granules that have Errors.
    new_etl_granule_ids__ERRORS = []
    # Keeps track of any affected Available Granule from this run (The nature of 'Available Granules' are Create_Or_Update, so this is just a list of affected ids.
    affected_Available_Granule_ids = []

    # A simple and quick way to tell if an error occurred in the pipeline.
    pipeline_had_error = False

    # This is the holder for the subtype instance
    Subtype_ETL_Instance = None

    # Default Constructor
    def __init__(self):
        self.class_name = "ETL_Pipeline"

    # Overriding the string function
    def __str__(self):
        outString = ""
        try:
            outString += "class_name: " + str(self.class_name)
            outString += ", "
            outString += "etl_dataset_uuid: " + str(self.etl_dataset_uuid)
            # TODO: More output Props here
        except:
            pass
        return outString


    # Function for quick output of all pipeline properties - Mainly used for easy debugging
    def to_JSONable_Object(self):
        retObj = {}

        # Pipeline Run UUID
        retObj["ETL_PipelineRun__UUID"]     = str(self.ETL_PipelineRun__UUID).strip()

        # Pipeline Config Options
        retObj["etl_dataset_uuid"]          = str(self.etl_dataset_uuid).strip()
        # Year Range
        retObj["START_YEAR_YYYY"]           = str(self.START_YEAR_YYYY).strip()
        retObj["END_YEAR_YYYY"]             = str(self.END_YEAR_YYYY).strip()
        # Month Range
        retObj["START_MONTH_MM"]    = str(self.START_MONTH_MM).strip()
        retObj["END_MONTH_MM"]      = str(self.END_MONTH_MM).strip()
        # Day Range
        retObj["START_DAY_DD"]      = str(self.START_DAY_DD).strip()
        retObj["END_DAY_DD"]        = str(self.END_DAY_DD).strip()
        # 30 Min Increment Range
        retObj["START_30MININCREMENT_NN"]   = str(self.START_30MININCREMENT_NN).strip()
        retObj["END_30MININCREMENT_NN"]     = str(self.END_30MININCREMENT_NN).strip()
        # Region Code
        retObj["REGION_CODE"] = str(self.REGION_CODE).strip()
        # Julian Date Weekly Offset
        retObj["WEEKLY_JULIAN_START_OFFSET"] = str(self.WEEKLY_JULIAN_START_OFFSET).strip()


        # Pipeline - Dataset Config Options - Set by Reading From the Database
        retObj["dataset_name"]              = str(self.dataset_name).strip()
        retObj["dataset_JSONable_Object"]   = str(self.dataset_JSONable_Object).strip()


        retObj["new_etl_log_ids__EVENTS"]   = str(self.new_etl_log_ids__EVENTS).strip()
        retObj["new_etl_log_ids__ERRORS"]   = str(self.new_etl_log_ids__ERRORS).strip()

        retObj["new_etl_granule_ids"]               = str(self.new_etl_granule_ids).strip()
        retObj["new_etl_granule_ids__ERRORS"]       = str(self.new_etl_granule_ids__ERRORS).strip()
        retObj["affected_Available_Granule_ids"]    = str(self.affected_Available_Granule_ids).strip()




        #retObj["FUTURE_PARAM"] = str(self.FUTURE_PARAM).strip()

        return retObj


    # Standard UTIL functions (Checking for and Making Directories, parsing file names, handling datetime objects, etc)

    # Utility for creating a directory if one does not exist.
    #@staticmethod
    def create_dir_if_not_exist(self, dir_path):
        ret_IsError = False
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                #print("DONE: log_etl_event - Created New Directory: " + str(dir_path))
                #activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_DIRECTORY_CREATED
                activity_event_type     = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_DIRECTORY_CREATED", default_or_error_return_value="Directory Created")
                activity_description    = "New Directory created at path: " + str(dir_path)
                additional_json         = self.to_JSONable_Object()
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)
                ret_IsError = False
            except:
                # Log the Error (Unable to create a new directory)
                sysErrorData = str(sys.exc_info())
                #activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description = "Unable to create new directory at: " + str(dir_path) + ".  Sys Error Message: " + str(sysErrorData)
                additional_json = self.to_JSONable_Object()
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                ret_IsError = True
        # END OF        if not os.path.exists(dir_path):
        return ret_IsError





    # ###########################################################################################
    # # STANDARD WRAPPER FUNCTIONS - Used by this class and many of the ETL Script Sub Classes
    # ###########################################################################################


    # Standard Function to record Events to the database
    # Wrapper for creating a row in the ETL Log Table (Logging Events) - Defaults are set
    def log_etl_event(self, activity_event_type="default_activity", activity_description="", etl_granule_uuid="", is_alert=False, additional_json={}):
        self__etl_pipeline_run_uuid     = self.ETL_PipelineRun__UUID
        self__etl_dataset_uuid          = self.etl_dataset_uuid
        self__etl_dataset_name          = "ETL_PIPELINE__" + self.dataset_name
        etl_Log_Row_UUID = ETL_Log.create_new_etl_log_row(activity_event_type=activity_event_type,
                                                          activity_description=activity_description,
                                                          etl_pipeline_run_uuid=self__etl_pipeline_run_uuid,
                                                          etl_dataset_uuid=self__etl_dataset_uuid,
                                                          etl_granule_uuid=etl_granule_uuid,
                                                          is_alert=is_alert,
                                                          created_by=self__etl_dataset_name,
                                                          additional_json=additional_json)
        self.new_etl_log_ids__EVENTS.append(etl_Log_Row_UUID)


    # Standard Function to record Errors to the database
    # Wrapper for creating a row in the ETL Log Table but with Error info set and storing the Error ID Row
    def log_etl_error(self, activity_event_type="default_error", activity_description="an error occurred", etl_granule_uuid="", is_alert=True, additional_json={}):
        self__etl_pipeline_run_uuid     = self.ETL_PipelineRun__UUID
        self__etl_dataset_uuid          = self.etl_dataset_uuid
        self__etl_dataset_name          = "ETL_PIPELINE__" + self.dataset_name
        etl_Log_Row_UUID = ETL_Log.create_new_etl_log_row(activity_event_type=activity_event_type, activity_description=activity_description, etl_pipeline_run_uuid=self__etl_pipeline_run_uuid, etl_dataset_uuid=self__etl_dataset_uuid, etl_granule_uuid=etl_granule_uuid, is_alert=is_alert, created_by=self__etl_dataset_name, additional_json=additional_json)
        self.new_etl_log_ids__EVENTS.append(etl_Log_Row_UUID)
        self.new_etl_log_ids__ERRORS.append(etl_Log_Row_UUID)
        #
        # Output something to the terminal - this can be very helpful during debugging.
        print("")
        print("  ERROR: (error description): " + str(activity_description))
        print("")
        #
        # Signal the pipeline object that errors did occur.
        self.pipeline_had_error = True




    # Standard Function to record all Attempted Granules for this pipeline run to the Database.
    # Wrapper for creating
    def log_etl_granule(self, granule_name="unknown_etl_granule_file_or_object_name", granule_contextual_information="", granule_pipeline_state="ATTEMPTING", additional_json={}):
        # granule_pipeline_state=settings.GRANULE_PIPELINE_STATE__ATTEMPTING

        self__etl_pipeline_run_uuid     = self.ETL_PipelineRun__UUID
        self__etl_dataset_uuid          = self.etl_dataset_uuid
        self__etl_dataset_name          = "ETL_PIPELINE__" + self.dataset_name
        etl_Granule_Row_UUID = ETL_Granule.create_new_ETL_Granule_row(granule_name=granule_name,
                                                                      granule_contextual_information=granule_contextual_information,
                                                                      etl_pipeline_run_uuid=self__etl_pipeline_run_uuid,
                                                                      etl_dataset_uuid=self__etl_dataset_uuid,
                                                                      granule_pipeline_state=granule_pipeline_state,
                                                                      created_by=self__etl_dataset_name,
                                                                      additional_json=additional_json)
        self.new_etl_granule_ids.append(etl_Granule_Row_UUID)
        return etl_Granule_Row_UUID

    # Standard Function to update the State of an individual ETL Granule's granule_pipeline_state property - (When a granule has succeeded or failed)
    # def update_existing_ETL_Granule__granule_pipeline_state(granule_uuid, new__granule_pipeline_state):
    def etl_granule__Update__granule_pipeline_state(self, granule_uuid, new__granule_pipeline_state, is_error=False):
        is_update_succeed = ETL_Granule.update_existing_ETL_Granule__granule_pipeline_state(granule_uuid=granule_uuid, new__granule_pipeline_state=new__granule_pipeline_state)
        if(is_error == True):
            self.new_etl_granule_ids__ERRORS.append(granule_uuid)
            # Placing this function call here means we don't have to ever call this from the type specific classes (Custom ETL Classes)
            is_update_succeed_2 = self.etl_granule__Update__is_missing_bool_val(granule_uuid=granule_uuid, new__is_missing__Bool_Val=True)
        return is_update_succeed

    # Standard Function to update the State of an individual if it is missing from the database or not. Updates the ETL Granule's is_missing property (bool)
    # def update_existing_ETL_Granule__is_missing_bool_val(granule_uuid, new__is_missing__Bool_Val):
    def etl_granule__Update__is_missing_bool_val(self, granule_uuid, new__is_missing__Bool_Val):
        is_update_succeed = ETL_Granule.update_existing_ETL_Granule__is_missing_bool_val(granule_uuid=granule_uuid, new__is_missing__Bool_Val=new__is_missing__Bool_Val)
        return is_update_succeed

    # Standard Function for adding new JSON data to an etl_granule (Expected Use Case: if we have an error, we can attach error info as a new JSON object to the existing record)
    # def update_existing_ETL_Granule__Append_To_Additional_JSON(granule_uuid, new_json_key_to_append, sub_jsonable_object):
    def etl_granule__Append_JSON_To_Additional_JSON(self, granule_uuid, new_json_key_to_append, sub_jsonable_object):
        is_update_succeed = ETL_Granule.update_existing_ETL_Granule__Append_To_Additional_JSON(granule_uuid=granule_uuid, new_json_key_to_append=new_json_key_to_append, sub_jsonable_object=sub_jsonable_object)
        return is_update_succeed

    # Standard Function to record Available Granules to the database (This is for the Front End - Need to better define this model first)
    # def create_or_update_existing_Available_Granule_row(granule_name, granule_contextual_information, etl_pipeline_run_uuid, etl_dataset_uuid, created_by, additional_json):
    def create_or_update_Available_Granule(self, granule_name, granule_contextual_information="", additional_json={}):
        self__etl_pipeline_run_uuid = self.ETL_PipelineRun__UUID
        self__etl_dataset_uuid = self.etl_dataset_uuid
        self__etl_dataset_name = "ETL_PIPELINE__" + self.dataset_name
        affected_Available_Granule_UUID = Available_Granule.create_or_update_existing_Available_Granule_row(granule_name=granule_name,
                                                                                                            granule_contextual_information=granule_contextual_information,
                                                                                                            etl_pipeline_run_uuid=self__etl_pipeline_run_uuid,
                                                                                                            etl_dataset_uuid=self__etl_dataset_uuid,
                                                                                                            created_by=self__etl_dataset_name,
                                                                                                            additional_json=additional_json)
        self.affected_Available_Granule_ids.append(affected_Available_Granule_UUID)
        return affected_Available_Granule_UUID



    # Convenient function to call just before using a return statement during 'execute_pipeline_control_function'
    def log__pipeline_run__exit(self):
        # Log Activity - Pipeline Ended
        #activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_ENDED
        activity_event_type     = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_ENDED", default_or_error_return_value="ETL Pipeline Ended")
        activity_description    = "Pipeline Completed for Dataset: " + str(self.dataset_name)
        additional_json         = self.to_JSONable_Object()
        self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)
        #
        # Print some output for the console.
        print(activity_description)
        if(self.pipeline_had_error == True):
            print("")
            print("  AT LEAST ONE ERROR OCCURRED DURING THIS LAST PIPELINE RUN.")
            print("    Open up the Admin tool to view the error alerts, or open the Django Admin in order to see them directly.")
            print("    For quick reference, below you can find the output of the pipeline state from the last run.")
            print("")
            print("================ START ---- TERMINAL DEBUG INFO ---- START ================")
            print(str(self.to_JSONable_Object()))
            print("================ END ---- TERMINAL DEBUG INFO ---- END ================")
            print("")



    # Execute The Pipeline based on what ever was pre-configured.
    # # This is the main control function for the ETL pipeline
    def execute_pipeline_control_function(self):


        # Create a new ETL_PipelineRun Database object and store the ID
        try:
            # Use the Django ORM to create a new database object for this Pipeline Run Instance and Save it with all of it's defaults.  (A new UUID gets generated in the model file)
            new__ETL_PipelineRun_Instance = ETL_PipelineRun()
            new__ETL_PipelineRun_Instance.save()
            self.ETL_PipelineRun__UUID = str(new__ETL_PipelineRun_Instance.uuid).strip() # Save this ID.
        except:
            # Log the Error (Unable to Create New Database Object for this Pipeline Run - This means something may be wrong with the database or the connection to the database.  This must be fixed for all of the below steps to work proplery.)
            sysErrorData            = str(sys.exc_info())
            #activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
            activity_event_type     = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
            activity_description    = "Unable to Create New Database Object for this Pipeline Run - This means something may be wrong with the database or the connection to the database.  This must be fixed for all of the below steps to work properly.   For Tracking Purposes: The Dataset UUID for this Error (etl_dataset_uuid) " + self.etl_dataset_uuid + "  System Error Message: " + str(sysErrorData)
            additional_json         = self.to_JSONable_Object()
            self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
            #
            # Exit the pipeline
            self.log__pipeline_run__exit()
            return



        # The Steps
        # (1) Read dataset info from the database
        self.dataset_JSONable_Object = {} #dataset_info_JSON = {} #
        dataset_name = ""
        try:
            self.dataset_JSONable_Object = ETL_Dataset.objects.filter(uuid=self.etl_dataset_uuid)[0].to_JSONable_Object()
            dataset_name = self.dataset_JSONable_Object['dataset_name']
        except:
            # Log the Error (Unable to read the dataset object from the database)
            sysErrorData            = str(sys.exc_info())
            #activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
            activity_event_type     = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
            activity_description    = "Unable to start pipeline.  Error Reading dataset (etl_dataset_uuid) " + self.etl_dataset_uuid + " from the database: Sys Error Message: " + str(sysErrorData)
            additional_json         = self.to_JSONable_Object()
            self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
            #
            # Exit the pipeline
            self.log__pipeline_run__exit()
            return

        # Set Params pulled from the database.
        self.dataset_name = dataset_name

        # Log Activity - Pipeline Started
        #activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STARTED
        activity_event_type     = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STARTED", default_or_error_return_value="ETL Pipeline Started")
        activity_description    = "Starting Pipeline for Dataset: " + str(self.dataset_name)
        additional_json         = self.to_JSONable_Object()
        self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)



        # Get the Dataset SubType
        current_Dataset_SubType = str(self.dataset_JSONable_Object['dataset_subtype']).strip()


        # Validate that the dataset subtype is NOT Blank
        current_Dataset_SubType = str(current_Dataset_SubType).strip()
        if(current_Dataset_SubType == ""):
            list_of_valid__dataset_subtypes = ETL_Dataset.get_all_subtypes_as_string_array()
            #activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
            activity_event_type = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
            activity_description = "Unable to start pipeline.  The dataset subtype was blank.  This value is required for etl pipeline operation.  This value comes from the Dataset object in the database.  To find the correct Dataset object to modify, look up the ETL_Dataset record with ID: " + str(self.etl_dataset_uuid) + " and set the dataset_subtype property to one of these values: " + str(list_of_valid__dataset_subtypes)
            additional_json = self.to_JSONable_Object()
            self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
            #
            # Exit the pipeline
            self.log__pipeline_run__exit()
            return

        # Validate that the dataset subtype is NOT Blank
        is_valid_subtype = ETL_Dataset.is_a_valid_subtype_string(input__string=current_Dataset_SubType)
        if(is_valid_subtype == False):
            list_of_valid__dataset_subtypes = ETL_Dataset.get_all_subtypes_as_string_array()
            #activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
            activity_event_type = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
            activity_description = "Unable to start pipeline.  The dataset subtype was invalid.  The value tried was: '" + current_Dataset_SubType + "'.  This value comes from the Dataset object in the database.  To find the correct Dataset object to modify, look up the ETL_Dataset record with ID: " + str(self.etl_dataset_uuid) + " and set the dataset_subtype property to one of these values: " + str(list_of_valid__dataset_subtypes)
            additional_json = self.to_JSONable_Object()
            self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
            #
            # Exit the pipeline
            self.log__pipeline_run__exit()
            return

        # ETL_DATASET_SUBTYPE__CHIRP          = "chrip"
        # ETL_DATASET_SUBTYPE__CHIRPS         = "chrips"
        # ETL_DATASET_SUBTYPE__CHIRPS_GEFS    = "chrips_gefs"
        # ETL_DATASET_SUBTYPE__EMODIS         = "emodis"
        # ETL_DATASET_SUBTYPE__ESI_4WEEK      = "esi_4week"
        # ETL_DATASET_SUBTYPE__ESI_12WEEK     = "esi_12week"
        # ETL_DATASET_SUBTYPE__IMERG_EARLY    = "imerg_early"
        # ETL_DATASET_SUBTYPE__IMERG_LATE     = "imerg_late"

        # Process the Subtype into setting an instance of the subtype (custom code) class
        # --- Reference --- ETL Dataset Subtypes: ['chrip', 'chrips', 'chrips_gefs', 'emodis', 'esi_4week', 'esi_12week', 'imerg_early', 'imerg_late']

        # CHIRPS (Currently 3 modes for chirps)
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRP", default_or_error_return_value="chrip")):   # settings.ETL_DATASET_SUBTYPE__CHIRP
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__chirps(self)
            # Chirps is special, requires setting which mode it is in
            self.Subtype_ETL_Instance.set_chirps_mode__To__chirp()
            # Set CHIRPS Params
            self.Subtype_ETL_Instance.set_chirps_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, DD__Day__Start=self.START_DAY_DD, DD__Day__End=self.END_DAY_DD)


        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS", default_or_error_return_value="chrips")):   # settings.ETL_DATASET_SUBTYPE__CHIRPS):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__chirps(self)
            # Chirps is special, requires setting which mode it is in
            self.Subtype_ETL_Instance.set_chirps_mode__To__chirps()
            # Set CHIRPS Params
            self.Subtype_ETL_Instance.set_chirps_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, DD__Day__Start=self.START_DAY_DD, DD__Day__End=self.END_DAY_DD)


        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS_GEFS", default_or_error_return_value="chrips_gefs")):   # settings.ETL_DATASET_SUBTYPE__CHIRPS_GEFS):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__chirps(self)
            # Chirps is special, requires setting which mode it is in
            self.Subtype_ETL_Instance.set_chirps_mode__To__chirps_gefs()
            # Set CHIRPS Params
            self.Subtype_ETL_Instance.set_chirps_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, DD__Day__Start=self.START_DAY_DD, DD__Day__End=self.END_DAY_DD)


        # EMODIS (Region is an input)
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__EMODIS", default_or_error_return_value="emodis")):   # settings.ETL_DATASET_SUBTYPE__EMODIS):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__emodis(self)
            # Set EMODIS Params
            self.Subtype_ETL_Instance.set_emodis_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, XX__Region_Code=self.REGION_CODE)


        # ESI 4 Week
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_4WEEK", default_or_error_return_value="esi_4week")):   # settings.ETL_DATASET_SUBTYPE__ESI_4WEEK):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__esi(self)
            # ESI is special, requires setting which mode it is in (12week or 4week)
            self.Subtype_ETL_Instance.set_esi_mode__To__4week()
            # Set ESI Params
            self.Subtype_ETL_Instance.set_esi_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, N_offset_for_weekly_julian_start_date=self.WEEKLY_JULIAN_START_OFFSET)


        # ESI 12 Week
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_12WEEK", default_or_error_return_value="esi_12week")):   # settings.ETL_DATASET_SUBTYPE__ESI_12WEEK):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__esi(self)
            # ESI is special, requires setting which mode it is in (12week or 4week)
            self.Subtype_ETL_Instance.set_esi_mode__To__12week()
            # Set ESI Params
            self.Subtype_ETL_Instance.set_esi_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, N_offset_for_weekly_julian_start_date=self.WEEKLY_JULIAN_START_OFFSET)



        # IMERG Early
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_EARLY", default_or_error_return_value="imerg_early")):   # settings.ETL_DATASET_SUBTYPE__IMERG_EARLY):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__imerg(self)
            # Imerg is special, requires setting which mode it is in
            self.Subtype_ETL_Instance.set_imerg_mode__To__Early()
            # Set IMERG Params
            self.Subtype_ETL_Instance.set_imerg_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, DD__Day__Start=self.START_DAY_DD, DD__Day__End=self.END_DAY_DD, NN__30MinIncrement__Start=self.START_30MININCREMENT_NN, NN__30MinIncrement__End=self.END_30MININCREMENT_NN)


        # IMERG Late
        if (current_Dataset_SubType == Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_LATE", default_or_error_return_value="imerg_late")):   # settings.ETL_DATASET_SUBTYPE__IMERG_LATE):
            # Create an instance of the subtype class - this class must implement each of the pipeline functions for this to work properly.
            self.Subtype_ETL_Instance = Subtype__imerg(self)
            # Imerg is special, requires setting which mode it is in
            self.Subtype_ETL_Instance.set_imerg_mode__To__Late()
            # Set IMERG Params
            self.Subtype_ETL_Instance.set_imerg_params(YYYY__Year__Start=self.START_YEAR_YYYY, YYYY__Year__End=self.END_YEAR_YYYY, MM__Month__Start=self.START_MONTH_MM, MM__Month__End=self.END_MONTH_MM, DD__Day__Start=self.START_DAY_DD, DD__Day__End=self.END_DAY_DD, NN__30MinIncrement__Start=self.START_30MININCREMENT_NN, NN__30MinIncrement__End=self.END_30MININCREMENT_NN)



        # Validate that 'self.Subtype_ETL_Instance' is NOT NONE
        if(self.Subtype_ETL_Instance is None):
            #activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
            activity_event_type = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
            activity_description = "Unable to start pipeline.  Error: etl_pipeline.Subtype_ETL_Instance was set to None.  This object needs to be set to a specific subclass which implements each of the pipeline steps in order to continue.  "
            additional_json = self.to_JSONable_Object()
            self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
            #
            # Exit the pipeline
            self.log__pipeline_run__exit()
            return







        # # Pipeline Steps List
        # self.execute__Step__Pre_ETL_Custom()
        # self.execute__Step__Download()
        # self.execute__Step__Extract()
        # self.execute__Step__Transform()
        # self.execute__Step__Load()
        # self.execute__Step__Post_ETL_Custom()
        # self.execute__Step__Clean_Up()






        # Standardized Pipeline Steps
        has_error = False  # Keeping track of if there is an error.



        # STEP: execute__Step__Pre_ETL_Custom
        if(has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__PRE_ETL_CUSTOM
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__PRE_ETL_CUSTOM", default_or_error_return_value="Pre ETL Custom")
            has_error, step_result = self.execute__Step__Pre_ETL_Custom()
            if(has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)



        # STEP: execute__Step__Download
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__DOWNLOAD
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__DOWNLOAD", default_or_error_return_value="ETL Download")
            has_error, step_result = self.execute__Step__Download()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)


        # STEP: execute__Step__Extract
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__EXTRACT
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__EXTRACT", default_or_error_return_value="ETL Extract")
            has_error, step_result = self.execute__Step__Extract()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)

        # STEP: execute__Step__Transform
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__TRANSFORM
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__TRANSFORM", default_or_error_return_value="ETL Transform")
            has_error, step_result = self.execute__Step__Transform()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)

        # STEP: execute__Step__Load
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__LOAD
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__LOAD", default_or_error_return_value="ETL Load")
            has_error, step_result = self.execute__Step__Load()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)

        # STEP: execute__Step__Post_ETL_Custom
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__POST_ETL_CUSTOM
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__POST_ETL_CUSTOM", default_or_error_return_value="Post ETL Custom")
            has_error, step_result = self.execute__Step__Post_ETL_Custom()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)

        # STEP: execute__Step__Clean_Up
        if (has_error == False):
            #step_name = settings.ETL_PIPELINE_STEP__CLEAN_UP
            step_name = Config_Setting.get_value(setting_name="ETL_PIPELINE_STEP__CLEAN_UP", default_or_error_return_value="ETL Cleanup")
            has_error, step_result = self.execute__Step__Clean_Up()
            if (has_error == True):
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR", default_or_error_return_value="ETL Error")
                activity_description            = "An Error Occurred in the pipeline while attempting step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
                #
                # Exit the pipeline
                self.log__pipeline_run__exit()
                return
            else:
                #activity_event_type             = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED + ": " + str(step_name)
                activity_event_type             = Config_Setting.get_value(setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED", default_or_error_return_value="ETL Step Completed")
                activity_event_type             = activity_event_type + ": " + str(step_name)
                activity_description            = "The pipeline just completed step: " + str(step_name)
                additional_json                 = self.to_JSONable_Object()
                additional_json['step_result']  = step_result
                self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)


        # Exit the pipeline
        self.log__pipeline_run__exit()
        return



        ################################################        CONSTRUCTION CLEANUP LINE       START         ############################################################################
        ################################################        CONSTRUCTION CLEANUP LINE       START         ############################################################################
        ################################################        CONSTRUCTION CLEANUP LINE       START         ############################################################################


        # Pipeline overall logic // ROUGH NOTES - Thinking through emodis logic
        # -get expected files list
        # --Emodis specific logic
        # ---List of files from the ftp directory (36 chunks per year)
        # -get expected granules (from file names, what we expect as we unzip each file)
        # --Emodis specific logic
        # ---1 tif (with matching world file) per zip
        # ---make sure to store all 3 directory paths with each granule (the ftp file to get, the local zip file path, and the extracted Granule)
        # // Double check, does emodis now do 3 per month? Maybe they always have?
        # // for ingest, do we need a special way to parse date times here?
        # -process each granule
        # --check for expected extracted tif file locally, if not, then check for expected local downloaded zip file, if not exists, then check for expected remote zip file on the ftp server
        # ---If still not found (all the way back at the source) - Then throw an error that the source file for this granule was missing or not found (AT THE FTP SOURCE)
        # ---At each of the other check steps, throw errors if they happen, but mainly we want to log events at each steps of what the script is doing ("File not found locally, Checking FTP Source, etc")
        # --Once we have the granule, ingest it.
        # ---If error, throw the error in the ETL Log (And make sure to store that the granule was missing 'is_missing' flag on the ETL_granule table (VERY IMPORTANT: The error on the ETL Log table needs to tells us that this granule is missing because it because it was not able to be processed))
        # ---at the end of ingest, update the database (Granule was ingested, and store the entry of the granule - even if this creates duplicates)
        # --check for cleanup settings, if turned off, then don't delete any of the local stuff (cleanup_temp_files True/False)

        # Pipeline Operations List
        #
        # -generate expected file list          // Sometimes a file contains more than one tif or other file(s)
        # -generate expected granule list       // Sometimes this is 1 to 1 with each zip file, sometimes it is not.
        # # Now for Each Granule
        # --Check for Granule                       // Is this file sitting in the locally expected temp spot? Checking locally for the extracted file(s) needed to process the current granule
        # --Check for source datafile locally       // Has this (zip)file already been downloaded, and is it sitting in the expected local hard disk place?
        # --Check for source datafile remotely      // Does this (zip)file exist on the server where we expect it to be?  (At the original datasource)?
        # --Download the remote datafile            // Actually go and get the file from the remote source and save it locally
        # --Process Local Datafile                  // Usually this is JUST extracting the file, sometimes can be more.
        # --Extract Local Datafile                  // Extract the zip file
        # --Process Granule                         // Perform operations of adding data to the granule as needed (Adding some kind of header / temporal info to a geotiff file, etc)
        # --Load Granule Data to THREDDS            // Load the granule data into the THREDDS server (NETCDF)
        # --Update Dataset Capabilities             // Update the Django DB Dataset Record to newer capabilities (This may include a special format of catching specific missing data, maybe in the form of analyzing the ETL Granule table, and then inserting specific granule list items as 'missing')

        # Analysis / Derived
        # --Read Granules from granule log, if there are any that are missing (and don't have replacements), need to generate a list of catching those.





        # (1) Script specific logic
        #
        #
        #
        # Starting with a basic NDVI example - this will draw out all questions to be answered and coded in.
        #print("HARD CODED NOTE: execute_pipeline_control_function: About to call HARD CODED NDVI West Africa Ingest")
        #self.HC_Execute_NDVI_West_Africa_Ingest()


        ################################################        CONSTRUCTION CLEANUP LINE       END         ############################################################################
        ################################################        CONSTRUCTION CLEANUP LINE       END         ############################################################################
        ################################################        CONSTRUCTION CLEANUP LINE       END         ############################################################################



        # # DEPRECATING - MOVED this block into the log__pipeline_run__exit() function
        #
        # # Log Activity - Pipeline Ended
        # activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_ENDED
        # activity_description    = "Pipeline Completed for Dataset: " + str(self.dataset_name)
        # additional_json         = self.to_JSONable_Object()
        # self.log_etl_event(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=False, additional_json=additional_json)
        #
        # # Exit the pipeline
        # self.log__pipeline_run__exit()
        # return
    # END OF MAIN PIPELINE FUNCITON




    # TODO - for Each Step
    # TODO -- Figure out which detail function to call (maybe th


    # Note:     Standard response object defined in common.py

    # Standard Response Object Reference
    #
    # step_result['class_name']         # String
    # step_result['function_name']      # String
    # step_result['is_error']           # Bool
    # step_result['event_description']  # String
    # step_result['error_description']  # String
    # step_result['detail_state_info']  # json.dumps(PyObject {})

    def execute__Step__Pre_ETL_Custom(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Pre_ETL_Custom()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Pre_ETL_Custom:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Download(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Download()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Download:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Extract(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Extract()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Extract:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Transform(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Transform()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Transform:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Load(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Load()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Load:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Post_ETL_Custom(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Post_ETL_Custom()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Post_ETL_Custom:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    def execute__Step__Clean_Up(self):
        has_error = False
        step_result = {}
        try:
            step_result = self.Subtype_ETL_Instance.execute__Step__Clean_Up()
            has_error = step_result['is_error']
        except:
            sysErrorData = str(sys.exc_info())
            step_result['sys_error'] = "System Error in function: execute__Step__Clean_Up:  System Error Message: " + str(sysErrorData)
            has_error = True
        return has_error, step_result



    # TODO - remove all the functions down here that are not used (These ended up getting reworked into simpler functions)



    # OLDER - FIRST DRAFT STUFF - BELOW




    # TODO: Finish rewiring and simplifying the wrapper functions!

    # def execute__Step__Pre_ETL_Custom(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Pre_ETL_Custom()
    #         has_error   = step_result['is_error']
    #         if(has_error == True):
    #             activity_event_type     = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR
    #             activity_description    = step_result['error_description']
    #             additional_json         = step_result #self.to_JSONable_Object()
    #             self.log_etl_error(activity_event_type=activity_event_type, activity_description=activity_description, etl_granule_uuid="", is_alert=True, additional_json=additional_json)
    #         else:
    #             # Don't report an event here, because the function that calls this pipeline step already does that upon return.
    #             pass
    #
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error

    #
    #
    # def execute__Step__Download(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Download()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error
    #
    #
    #
    # def execute__Step__Extract(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Extract()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error
    #
    #
    #
    # def execute__Step__Transform(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Transform()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error
    #
    #
    #
    # def execute__Step__Load(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Load()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error
    #
    #
    #
    # def execute__Step__Post_ETL_Custom(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Post_ETL_Custom()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error
    #
    #
    #
    # def execute__Step__Clean_Up(self):
    #     has_error = False
    #     try:
    #         step_result = self.Subtype_ETL_Instance.execute__Step__Clean_Up()
    #         # TODO: Check if 'step_result' has an error.
    #         # # TODO: If it did, then log that error, and then return True, otherwise, don't do anything
    #         # # # TODO: The same code here for just submitting an Error Event
    #     except:
    #         # TODO: Write the error parsing here (This particular Error happens when there is actually something wrong with the SubType ETL Instance Code.)
    #         # TODO: The same code here for just submitting an Error Event
    #         has_error = True
    #     return has_error




    # TODO - REMOVE THESE BELOW FUNCTIONS - PUT THE ONES THAT ARE NEEDED IN ANY GIVEN EXISTING SUB TYPE SPECIFIC ETL SCRIPT
    # TODO - REMOVE THESE BELOW FUNCTIONS - PUT THE ONES THAT ARE NEEDED IN ANY GIVEN EXISTING SUB TYPE SPECIFIC ETL SCRIPT
    # TODO - REMOVE THESE BELOW FUNCTIONS - PUT THE ONES THAT ARE NEEDED IN ANY GIVEN EXISTING SUB TYPE SPECIFIC ETL SCRIPT
    # TODO - REMOVE THESE BELOW FUNCTIONS - PUT THE ONES THAT ARE NEEDED IN ANY GIVEN EXISTING SUB TYPE SPECIFIC ETL SCRIPT



    # Operational Pipeline Step Functions - These are the big picture functions, called by the main pipeline.  These will use the detail functions as needed.
    # # Some of these are also wrappers for specific subtypes of datasets.
    # TODO - Get Expected Files
    # TODO - Get Expected Granules


    # Usually refers to a ZIP file (just generating a list of files based on the parameters inputs)
    def get_expected_files_list(self, THE_PARAMS_HERE):
        pass

    # Usually refers to the contents of a zip file (just generating a list of granules/files based on the parameters inputs)
    def get_expected_granules_list(self, THE_PARAMS_HERE):
        pass

    # Process all the expected granules in this run // Processes the entire list
    def process_expected_granules(self, THE_PARAMS_HERE):
        pass

    # Process current expected granule  // Single Granule
    def proces_current_expected_granule(self, THE_PARAMS_HERE):
        pass


    # Operational Detail Functions - Most of these are wrappers for specific subtypes of datasets (Each subtype has it's own logic, Emodis, chirps, imerg, etc)

    def check_for_local_granule(self, THE_PARAMS_HERE):
        pass
    def check_for_local_source_datafile(self, THE_PARAMS_HERE):
        pass
    def check_for_remote_source_datafile(self, THE_PARAMS_HERE):
        pass
    def download_remote_datafile(self, THE_PARAMS_HERE):
        pass
    def extract_local_datafile(self, THE_PARAMS_HERE):
        pass
    def process_local_datafile(self, THE_PARAMS_HERE):
        pass
    # def process_granule(self, THE_PARAMS_HERE):
    #     pass
    def add_data_to_granule_data(self, THE_PARAMS_HERE):
        pass
    def load_granule_data_to_THREDDS(self, THE_PARAMS_HERE):
        pass
    def update_dataset_capabilities_info(self, THE_PARAMS_HERE):
        pass














    def HC_Execute_NDVI_West_Africa_Ingest(self):
        print("ETL_Pipeline.HC_Execute_NDVI_West_Africa_Ingest HAS STARTED")

        # ClimateSERV 1.0 did this
        # echo "Running West Africa NDVI Download from ${autoDate} to ${autoDate}"
        # python CHIRPS/utils/ftp/eMODISWestAfricaDownloader.py ${autoDate} ${autoDate}
        # echo "Done running Chirps eMODISWestAfricaDownloader"
        # python CHIRPS/utils/ingest/HDFIngestMODISNDVIData.py ${autoDate} ${autoDate}
        # echo "Done running eMODIS NDVI West Africa Ingest"

        # Understanding what is happening here
        #
        # # Files from the data source look something like this
        # ...
        # wa1932.zip              2019-12-21 18:21   59M
        # wa1933.zip              2020-01-01 18:48   58M
        # wa1934.zip              2020-01-14 20:07   56M
        # wa1935.zip              2020-01-22 20:34   54M
        # wa1936.zip              2020-02-01 11:30   53M
        # wa2001.zip              2020-02-11 11:51   52M
        # wa2002.zip              2020-02-21 11:35   50M
        # wa2003.zip              2020-03-01 11:33   49M
        # wa2004.zip              2020-03-17 21:17   48M
        # ...


        # # TODO: To Become Input Params
        #
        START_YYYY  = int(self.START_YEAR_YYYY)     # 2020
        END_YYYY    = int(self.END_YEAR_YYYY)       # 2020


        # # TODO: To Become Database Params
        #
        roothttp        = 'https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/west/dekadal/emodis/ndvi_c6/temporallysmoothedndvi/downloads/dekadal/'
        rootoutputdir   = '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/data/image/input/emodis/westafrica/'  # params.dataTypes[1]['inputDataLocation']

        # Create Download Output Directory if it does not exist
        #ETL_Pipeline.create_dir_if_not_exist(rootoutputdir)
        is_error_creating_directory = self.create_dir_if_not_exist(rootoutputdir)

        # Get the list of years to process.
        years_range = range(START_YYYY, END_YYYY + 1)

        # NEXT - GET EXPECTED GRANULES

        for current_year in years_range:
            # Make a new subdirectory for the current year
            outputdir_current_year = os.path.join(rootoutputdir, str(current_year))
            #ETL_Pipeline.create_dir_if_not_exist(outputdir_current_year)
            is_error_creating_directory = self.create_dir_if_not_exist(outputdir_current_year)
            for current_dekadal in range(1, 13):
                print(current_dekadal)
                print("THIS IS WHERE THE SUB FUNCTIONS START GETTING CALLED - PAUSED HERE FOR A MIN - NOW TIME TO GET THE LOGGING AND EVENTS STUFF WORKING.")
                self.emodis__getFileForYearAndDekadal(yearToGet=current_year, dekadalToGet=current_dekadal, roothttp=roothttp, rootoutputdir=rootoutputdir)

        print("ETL_Pipeline.HC_Execute_NDVI_West_Africa_Ingest HAS END")
        pass






    # CONSTRUCTION
    def emodis__getFileForYearAndDekadal(self, yearToGet, dekadalToGet, roothttp, rootoutputdir):
        print("-------------------------------Working on ", dekadalToGet, "/", yearToGet, "------------------------------------")

        filenum = "{:0>2d}{:0>2d}".format(yearToGet - 2000, dekadalToGet)
        revfilenum = "{:0>2d}{:0>2d}".format(dekadalToGet, yearToGet - 2000)
        year_from_zip = int(filenum[0:2])
        dekad_from_zip = int(filenum[2:4])
        url = roothttp + "wa" + filenum + '.zip'

        print("url: " + url)

        enddirectory = rootoutputdir + str(yearToGet) + "/"
        endfilename = enddirectory + "wa" + filenum + '.zip'
        revEndfilename = enddirectory + "wa" + revfilenum + '.tif'

        print("endfilename: " + endfilename)
        print("str(os.path.exists(endfilename) or filenum == '0103'): " + str(os.path.exists(endfilename) or filenum == '0103'))

        if (os.path.exists(endfilename.replace(".zip", ".tif"))) or (os.path.exists(revEndfilename)):
            print("File already here ")
        else:
            try:
                # urllib.urlretrieve(url, endfilename)
                # urllib.request.urlretrieve(url, endfilename)
                urllib_request.urlretrieve(url, endfilename)
                list_of_filenames_inside_zipfile = []
                isRenameFiles = False
                with zipfile.ZipFile(endfilename, "r") as z:
                    list_of_filenames_inside_zipfile = z.namelist()
                    isRenameFiles = self.emodis__should_rename_files(year_from_zip, list_of_filenames_inside_zipfile)
                    z.extractall(enddirectory)
                if isRenameFiles == True:
                    self.emodis__rename_files_to_new_format(enddirectory, list_of_filenames_inside_zipfile)

                self.emodis__removeTFWfiles(enddirectory)
                print("EndFile ", endfilename)
            except:
                os.remove(endfilename)
        print("-----------------------------Done working on ", dekadalToGet, "/", yearToGet, "---------------------------------")


    # Check the list of filenames and if their years are in the wrong place, return True,
    # # Called by :   def emodis__getFileForYearAndDekadal(self, yearToGet, dekadalToGet, roothttp, rootoutputdir):
    def emodis__should_rename_files(self, year_from_zip, list_of_filenames):
        for current_filename in list_of_filenames:
            part_to_compare = current_filename[4:6]
            # compare these strings, if they do NOT match.. then return True
            # Double cast here to remove extra zeros from the strings..
            if str(int(part_to_compare)) != str(int(year_from_zip)):
                print("Detected a naming format the ingest procedure will not recognize.  An attempt will be made at renaming the files.")
                return True
        return False

    # Renames the files that are in the list. # switches ea1529.tif to ea2915.tif
    def emodis__rename_files_to_new_format(self, folder_path_to_files, list_of_filenames):
        print("Attempting to rename files to match the new naming format.  This is so that the ingest will properly handle them.")
        for current_filename in list_of_filenames:
            part_to_save_pre = current_filename[0:2]
            part_to_switch_1 = current_filename[2:4]
            part_to_switch_2 = current_filename[4:6]
            part_to_save_post = current_filename[-4:]
            new_filename = part_to_save_pre + part_to_switch_2 + part_to_switch_1 + part_to_save_post
            fullpath_to_current_file = os.path.join(folder_path_to_files, current_filename)
            fullpath_to_new_filename = os.path.join(folder_path_to_files, new_filename)
            try:
                os.rename(fullpath_to_current_file, fullpath_to_new_filename)
            except:
                print("WARNING!!!!")
                print("  Failed to rename file: ")
                print("  " + str(fullpath_to_current_file))
                print("  to: ")
                print("  " + str(fullpath_to_new_filename))
                print("  To resolve this issue, rename this file manually or the ingest procedure will give very much unexpected results.")
        print("file rename procedures have finished.")

    def emodis__removeTFWfiles(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".tfw") or filename.endswith(".zip"):
                # print "Removing "+directory+filename
                os.remove(directory + filename)


    @staticmethod
    def test_function_call():
        print("ETL_Pipeline.test_function_call: Reached the End")
        pass



# ROUGH NOTES
#

# GARBAGE
#print("DONE: SET: self.Subtype_ETL_Instance to the correct class for subtype: " + str(current_Dataset_SubType))


# END
