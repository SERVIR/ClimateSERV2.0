# ETL Datasets // For keeping track of each ETL job (Each unique ETL Job has it's own entry in this table.  Each
# Unique pipeline run (unique set of logic to pull in external data) has an entry here)

from django.db import models
from common_utils import utils as common_utils
import json
import sys

from django.conf import settings
from api_v2.app_models.model_Config_Setting import Config_Setting


# Import This Model - Usage Example
# # from api_v2.app_models.model_ETL_Dataset import ETL_Dataset



class ETL_Dataset(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)

    # Additional Columns Here
    dataset_name            = models.CharField('Human Readable Dataset Short Name', max_length=90, blank=False, default="Unknown Dataset Name", help_text="A Human Readable Custom Name to identify this dataset.  Typically expected usage would be for Admin to set this name so they can quickly understand which data set they are looking at.  They could also use the other TDS fields to understand exactly which dataset this refers to.")
    dataset_subtype         = models.CharField('Dataset Subtype', max_length=90, blank=False, default="Unknown_Dataset_Subtype", help_text="IMPORTANT: This setting is used by the pipeline to select which specific sub type script logic gets used to execute the ETL job.  There are a set list of Subtypes, use python manage.py list_etl_dataset_subtypes to see a list of all subtypes.")
    is_pipeline_enabled     = models.BooleanField(default=False, help_text="Is this ETL Dataset currently set to 'enabled' for ETL Pipeline processing?  If this is set to False, then when the ETL job runs to process this incoming data, the ETL pipeline for this process will be stopped before it makes an attempt.  This is intended as a way for admin to just 'turn off' or 'turn on' a specific ETL job that has been setup.")
    is_pipeline_active      = models.BooleanField(default=False, help_text="Is this ETL Dataset currently being run through the ETL Pipeline? If this is set to True, that means an ETL job is actually running for this specific dataset and data ingestion is currently in progress.  When a pipeline finishes (success or error) this value should be set to False by the pipeline code.")
    capabilities            = models.TextField('JSON Data', default="{}", help_text="Set Automatically by ETL Pipeline.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.  This is a field to hold Dataset specific information that the clientside code may need access to in order to properly render the details from this dataset.  (In ClimateSERV 1.0, some of this was a GeoReference, Time/Date Ranges, and other information.)")
    #
    # THREDDS Columns (Following Threads Data Server Conventions (TDS))
    tds_product_name        = models.CharField('(TDS Conventions) Product Name', max_length=90, blank=False, default="UNKNOWN_PRODUCT_NAME", help_text="The Product name as defined on the THREDDS Data Server (TDS) Conventions Document.  Example Value: 'EMODIS-NDVI'")
    tds_region              = models.CharField('(TDS Conventions) Region', max_length=90, blank=False, default="UNKNOWN_REGION", help_text="The Region as defined on the THREDDS Data Server (TDS) Conventions Document.  Example Value: 'Global'")
    tds_spatial_resolution  = models.CharField('(TDS Conventions) Spatial Resolution', max_length=90, blank=False, default="UNKNOWN_SPATIAL_RESOLUTION", help_text="The Spatial Resolution as defined on the THREDDS Data Server (TDS) Conventions Document.  Example Value: '250m'")
    tds_temporal_resolution = models.CharField('(TDS Conventions) Temporal Resolution', max_length=90, blank=False, default="UNKNOWN_TEMPORAL_RESOLUTION", help_text="The Temporal Resolution as defined on the THREDDS Data Server (TDS) Conventions Document.  Example Value: '2mon'")

    # New fields needed during Job Processing
    dataset_legacy_datatype     = models.CharField('Legacy datatype', max_length=5, blank=False, default="9999", help_text="The 'datatype' number from ClimateSERV 1.0.  This is mapped in support of Legacy API Requests")
    dataset_nc4_variable_name   = models.CharField('Variable Name inside NC4 File', max_length=40, blank=False, default="ndvi", help_text="To select data from an NC4 file requires a variable name.  This is the field where a variable name must be set for the selection from NC4 file to work properly.")
    is_lat_order_reversed       = models.BooleanField(default=False, help_text="Some datasets have their lat order reversed.  The downstream affect of this has to do with NC4 data selection.  If this flag is set to True then we use, latitude=slice(max_Lat, min_Lat), if it is set to false, then the selection uses latitude=slice(min_Lat, max_Lat) - Note, at the time of this writing, NDVI types should be set to False")
    dataset_base_directory_path = models.CharField('Base Directory Path', max_length=255, blank=False, default="UNSET", help_text="This is a field that tells the job processing code where to look to find ALL of the NetCDF files (NC4 files) for this dataset.  In many cases (at this time all cases) this is the same as the setting for the THREDDS output directory. This is an absolute path which means the directory path should begin with /.  The code that uses this also expects a / at the end of the directory name.")
    #get_dataset_base_directory_path

    # TODO: Latency Tracking/info
    #
    # TODO: Consider Pipeline Scheduling
    #
    # TODO: JSON Configuration
    #


    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")




    class_name_string = "ETL_Dataset"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | dataset_name: " + str(self.dataset_name) + " | dataset_subtype: " + str(self.dataset_subtype) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | dataset_name: " + str(self.dataset_name) + " | dataset_subtype: " + str(self.dataset_subtype) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
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
        retObj["dataset_name"]              = str(self.dataset_name).strip()
        retObj["dataset_subtype"]           = str(self.dataset_subtype).strip()
        retObj["is_pipeline_enabled"]       = str(self.is_pipeline_enabled).strip()
        retObj["is_pipeline_active"]        = str(self.is_pipeline_active).strip()
        retObj["capabilities"]              = str(self.capabilities).strip()
        retObj["tds_product_name"]          = str(self.tds_product_name).strip()
        retObj["tds_region"]                = str(self.tds_region).strip()
        retObj["tds_spatial_resolution"]    = str(self.tds_spatial_resolution).strip()
        retObj["tds_temporal_resolution"]   = str(self.tds_temporal_resolution).strip()

        retObj["dataset_legacy_datatype"] = str(self.dataset_legacy_datatype).strip()
        retObj["dataset_nc4_variable_name"] = str(self.dataset_nc4_variable_name).strip()
        retObj["is_lat_order_reversed"]     = str(self.is_lat_order_reversed).strip()
        retObj["dataset_base_directory_path"] = str(self.dataset_base_directory_path).strip()





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

    # For listing just the DatasetName and UUIDs together
    def to_JSONable_Object__For_UUID_DatasetName_PreviewList(self):
        retObj = {}
        retObj["uuid"] = str(self.uuid).strip()
        retObj["dataset_name"] = str(self.dataset_name).strip()
        return retObj

    @staticmethod
    def is_datasetname_avalaible(input__datasetname):
        retBool = True
        try:
            existing_auth_user = ETL_Dataset.objects.filter(dataset_name=str(input__datasetname).strip())[0]
            retBool = False
        except:
            retBool = True
        return retBool

    @staticmethod
    def create_etl_dataset_from_datasetname_only(input__datasetname, created_by="create_dataset_from_datasetname_only"):
        ret_did_create_dataset = False
        ret_Dataset_UUID = ""
        try:
            new_ETL_Dataset = ETL_Dataset()
            new_ETL_Dataset.dataset_name = str(input__datasetname).strip()
            new_ETL_Dataset.created_by = str(created_by).strip()
            new_ETL_Dataset.save()
            ret_Dataset_UUID = new_ETL_Dataset.uuid
            ret_did_create_dataset = True
        except:
            ret_Dataset_UUID = ""
            ret_did_create_dataset = False
        return ret_did_create_dataset, ret_Dataset_UUID

    @staticmethod
    def does_etl_dataset_exist__by_uuid(input__uuid):
        ret_DoesExist = False
        try:
            existing_etl_dataset = ETL_Dataset.objects.filter(uuid=str(input__uuid).strip())[0]
            ret_DoesExist = True
        except:
            ret_DoesExist = False
        return ret_DoesExist

    @staticmethod
    def get_all_etl_datasets_preview_list():
        ret_List = []
        try:
            all_datasets = ETL_Dataset.objects.all()
            for current_dataset in all_datasets:
                ret_List.append(current_dataset.to_JSONable_Object__For_UUID_DatasetName_PreviewList())
        except:
            ret_List = []
        return ret_List


    @staticmethod
    def get_all_subtypes_as_string_array():
        retArray = []
        # Refactor Note: Some Settings are now coming from the database (instead of the django settings file)
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__CHIRP)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRP", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__CHIRPS)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__CHIRPS_GEFS)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS_GEFS", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__EMODIS)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__EMODIS", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__ESI_4WEEK)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_4WEEK", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__ESI_12WEEK)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_12WEEK", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__IMERG_EARLY)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_EARLY", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__IMERG_LATE)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_LATE", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__IMERG_LATE)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_1_Day_LATE", default_or_error_return_value=""))
        except:
            pass
        try:
            #retArray.append(settings.ETL_DATASET_SUBTYPE__IMERG_LATE)
            retArray.append(Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_1_Day_EARLY", default_or_error_return_value=""))
        except:
            pass
        return retArray

    # Helper function for checking if an input string is one of the valid subtypes.
    @staticmethod
    def is_a_valid_subtype_string(input__string):
        retBool = False
        try:
            input__string = str(input__string).strip()
            valid_subtypes_string_list = ETL_Dataset.get_all_subtypes_as_string_array()
            if (input__string in valid_subtypes_string_list):
                retBool = True
        except:
            retBool = False
        return retBool



    # def get_dataset_by_legacy_datatype(legacy_datatype="0"):  // return existing_dataset_json, is_error, error_message
    @staticmethod
    def get_dataset_by_legacy_datatype(legacy_datatype="0"):
        is_error = False
        error_message = ""
        existing_dataset_json = {}
        try:
            existing_dataset_json = ETL_Dataset.objects.filter(dataset_legacy_datatype=str(legacy_datatype).strip())[0].to_JSONable_Object()
        except:
            is_error = True
            error_message = "get_dataset_by_legacy_datatype: No dataset found for legacy_datatype: " + str(legacy_datatype)
        return existing_dataset_json, is_error, error_message


    # @staticmethod
    # def get_dataset_base_directory_path(dataset_id):
    #     print("UPDATE: THIS FUNCTION IS NOT NEEDED- get_dataset_base_directory_path - from param - dataset_id")
    #     pass


    # Setup Legacy Dataset Numbers
    #
    # To run locally, do this
    # # from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
    # # processed_dataset_names_list = ETL_Dataset.run_initial_DB_Setup__LegacyDatasetTypes(is_production=False)
    @staticmethod
    def run_initial_DB_Setup__LegacyDatasetTypes(is_production=True):
        dataset_name_to_types_map = []
        dataset_name_to_types_map.append({"dataset_name": "chirp_global_0_05deg_1dy",               "dataset_legacy_datatype": "0",     "is_lat_order_reversed":True,  "dataset_nc4_variable_name": "precipitation_amount",    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirp/global/0.05deg/daily/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/ucsb-chirp/global/0.05deg/daily/"      })
        dataset_name_to_types_map.append({"dataset_name": "chirps_global_0_05deg_1dy",              "dataset_legacy_datatype": "211",   "is_lat_order_reversed":True,  "dataset_nc4_variable_name": "precipitation_amount",    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirps/global/0.05deg/daily/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/ucsb-chirps/global/0.05deg/daily/"      })
        dataset_name_to_types_map.append({"dataset_name": "chirpsgef_global_0_05deg_1dy",           "dataset_legacy_datatype": "32",    "is_lat_order_reversed":True,  "dataset_nc4_variable_name": "precipitation_amount",    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/ucsb-chirps-gefs/global/0.05deg/daily/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/ucsb-chirps-gefs/global/0.05deg/daily/"      })

        dataset_name_to_types_map.append({"dataset_name": "esi_global_0_05deg_4wk",                 "dataset_legacy_datatype": "221",   "is_lat_order_reversed":True,  "dataset_nc4_variable_name": "esi",                     "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/sport-esi/global/0.05deg/4wk/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/sport-esi/global/0.05deg/4wk/"      })
        dataset_name_to_types_map.append({"dataset_name": "esi_global_0_05deg_12wk",                "dataset_legacy_datatype": "33",    "is_lat_order_reversed":True,  "dataset_nc4_variable_name": "esi",                     "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/sport-esi/global/0.05deg/12wk/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/sport-esi/global/0.05deg/12wk/"      })

        dataset_name_to_types_map.append({"dataset_name": "emodis_ndvi_centralasia_250m_10dy",      "dataset_legacy_datatype": "28",    "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "ndvi",                    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/centralasia/250m/10dy/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/emodis-ndvi/centralasia/250m/10dy/"      })
        dataset_name_to_types_map.append({"dataset_name": "emodis_ndvi_southernafrica_250m_10dy",   "dataset_legacy_datatype": "5",     "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "ndvi",                    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/southernafrica/250m/10dy/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/emodis-ndvi/southernafrica/250m/10dy/"      })
        dataset_name_to_types_map.append({"dataset_name": "emodis_ndvi_westafrica_250m_10dy",       "dataset_legacy_datatype": "1",     "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "ndvi",                    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/westafrica/250m/10dy/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/emodis-ndvi/westafrica/250m/10dy/"      })
        dataset_name_to_types_map.append({"dataset_name": "emodis_ndvi_eastafrica_250m_10dy",       "dataset_legacy_datatype": "2",     "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "ndvi",                    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/emodis-ndvi/eastafrica/250m/10dy/"      })

        dataset_name_to_types_map.append({"dataset_name": "imerg_late_global_0_1deg_30min",         "dataset_legacy_datatype": "201",   "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "precipitation_amount",    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/nasa-imerg-late/global/0.1deg/30min/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/nasa-imerg-late/global/0.1deg/30min/"      })
        dataset_name_to_types_map.append({"dataset_name": "imerg_early_global_0_1deg_30min",        "dataset_legacy_datatype": "202",   "is_lat_order_reversed":True,   "dataset_nc4_variable_name": "precipitation_amount",    "LOCAL__dataset_base_directory_path": "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/nasa-imerg-early/global/0.1deg/30min/",       "PRODUCTION__dataset_base_directory_path": "/mnt/climateserv/nasa-imerg-early/global/0.1deg/30min/"      })

        dataset_name_to_types_map.append({"dataset_name": "CSERV-TEST_PIPELINE_DATASET",            "dataset_legacy_datatype": "999",   "is_lat_order_reversed":False,  "dataset_nc4_variable_name": "unset",                   "LOCAL__dataset_base_directory_path": "/UNSET/",       "PRODUCTION__dataset_base_directory_path": "/UNSET/"      })


        processed_dataset_names_list = []

        try:
            for dataset_info in dataset_name_to_types_map:
                dataset_name                = str(dataset_info["dataset_name"]).strip()
                dataset_legacy_datatype     = str(dataset_info["dataset_legacy_datatype"]).strip()
                dataset_nc4_variable_name   = str(dataset_info["dataset_nc4_variable_name"]).strip()
                is_lat_order_reversed       = dataset_info["is_lat_order_reversed"]

                dataset_base_directory_path = "/UNSET/"
                if(is_production == True):
                    dataset_base_directory_path = str(dataset_info["PRODUCTION__dataset_base_directory_path"]).strip()
                else:
                    dataset_base_directory_path = str(dataset_info["LOCAL__dataset_base_directory_path"]).strip()

                try:
                    current_dataset = ETL_Dataset.objects.filter(dataset_name=dataset_name)[0]
                    current_dataset.dataset_legacy_datatype         = dataset_legacy_datatype
                    current_dataset.dataset_nc4_variable_name       = dataset_nc4_variable_name
                    current_dataset.is_lat_order_reversed           = is_lat_order_reversed
                    current_dataset.dataset_base_directory_path     = dataset_base_directory_path
                    current_dataset.save()
                    processed_dataset_names_list.append(dataset_name)
                except:
                    sysErrorData = str(sys.exc_info())
                    print("run_initial_DB_Setup__LegacyDatasetTypes: Uncaught Error in inner loop when attempting to set (dataset name): " + str(dataset_name) + ".  System Error Message: " + str(sysErrorData))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup__LegacyDatasetTypes: Uncaught Error in outer loop.  System Error Message: " + str(sysErrorData))

        print("run_initial_DB_Setup__LegacyDatasetTypes: Completed: (processed_dataset_names_list): " + str(processed_dataset_names_list))

        return processed_dataset_names_list



    # This function was written AFTER the initial one was already installed on production.  This only ONLY (re)sets the 3 Chirp(s) dataset types
    #
    # This function sets the database to have all the current Dataset Types.  This is a shortcut to getting started.
    # # Note, running this AFTER the server is has already been configured (and maybe some settings changed) will cause all settings to revert back to defaults.
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
    # # # result_uuids = ETL_Dataset.run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only()
    @staticmethod
    def run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only():
        created_uuid_list = []

        # ETL_DATASET_SUBTYPE__CHIRP          = "chirp"
        # ETL_DATASET_SUBTYPE__CHIRPS         = "chirps"
        # ETL_DATASET_SUBTYPE__CHIRPS_GEFS    = "chirps_gefs"

        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRP = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS_GEFS = "default_subtype"

        try:
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRP         = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRP", default_or_error_return_value="chirp")
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS        = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS", default_or_error_return_value="chirps")
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS_GEFS   = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS_GEFS", default_or_error_return_value="chirps_gefs")
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only: Error getting Dataset Subtypes.  Database was not populated with these preset types.  Exiting now.  System Error Message: " + str(sysErrorData))
            return

        # ########################
        # # DATASETS - CHIRPS
        # ########################
        dataset_name__chirp_global_0_05deg_1dy      = "chirp_global_0_05deg_1dy"
        dataset_name__chirps_global_0_05deg_1dy     = "chirps_global_0_05deg_1dy"
        dataset_name__chirpsgef_global_0_05deg_1dy  = "chirpsgef_global_0_05deg_1dy"

        # Chirp - 1 day Chirp
        # dataset_name__chrip_global_0_05deg_1dy      = "chirp_global_0_05deg_1dy"
        etl_dataset_name = str(dataset_name__chirp_global_0_05deg_1dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name = etl_dataset_name
            etl_dataset.dataset_subtype = str(dataset_subtype__ETL_DATASET_SUBTYPE__CHIRP).strip()
            etl_dataset.created_by = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled = True
            etl_dataset.is_pipeline_active = True
            etl_dataset.tds_product_name = "UCSB-CHIRP"
            etl_dataset.tds_region = "Global"
            etl_dataset.tds_spatial_resolution = "0.05deg"
            etl_dataset.tds_temporal_resolution = "1dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # Chirps - 1 day Chirps (Chirps 2.0)
        # dataset_name__chirps_global_0_05deg_1dy     = "chirps_global_0_05deg_1dy"
        etl_dataset_name = str(dataset_name__chirps_global_0_05deg_1dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name = etl_dataset_name
            etl_dataset.dataset_subtype = str(dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS).strip()
            etl_dataset.created_by = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled = True
            etl_dataset.is_pipeline_active = True
            etl_dataset.tds_product_name = "UCSB-CHIRPS"
            etl_dataset.tds_region = "Global"
            etl_dataset.tds_spatial_resolution = "0.05deg"
            etl_dataset.tds_temporal_resolution = "1dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # Chirps GEF - 1 day Chirps (Chirps GEF)
        # dataset_name__chirpsgef_global_0_05deg_1dy  = "chirpsgef_global_0_05deg_1dy"
        etl_dataset_name = str(dataset_name__chirpsgef_global_0_05deg_1dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name = etl_dataset_name
            etl_dataset.dataset_subtype = str(dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS_GEFS).strip()
            etl_dataset.created_by = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled = True
            etl_dataset.is_pipeline_active = True
            etl_dataset.tds_product_name = "UCSB-CHIRPS-GEFS"
            etl_dataset.tds_region = "Global"
            etl_dataset.tds_spatial_resolution = "0.05deg"
            etl_dataset.tds_temporal_resolution = "1dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets__Chirps_Only: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        return created_uuid_list


    # This function sets the database to have all the current Dataset Types.  This is a shortcut to getting started.
    # # Note, running this AFTER the server is has already been configured (and maybe some settings changed) will cause all settings to revert back to defaults.
    #
    # Usage:
    # # Python Console
    # # # from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
    # # # result_uuids = ETL_Dataset.run_initial_DB_Setup_For_ETL_Datasets()
    @staticmethod
    def run_initial_DB_Setup_For_ETL_Datasets():
        created_uuid_list = []

        # ETL_DATASET_SUBTYPE__CHIRP          = "chirp"
        # ETL_DATASET_SUBTYPE__CHIRPS         = "chirps"
        # ETL_DATASET_SUBTYPE__CHIRPS_GEFS    = "chirps_gefs"
        # ETL_DATASET_SUBTYPE__EMODIS         = "emodis"
        # ETL_DATASET_SUBTYPE__ESI_4WEEK      = "esi_4week"
        # ETL_DATASET_SUBTYPE__ESI_12WEEK     = "esi_12week"
        # ETL_DATASET_SUBTYPE__IMERG_EARLY    = "imerg_early"
        # ETL_DATASET_SUBTYPE__IMERG_LATE     = "imerg_late"



        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRP = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS_GEFS = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__ESI_4WEEK = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__ESI_12WEEK = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_EARLY = "default_subtype"
        dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_LATE = "default_subtype"

        try:
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRP         = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRP", default_or_error_return_value="chirp")
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS        = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS", default_or_error_return_value="chirps")
            dataset_subtype__ETL_DATASET_SUBTYPE__CHIRPS_GEFS   = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS_GEFS", default_or_error_return_value="chirps_gefs")
            dataset_subtype__ETL_DATASET_SUBTYPE__ESI_4WEEK     = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_4WEEK", default_or_error_return_value="esi_4week")
            dataset_subtype__ETL_DATASET_SUBTYPE__ESI_12WEEK    = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_12WEEK", default_or_error_return_value="esi_12week")
            dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS        = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__EMODIS", default_or_error_return_value="emodis")
            dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_EARLY   = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_EARLY", default_or_error_return_value="imerg_early")
            dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_LATE    = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_LATE", default_or_error_return_value="imerg_late")
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error getting Dataset Subtypes.  Database was not populated with these preset types.  Exiting now.  System Error Message: " + str(sysErrorData))
            return





        # ########################
        # # DATASETS - IMERG
        # ########################

        dataset_name__imerg_early_global_0_1deg_30min   = "imerg_early_global_0_1deg_30min"
        dataset_name__imerg_late_global_0_1deg_30min    = "imerg_late_global_0_1deg_30min"

        # IMERG Early
        # dataset_name__imerg_early_global_0_1deg_30min = "imerg_early_global_0_1deg_30min"
        etl_dataset_name = str(dataset_name__imerg_early_global_0_1deg_30min).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_EARLY).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "NASA-IMERG_EARLY"
            etl_dataset.tds_region              = "Global"
            etl_dataset.tds_spatial_resolution  = "0.1deg"
            etl_dataset.tds_temporal_resolution = "30min"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset: () " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))


        # IMERG Late
        # dataset_name__imerg_late_global_0_1deg_30min = "imerg_late_global_0_1deg_30min"
        etl_dataset_name = str(dataset_name__imerg_late_global_0_1deg_30min).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__IMERG_LATE).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "NASA-IMERG_LATE"
            etl_dataset.tds_region              = "Global"
            etl_dataset.tds_spatial_resolution  = "0.1deg"
            etl_dataset.tds_temporal_resolution = "30min"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))






        # ########################
        # # DATASETS - EMODIS
        # ########################

        dataset_name__emodis_ndvi_eastafrica_250m_10dy      = "emodis_ndvi_eastafrica_250m_10dy"
        dataset_name__emodis_ndvi_westafrica_250m_10dy      = "emodis_ndvi_westafrica_250m_10dy"
        dataset_name__emodis_ndvi_southernafrica_250m_10dy  = "emodis_ndvi_southernafrica_250m_10dy"
        dataset_name__emodis_ndvi_centralasia_250m_10dy     = "emodis_ndvi_centralasia_250m_10dy"

        # EMODIS - East Africa
        # dataset_name__emodis_ndvi_eastafrica_250m_10dy      = "emodis_ndvi_eastafrica_250m_10dy"
        etl_dataset_name = str(dataset_name__emodis_ndvi_eastafrica_250m_10dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "EMODIS-NDVI"
            etl_dataset.tds_region              = "EastAfrica"
            etl_dataset.tds_spatial_resolution  = "250m"
            etl_dataset.tds_temporal_resolution = "10dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # EMODIS - West Africa
        # dataset_name__emodis_ndvi_westafrica_250m_10dy      = "emodis_ndvi_westafrica_250m_10dy"
        etl_dataset_name = str(dataset_name__emodis_ndvi_westafrica_250m_10dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "EMODIS-NDVI"
            etl_dataset.tds_region              = "WestAfrica"
            etl_dataset.tds_spatial_resolution  = "250m"
            etl_dataset.tds_temporal_resolution = "10dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # EMODIS - Southern Africa
        # dataset_name__emodis_ndvi_southernafrica_250m_10dy  = "emodis_ndvi_southernafrica_250m_10dy"
        etl_dataset_name = str(dataset_name__emodis_ndvi_southernafrica_250m_10dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "EMODIS-NDVI"
            etl_dataset.tds_region              = "SouthernAfrica"
            etl_dataset.tds_spatial_resolution  = "250m"
            etl_dataset.tds_temporal_resolution = "10dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # EMODIS - central Asia
        # dataset_name__emodis_ndvi_centralasia_250m_10dy = "emodis_ndvi_centralasia_250m_10dy"
        etl_dataset_name = str(dataset_name__emodis_ndvi_centralasia_250m_10dy).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__EMODIS).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "EMODIS-NDVI"
            etl_dataset.tds_region              = "CentralAsia"
            etl_dataset.tds_spatial_resolution  = "250m"
            etl_dataset.tds_temporal_resolution = "10dy"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))





        # ########################
        # # DATASETS - ESI
        # ########################
        dataset_name__esi_global_0_05deg_4wk = "esi_global_0_05deg_4wk"
        dataset_name__esi_global_0_05deg_12wk = "esi_global_0_05deg_12wk"


        # ESI - 4 Week
        # dataset_name__esi_global_0_05deg_4wk = "esi_global_0_05deg_4wk"
        etl_dataset_name = str(dataset_name__esi_global_0_05deg_4wk).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name            = etl_dataset_name
            etl_dataset.dataset_subtype         = str(dataset_subtype__ETL_DATASET_SUBTYPE__ESI_4WEEK).strip()
            etl_dataset.created_by              = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "SPORT-ESI"
            etl_dataset.tds_region              = "Global"
            etl_dataset.tds_spatial_resolution  = "0.05deg"
            etl_dataset.tds_temporal_resolution = "4wk"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))

        # ESI - 12 Week
        # dataset_name__esi_global_0_05deg_12wk = "esi_global_0_05deg_12wk"
        etl_dataset_name = str(dataset_name__esi_global_0_05deg_12wk).strip()
        try:
            # Get or Create dataset with this exact name
            etl_dataset = ""
            try:
                etl_dataset = ETL_Dataset.objects.filter(dataset_name=etl_dataset_name)[0]
            except:
                etl_dataset = ETL_Dataset()
            etl_dataset.dataset_name = etl_dataset_name
            etl_dataset.dataset_subtype = str(dataset_subtype__ETL_DATASET_SUBTYPE__ESI_12WEEK).strip()
            etl_dataset.created_by = str("initial_database_seed_process").strip()
            etl_dataset.is_pipeline_enabled     = True
            etl_dataset.is_pipeline_active      = True
            etl_dataset.tds_product_name        = "SPORT-ESI"
            etl_dataset.tds_region              = "Global"
            etl_dataset.tds_spatial_resolution  = "0.05deg"
            etl_dataset.tds_temporal_resolution = "12wk"
            etl_dataset.save()
            created_uuid_list.append(str(etl_dataset.uuid))
        except:
            sysErrorData = str(sys.exc_info())
            print("run_initial_DB_Setup_For_ETL_Datasets: Error creating or modifying dataset name: " + str(etl_dataset_name) + ".  System Error Message: " + str(sysErrorData))






        # ETL_DATASET_SUBTYPE__ESI_4WEEK, ETL_DATASET_SUBTYPE__ESI_12WEEK
        # dataset_subtype__ETL_DATASET_SUBTYPE__ESI_4WEEK, dataset_subtype__ETL_DATASET_SUBTYPE__ESI_12WEEK
        #
        # dataset_name__esi_global_0_05deg_12wk = "esi_global_0_05deg_12wk"
        # dataset_name__esi_global_0_05deg_4wk = "esi_global_0_05deg_4wk"



        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRP = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRP", default_or_error_return_value="chirp")
        #
        # except:
        #     sysErrorData = str(sys.exc_info())
        #     print("run_initial_DB_Setup_For_ETL_Datasets: Warning.  Could not pre populate dataset:   System Error Message: " + str(sysErrorData))
        #
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS", default_or_error_return_value="chirps")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__CHIRPS_GEFS", default_or_error_return_value="chirps_gefs")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__EMODIS", default_or_error_return_value="emodis")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_4WEEK", default_or_error_return_value="esi_4week")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__ESI_12WEEK", default_or_error_return_value="esi_12week")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_EARLY", default_or_error_return_value="imerg_early")
        #
        # except:
        #     pass
        #
        # try:
        #     dataset_name__ETL_DATASET_SUBTYPE__CHIRPS = Config_Setting.get_value(setting_name="ETL_DATASET_SUBTYPE__IMERG_LATE", default_or_error_return_value="imerg_late")
        #
        # except:
        #     pass


        #
        # #dataset_name__emodis =
        # try:
        #     new_ETL_Dataset = ETL_Dataset()
        #     new_ETL_Dataset.dataset_name    = str("emodis").strip()
        #     #new_ETL_Dataset.dataset_subtype = ""#
        #     new_ETL_Dataset.created_by      = str("initial_database_seed_process").strip()
        #     new_ETL_Dataset.save()
        #     created_uuid_list.append(str(new_ETL_Dataset.uuid))
        # except:
        #     print("run_initial_DB_Setup_For_ETL_Datasets: Error creating ")

        return created_uuid_list



# MAKE MIGRATIONS
# --Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate


# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate






# END OF FILE!