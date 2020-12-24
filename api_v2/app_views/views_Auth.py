# views_Auth.py

# Came with Django
from django.shortcuts import render

# Needed for normal Views-API app Operations
from django.http import HttpResponse
from django.http import JsonResponse    # For returning JSON
from django.views.decorators.csrf import csrf_exempt        # For the @csrf_exempt lines
from django.conf import settings

# For getting session info
from django.contrib.sessions.models import Session

from api_v2 import views


import sys
import json

# Custom stuff
from common_utils import utils as common_utils
from common_utils import views as common_views_utils


from django.contrib.auth import authenticate

from api_v2.app_models.model_User import User as api_v2__user





# Authenticate User - Returns True or False - True means the credentials are valid.
# is_user_authenticated, authenticated_user = is_user_authenticated(username, password):
# dir(user)
# # ['DoesNotExist', 'EMAIL_FIELD', 'Meta', 'MultipleObjectsReturned', 'REQUIRED_FIELDS', 'USERNAME_FIELD', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_column_name_clashes', '_check_constraints', '_check_field_name_clashes', '_check_fields', '_check_id_field', '_check_index_together', '_check_indexes', '_check_local_fields', '_check_long_column_names', '_check_m2m_through_same_relationship', '_check_managers', '_check_model', '_check_model_name_db_lookup_clashes', '_check_ordering', '_check_property_name_related_field_accessor_clashes', '_check_single_primary_key', '_check_swappable', '_check_unique_together', '_do_insert', '_do_update', '_get_FIELD_display', '_get_next_or_previous_by_FIELD', '_get_next_or_previous_in_order', '_get_pk_val', '_get_unique_checks', '_meta', '_password', '_perform_date_checks', '_perform_unique_checks', '_save_parents', '_save_table', '_set_pk_val', '_state', 'backend', 'check', 'check_password', 'clean', 'clean_fields', 'date_error_message', 'date_joined', 'delete', 'email', 'email_user', 'first_name', 'from_db', 'full_clean', 'get_all_permissions', 'get_deferred_fields', 'get_email_field_name', 'get_full_name', 'get_group_permissions', 'get_next_by_date_joined', 'get_previous_by_date_joined', 'get_session_auth_hash', 'get_short_name', 'get_username', 'groups', 'has_module_perms', 'has_perm', 'has_perms', 'has_usable_password', 'id', 'is_active', 'is_anonymous', 'is_authenticated', 'is_staff', 'is_superuser', 'last_login', 'last_name', 'logentry_set', 'natural_key', 'normalize_username', 'objects', 'password', 'pk', 'prepare_database_save', 'refresh_from_db', 'save', 'save_base', 'serializable_value', 'set_password', 'set_unusable_password', 'unique_error_message', 'user_permissions', 'username', 'username_validator', 'validate_unique']
def check_and_get_authenticated_user(username, password):
    retBool = False
    retUser = {}
    try:
        user = authenticate(username=username, password=password)
        if (str(user) == 'None'):
            # No backend authenticated the credentials
            retBool = False
        else:
            # A backend DID authenticate the credentials
            retBool = True
            retUser = user
    except:
        retBool = False
    return retBool, retUser



#
# Create Session for an Authenticated User - this is also the place where we check the auth.user table and combine with anything needed from the CSERV Users Table
#
# session['cserv_user'] :  This is the JSONable data from an api_v2.User record, so, session['cserv_user']['uuid'] should be something like "xyzabc1234etc"
def create_session_for_authenticated_user(authenticated_user, request):

    # Get the Authenticated User ID (Auth.User.id)
    auth_user_id__STR = str(authenticated_user.id).strip()  # converting 2 to '2'
    cserv_user_exists = False

    # Check to see if this user already exists.
    cserv_user_exists, cserv_user_JSON = api_v2__user.does_user_exist__by_auth_id(auth_id=auth_user_id__STR)

    # If the cserv user does not yet exist, create it now.
    if(cserv_user_exists == False):
        cserv_user_exists, cserv_user_JSON = api_v2__user.create_new_user__ForSessionCreation(auth_user_id=auth_user_id__STR)

    # Get the CServ User's UUID
    #cserv_user_uuid = str(cserv_user_JSON['uuid']).strip()
    username    = str(authenticated_user.username)
    email       = str(authenticated_user.email)
    #other_auth_user_property  =  str(authenticated_user.other_auth_user_property)
    auth_user = {}
    auth_user['username']   = username
    auth_user['email']      = email


    # #

    # Make sure the session is never None  (Creates a new session if the request value of 'session_key' is None)
    if not request.session.session_key:
        request.session.save()
    session_id = request.session.session_key
    session__Key__Value = session_id  # request.session.session_key

    # Add the cserv_user info to the session.
    request.session['cserv_user']   = cserv_user_JSON
    request.session['auth_user']    = auth_user
    request.session.save()

    return session__Key__Value


