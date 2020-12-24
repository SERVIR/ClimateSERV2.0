# views_ManageUsers.py

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

from django.db.models import Q

import sys
import json

# Custom stuff
from common_utils import utils as common_utils
from common_utils import views as common_views_utils


#from django.contrib.auth import authenticate
# 'APILog', 'AvailableGranule', 'ETLDataset', 'ETLGranule', 'ETLLog', 'ETLPipelineRun', 'User'
from api_v2.app_models.model_API_Log            import API_Log
from api_v2.app_models.model_Available_Granule  import Available_Granule
from api_v2.app_models.model_ETL_Dataset        import ETL_Dataset
from api_v2.app_models.model_ETL_Granule        import ETL_Granule
from api_v2.app_models.model_ETL_Log            import ETL_Log
from api_v2.app_models.model_ETL_PipelineRun    import ETL_PipelineRun
from api_v2.app_models.model_User               import User as api_v2__user


from datetime import datetime, timedelta



# # Possible values: // THE_LAST_7_DAYS, THE_LAST_30_DAYS, ALL
# print("time_enum: " + str(time_enum))
def convert_time_enum_to_time_delta(time_enum):
    # d = datetime.today() - timedelta(days=days_to_subtract)
    # datetime.datetime.utcnow()
    #ret_datetime = earliest_datetime = datetime(year=2000, month=1, day=1) #datetime.datetime.utcnow()
    ret_datetime = datetime.utcnow()
    if(time_enum == "THE_LAST_7_DAYS"):
        ret_datetime = ret_datetime - timedelta(days=7)
    if (time_enum == "THE_LAST_30_DAYS"):
        ret_datetime = ret_datetime - timedelta(days=30)
    return ret_datetime


# Helper - Every function should have this at the end (For api logging and returning)
#       # Return the Response
#       new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
#       return JsonResponse(response_data)

# admin_get_db_item
# Generic Getter for any specific white listed database object by type and id.
# url(r'admin_get_db_item/',  views_Admin_Generic.admin_get_db_item,  name='admin_get_db_item'),
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_db_item(request):
    response_data = {}
    api_function_name = "admin_get_db_item"
    api_function_code = "A2AGDI"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'object_uuid', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'object_type', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

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

            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        is_Pass_Biz_Validation = True
        validation_error_message = ""

        session_info    = processed_RequestParams['session_info']
        object_uuid     = processed_RequestParams['object_uuid']
        object_type     = processed_RequestParams['object_type']

        #print("DEBUG: (session_info) " + str(session_info))
        #print("DEBUG: (object_uuid) " + str(object_uuid))
        #print("DEBUG: (object_type) " + str(object_type))

        # The TYPES of objects that admin tool can retrieve by database id
        ADMIN_GET_DB_OBJECT_TYPES = ['APILog', 'AvailableGranule', 'ETLDataset', 'ETLGranule', 'ETLLog', 'ETLPipelineRun', 'ServerLog', 'User', 'Task_Log']
        if(object_type not in ADMIN_GET_DB_OBJECT_TYPES):
            is_Pass_Biz_Validation = False
            validation_error_message += "Object Type: " +str(object_type) + ", not found in list: " + str(ADMIN_GET_DB_OBJECT_TYPES) + "  The API won't let a type that is not recognized pass the validation.  The list of types are case sensitive.  "

        #print(str(session_info))
        current_user__has_permissions = False
        try:
            current_user__is_admin = views.is_this_an_admin_user(session_info=session_info)
            if (current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            #print("We hit the except block.. Lets find out what went wrong..")
            pass
        if (current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to get database objects.  "


        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Grab the requested object
            #

            try:
                # 'APILog', 'AvailableGranule', 'ETLDataset', 'ETLGranule', 'ETLLog', 'ETLPipelineRun', 'User'

                # 'APILog', 'AvailableGranule', 'ETLDataset', 'ETLGranule', 'ETLLog', 'ETLPipelineRun', 'User'
                # from api_v2.app_models.model_API_Log import API_Log
                # from api_v2.app_models.model_Available_Granule import Available_Granule
                # from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
                # from api_v2.app_models.model_ETL_Granule import ETL_Granule
                # from api_v2.app_models.model_ETL_Log import ETL_Log
                # from api_v2.app_models.model_ETL_PipelineRun import ETL_PipelineRun
                # from api_v2.app_models.model_User import User as api_v2__user

                retObj = {}
                if(object_type == 'APILog'):
                    retObj = API_Log.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'AvailableGranule'):
                    retObj = Available_Granule.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'ETLDataset'):
                    retObj = ETL_Dataset.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'ETLGranule'):
                    retObj = ETL_Granule.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'ETLLog'):
                    retObj = ETL_Log.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'ETLPipelineRun'):
                    retObj = ETL_PipelineRun.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()
                if (object_type == 'User'):
                    retObj = api_v2__user.objects.filter(uuid=object_uuid)[0].to_JSONable_Object()

                # Get the success response data
                response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
                response_data['object_type']    = str(object_type).strip()
                response_data['object_uuid']    = str(object_uuid).strip()
                response_data['object_json']    = retObj

            except:
                # Uncaught Generic Error - Prep the response
                sys_error_info = sys.exc_info()
                human_readable_error = "An Error Occurred when trying to get an individual, specific database object.  It may be the case that the object_type and object_uuid combination was not found.  object_type: " + str(object_type) + ", object_uuid: " + str(object_uuid)
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

                # Report the API Error to the server for tracking and feedback
                # additional_request_data_py_obj['extra_information'] = "none"
                # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()


    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

    # Return the Response
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
    return JsonResponse(response_data)





