from django.db import models
from common_utils import utils as common_utils
import json
import sys

# Auth User Stuff
from django.contrib.auth.models import User as AuthUser

# Import This Model - Usage Example
# # from api_v2.app_models.model_User import User



class User(models.Model):
    id                  = models.BigAutoField(  primary_key=True)       # The Table's Counting Integer (Internal, don't usually expose or use this)
    uuid                = models.CharField(     default=common_utils.get_Random_String_UniqueID_20Chars, editable=False, max_length=40, blank=False)    # The Table's Unique ID (Globally Unique String)
    auth_id             = models.CharField(default="UNKNOWN_AUTH_ID", max_length=40, blank=False, help_text="")  # The ID on the Auth.User's table that matches this record (1 to 1 relationship)

    is_admin            = models.BooleanField(default=False, help_text="Is this user an Admin?")
    can_manage_users = models.BooleanField(default=False, help_text="Does this user have permissions to manage Users?")
    can_manage_etl_logs = models.BooleanField(default=False, help_text="Does this user have permissions to manage ETL Logs?")
    can_manage_api_logs = models.BooleanField(default=False, help_text="Does this user have permissions to manage API Logs?")
    can_manage_server_logs = models.BooleanField(default=False, help_text="Does this user have permissions to manage Server Logs?")

    additional_json = models.TextField('JSON Data', default="{}", help_text="Extra data field.  Please don't touch this!  Messing with this will likely result in broken content elsewhere in the system.")
    is_test_object = models.BooleanField(default=False, help_text="Is this Instance meant to be used ONLY for internal platform testing? (Used only for easy cleanup - DO NOT DEPEND ON FOR VALIDATION)")
    created_at = models.DateTimeField('created_at', auto_now_add=True, blank=True)
    created_by = models.CharField('Created By User or Process Name or ID', max_length=90, blank=False, default="Table_Default_Process", help_text="Who or What Process created this record? 90 chars max")

    # Additional Columns Here



    class_name_string = "User"

    # Add More Static Properties here if needed

    # Add Enums hooked to settings if needed



    def get_Auth_Username(self):
        current_auth_username = "Current_UserName_Unknown"
        try:
            current_auth_username = AuthUser.objects.filter(id=self.auth_id)[0].username
        except:
            current_auth_username = "Current_UserName_Unknown"
        return current_auth_username

    # Output object as a string (primary use for this is admin panels)
    def __str__(self):
        current_auth_username = "Current_UserName_Unknown"
        try:
            current_auth_username = AuthUser.objects.filter(id=self.auth_id)[0].username
        except:
            current_auth_username = "Current_UserName_Unknown"
        try:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | auth_id: " + str(self.auth_id) + " | Auth Username: " + str(current_auth_username) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        except:
            outString = "id: " + str(self.id) + " | uuid: " + str(self.uuid) + " | auth_id: " + str(self.auth_id) + " | Auth Username: " + str(current_auth_username) + " | created_at: " + str(self.created_at) + " | created_by: " + str(self.created_by) + " | is_test_object: " + str(self.is_test_object)
        return outString


    # Non Static, Serialize current element to JSON
    def to_JSONable_Object(self):
        retObj = {}
        retObj["id"]                            = str(self.id).strip()
        retObj["uuid"]                          = str(self.uuid).strip()
        retObj["created_at"]                    = str(self.created_at).strip()
        retObj["created_by"]                    = str(self.created_by).strip()
        retObj["additional_json"]               = json.loads(self.additional_json)
        retObj["is_test_object"]                = str(self.is_test_object).strip()

        # Add Custom Export to JSON Content Here - Fields/Columns Serialization (stringifying)
        retObj["auth_id"]                   = str(self.auth_id).strip()
        retObj["is_admin"]                  = str(self.is_admin).strip()
        retObj["can_manage_users"]          = str(self.can_manage_users).strip()
        retObj["can_manage_etl_logs"]       = str(self.can_manage_etl_logs).strip()
        retObj["can_manage_api_logs"]       = str(self.can_manage_api_logs).strip()
        retObj["can_manage_server_logs"]    = str(self.can_manage_server_logs).strip()

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



    # Check to see if a user exists, by it's 'auth_id' property.
    # # If it does exist, return True AND the JSONable info for that user.
    # # does_user_exist__by_auth_id(auth_id):  # return ret_Bool, ret_UserJSON
    @staticmethod
    def does_user_exist__by_auth_id(auth_id):

        ret_Bool = False
        ret_UserJSON = {}
        try:
            # auth_id   str(auth_id)
            user_Results = User.objects.filter(auth_id=str(auth_id))
            ret_Bool = True
            ret_UserJSON = user_Results[0].to_JSONable_Object()
        except:
            ret_Bool = False
            ret_UserJSON = {}
        return ret_Bool, ret_UserJSON


    # Create a new user, specifically called from Session Creation process
    # # create_new_user__ForSessionCreation(auth_user_id):  return ret_did_Create_User, ret_UserJSON
    @staticmethod
    def create_new_user__ForSessionCreation(auth_user_id):
        ret_did_Create_User = False
        ret_UserJSON = {}
        try:
            # Create the New Record, set props, and then save
            newUser             = User()
            newUser.auth_id     = str(auth_user_id).strip()
            newUser.created_by  = "Created_During_Auto_Session_Creation_Process"  #"Auto_Session_Creation_Process"
            newUser.save()

            ret_UserJSON = newUser.to_JSONable_Object()
            ret_did_Create_User = True
        except:
            ret_did_Create_User = False
            ret_UserJSON = {}
        return ret_did_Create_User, ret_UserJSON


    # Get Count (total number of users) - For the Dashboard
    @staticmethod
    def get_total_user_count():
        numberOfUsers = User.objects.all().count
        return numberOfUsers



    # #########################
    # # AUTH USER FUNCTIONS
    # #########################
    @staticmethod
    def auth_user__is_username_avalaible(input__username):
        retBool = True
        try:
            existing_auth_user = AuthUser.objects.filter(username=str(input__username).strip())[0]
            retBool = False
        except:
            retBool = True
        return retBool

    @staticmethod
    def auth_user__is_email_avalaible(input__email):
        retBool = True
        try:
            existing_auth_user = AuthUser.objects.filter(email=str(input__email).strip())[0]
            retBool = False
        except:
            retBool = True
        return retBool

    @staticmethod
    def auth_user__create_user(input__username, input__firstname, input__lastname, input__email, input__password):
        # Create a new Auth user and return the ID
        new_AuthUser = AuthUser.objects.create_user(str(input__username).strip(), str(input__email).strip(), str(input__password).strip())
        new_AuthUser.first_name = str(input__firstname).strip()
        new_AuthUser.last_name = str(input__lastname).strip()
        new_AuthUser.save()
        new_AuthUser_ID = str(new_AuthUser.id).strip()
        return new_AuthUser_ID

# MAKE MIGRATIONS
#--Migrations
# # python manage.py makemigrations api_v2
# # python manage.py migrate


# --Make Migration
# ---api_v2/migrations/0001_initial.py
# ----Create model User
# --Migrate
# ---Applying api_v2.0001_initial... OK








# END OF FILE!