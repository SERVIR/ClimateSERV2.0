# ETL Granules
# // For keeping track of each specific etl granule that was ingested (or expected granule that is missing) for each dataset
# // ETL Jobs can be run more than once.  This will result in multiple granules created for a single dataset and time combination.  This is ok and actually planned behavior.
# # This lets us do things like, keep track of multiple attempts at getting a specific granule.
#
# When the pipeline runs, it makes a list of expected granules, whether or not it actually is able to process those granules, an entry is made in this table.
# # One entry per expected granule per dataset per ingest run.


from django.db import models
from common_utils import utils as common_utils
import json
import sys

from django.conf import settings

# Import This Model - Usage Example
# # from api_v2.app_models.model_ETL_Granule import ETL_Granule



class ETL_Granule(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)

    # Additional Columns Here
    granule_name                    = models.CharField('Granule Name', max_length=250, blank=False, default="Unknown Granule Name", help_text="Most of the time, this may be a filename.  Sometimes it is not.  It should be a name that is unique to the combination of dataset and temporal data value.  This row should be useful in tracking down the specific granule's file/source info.")
    granule_contextual_information  = models.TextField('Granule Contextual Information', default="No Additional Information", help_text="A way to capture additional contextual information around a granule, if needed.")
    etl_pipeline_run_uuid           = models.CharField('ETL Pipeline Run UUID', max_length=40, blank=False, default="UNSET_DATASET_UUID", help_text="Each time the ETL Pipeline runs, there is a unique ID generated, this field operates like a way to tag which pipeline this row is attached to")
    etl_dataset_uuid                = models.CharField('ETL Dataset UUID', max_length=40, blank=False, default="UNSET_DATASET_UUID", help_text="Each Individual Granule has a parent ETL Dataset, storing the association here")
    is_missing                      = models.BooleanField(  default=False, help_text="Was this expected granule missing at the time of processing?  If this is set to True, that means during an ingest run, there was an expected granule that was either not found at the data source, or had an error that made it unable to be processed and ingested.  The time that this record gets created as compared to ETL Log rows would be a good way to nail down the exact issue as more data is stored about issues in the ETL Log table.")
    granule_pipeline_state          = models.CharField('Granule Pipeline State', max_length=20, blank=False, default="UNSET_ATTEMPTED", help_text="Each Individual Granule has a pipeline state.  This lets us easily understand if the Granule succeeded or failed")
    # TODO: More Columns on this table as needed.

    # For now, Only FAILED granule_pipeline_states have additional info stored in this field.
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")




    class_name_string = "ETL_Granule"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed


    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | granule_pipeline_state: " + str(self.granule_pipeline_state) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | granule_pipeline_state: " + str(self.granule_pipeline_state) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        return outString


    # Non Static, Serialize current element to JSON
    def to_JSONable_Object(self):
        retObj = {}
        retObj["id"]                            = str(self.id).strip()
        retObj["uuid"]                          = str(self.uuid).strip()

        # Add Custom Export to JSON Content Here - Fields/Columns Serialization (stringifying)
        retObj["granule_name"]                      = str(self.granule_name).strip()
        retObj["granule_contextual_information"]    = str(self.granule_contextual_information).strip()
        retObj["etl_pipeline_run_uuid"]             = str(self.etl_pipeline_run_uuid).strip()
        retObj["etl_dataset_uuid"]                  = str(self.etl_dataset_uuid).strip()
        retObj["is_missing"]                        = str(self.is_missing).strip()
        retObj["granule_pipeline_state"]            = str(self.granule_pipeline_state).strip()


        retObj["created_at"]                    = str(self.created_at).strip()
        retObj["created_by"]                    = str(self.created_by).strip()
        retObj["is_test_object"]                = str(self.is_test_object).strip()
        retObj["additional_json"]               = json.loads(self.additional_json)



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


    # Creates a brand new ETL Granule Row
    @staticmethod
    def create_new_ETL_Granule_row(granule_name, granule_contextual_information, etl_pipeline_run_uuid, etl_dataset_uuid, granule_pipeline_state, created_by, additional_json):
        ret__new_ETL_Granule_UUID = ""
        try:

            additional_json_STR = json.dumps({})
            try:
                additional_json_STR = json.dumps(additional_json)
            except:
                # Error parsing input as a JSONable python object
                additional_json_STR = json.dumps({})

            try:
                new_ETL_Granule = ETL_Granule()
                new_ETL_Granule.granule_name                    = str(granule_name).strip()
                new_ETL_Granule.granule_contextual_information  = str(granule_contextual_information).strip()
                new_ETL_Granule.etl_pipeline_run_uuid           = str(etl_pipeline_run_uuid).strip()
                new_ETL_Granule.etl_dataset_uuid                = str(etl_dataset_uuid).strip()
                new_ETL_Granule.is_missing                      = False
                new_ETL_Granule.granule_pipeline_state          = str(granule_pipeline_state).strip()
                new_ETL_Granule.created_by                      = str(created_by).strip()
                new_ETL_Granule.additional_json                 = additional_json_STR  # try/except of json.dumps( additional_json )   # Use json.loads(self.additional_json) to get data out
                new_ETL_Granule.save()
                ret__new_ETL_Granule_UUID   = str(new_ETL_Granule.uuid).strip()
            except:
                # Error Setting Log Entry props and saving
                pass

        except:
            # Error Creating a new ETL Granule Row Entry
            pass

        return ret__new_ETL_Granule_UUID


    # Updates the Granule Pipeline State
    # # Example: See settings for: settings.GRANULE_PIPELINE_STATE__ATTEMPTED  (and the other possible states)
    @staticmethod
    def update_existing_ETL_Granule__granule_pipeline_state(granule_uuid, new__granule_pipeline_state):
        ret__update_is_success = False
        try:
            existing_ETL_Granule_Row = ETL_Granule.objects.filter(uuid=str(granule_uuid).strip())[0]
            existing_ETL_Granule_Row.granule_pipeline_state = str(new__granule_pipeline_state).strip()
            existing_ETL_Granule_Row.save()
            ret__update_is_success = True
        except:
            # Error updating the record
            ret__update_is_success = False
        return ret__update_is_success

    # If a granule is found to be missing from the completed dataset - Note, this is regarding an ETL job.
    # # This field is to be used for being able to quickly tell if a granule failed an ingest (ETL) procedure
    # # This field is NOT to be used for End User Client App consumption (different table for storing all those granules) (Possible_Dataset_Granule - which is a listing of all Possible Dataset Granules)
    @staticmethod
    def update_existing_ETL_Granule__is_missing_bool_val(granule_uuid, new__is_missing__Bool_Val):
        ret__update_is_success = False
        try:
            is_missing__BOOL = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=new__is_missing__Bool_Val, defaultBoolValue=True)  # Usually when this function is called, it is because there was an error and the granule is missing..
            existing_ETL_Granule_Row = ETL_Granule.objects.filter(uuid=str(granule_uuid).strip())[0]
            existing_ETL_Granule_Row.is_missing = is_missing__BOOL
            existing_ETL_Granule_Row.save()
            ret__update_is_success = True
        except:
            # Error updating the record
            ret__update_is_success = False
        return ret__update_is_success


    # Append info to the JSON - The use case here is to attach an error (and additional) data object to the existing Additional JSON.
    @staticmethod
    def update_existing_ETL_Granule__Append_To_Additional_JSON(granule_uuid, new_json_key_to_append, sub_jsonable_object):
        ret__update_is_success = False
        try:
            new_json_key_to_append = str(new_json_key_to_append).strip()

            existing_ETL_Granule_Row = ETL_Granule.objects.filter(uuid=str(granule_uuid).strip())[0]

            current_Additional_JSON                         = json.loads(existing_ETL_Granule_Row.additional_json)
            current_Additional_JSON[new_json_key_to_append] = sub_jsonable_object

            existing_ETL_Granule_Row.additional_json = json.dumps(current_Additional_JSON)
            existing_ETL_Granule_Row.save()

            ret__update_is_success = True
        except:
            # Error updating the record
            ret__update_is_success = False
        return ret__update_is_success



# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate








# END OF FILE!