# ETL Logs
# // For keeping track of Activities (ETL Events Log) and Alerts (Errors which need to be shown to Admin Users and handled)

from django.db import models
from django.db.models import Count
from common_utils import utils as common_utils
import json
import sys

from django.conf import settings

#import datetime     # Remove me - AFter testing the Datetime stuff

# Import This Model - Usage Example
# # from api_v2.app_models.model_ETL_Log import ETL_Log



class ETL_Log(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)

    # Additional Columns Here
    activity_event_type     = models.CharField('Standardized Activity Event Type', max_length=90, blank=False, default="Unknown ETL Activity Event Type", help_text="What is the standardized type for this ETL Activity Event?")
    activity_description    = models.TextField('Activity Description', default="No Description", help_text="A field for more detailed information on an ETL Event Activity")
    etl_pipeline_run_uuid   = models.CharField('ETL Pipeline Run UUID', max_length=40, blank=False, default="UNSET_DATASET_UUID", help_text="Each time the ETL Pipeline runs, there is a unique ID generated, this field operates like a way to tag which pipeline this row is attached to.")
    etl_dataset_uuid        = models.CharField('ETL Dataset UUID', max_length=40, blank=False, default="UNSET_DATASET_UUID", help_text="If there is an associated ETL Dataset UUID, it should appear here.  Note: This field may be blank or unset, not all events will have one of these associated items.")
    etl_granule_uuid        = models.CharField('ETL Granule UUID', max_length=40, blank=False, default="UNSET_GRANULE_UUID", help_text="If there is an associated ETL Granule UUID, it should appear here.  Note: This field may be blank or unset, not all events will have one of these associated items.")
    is_alert                = models.BooleanField(default=False, help_text="Is this an Item that should be considered an alert?  (by default, all errors and warnings are considered alerts)")
    is_alert_dismissed      = models.BooleanField(default=False, help_text="Setting this to True will change the display style for the admin.")
    # More fields will likely be needed.

    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")




    class_name_string = "ETL_Log"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | activity_event_type: " + str(self.activity_event_type) + " | activity_description: " + str(self.activity_description) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | activity_event_type: " + str(self.activity_event_type) + " | activity_description: " + str(self.activity_description) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        return outString


    # Non Static, Serialize current element to JSON
    def to_JSONable_Object(self):
        retObj = {}
        retObj["id"]                            = str(self.id).strip()
        retObj["uuid"]                          = str(self.uuid).strip()

        retObj["activity_event_type"]   = str(self.activity_event_type).strip()
        retObj["activity_description"]  = str(self.activity_description).strip()
        retObj["etl_pipeline_run_uuid"] = str(self.etl_pipeline_run_uuid).strip()
        retObj["etl_dataset_uuid"]      = str(self.etl_dataset_uuid).strip()
        retObj["etl_granule_uuid"]      = str(self.etl_granule_uuid).strip()
        retObj["is_alert"]              = str(self.is_alert).strip()
        retObj["is_alert_dismissed"]    = str(self.is_alert_dismissed).strip()

        retObj["created_at"]                    = str(self.created_at).strip()
        retObj["created_by"]                    = str(self.created_by).strip()
        retObj["is_test_object"]                = str(self.is_test_object).strip()
        retObj["additional_json"]               = json.loads(self.additional_json)

        # Add Custom Export to JSON Content Here - Fields/Columns Serialization (stringifying)

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


    @staticmethod
    def create_new_etl_log_row(activity_event_type, activity_description, etl_pipeline_run_uuid, etl_dataset_uuid, etl_granule_uuid, is_alert, created_by, additional_json):
        ret__new_ETL_Log_UUID = ""
        try:

            is_alert__BOOL = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=is_alert, defaultBoolValue=False)

            additional_json_STR = json.dumps( {} )
            try:
                additional_json_STR = json.dumps( additional_json )
            except:
                # Error parsing input as a JSONable python object
                additional_json_STR = json.dumps({})

            try:
                new_ETL_Log = ETL_Log()
                new_ETL_Log.activity_event_type     = str(activity_event_type).strip()
                new_ETL_Log.activity_description    = str(activity_description).strip()
                new_ETL_Log.etl_pipeline_run_uuid   = str(etl_pipeline_run_uuid).strip()
                new_ETL_Log.etl_dataset_uuid        = str(etl_dataset_uuid).strip()
                new_ETL_Log.etl_granule_uuid        = str(etl_granule_uuid).strip()
                new_ETL_Log.is_alert                = is_alert__BOOL
                new_ETL_Log.created_by              = str(created_by).strip()
                new_ETL_Log.additional_json         = additional_json_STR       # try/except of json.dumps( additional_json )   # Use json.loads(self.additional_json) to get data out
                new_ETL_Log.save()
                ret__new_ETL_Log_UUID = str(new_ETL_Log.uuid).strip()
            except:
                # Error Setting Log Entry props and saving
                pass
        except:
            # Error Creating a new Log Entry
            pass
        return ret__new_ETL_Log_UUID

    # The returned keys are: 'field_name' and 'count'
    @staticmethod
    def get_distinct_count_list_for_field(field_name, earliest_datetime):
        ret__List = []
        try:
            distinct_objects_with_count = ETL_Log.objects.all().filter(created_at__gte=earliest_datetime).values(field_name).annotate(count=Count(field_name)).order_by('-count')
            #distinct_objects_with_count = ETL_Log.objects.all().values(field_name).annotate(count=Count(field_name)).order_by('-count')  # No filters
            # distinct_objects = API_Log.objects.values(field_name).distinct()
            for distinct_object in distinct_objects_with_count:
                current_obj = {}
                current_obj[field_name] = str(distinct_object[field_name]).strip()
                current_obj['count'] = str(distinct_object['count']).strip()
                ret__List.append(current_obj)
        except:
            # Error Getting distinct objects.
            pass
        return ret__List

    # distinct_objects_with_count = API_Log.objects.all().values(field_name).annotate(count=Count('endpoint')).order_by('-count')

    @staticmethod
    def get_stats(earliest_datetime):
        ret_obj = {}

        field_list = ['activity_event_type', 'etl_pipeline_run_uuid', 'etl_dataset_uuid', 'is_alert', 'is_alert_dismissed']
        ret_obj['stats_by_field'] = {}  # A container for all the stats
        for field in field_list:
            ret_obj['stats_by_field'][field] = {}
            ret_obj['stats_by_field'][field]['distinct_counts'] = ETL_Log.get_distinct_count_list_for_field(field_name=field, earliest_datetime=earliest_datetime)
            # counts_for_field = API_Log.get_distinct_count_list_for_field(field)

        ret_obj['total_db_objects'] = ETL_Log.objects.count()

        ret_obj['field_list'] = field_list
        return ret_obj






# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate

# --Migrations for api_v2:
# ---api_v2/migrations/0002_auto_20200628_2315.py
# ----Create model ETL_Dataset
# ----Create model ETL_Granule
# ----Create model ETL_Log
# ----Alter field auth_id on user

# python manage.py migrate
# --Migrate
# ---Applying api_v2.0002_auto_20200628_2315... OK








# END OF FILE!