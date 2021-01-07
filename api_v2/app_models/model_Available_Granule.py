from django.db import models
from common_utils import utils as common_utils
import json
import sys


# Import This Model - Usage Example
# # from api_v2.app_models.model_Available_Granule import Available_Granule



# Available Granule database rows get added at the time they are successfully ingested to the system (as soon as they are in the THREDDS monitoring area without errors)



class Available_Granule(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")


    # Additional Columns Here
    granule_name = models.CharField('Granule Name', max_length=250, blank=False, default="Unknown_Granule_Name", help_text="Most of the time, this may be a filename.  Sometimes it is not.  It should be a name that is unique to the combination of dataset and temporal data value.  This row should be useful in tracking down the specific granule's file/source info.")
    # TODO - Add the fields that are needed by the clientside right here.

    class_name_string = "Available_Granule"

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


        retObj["granule_name"] = str(self.granule_name).strip()


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

    # Creates a brand new or Updates an existing ETL Granule Row
    @staticmethod
    def create_or_update_existing_Available_Granule_row(granule_name, granule_contextual_information, etl_pipeline_run_uuid, etl_dataset_uuid, created_by, additional_json):
        ret__Available_Granule_UUID = ""

        granule_name = str(granule_name).strip()
        if(granule_name == ""):
            return ""

        the_Available_Granule = None
        try:
            the_Available_Granule = Available_Granule.objects.filter(granule_name=granule_name)[0]
            # At this point in the code, the Available Granule does exist and was found
        except:
            # At this point in the code, the Available Granule does not exist and is being created here
            the_Available_Granule = Available_Granule()
            the_Available_Granule.save()

        try:
            # Now update the Granule's info
            # Put some of the stuff in the additional JSON area.


            additional_json_STR = json.dumps({})
            try:
                additional_json['most_recent__etl_pipeline_run_uuid'] = str(etl_pipeline_run_uuid).strip()
                additional_json['etl_dataset_uuid'] = str(etl_dataset_uuid).strip()
                additional_json['granule_contextual_information'] = str(granule_contextual_information).strip()
                additional_json_STR = json.dumps(additional_json)
            except:
                # Error parsing input as a JSONable python object
                additional_json = {}
                additional_json['most_recent__etl_pipeline_run_uuid'] = str(etl_pipeline_run_uuid).strip()
                additional_json['etl_dataset_uuid'] = str(etl_dataset_uuid).strip()
                additional_json['granule_contextual_information'] = str(granule_contextual_information).strip()
                additional_json_STR = json.dumps(additional_json ) # additional_json_STR = json.dumps({})

            try:

                the_Available_Granule.granule_name      = str(granule_name).strip()
                the_Available_Granule.created_by        = str(created_by).strip()
                the_Available_Granule.additional_json   = additional_json_STR
                the_Available_Granule.save()
                ret__Available_Granule_UUID = str(the_Available_Granule.uuid).strip()
            except:
                # Error Setting Log Entry props and saving
                pass

        except:
            # Error Creating a new ETL Granule Row Entry
            pass

        return ret__Available_Granule_UUID




# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate

# # Migrations for 'api_v2':
#   api_v2/migrations/0006_available_granule.py
#     - Create model Available_Granule
#
# Running migrations:
#  Applying api_v2.0006_available_granule... OK



# Migrations for 'api_v2':
#  api_v2/migrations/0007_available_granule_granule_name.py
#    - Add field granule_name to available_granule
#
# Running migrations:
#  Applying api_v2.0007_available_granule_granule_name... OK


# END OF FILE!