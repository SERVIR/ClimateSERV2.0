# model_Config_Setting.py

# TODO: IMPORTANT TODO - CONVERT ALL SETTINGS OVER TO THIS CONFIG SETTINGS OBJECT, POPULATE THE DATABASE DEFAULT SETTINGS.

from django.db import models
from common_utils import utils as common_utils
import json
import sys


# Import This Model - Usage Example
# # from api_v2.app_models.model_Config_Setting import Config_Setting



class Config_Setting(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    setting_name        = models.CharField('Setting Name', max_length=250, blank=False, default="UNKNOWN_SETTING", help_text="What is the name of this setting.  These are meant to be unique but not constrained by the database.  If there are any settings with the exact same name, please delete the duplicates.")
    setting_value       = models.TextField('Setting Value', default="{}", help_text="Setting Value.  Can be a string, or JSON Object, etc.  If this value is just a string or number only, remove the {} default.")
    setting_data_type   = models.CharField('Setting Data Type', max_length=250, blank=False, default="STRING", help_text="Setting Datatype.  This is important.  Choices are: 'STRING', 'LIST', 'JSON'.  If the datatype is not recognized, then STRING is used.  Note: JSON types are loaded with json.loads(<value>).  Note: LIST types are read as comma separated strings.  Something like '1,2,3' would get converted into ['1','2','3'] to be used in the code.  List Items have to be strings, not numbers, and not complex objects.  List Item Type conversion and validation happens at the code where it is needed.")
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)


    # Additional Columns Here

    class_name_string = "Config_Setting"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | setting_name: " + str(self.setting_name) + " | setting_data_type: " + str(self.setting_data_type) + " | setting_value: " + str(self.setting_value) + " | created_at: " + str(self.created_at)
        except:
            outString = "id: " + str(self.id) + " | setting_name: " + str(self.setting_name) + " | setting_data_type: " + str(self.setting_data_type) + " | setting_value: " + str(self.setting_value) + " | created_at: " + str(self.created_at)
        return outString


    # Non Static, Serialize current element to JSON
    def to_JSONable_Object(self):
        retObj = {}
        retObj["id"]                            = str(self.id).strip()
        retObj["setting_name"]                  = str(self.setting_name).strip()
        retObj["setting_data_type"]             = str(self.setting_data_type).strip()
        retObj["created_at"]                    = str(self.created_at).strip()


        # Pullin the Setting Value based on the datatype
        setting_data_type = str(self.setting_data_type).strip()
        try:
            if(setting_data_type == "JSON"):
                retObj["setting_value"] = json.loads(self.setting_value)
            elif(setting_data_type == "LIST"):
                retObj["setting_value"] = self.setting_value.split(',')
            else:
                # If all the above failed, just grab it as a string
                retObj["setting_value"] = str(self.setting_value).strip()
        except:
            retObj["setting_value"] = "ERROR_GETTING_VALUE"

        return retObj



    @staticmethod
    def set_value(setting_name="", setting_type="STRING", setting_value=""):
        ret_id = -1
        try:
            # Filter and Validate.
            setting_name = str(setting_name).strip()
            setting_type = str(setting_type).strip()
            if(setting_name == ""):
                print("model_Config_Setting.py: set_value: Validation Error: setting_name cannot be blank.")
                return ret_id

            # First try and see if a setting with this name already exists.  If it does, overwrite the value and type.  If not, then create a new setting and set the value and type.
            model_instance = ""
            try:
                # Get the existing model
                model_instance = Config_Setting.objects.filter(setting_name=setting_name)[0]
            except:
                # A Model does not exist, creat a new one.
                model_instance = Config_Setting()
                model_instance.setting_name = setting_name
                model_instance.save()

            # Now do the overwriting
            model_instance.setting_data_type = setting_type

            # Set the new setting_value.
            if(setting_type == "JSON"):
                model_instance.setting_value = json.dumps(setting_value)
            elif(setting_type == "LIST"):
                model_instance.setting_value = ','.join(setting_value)      # Converts ['1', '2', '3'] into '1,2,3'  // '1,2,3' is what gets stored in the database.
            else:
                model_instance.setting_value = str(setting_value).strip()

            # Save the model_instance
            model_instance.save()

            # Set the return value to the id
            ret_id = model_instance.id

        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: set_value: A Generic Error Occurred when trying to set the value a setting.  (setting_name, setting_type, setting_value): " + str(setting_name) + ", " + str(setting_type) + ", " + str(setting_value) + "  Please try again later.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)

        return ret_id



    @staticmethod
    def get_value(setting_name="", default_or_error_return_value=""):
        ret_val = ""
        try:
            # Filter and Validate.
            setting_name = str(setting_name).strip()
            if (setting_name == ""):
                print("model_Config_Setting.py: get_value: Validation Error: setting_name cannot be blank.")
                ret_val = default_or_error_return_value
                return ret_val

            # Get the first instance that matches this setting name.
            model_instance = Config_Setting.objects.filter(setting_name=setting_name)[0]

            # Get the value, the method of getting the value is based on the datatype.
            setting_value = ""
            setting_data_type = str(model_instance.setting_data_type).strip()
            if (setting_data_type == "JSON"):
                setting_value = json.loads(model_instance.setting_value)
            elif (setting_data_type == "LIST"):
                setting_value = model_instance.setting_value.split(',')
            else:
                # If all the above failed, just grab it as a string
                setting_value = str(model_instance.setting_value).strip()

            # Set the return value.
            ret_val = setting_value

        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: get_value: A Generic Error Occurred when trying to get the value a setting.  (setting_name): " + str(setting_name) + "  Please try again later.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)
            ret_val = default_or_error_return_value
        return ret_val



    # NEW CHIRPS ONLY Settings (Production Overrides)
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_Config_Setting import Config_Setting
    # # # Config_Setting.run_initial_DB_Setup_For_Config_Settings__ProductionOverrides__CHIRPS_ONLY()
    @staticmethod
    def run_initial_DB_Setup_For_Config_Settings__ProductionOverrides__CHIRPS_ONLY():
        try:
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRP', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirp/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRPS', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirps/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRPS_GEFS', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirps_gefs/')

            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRP', setting_type='STRING', setting_value='/mnt/climateserv/ucsb-chirp/global/0.05deg/daily/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRPS', setting_type='STRING', setting_value='/mnt/climateserv/ucsb-chirps/global/0.05deg/daily/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRPS_GEFS', setting_type='STRING', setting_value='/mnt/climateserv/ucsb-chirps-gefs/global/0.05deg/daily/')

            # Server Geo Processing Settings
            Config_Setting.set_value(setting_name='PATH__BASE_TEMP_WORKING_DIR__TASKS', setting_type='STRING', setting_value='/cserv2/job_data/temp_tasks_processing/')  # Append   "<Job_UUID>/"
            Config_Setting.set_value(setting_name='PATH__BASE_DATA_OUTPUT_DIR__TASKS', setting_type='STRING', setting_value='/cserv2/job_data/tasks_data_out/')  # Append   "<Job_UUID>/"

        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: run_initial_DB_Setup_For_Config_Settings__ProductionOverrides__CHIRPS_ONLY: A Generic Error Occurred when trying to setup the additional CHIRPS settings for Production.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)

        print("Finished run_initial_DB_Setup_For_Config_Settings__ProductionOverrides__CHIRPS_ONLY()")


    # NEW CHIRPS ONLY Settings
    #
    # UPDATED THIS: Updated this to include the jobs processing directory as well.
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_Config_Setting import Config_Setting
    # # # Config_Setting.run_initial_DB_Setup_For_Config_Settings__CHIRPS_ONLY()
    @staticmethod
    def run_initial_DB_Setup_For_Config_Settings__CHIRPS_ONLY():
        try:
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__CHIRP', setting_type='STRING', setting_value='https://data.chc.ucsb.edu/products/CHIRP/daily/')
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__CHIRPS', setting_type='STRING', setting_value='https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/')
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__CHIRPS_GEFS', setting_type='STRING', setting_value='https://data.chc.ucsb.edu/products/CHIRPS-GEFS_precip/daily_last/')

            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRP', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirp/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRPS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirps/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__CHIRPS_GEFS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/chirps/chirps_gefs/')

            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRP', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirp/global/0.05deg/daily/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRPS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirps/global/0.05deg/daily/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__CHIRPS_GEFS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirps-gefs/global/0.05deg/daily/')

            # Server Geo Processing Settings
            Config_Setting.set_value(setting_name='PATH__BASE_TEMP_WORKING_DIR__TASKS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/temp_tasks_processing/')    # Append   "<Job_UUID>/"
            Config_Setting.set_value(setting_name='PATH__BASE_DATA_OUTPUT_DIR__TASKS', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/')            # Append   "<Job_UUID>/"

        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: run_initial_DB_Setup_For_Config_Settings__CHIRPS_ONLY: A Generic Error Occurred when trying to setup the additional CHIRPS settings.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)

        print("Finished run_initial_DB_Setup_For_Config_Settings__CHIRPS_ONLY()")


    # Run this one after running run_initial_DB_Setup_For_Config_Settings
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_Config_Setting import Config_Setting
    # # # Config_Setting.run_initial_DB_Setup_For_Config_Settings__ProductionOverrides()
    @staticmethod
    def run_initial_DB_Setup_For_Config_Settings__ProductionOverrides():
        try:
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__EA', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/eastafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__WA', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/westafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__SA', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/southernafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__CTA', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/centralasia/')
            #
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__IMERG__EARLY', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/early/')  # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__IMERG__LATE', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/late/')  # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            #
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__ESI__4WEEK', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/esi/4week/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__ESI__12WEEK', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/esi/12week/')
            #
            # # The Directory on the server's local filesystem where THREDDS is monitoring for NC4 files - This is the destination directory where the load step places the final granule NC4 files.
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__EA', setting_type='STRING', setting_value='/mnt/climateserv/emodis-ndvi/eastafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__WA', setting_type='STRING', setting_value='/mnt/climateserv/emodis-ndvi/westafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__SA', setting_type='STRING', setting_value='/mnt/climateserv/emodis-ndvi/southernafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__CTA', setting_type='STRING', setting_value='/mnt/climateserv/emodis-ndvi/centralasia/250m/10dy/')
            #
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__IMERG__EARLY', setting_type='STRING', setting_value='/mnt/climateserv/nasa-imerg-early/global/0.1deg/30min/')  # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__IMERG__LATE', setting_type='STRING', setting_value='/mnt/climateserv/nasa-imerg-late/global/0.1deg/30min/')  # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            #
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__ESI__4WEEK', setting_type='STRING', setting_value='/mnt/climateserv/sport-esi/global/0.05deg/4wk/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__ESI__12WEEK', setting_type='STRING', setting_value='/mnt/climateserv/sport-esi/global/0.05deg/12wk/')

            # DEFAULT PATH SETTINGS
            #
            # Default Path Settings - This is the default/fall back location for where temp files are processed and where THREDDS files are placed if there are any issues in the logic for selecting the correct paths
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__DEFAULT', setting_type='STRING', setting_value='/data/etl/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/UNKNOWN/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__DEFAULT', setting_type='STRING', setting_value='/mnt/climateserv/UNKNOWN/')


        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: run_initial_DB_Setup_For_Config_Settings__ProductionOverrides: A Generic Error Occurred when trying to setup the default settings for Production.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)

        print("Finished run_initial_DB_Setup_For_Config_Settings__ProductionOverrides()")

    # This function sets the database to have all the needed configuration options to run the app on it's own.  Without these config settings, the application won't work properly.
    # # Note, running this AFTER the server is has already been configured (and maybe some settings changed) will cause all settings to revert back to defaults.
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_Config_Setting import Config_Setting
    # # # Config_Setting.run_initial_DB_Setup_For_Config_Settings()
    @staticmethod
    def run_initial_DB_Setup_For_Config_Settings():
        try:
            # Example function call to set value (Creates or updates a new settings)
            # # Config_Setting.set_value(setting_name='config_setting_name', setting_type='STRING', setting_value='config_setting_val')

            # Examples showing how to use the settings
            example_complex_obj = {}
            example_complex_obj['key_1'] = 'val_1'
            example_complex_obj['key_2'] = 2
            example_complex_obj['key_3'] = {}
            example_complex_obj['key_3']['sub_key_a'] = 'key_3.a_val'
            Config_Setting.set_value(setting_name='AN_EXAMPLE_SETTING_STRING', setting_type='STRING', setting_value='example_string_value')
            Config_Setting.set_value(setting_name='AN_EXAMPLE_SETTING_LIST', setting_type='STRING', setting_value=['1', '2', '3'])              # Note: [1,2,3] will NOT work, must be lists of strings, ['1','2','3']
            Config_Setting.set_value(setting_name='AN_EXAMPLE_SETTING_JSON', setting_type='STRING', setting_value=example_complex_obj)


            Config_Setting.set_value(setting_name='ZMQ_LOCAL_QUEUE_ADDRESS', setting_type='STRING', setting_value='ipc:///tmp/servir/Q1/input')


            # LOCAL PATH Settings
            #
            # # The Temp Directory on the server's local filesystem where files are downloaded, extracted and transformed
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__EA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/eastafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__WA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/westafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__SA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/southernafrica/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__EMODIS__CTA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/emodis/centralasia/')
            #
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__IMERG__EARLY', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/early/')         # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__IMERG__LATE', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/late/')           # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            #
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__ESI__4WEEK', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/esi/4week/')
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__ESI__12WEEK', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/esi/12week/')
            #
            # # The Directory on the server's local filesystem where THREDDS is monitoring for NC4 files - This is the destination directory where the load step places the final granule NC4 files.
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__EA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__WA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/westafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__SA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/southernafrica/250m/10dy/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__EMODIS__CTA', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/centralasia/250m/10dy/')
            #
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__IMERG__EARLY', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/nasa-imerg-early/global/0.1deg/30min/')   # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__IMERG__LATE', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/nasa-imerg-late/global/0.1deg/30min/')     # NOTE: the Year must be appended to the end of this one, ex: setting + /2019/
            #
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__ESI__4WEEK', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/sport-esi/global/0.05deg/4wk/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__ESI__12WEEK', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/sport-esi/global/0.05deg/12wk/')

            # DEFAULT PATH SETTINGS
            #
            # Default Path Settings - This is the default/fall back location for where temp files are processed and where THREDDS files are placed if there are any issues in the logic for selecting the correct paths
            Config_Setting.set_value(setting_name='PATH__TEMP_WORKING_DIR__DEFAULT', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/UNKNOWN/')
            Config_Setting.set_value(setting_name='PATH__THREDDS_MONITORING_DIR__DEFAULT', setting_type='STRING', setting_value='/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/UNKNOWN/')

            # REMOTE PATH SETTINGS
            #
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__EMODIS__EA', setting_type='STRING', setting_value='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/east/dekadal/emodis/ndvi_c6/temporallysmoothedndvi/downloads/dekadal/')  # East Africa
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__EMODIS__WA', setting_type='STRING', setting_value='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/west/dekadal/emodis/ndvi_c6/temporallysmoothedndvi/downloads/dekadal/')  # West Africa
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__EMODIS__SA', setting_type='STRING', setting_value='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/africa/southern/dekadal/emodis/ndvi_c6/temporallysmoothedndvi/downloads/dekadal/') # Southern Africa
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__EMODIS__CTA', setting_type='STRING', setting_value='https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/asia/centralasia/dekadal/emodis/ndvi_c6/temporallysmoothedndvi/downloads/dekadal/') # Central Asia
            #
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__IMERG__EARLY', setting_type='STRING', setting_value='/data/imerg/gis/early/')    # Note: EARLY, from here only requires /yyyy/mm/ appended to path  # // ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/early/
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__IMERG__LATE', setting_type='STRING', setting_value='/data/imerg/gis/')           # Note: LATE, from here only requires /yyyy/mm/ appended to path  # // ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/
            #
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__ESI_4WK', setting_type='STRING', setting_value='https://geo.nsstc.nasa.gov/SPoRT/outgoing/crh/4servir/')  # Both 12 and 4 week products dump to the same directory - just have different file names
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__ESI_12WK', setting_type='STRING', setting_value='https://geo.nsstc.nasa.gov/SPoRT/outgoing/crh/4servir/')
            #
            # TODO - Chirps
            #
            # Default Remote Path
            Config_Setting.set_value(setting_name='REMOTE_PATH__ROOT_HTTP__DEFAULT', setting_type='STRING', setting_value='localhost://UNKNOWN_URL')

            # ETL Logs - Activity Types
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__DEFAULT', setting_type='STRING', setting_value='Default ETL Activity Event Type')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__UNKNOWN', setting_type='STRING', setting_value='Unknown ETL Activity Event Type')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STARTED', setting_type='STRING', setting_value='ETL Pipeline Run Started')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_DIRECTORY_CREATED', setting_type='STRING', setting_value='ETL Pipeline Created a new directory.')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_STEP_COMPLETED', setting_type='STRING', setting_value='ETL Pipeline Completed Step')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__PIPELINE_ENDED', setting_type='STRING', setting_value='ETL Pipeline Run Ended')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR', setting_type='STRING', setting_value='ETL Error')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING', setting_type='STRING', setting_value='ETL Warning')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_BLANK', setting_type='STRING', setting_value='Temp ETL Working Directory was blank')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_REMOVED', setting_type='STRING', setting_value='Temp ETL Working Directory was removed')
            Config_Setting.set_value(setting_name='ETL_LOG_ACTIVITY_EVENT_TYPE__DOWNLOAD_PROGRESS', setting_type='STRING', setting_value='ETL Pipeline Download Progress')

            #
            # # Step Specific Pipeline Event Tracking - Standardized, human readable names used in the descriptions of event tracking.
            # # The Standardization makes it easier for aggregating the Events into groups.
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__PRE_ETL_CUSTOM', setting_type='STRING', setting_value="ETL Pipeline Step 'Pre ETL Custom Processing'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__DOWNLOAD', setting_type='STRING', setting_value="ETL Pipeline Step 'Download'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__EXTRACT', setting_type='STRING', setting_value="ETL Pipeline Step 'Extract'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__TRANSFORM', setting_type='STRING', setting_value="ETL Pipeline Step 'Transform'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__LOAD', setting_type='STRING', setting_value="ETL Pipeline Step 'Load'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__POST_ETL_CUSTOM', setting_type='STRING', setting_value="ETL Pipeline Step 'Post ETL Custom Processing'")
            Config_Setting.set_value(setting_name='ETL_PIPELINE_STEP__CLEAN_UP', setting_type='STRING', setting_value="ETL Pipeline Step 'Clean up'")
            #
            #
            # ETL Dataset SubTypes
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__CHIRP', setting_type='STRING', setting_value='chirp')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__CHIRPS', setting_type='STRING', setting_value='chirps')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__CHIRPS_GEFS', setting_type='STRING', setting_value='chirps_gefs')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__EMODIS', setting_type='STRING', setting_value='emodis')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__ESI_4WEEK', setting_type='STRING', setting_value='esi_4week')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__ESI_12WEEK', setting_type='STRING', setting_value='esi_12week')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__IMERG_EARLY', setting_type='STRING', setting_value='imerg_early')
            Config_Setting.set_value(setting_name='ETL_DATASET_SUBTYPE__IMERG_LATE', setting_type='STRING', setting_value='imerg_late')

            Config_Setting.set_value(setting_name='GRANULE_PIPELINE_STATE__ATTEMPTING', setting_type='STRING', setting_value='ATTEMPTING')
            Config_Setting.set_value(setting_name='GRANULE_PIPELINE_STATE__ATTEMPTED', setting_type='STRING', setting_value='ATTEMPTED')
            Config_Setting.set_value(setting_name='GRANULE_PIPELINE_STATE__SUCCESS', setting_type='STRING', setting_value='SUCCESS')
            Config_Setting.set_value(setting_name='GRANULE_PIPELINE_STATE__FAILED', setting_type='STRING', setting_value='FAILED')

            # Placeholder Credential Settings
            print("model_Config_Setting.py: run_initial_DB_Setup_For_Config_Settings: About to add the settings for Credentials, please remember to fill this out or the ETLs the processes that require credentials will not work.")
            Config_Setting.set_value(setting_name='FTP_CREDENTIAL_IMERG__USER', setting_type='STRING', setting_value='billy.ashmall@nasa.gov')
            Config_Setting.set_value(setting_name='FTP_CREDENTIAL_IMERG__PASS', setting_type='STRING', setting_value='billy.ashmall@nasa.gov')
            Config_Setting.set_value(setting_name='FTP_CREDENTIAL_IMERG__HOST', setting_type='STRING', setting_value='jsimpson.pps.eosdis.nasa.gov')


            # LIST TYPES
            # API LOGGING SETTINGS
            API_LOGGING_ENDPOINT_IGNORE_LIST = [
                # '/api_v2/get_server_versions/',
                '/api_v2/admin_get_db_item/',
                '/api_v2/admin_get_api_logs/',
                '/api_v2/admin_get_etl_logs/',
                '/api_v2/admin_get_dashboard_data/',
            ]
            Config_Setting.set_value(setting_name='API_LOGGING_ENDPOINT_IGNORE_LIST', setting_type='LIST', setting_value=API_LOGGING_ENDPOINT_IGNORE_LIST)

            # # Example to add more to the settings
            # Config_Setting.set_value(setting_name='config_setting_name', setting_type='STRING', setting_value='config_setting_val')

        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "model_Config_Setting.py: run_initial_DB_Setup_For_Config_Settings: A Generic Error Occurred when trying to setup ALL of the default settings.  System Error Message: " + str(sys_error_info)
            print(human_readable_error)

        print("Finished run_initial_DB_Setup_For_Config_Settings()")
        # return # some return value?
    # END OF    def run_initial_DB_Setup():




# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate

# Migrations for 'api_v2':
#  api_v2/migrations/0010_config_setting.py
#    - Create model Config_Setting
# Applying api_v2.0010_config_setting... OK


# Changed type from TextField to CharField
#
# Make Migrations
#   api_v2/migrations/0011_auto_20200822_2039.py
#           - Alter field setting_data_type on config_setting
# Run Migrations
#   Applying api_v2.0011_auto_20200822_2039... OK
#





# END OF FILE!