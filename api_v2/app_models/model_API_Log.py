from django.db import models
from django.db.models import Count
from common_utils import utils as common_utils
import json
import sys


# Import This Model - Usage Example
# # from api_v2.app_models.model_API_Log import API_Log

import datetime     # Remove me - AFter testing the Datetime stuff


class API_Log(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")


    # Additional Columns Here
    endpoint            = models.CharField('Which Endpoint Address was hit', max_length=90, blank=False, default="/unknown_endpoint/", help_text="What was the relative endpoint path that associated with this entry.")
    ip_address          = models.CharField('What was the IP Address', max_length=90, blank=False, default="UNKNOWN_IP", help_text="What was the IP address of the computer that requested this endpoint?")
    server_result_state = models.CharField('Result of the API Request', max_length=30, blank=False, default="UNSET", help_text="What was the server's result of this endpoint call.  This value will usually be 'success' or 'error'.  In rare cases this may be set to 'UNSET' or 'UNKNOWN' ")
    # all the rest into the additional JSON, including parameters that were passed in

    class_name_string = "API_Log"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | endpoint: " + str(self.endpoint) + " | server_result_state: " + str(self.server_result_state) + " | ip_address: " + str(self.ip_address) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | endpoint: " + str(self.endpoint) + " | server_result_state: " + str(self.server_result_state) + " | ip_address: " + str(self.ip_address) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
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

        retObj["endpoint"] = str(self.endpoint).strip()
        retObj["ip_address"] = str(self.ip_address).strip()
        retObj["server_result_state"] = str(self.server_result_state).strip()




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
    def create_new_api_log_row(endpoint, server_result_state, ip_address, created_by, additional_json):
        ret__new_API_Log_UUID = ""
        try:

            additional_json_STR = json.dumps({})
            try:
                additional_json_STR = json.dumps(additional_json)
            except:
                # Error parsing input as a JSONable python object
                additional_json_STR = json.dumps({})

            try:
                new_API_Log = API_Log()
                new_API_Log.endpoint                = str(endpoint).strip()
                new_API_Log.ip_address              = str(ip_address).strip()
                new_API_Log.server_result_state     = str(server_result_state).strip()
                new_API_Log.created_by              = str(created_by).strip()
                new_API_Log.additional_json = additional_json_STR  # try/except of json.dumps( additional_json )   # Use json.loads(self.additional_json) to get data out
                new_API_Log.save()
                ret__new_API_Log_UUID = str(new_API_Log.uuid).strip()
            except:
                # Error Setting Log Entry props and saving
                pass
        except:
            # Error Creating a new Log Entry
            pass
        return ret__new_API_Log_UUID



    # # Just returns a plain list
    # @staticmethod
    # def get_distinct_list_for_field(field_name):
    #     ret__List = []
    #     try:
    #         distinct_objects = API_Log.objects.values(field_name).distinct()
    #         for distinct_object in distinct_objects:
    #             current_obj = str(distinct_object[field_name]).strip()
    #             ret__List.append(current_obj)
    #     except:
    #         # Error Getting distinct objects.
    #         pass
    #     return ret__List

    # The returned keys are: 'field_name' and 'count'
    @staticmethod
    def get_distinct_count_list_for_field(field_name, earliest_datetime):

        # HC_DateTime = datetime.datetime.utcnow()
        # start_Date = datetime.datetime(year=self.YYYY__Year__Start, month=self.MM__Month__Start, day=self.DD__Day__Start)
        #HC_DateTime = datetime.datetime(year=2020, month=10, day=1)


        ret__List = []
        try:
            distinct_objects_with_count = API_Log.objects.all().filter(created_at__gte=earliest_datetime).values(field_name).annotate(count=Count(field_name)).order_by('-count')
            #distinct_objects_with_count = API_Log.objects.all().values(field_name).annotate(count=Count(field_name)).order_by('-count')
            # distinct_objects = API_Log.objects.values(field_name).distinct()
            for distinct_object in distinct_objects_with_count:
                current_obj = {}
                current_obj[field_name] = str(distinct_object[field_name]).strip()
                current_obj['count']    = str(distinct_object['count']).strip()
                ret__List.append(current_obj)
        except:
            # Error Getting distinct objects.
            pass
        return ret__List
    #distinct_objects_with_count = API_Log.objects.all().values(field_name).annotate(count=Count('endpoint')).order_by('-count')

    @staticmethod
    def get_stats(earliest_datetime):
        ret_obj = {}

        field_list = ['endpoint', 'ip_address', 'server_result_state']
        ret_obj['stats_by_field'] = {}  # A container for all the stats
        for field in field_list:
            ret_obj['stats_by_field'][field] = {}
            ret_obj['stats_by_field'][field]['distinct_counts'] = API_Log.get_distinct_count_list_for_field(field_name=field, earliest_datetime=earliest_datetime)
            #counts_for_field = API_Log.get_distinct_count_list_for_field(field)

        ret_obj['total_db_objects'] = API_Log.objects.count()

        ret_obj['field_list'] = field_list
        return ret_obj




# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate

#  api_v2/migrations/0008_api_log.py
#    - Create model API_Log
#
#   Applying api_v2.0008_api_log... OK


#   api_v2/migrations/0009_api_log_server_result_state.py
#    - Add field server_result_state to api_log
#
#   Applying api_v2.0009_api_log_server_result_state... OK




# END OF FILE!