# Moved to 'views.py'
# def get_cserv_user_and_auth_user_from_Session(sid):







# process_signin
# Signing User in - Process a signin request (requires a username and password)
# url(r'process_signin/',  views_Auth.process_signin,  name='process_signin'),
@csrf_exempt  # POST REQUESTS ONLY
def process_signin(request):
    response_data = {}
    api_function_name = "process_signin"
    api_function_code = "A2PSI_1_0_0"
    additional_request_data_py_obj = {}
    retSessionInfo = ""
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj   = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'username', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},
            {'inputKey_Str': 'password', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},
        ]

        # Validate Input Params
        processed_RequestParams = {}
        isValidationError = False
        validationErrorMessages = ""
        validationSysErrorData = ""
        processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData = common_views_utils.validate_extract_process_requestParams(requestData_PyObj=theData_PyObj, paramsInfo=paramsInfo)

        # Return if Validation Error
        if (isValidationError == True):
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage="Validation Error Occurred: " + str(validationErrorMessages), errorCode=api_function_code, errorData=validationSysErrorData)

            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        username = processed_RequestParams['username']
        password = processed_RequestParams['password']

        is_user_authenticated, authenticated_user = check_and_get_authenticated_user(username=username, password=password)

        if(is_user_authenticated == False):
            human_readable_error = "Username or Password is incorrect."
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData={})

        else:
            # Get Session ID (or create one) for this authenticated user.
            session_id = ""
            session_id = create_session_for_authenticated_user(authenticated_user, request)
            retSessionInfo = session_id

            response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
            response_data['sid'] = str(session_id) #"" #

            cserv_user, auth_user = views.get_cserv_user_and_auth_user_from_Session(str(session_id))
            #response_data['DEBUG__cserv_user_info'] = cserv_user
            #response_data['DEBUG__auth_user_info'] = auth_user


        #print("username: " + str(username))
        #print("password: " + str(password))
        #print("is_user_authenticated: " + str(is_user_authenticated))
        #print("authenticated_user: " + str(authenticated_user))
        #
        # Get the success response data
        #response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
        #response_data['PLACEHOLDER'] = "Placeholder"
    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        #additional_request_data_py_obj['extra_information'] = "none"
        #views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()



    # Return the Response
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
    # Special, on signin, we want to keep the session info in the return (this is where the client actually receives it).
    # # # Without this line, the client is never actually able to login.
    try:
        response_data['sid'] = retSessionInfo
    except:
        pass
    return JsonResponse(response_data)





# process_signout
# Signing User in - Process a signin request (requires a username and password)
# url(r'process_signout/',  views_Auth.process_signout,  name='process_signout'),
@csrf_exempt  # POST REQUESTS ONLY
def process_signout(request):
    response_data = {}
    api_function_name = "process_signout"
    api_function_code = "A2PSO_1_0_0"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj   = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        #views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},
        ]

        # Validate Input Params
        processed_RequestParams = {}
        isValidationError = False
        validationErrorMessages = ""
        validationSysErrorData = ""
        processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData = common_views_utils.validate_extract_process_requestParams(requestData_PyObj=theData_PyObj, paramsInfo=paramsInfo)

        # Return if Validation Error
        if (isValidationError == True):
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage="Validation Error Occurred: " + str(validationErrorMessages), errorCode=api_function_code, errorData=validationSysErrorData)

            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        session_info = processed_RequestParams['session_info']

        print("process_signout: (session_info): " + session_info)
        views.delete_session(sid=session_info)

        # Get the success response data
        response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Load up info for Reporting the API Error (As an API Call) for tracking and feedback
        #additional_request_data_py_obj['extra_information'] = "none"
        #views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()


    # Return the Response
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
    return JsonResponse(response_data)