# ########################################################################
# # List Types - Support paging and Custom Param Sorting
# ########################################################################


# # /api_v2/admin_get_api_logs  //
# url(r'admin_get_api_logs/',  views_Admin_Generic.admin_get_api_logs,  name='admin_get_api_logs'),               # # /api_v2/admin_get_api_logs  //
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_api_logs(request):
    response_data = {}
    api_function_name = "admin_get_api_logs"
    api_function_code = "A2AGAL"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'page_number', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 0},

            {'inputKey_Str': 'items_per_page', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 50},

            {'inputKey_Str': 'search_string', 'inputType_ClassName': 'str', 'isParamOptional': 'True', 'isValidate_ForNotEmpty': 'False', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'endpoint_name', 'inputType_ClassName': 'str', 'isParamOptional': 'True', 'isValidate_ForNotEmpty': 'False', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'ip_address', 'inputType_ClassName': 'str', 'isParamOptional': 'True', 'isValidate_ForNotEmpty': 'False', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'errors_only', 'inputType_ClassName': 'bool', 'isParamOptional': 'True', 'isValidate_ForNotEmpty': 'False', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': False},

            {'inputKey_Str': 'success_only', 'inputType_ClassName': 'bool', 'isParamOptional': 'True', 'isValidate_ForNotEmpty': 'False', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': False},

            # {'inputKey_Str': 'object_type', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

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

            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        is_Pass_Biz_Validation = True
        validation_error_message = ""

        session_info    = processed_RequestParams['session_info']
        page_number     = processed_RequestParams['page_number']
        items_per_page  = processed_RequestParams['items_per_page']
        search_string   = processed_RequestParams['search_string']
        endpoint_name   = processed_RequestParams['endpoint_name']
        ip_address      = processed_RequestParams['ip_address']
        errors_only     = processed_RequestParams['errors_only']
        success_only    = processed_RequestParams['success_only']

        current_user__has_permissions = False
        try:
            current_user__is_admin = views.is_this_an_admin_user(session_info=session_info)
            if (current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            # print("We hit the except block.. Lets find out what went wrong..")
            pass
        if (current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to get database objects.  "

        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Grab the requested object
            try:
                retList = []

                # Setup the filter params
                #qFilter_Params = {}
                qFilter_Params = Q()
                if(search_string != ''):
                    qFilter_Params.add(Q(ip_address__icontains=search_string), Q.OR)
                    qFilter_Params.add(Q(endpoint__icontains=search_string), Q.OR)
                    qFilter_Params.add(Q(additional_json__icontains=search_string), Q.OR)
                    qFilter_Params.add(Q(server_result_state__icontains=search_string), Q.OR)
                    # qFilter_Params['column__icontains'] = search_string
                    pass
                if(endpoint_name != ''):
                    qFilter_Params.add(Q(endpoint=endpoint_name), Q.AND)
                    #query.add(Q(last_name='doe'), Q.AND)
                    #qFilter_Params
                    #qFilter_Params['endpoint'] = endpoint_name
                if(ip_address != ''):
                    qFilter_Params.add(Q(ip_address=ip_address), Q.AND)
                    #qFilter_Params['ip_address'] = ip_address
                if(errors_only == True):
                    qFilter_Params.add(Q(server_result_state="error"), Q.AND) # errors_only
                    # server_result_state possibilities:     # success   # error
                if (success_only == True):
                    qFilter_Params.add(Q(server_result_state="success"), Q.AND)  # errors_only
                    # server_result_state possibilities:     # success   # error


                # TODO - API Custom Query Filter - Generic Search (Many Fields)
                # TODO - API Custom Query Filter - endpoint name
                # TODO - API Custom Query Filter - ip address
                # TODO - API Custom Query Filter - Errors only (When object.server_result_state == 'error')   (And the inverse, when object.server_result_state == 'success')
                # TODO - API Custom Query Filter - counts for all these

                # TODO - BRAIN_STORMING
                # # TODO - API Custom Query Filter - Special Query (Get_Stats_for_type) - Add some functions to the models themselves which calculate all these interesting stats and add these to the return
                # # # TODO - API Custom Query Filter - Special Query (maybe different function) - that counts the errors and successes and returns those (That is part of get_stats_for_type


                print("admin_get_api_logs: TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc")
                # TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc
                #db_objects = API_Log.objects.filter(**qFilter_Params).order_by('-created_at')[(items_per_page * page_number):(items_per_page * page_number) + items_per_page] #.all()
                db_objects = API_Log.objects.filter(qFilter_Params).order_by('-created_at')[(items_per_page * page_number):(items_per_page * page_number) + items_per_page]  # .all()
                for db_object in db_objects:
                    retList.append(db_object.to_JSONable_Object())

                # Get the total objects count for this query.
                #total_db_objects_count_for_query = API_Log.objects.filter(**qFilter_Params).count()
                total_db_objects_count_for_query = API_Log.objects.filter(qFilter_Params).count()

                # Get the success response data
                response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
                response_data['PLACEHOLDER'] = str("TODO_FINISH_THIS_FUNCTION_ON_THE_SERVER").strip()
                response_data['items_per_page'] = str(items_per_page).strip()
                response_data['page_number'] = str(page_number).strip()
                response_data['objects_type'] = str("API_Log").strip()
                response_data['objects_count'] = str(len(retList)).strip()
                response_data['objects_list'] = retList
                response_data['total_db_objects_count_for_query'] = total_db_objects_count_for_query # str(len(total_db_objects_count_for_query)).strip()  # how many total objects exist in the database for this query.

            except:
                # Uncaught Generic Error - Prep the response
                sys_error_info = sys.exc_info()
                human_readable_error = "An Error Occurred when trying to get a list of API Logs from the database."
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

                # Report the API Error to the server for tracking and feedback
                # additional_request_data_py_obj['extra_information'] = "none"
                # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()


    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

    # Return the Response
    response_data_COPY = dict(response_data)
    response_data_COPY['objects_list'] = ["Objects_Removed_For_Logging"]
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)




# admin_get_etl_logs
# # /api_v2/admin_get_etl_logs  //
# url(r'admin_get_etl_logs/',  views_Admin_Generic.admin_get_etl_logs,  name='admin_get_etl_logs'),               # # /api_v2/admin_get_etl_logs  //
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_etl_logs(request):
    response_data = {}
    api_function_name = "admin_get_etl_logs"
    api_function_code = "A2AGEL"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'page_number', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 0},

            {'inputKey_Str': 'items_per_page', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 50},

           # {'inputKey_Str': 'object_type', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

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

            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        is_Pass_Biz_Validation = True
        validation_error_message = ""

        session_info = processed_RequestParams['session_info']
        page_number = processed_RequestParams['page_number']
        items_per_page = processed_RequestParams['items_per_page']

        current_user__has_permissions = False
        try:
            current_user__is_admin = views.is_this_an_admin_user(session_info=session_info)
            if (current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            # print("We hit the except block.. Lets find out what went wrong..")
            pass
        if (current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to get database objects.  "

        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Grab the requested object
            try:
                retList = []

                # Setup the filter params
                qFilter_Params = {}
                # if (endpoint_name != ''):
                #     qFilter_Params['endpoint'] = endpoint_name

                # TODO - ETL Custom Query Filter - is_alert  (is_alert == True is something an admin should see ASAP)
                # TODO - ETL Custom Query Filter - Filter down by: etl_pipeline_run_uuid - And Optional subfiltering activity_event_type
                # TODO - ETL Custom Query Filter - Filter down by: etl_dataset_uuid - And Optional subfiltering activity_event_type
                # TODO - ETL Custom Query Filter - Filter down by: etl_granule_uuid - And Optional subfiltering activity_event_type
                #
                # TODO - ETL Custom Query Filter - Filter down by: activity_event_type by itself (These are actually how we find the 'errors' in a query settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_ERROR and settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING)
                #
                # TODO - ETL Custom Query Filter - counts for all these

                # TODO - Additional Tables and Views
                # # TODO - Endpoint for toggling the 'is_alert' value for a given ETLLog UUID value.
                # # TODO - (ETL_Dataset Model)      - Endpoint for viewing lists of Datasets
                # # TODO - (ETL_Granule Model)      - Endpoint for viewing lists of Granules
                # # TODO - (ETL_PipelineRun Model)  - Endpoint for viewing lists of Pipeline Runs




                print("admin_get_etl_logs: TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc")
                # TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc
                db_objects = ETL_Log.objects.filter(**qFilter_Params).order_by('-created_at')[(items_per_page * page_number):(items_per_page * page_number) + items_per_page] #.all()
                for db_object in db_objects:
                    retList.append(db_object.to_JSONable_Object())

                # Get the total objects count for this query.
                total_db_objects_count_for_query = ETL_Log.objects.filter(**qFilter_Params).count()

                # Get the success response data
                response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
                response_data['PLACEHOLDER'] = str("TODO_FINISH_THIS_FUNCTION_ON_THE_SERVER").strip()
                response_data['items_per_page'] = str(items_per_page).strip()
                response_data['page_number'] = str(page_number).strip()
                response_data['objects_type'] = str("ETL_Log").strip()
                response_data['objects_count'] = str(len(retList)).strip()
                response_data['objects_list'] = retList
                response_data['total_db_objects_count_for_query'] = total_db_objects_count_for_query # str(len(total_db_objects_count_for_query)).strip()  # how many total objects exist in the database for this query.
            except:
                # Uncaught Generic Error - Prep the response
                sys_error_info = sys.exc_info()
                human_readable_error = "An Error Occurred when trying to get a list of ETL Logs from the database."
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

                # Report the API Error to the server for tracking and feedback
                # additional_request_data_py_obj['extra_information'] = "none"
                # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()




    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

    # Return the Response
    response_data_COPY = dict(response_data)
    response_data_COPY['objects_list'] = ["Objects_Removed_For_Logging"]
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)



# admin_get_server_logs
# # /api_v2/admin_get_server_logs  //
# url(r'admin_get_server_logs/',  views_Admin_Generic.admin_get_server_logs,  name='admin_get_server_logs'),      # # /api_v2/admin_get_server_logs  //
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_server_logs(request):
    response_data = {}
    api_function_name = "admin_get_server_logs"
    api_function_code = "A2AGSL"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'page_number', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 0},

            {'inputKey_Str': 'items_per_page', 'inputType_ClassName': 'int', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 50},

            #{'inputKey_Str': 'object_type', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

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

            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        is_Pass_Biz_Validation = True
        validation_error_message = ""

        session_info = processed_RequestParams['session_info']
        page_number = processed_RequestParams['page_number']
        items_per_page = processed_RequestParams['items_per_page']

        current_user__has_permissions = False
        try:
            current_user__is_admin = views.is_this_an_admin_user(session_info=session_info)
            if (current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            # print("We hit the except block.. Lets find out what went wrong..")
            pass
        if (current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to get database objects.  "

        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Grab the requested object
            try:
                retList = []

                # Setup the filter params
                qFilter_Params = {}
                # TODO - Figure out what the filters for this query are.
                #if (endpoint_name != ''):
                #    qFilter_Params['endpoint'] = endpoint_name

                print("admin_get_server_logs: TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc")
                print("admin_get_server_logs: TODO: Finish the ServerLogs model and all that")
                print("admin_get_server_logs: TODO: Figure out what 'special' queries are needed - like some kind of filtering, etc")
                # TODO - add Custom Params (For Custom Filtering - Example: Return only 'errors', etc
                # # TODO: Finish the ServerLogs model and all that
                #db_objects = Server_Log.objects.filter(**qFilter_Params).order_by('-created_at')[(items_per_page * page_number):(items_per_page * page_number) + items_per_page] #.all()
                #for db_object in db_objects:
                #    retList.append(db_object.to_JSONable_Object())

                # TODO - Uncomment this line once we have a working model
                # Get the total objects count for this query.
                #total_db_objects_count_for_query = Server_Log.objects.filter(**qFilter_Params).count()
                total_db_objects_count_for_query = 0

                # Get the success response data
                response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
                response_data['PLACEHOLDER'] = str("TODO_FINISH_THIS_FUNCTION_ON_THE_SERVER").strip()
                response_data['items_per_page'] = str(items_per_page).strip()
                response_data['page_number'] = str(page_number).strip()
                response_data['objects_type'] = str("Server_Log").strip()
                response_data['objects_count'] = str(len(retList)).strip()
                response_data['objects_list'] = retList
                response_data['total_db_objects_count_for_query'] = total_db_objects_count_for_query # str(len(total_db_objects_count_for_query)).strip()  # how many total objects exist in the database for this query.
            except:
                # Uncaught Generic Error - Prep the response
                sys_error_info = sys.exc_info()
                human_readable_error = "An Error Occurred when trying to get a list of Server Logs from the database."
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

                # Report the API Error to the server for tracking and feedback
                # additional_request_data_py_obj['extra_information'] = "none"
                # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()




    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

    # Return the Response
    response_data_COPY = dict(response_data)
    response_data_COPY['objects_list'] = ["Objects_Removed_For_Logging"]
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
    return JsonResponse(response_data)




# admin_get_stats_for_type
# # admin_get_stats_for_type // Types are: "APILog", "ETLLog", "ServerLog", "ETLGranule"  // And maybe others in the future
# url(r'admin_get_stats_for_type/',  views_Admin_Generic.admin_get_stats_for_type,  name='admin_get_stats_for_type'),      # # /api_v2/admin_get_stats_for_type  //
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_stats_for_type(request):
    response_data = {}
    api_function_name = "admin_get_stats_for_type"
    api_function_code = "A2AGSFT"
    additional_request_data_py_obj = {}
    try:
        print("admin_get_stats_for_type: TODO - WRITE THIS FUNCTION - THIS IS FOR ALL THE TYPES - IT IS ALSO DEPENDENT ON MODEL FUNCTIONS - EACH MODEL NEEDS IT'S OWN STATS FUNCTIONS")
        print("admin_get_stats_for_type: TODO - WRITE THIS FUNCTION - THIS IS FOR ALL THE TYPES - IT IS ALSO DEPENDENT ON MODEL FUNCTIONS - EACH MODEL NEEDS IT'S OWN STATS FUNCTIONS")
        print("admin_get_stats_for_type: TODO - WRITE THIS FUNCTION - THIS IS FOR ALL THE TYPES - IT IS ALSO DEPENDENT ON MODEL FUNCTIONS - EACH MODEL NEEDS IT'S OWN STATS FUNCTIONS")
        print("admin_get_stats_for_type: TODO - WRITE THIS FUNCTION - THIS IS FOR ALL THE TYPES - IT IS ALSO DEPENDENT ON MODEL FUNCTIONS - EACH MODEL NEEDS IT'S OWN STATS FUNCTIONS")
        pass
    except:
        pass
    # Return the Response
    response_data_COPY = dict(response_data)
    response_data_COPY['objects_list'] = ["Objects_Removed_For_Logging"]
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)




# admin_get_dashboard_data
# # admin_get_dashboard_data
# url(r'admin_get_dashboard_data/',  views_Admin_Generic.admin_get_dashboard_data,  name='admin_get_dashboard_data'),      # # /api_v2/admin_get_dashboard_data  //
@csrf_exempt  # POST REQUESTS ONLY
def admin_get_dashboard_data(request):
    response_data = {}
    api_function_name = "admin_get_dashboard_data"
    api_function_code = "A2AGDD"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        # views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [

            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'time_enum', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': 'ALL'},

            # {'inputKey_Str': 'limit_by_data_type', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

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

            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = "Validation Error Occurred: " + str(validationErrorMessages)
            additional_request_data_py_obj['errorData'] = str(validationSysErrorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)
            return JsonResponse(response_data)

        # API Function Biz Logic here
        is_Pass_Biz_Validation = True
        validation_error_message = ""

        session_info        = processed_RequestParams['session_info']
        time_enum           = processed_RequestParams['time_enum']              # Possible values: // THE_LAST_7_DAYS, THE_LAST_30_DAYS, ALL

        earliest_datetime = datetime(year=2000, month=1, day=1)  # datetime.datetime.utcnow()
        if(time_enum != "ALL"):
            earliest_datetime = convert_time_enum_to_time_delta(time_enum)

        #print("time_enum: " + str(time_enum))
        #print("time_filter: " + str(earliest_datetime))



        #limit_by_data_type  = processed_RequestParams['limit_by_data_type']


        current_user__has_permissions = False
        try:
            current_user__is_admin = views.is_this_an_admin_user(session_info=session_info)
            if (current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            # print("We hit the except block.. Lets find out what went wrong..")
            pass
        if (current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to get database objects.  "

        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Grab the requested object
            try:
                dashboard_data = {}

                dashboard_data['API_Log'] = API_Log.get_stats(earliest_datetime=earliest_datetime)
                dashboard_data['ETL_Log'] = ETL_Log.get_stats(earliest_datetime=earliest_datetime)
                dashboard_data['ETL_Granule'] = "TODO Add get_stats() function to ETL Granule"
                dashboard_data['Server_Log'] = "TODO Add get_stats() function to Server Log"

                # Get the success response data
                response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
                response_data['dashboard_data'] = dashboard_data
            except:
                # Uncaught Generic Error - Prep the response
                sys_error_info = sys.exc_info()
                human_readable_error = "An Error Occurred when trying to get a list of Server Logs from the database."
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

                # Report the API Error to the server for tracking and feedback
                # additional_request_data_py_obj['extra_information'] = "none"
                # views.report_API_Error(api_function_name=api_function_name, api_function_code=api_function_code, human_readable_error=human_readable_error, sys_error_info=sys_error_info, additional_request_data_py_obj=additional_request_data_py_obj)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
        #get_stats
        pass
    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

    # Return the Response
    response_data_COPY = dict(response_data)
    response_data_COPY['dashboard_data'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)





