
from django.shortcuts import render

# Needed for normal Views-API app Operations
from django.http import HttpResponse
from django.http import JsonResponse                        # For returning JSON
from django.views.decorators.csrf import csrf_exempt        # For the @csrf_exempt lines
from django.conf import settings
from api_v2.app_models.model_Config_Setting import Config_Setting
from django.contrib.sessions.models import Session

import sys
import json


# Custom stuff
from common_utils import utils as common_utils
from common_utils import views as common_views_utils

# For getting session info
from django.contrib.sessions.models import Session


from api_v2.app_models.model_API_Log        import API_Log
#from api_v2.app_models.model_Server_Log     import Server_Log


# # API REPORTING
# ########

# This function should be called with EVERY api request - so the the info can go straight into the DB Logs
#
# Keys that should exist if there is an error,
# # additional_request_data_py_obj['errorMessage']  // Human Readable Message (Similar or same as what gets passed back to the client)
# # additional_request_data_py_obj['errorData']     // System Output - should contain enough debugging info to nail down the source of the error.
def report_API_Call_Event(request_obj, api_function_name, api_function_code, additional_request_data_py_obj, server_response_json):




    # In the request data, Replace 'password' with "PASSWORD_REMOVED_FOR_LOGGING"
    try:
        # Checking for additional_request_data_py_obj['raw_httpbody_POST_params']['password']
        if 'password' in additional_request_data_py_obj['raw_httpbody_POST_params'].keys():
            additional_request_data_py_obj['raw_httpbody_POST_params']['password'] = "PASSWORD_REMOVED_FOR_LOGGING"
    except:
        pass

    # In the request data, Replace 'session_info' with "SESSION_INFO_REMOVED_FOR_LOGGING"
    try:
        # Checking for additional_request_data_py_obj['raw_httpbody_POST_params']['password']
        if 'session_info' in additional_request_data_py_obj['raw_httpbody_POST_params'].keys():
            additional_request_data_py_obj['raw_httpbody_POST_params']['session_info'] = "SESSION_INFO_REMOVED_FOR_LOGGING"
    except:
        pass

    # In the server's response data, Replace 'session_info' with "SESSION_INFO_REMOVED_FOR_LOGGING"
    try:
        # Checking for additional_request_data_py_obj['raw_httpbody_POST_params']['password']
        if 'sid' in server_response_json.keys():
            server_response_json['sid'] = "SESSION_INFO_REMOVED_FOR_LOGGING"
    except:
        pass

    # Get the response state (from the server_response_json)
    server_result_state = "UNSET"
    try:
        server_result_state = server_response_json['result']
    except:
        server_result_state = "UNKNOWN"

    # Try and get the query string
    query_string = ""
    try:
        query_string = str(request_obj.META['QUERY_STRING']).strip()
    except:
        pass


    # Try and get IP
    REMOTE_ADDR = ""
    try:
        REMOTE_ADDR = common_utils.get_client_ip(request=request_obj)
    except:
        pass

    # Try and get the endpoint (This should always work)
    path_info = ""
    try:
        path_info = str(request_obj.path_info)
    except:
        pass

    endpoint = str(path_info).strip()

    # Check ignore list - if endpoint is in the ignore list, then don't do the logging, just return blank string
    try:
        #endpoint_ignore_list = settings.API_LOGGING_ENDPOINT_IGNORE_LIST
        endpoint_ignore_list = Config_Setting.get_value(setting_name="API_LOGGING_ENDPOINT_IGNORE_LIST", default_or_error_return_value=[])
        if (endpoint in endpoint_ignore_list):
            # Looks like this endpoint was contained in the ignore list, skip the logging and just return a blank string.
            ret_val = ""
            return ret_val
    except:
        pass


    # endpoint        = str(path_info).strip()      # Moved up, so we can check the ignore list
    ip_address      = str(REMOTE_ADDR).strip()
    created_by      = str(api_function_name).strip()
    additional_json = {}
    additional_json['api_function_name']                = str(api_function_name).strip()
    additional_json['api_function_code']                = str(api_function_code).strip()
    additional_json['additional_request_data_py_obj']   = additional_request_data_py_obj
    additional_json['query_string']                     = query_string
    additional_json['server_response_json']             = server_response_json

    new_API_Log_UUID = API_Log.create_new_api_log_row(endpoint=endpoint, server_result_state=server_result_state, ip_address=ip_address, created_by=created_by, additional_json=additional_json)
    #new_API_Log_UUID = "TEST_API_LOG_UUID"

    #
    # print("")
    # print("report_API_Call_Event: DEBUG: (additional_json) " + str(additional_json))
    # print("report_API_Call_Event: DEBUG: (new_API_Log_UUID) " + str(new_API_Log_UUID))
    # print("")

    return new_API_Log_UUID

# DEPRECATING (Now all API Logs go through the function: report_API_Call_Event(request_obj, api_function_name, api_function_code, additional_request_data_py_obj, server_response_json):)
# # If an error exists, it can be found in the object 'server_response_json'
# This is the part of the code where we can send API Call Errors to the data model.
def report_API_Error(api_function_name, api_function_code, human_readable_error, sys_error_info, additional_request_data_py_obj):
    print("report_API_Error: TODO: Hook this up to a Data model")
    pass





# # SESSIONS
def delete_session(sid):
    try:
        s = Session.objects.get(pk=str(sid))
        s.delete()
    except:
        pass


# For Dealing with manually getting a session from an id (rather than from the request)
def get_cserv_user_and_auth_user_from_Session(sid):
    # cserv_user_info = {}
    # try:
    #     cserv_user_info = request.session.get('cserv_user', {})
    # except:
    #     cserv_user_info = {}
    # return cserv_user_info
    cserv_user = {}
    auth_user = {}
    try:
        s = Session.objects.get(pk=str(sid))
        decoded_Session = s.get_decoded()
        cserv_user = decoded_Session['cserv_user']
        auth_user = decoded_Session['auth_user']
    except:
        cserv_user = {}
        auth_user = {}
    return cserv_user, auth_user




# ADMIN Permissions Check
def is_this_an_admin_user(session_info):
    current_user__is_admin = False
    cserv_user_info_obj, auth_user_info_obj = get_cserv_user_and_auth_user_from_Session(sid=session_info)
    try:
        current_user__is_admin = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=cserv_user_info_obj['is_admin'], defaultBoolValue=False)
    except:
        current_user__is_admin = False
    return current_user__is_admin



API_VERSION = "2.0.0"



# ACTION: Get ServerApp and API Versions (No Auth)
# ex: /api_v2/get_server_versions       # Code Ex: errorCode = "AGSV_1_0_0"
#url(r'^get_server_versions/', views.get_server_versions, name='get_server_versions'),
@csrf_exempt # POST REQUESTS ONLY
def get_server_versions(request):
    #print("def get_server_versions(request):")
    errorCode = "AGSV_1_0_0"
    response_data = {}
    api_function_name = "get_server_versions"
    api_function_code = "A2GSV_1_0_0"
    additional_request_data_py_obj = {}
    try:
        # a = 1/0
        # # No input request processing here.
        response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
        response_data['server_app_version'] = settings.SERVERSIDE_APP_VERSION_STRING
        response_data['api_version'] = API_VERSION
    except:
        # # Uncaught Generic Error
        sysErrorData = sys.exc_info()  # sysErrorData = sys.exc_info()[0]
        human_readable_error = "An Unknown Error Occurred"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=errorCode, errorData=sysErrorData)

        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sysErrorData).strip()

    # Return the Response
    new_API_Log_UUID = report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
    return JsonResponse(response_data)



# Some other endpoints views code here...




# END OF FILE