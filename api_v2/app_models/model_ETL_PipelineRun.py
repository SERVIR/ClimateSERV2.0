from django.db import models
from common_utils import utils as common_utils
import json
import sys


# Import This Model - Usage Example
# # from api_v2.app_models.model_ETL_PipelineRun import ETL_PipelineRun



class ETL_PipelineRun(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    created_at          = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by          = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")
    additional_json     = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object      = models.BooleanField(  default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")


    # Additional Columns Here

    class_name_string = "ETL_PipelineRun"

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






# # python manage.py makemigrations api_v2
# # python manage.py migrate

# # MAKE MIGRATIONS
# #--Migrations
# # # python manage.py makemigrations api_v2
# # # python manage.py migrate
#
# # # Migrations for 'api_v2':
# #   api_v2/migrations/0004_auto_20200726_1749.py
# #     - Add field etl_pipeline_run_uuid to etl_granule
# #     - Add field granule_pipeline_state to etl_granule
# #     - Add field etl_pipeline_run_uuid to etl_log
# #
# # Running migrations:
# #    # Applying api_v2.0004_auto_20200726_1749... OK

# # Migrations for 'api_v2':
#   api_v2/migrations/0005_etl_pipelinerun.py
#     - Create model ETL_PipelineRun
# (venv.3_7_3_climateserv-2-0-server) ➜  ClimateSERV-2.0-Server git:(dev) ✗ python manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, api_v2, auth, contenttypes, sessions
# Running migrations:
#   Applying api_v2.0005_etl_pipelinerun... OK





# END OF FILE!