#
#
#
# # Debug Endpoints # TODO - Make these real
# url(r'^session_output_test/',                 views_Auth.session_output_test,                 name='session_output_test'),
# url(r'^process_signin_as_test_user_1/',       views_Auth.process_signin_as_test_user_1,       name='process_signin_as_test_user_1'),
# url(r'^process_signin_as_test_user_2/',       views_Auth.process_signin_as_test_user_2,       name='process_signin_as_test_user_2'),
# url(r'^process_signin_as_test_admin_user_1/', views_Auth.process_signin_as_test_admin_user_1, name='process_signin_as_test_admin_user_1'),






# session_output_test
#
# url(r'^session_output_test/',                 views_Auth.session_output_test,                 name='session_output_test'),
@csrf_exempt  # POST REQUESTS ONLY
def session_output_test(request):
    outputHTML = ""



    did_Get_Session_Cookie = False
    sessionID__From_Cookie = "UNSET"
    try:
        sessionID__From_Cookie = request.COOKIES['sessionid']
        did_Get_Session_Cookie = True
    except:
        did_Get_Session_Cookie = False


    request.session['foo'] = 'bar'

    # Output
    outputHTML += "Hello (This is the Session Output Test)<br />"
    outputHTML += "<br />"
    outputHTML += "Session Output: <br />"
    outputHTML += "  Raw: (inspect element to see):  " + str(request.session) + "<br />"
    outputHTML += "  some_not_used_key: " + str(request.session.get('some_not_used_key', "Some Default Value")) + "<br />"
    outputHTML += "  request.session.keys(): " + str(request.session.keys()) + "<br />"
    outputHTML += "  request.session.session_key: " + str(request.session.session_key) + "<br />"
    outputHTML += "  request.COOKIES['sessionid'] Stored as: (sessionID__From_Cookie): " + str(sessionID__From_Cookie) + "<br />"
    try:
        # This is the part that should only be set if the user is 'logged in'
        custom_user_info = request.session.get('custom_user_info', {})

        # # Session Variables
        # Most Common Session vars
        custom_user_info__field_name            = custom_user_info['field_name']


        outputHTML += "<br />Application Specific Session Vars<br /><br />"
        outputHTML += " -<b>Most Common App Specific Session Vars</b><br />"
        outputHTML += "  request.session['custom_user_info']['field_name']: " + str(custom_user_info__field_name) + "<br />"


    except:
        pass


    signedIn_HTML = ""

    outputHTML += "<br /><br /><br />"
    outputHTML += "Prototyping the Sign in Button (or Signed In as XYZ Label) <br /><br />"
    outputHTML += signedIn_HTML


    return HttpResponse(outputHTML)
# END OF:       def session_output_test(request):




# GARBAGE

    # Left over from doing Session creation work
    #
    #
# # create_new_user__ForSessionCreation(auth_user_id):  return ret_did_Create_User, ret_UserJSON
    #
    #does_user_exist__by_auth_id(auth_id):  # return ret_Bool, ret_UserJSON
    #api_v2__user.objects.all().filter();
    #
    #api_v2__user
    #
    # DONE: Checkpoint
    # Check and see if this user already exists in our user table.
    # # By Comparing the auth.user id with the api_v2.user record
    #auth_user_id__STR = str(authenticated_user.id).strip()  # converting 2 to '2'
    # # If this user does not already exist, then create it now. - CreatedBy - Created_During_Auto_session_Creation
    #
    #
    #cserv_user_id = "abcdefg"  # DONE - Change this to an ACTUAL ID after datamodel exists.
    ##
    #cserv_user_JSON = {} # DONE, Get the JSON Version of some of the CSERV User's data