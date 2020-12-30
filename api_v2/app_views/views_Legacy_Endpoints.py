# TODO - Support views_Legacy_Endpoints.py

# Note: At the time of creating this file, These are called directly from the root URLs object

# views_ManageUsers.py

# Came with Django
from django.shortcuts import render

# Needed for normal Views-API app Operations
from django.http import HttpResponse
from django.http import JsonResponse    # For returning JSON
from django.views.decorators.csrf import csrf_exempt        # For the @csrf_exempt lines

from django.conf import settings
from api_v2.app_models.model_Config_Setting import Config_Setting
from api_v2.app_models.model_Task_Log import Task_Log

# Can't seem to call these from inside of django..
#from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf as SelectFromNetCDF
#import api_v2.processing_objects.select_data.select_from_netcdf


# For getting session info
from django.contrib.sessions.models import Session

from api_v2 import views

from django.db.models import Q

import sys
import json
from wsgiref.util import FileWrapper
from django.http import FileResponse        # response = FileResponse(open('myfile.png', 'rb'))



# Custom stuff
from common_utils import utils as common_utils
from common_utils import views as common_views_utils


#from django.contrib.auth import authenticate
# 'APILog', 'AvailableGranule', 'ETLDataset', 'ETLGranule', 'ETLLog', 'ETLPipelineRun', 'User'
from api_v2.app_models.model_API_Log            import API_Log



import zmq



# API TOKEN SUPPORT

# Token List (HardCoded for now, Move this to params very soon)
scriptAccess_Tokens = [
    {'isActive': True, 'token': '95ccb7bd40264379acb64aa229e41e19_ks', 'id': '0', 'name': 'Kris_TestToken_1',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': False, 'token': '23bd3de81db74be78325ab846d06e6bf_ks', 'id': '1', 'name': 'Kris_TestToken_2',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': 'ed2f3a1c82b04d0a961fba1ceedf0abc_as', 'id': '2',
     'name': 'Ashutosh_EarlyRelease_Token_1', 'contactEmail': 'ashutosh.limaye@nasa.gov'},
    {'isActive': True, 'token': 'b64e1306fa2e4ffcb1ee16c9b6155dad_as', 'id': '3',
     'name': 'Ashutosh_EarlyRelease_Token_2', 'contactEmail': 'ashutosh.limaye@nasa.gov'},
    {'isActive': True, 'token': '1dd4d855e8b64a35b65b4841dcdbaa8b_as', 'id': '7',
     'name': 'Ashutosh_EarlyRelease_Token_3', 'contactEmail': 'ashutosh.limaye@nasa.gov'},
    {'isActive': True, 'token': '9c4b7ae9ffe04e42873a808d726f7b55_as', 'id': '8',
     'name': 'Ashutosh_EarlyRelease_Token_4', 'contactEmail': 'ashutosh.limaye@nasa.gov'},
    {'isActive': True, 'token': 'f01e9e812068433cba2ecc6eadf15dba_af', 'id': '9', 'name': 'Africa_EarlyRelease_Token_1',
     'contactEmail': 'africaixmucane.florescordova@nasa.gov'},
    {'isActive': True, 'token': '15323f888b994ac49c1678c3e1e5e3a2_ic', 'id': '4', 'name': 'ICIMOD_Token_1',
     'contactEmail': 'eric.anderson@nasa.gov'},
    {'isActive': True, 'token': 'beca5860f93f476d96da764920eec546_rc', 'id': '5', 'name': 'RCMRD_Token_1',
     'contactEmail': 'africaixmucane.florescordova@nasa.gov'},
    {'isActive': True, 'token': '6daa6bbc95ff406f9eb40de3c35f565a_rc', 'id': '11', 'name': 'RCMRD_Token_2_JamesWanjohi',
     'contactEmail': 'jwanjohi@rcmrd.org'},
    {'isActive': True, 'token': '1c3f209dc5e64dcc8b7415ecce6f8355_ad', 'id': '6', 'name': 'ADPC_Token_1',
     'contactEmail': 'bill.crosson@nasa.gov'},
    {'isActive': True, 'token': '83e9be7ddbdf415b8032479f34777281_ad', 'id': '10', 'name': 'ADPC_Token_2',
     'contactEmail': 'bill.crosson@nasa.gov'},
    {'isActive': True, 'token': '9065934583cd45a1af90252761ab8d0e_pc', 'id': '12', 'name': 'Pat_Cappelaere',
     'contactEmail': 'pat@cappelaere.com'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '13', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '14', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '15', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '16', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '17', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '18', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'},
    {'isActive': True, 'token': '6a36175d28a74c34b5497ff218f80171_UU', 'id': '19', 'name': 'UNUSED_NAME',
     'contactEmail': 'kris.stanton@nasa.gov'}

]

# Check submitted token against list to see if it is valid.  If it is valid, return the key ID, if not, return an error message.
# Refactor: Updated the returns to always be:
# # # return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
def isTokenValid(token_ToCheck):
    ret_is_Token_Valid = False
    ret_Token_ID = -1
    ret_error_message = ""
    ret_sys_error_data = ""
    try:
        the_ScriptAccess_Tokens = scriptAccess_Tokens  # Replace this with a datasource upon development of the db part of the token system.

        for currentToken in the_ScriptAccess_Tokens:
            currentToken_Value = currentToken['token']
            if currentToken_Value == token_ToCheck:
                # token passed in IS on the list, now only allow access if it is active
                if currentToken['isActive'] == True:
                    ret_is_Token_Valid  = True
                    ret_Token_ID        = currentToken['id']
                    return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
                    #return True, currentToken['id']
                else:
                    ret_is_Token_Valid  = False
                    ret_Token_ID        = currentToken['id']
                    ret_error_message   = "Access Denied: Key ( " + ret_Token_ID + " ) is not currently active."
                    return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
                    #errMsg = "Access Denied: Key ( " + currentToken['id'] + " ) is not currently active."
                    #return False, errMsg
            else:
                # Current Token did not match, check the next one..
                pass
        # If we made it this far, the key was not in the list
        ret_is_Token_Valid = False
        ret_error_message = "Access Denied: Invalid Key"
        return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
        #return False, "Access Denied: Invalid Key"
    except:
        e = sys.exc_info()[0]
        ret_is_Token_Valid = False
        ret_sys_error_data = "ERROR isTokenValid: There was an error trying to check the_ScriptAccess_Tokens.  System error message: " + str(e)
        #errorMsg = "ERROR isTokenValid: There was an error trying to check the_ScriptAccess_Tokens.  System error message: " + str(e)
        #logger.error(errorMsg)

    ret_error_message = "Access Denied: Unspecified reason"
    return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
    #return False, "Access Denied: Unspecified reason"



# Legacy function for trying to parse an int from a 'value'
def intTryParse(value):
    """Function to try to parse an int from a string.
         If the value is not convertible it returns the orignal string and False
        :param value: Value to be convertedfrom CHIRPS.utils.processtools import uutools as uutools
        :rtype: Return integer and boolean to indicate that it was or wasn't decoded properly.
    """
    try:
        return int(value), True
    except ValueError:
        return value, False




# Legacy method for sending data back to the client (JSON inside an HTTP Request)
# # Note: Only doing this inside of the scriptAccess function (All other functions will be ported to the new method).
# # # And the Subsequent functions which are called and depend on this process which ar:
# # # # getDataFromRequest
# # # # getFileForJobID
# # # # getDataRequestProgress
# # # # submitDataRequest
def processCallBack(request, output, contenttype):
    '''
    Creates the HTTP response loaded with the callback to allow javascript callback. Even for
    Non-same origin output
    :param request: Given request that formulated the intial response
    :param output: dictinoary that contains the response
    :param contenttype: output mime type
    :rtype: response wrapped in call back.
    '''

    # All requests get pumped through this function, so using it as the entry point of the logging all requests
    # Log the Request
    # dataThatWasLogged = set_LogRequest(request, get_client_ip(request))

    if request.method == 'POST':
        try:
            callback = request.POST["callback"]
            return HttpResponse(callback + "(" + output + ")", content_type=contenttype)
        except KeyError:
            return HttpResponse(output)

    if request.method == 'GET':
        try:
            callback = request.GET["callback"]
            return HttpResponse(callback + "(" + output + ")", content_type=contenttype)
        except KeyError:
            return HttpResponse(output)

# Serverside Script Access
# def scriptAccess_isValidate_Params(operationValue, datasetValue, intevalTypeValue):
def scriptAccess_isValidate_Params(request):
    # (request.GET['datatype'], request.GET['operationtype'], request.GET['intervaltype'])
    isValidated = True
    try:
        operationValue = request.GET['operationtype']
        # Dataset Value (datatype) has changed
        #datasetValue = request.GET['datatype']
        # Deprecating Intervaltype
        #intevalTypeValue = request.GET['intervaltype']

        operation_Int = int(operationValue)
        # Dataset Value (datatype) has changed
        #dataset_Int = int(datasetValue)
        # Deprecating Intervaltype
        #intervalType_Int = int(intevalTypeValue)

        # Rule: operationValue must be one of these ints  0,1,5,6
        if not ((operation_Int == 0) or (operation_Int == 1) or (operation_Int == 5) or (operation_Int == 6)):
            isValidated = False

        ## Rule: if download operation value is submitted (6), than datatypes must be between 6 and 25 (including 6 and 25)
        #if (operation_Int == 6):
        #    if not (6 <= dataset_Int <= 25):
        #        isValidated = False

        # Dataset Value (datatype) has changed
        ## Rule: DatasetValue must be valid (until we have the system wide capabilities setup going, we have to hardcode this list in here)
        #if not ((dataset_Int == 0) or (dataset_Int == 1) or (6 <= dataset_Int <= 26)):
        #    isValidated = False

        # Deprecating Intervaltype
        ## Rule: Intervaltype must be 0 (daily or (pentadal for eMODIS))
        #if not (intervalType_Int == 0):
        #    isValidated = False

    except:
        # Something went wrong, most likely a parameter failed conversion... default to False
        isValidated = False

    return isValidated




# TODO: Define what is needed for this function and then implement it.
# # Note: The old script access functions let users input their operation type, data type and interval type with very simple inputs.  These inputs were encoded to the last version of ClimateSERV's non-dynamic info (HardCoded).  This function may be necessary in order to get the necessary info back to the functions that need to know about these things.  Perhaps some kind of simple data mapping can be done here to link legacy dataset types to current datasets in the database.  The same could be done for intervals and operations which would likely be defined in the application settings.
def translate_scriptAccess_Params():
    pass






# admin_doc
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def admin_doc(request):
    response_data = {}
    api_function_name = "admin_doc"
    api_function_code = "A2AD"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)










# pydash
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def pydash(request):
    response_data = {}
    api_function_name = "pydash"
    api_function_code = "A2PD"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)









# metrics
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def metrics(request):
    response_data = {}
    api_function_name = "metrics"
    api_function_code = "A2M"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)









# getParameterTypes
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getParameterTypes(request):
    response_data = {}
    api_function_name = "getParameterTypes"
    api_function_code = "A2GPT"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)










# getRequiredElements
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getRequiredElements(request):
    response_data = {}
    api_function_name = "getRequiredElements"
    api_function_code = "A2GRE"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)




















# getFeatureLayers
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getFeatureLayers(request):
    response_data = {}
    api_function_name = "getFeatureLayers"
    api_function_code = "A2GFL"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)












# getCapabilitiesForDataset
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getCapabilitiesForDataset(request):
    response_data = {}
    api_function_name = "getCapabilitiesForDataset"
    api_function_code = "A2GCFD"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)












# getClimateScenarioInfo
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getClimateScenarioInfo(request):
    response_data = {}
    api_function_name = "getClimateScenarioInfo"
    api_function_code = "A2GCSI"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)










# getRequestLogs
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def getRequestLogs(request):
    response_data = {}
    api_function_name = "getRequestLogs"
    api_function_code = "A2GRL"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)







# submitMonthlyGEFSRainfallAnalysisRequest
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def submitMonthlyGEFSRainfallAnalysisRequest(request):
    response_data = {}
    api_function_name = "submitMonthlyGEFSRainfallAnalysisRequest"
    api_function_code = "A2SMGRAR"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)











# submitMonthlyRainfallAnalysisRequest
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def submitMonthlyRainfallAnalysisRequest(request):
    response_data = {}
    api_function_name = "submitMonthlyRainfallAnalysisRequest"
    api_function_code = "A2SMRAR"
    additional_request_data_py_obj = {}
    try:
        response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
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
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)















# getDataRequestProgress
# DESCRIPTION
# URL_LINE
# # USES SCRIPT ACCESS
@csrf_exempt  # POST REQUESTS ONLY
def getDataRequestProgress(request):
    response_data = {}
    api_function_name = "getDataRequestProgress"
    api_function_code = "A2GDRP"
    additional_request_data_py_obj = {}
    try:
        request_method = request.method

        id = None
        # operationtype (Required)
        try:
            if (request_method == 'POST'):
                id = str(request.POST["id"])
            elif (request_method == 'GET'):
                id = str(request.GET["id"])
            if (id == None):
                raise Exception("Unable to read from request params.  id is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'id'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")


        # Look up the Task ID
        job_progress = Task_Log.get_job_progress(job_uuid=str(id))
        response_data['job_progress'] = str(job_progress)

        # Return the response
        response_data_COPY = dict(response_data)
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        return processCallBack(request, json.dumps([job_progress]), "application/json")

        #response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"

        # # Legacy Style SUCCESS return was like this.
        # # Return the Response
        # response_data_COPY = dict(response_data)
        # # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        # new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        # # return JsonResponse(response_data)
        # # Normal response
        # # return JsonResponse(response_data)
        # #
        # # return processCallBack(request, json.dumps([uniqueid]), "application/json")
        # return processCallBack(request, json.dumps([job_uuid]), "application/json")


    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
        #
        response_data_COPY = dict(response_data)
        # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        #
        # Legacy Style ERROR return was like this.
        return processCallBack(request, json.dumps(human_readable_error), "application/json")

    # # Return the Response
    # response_data_COPY = dict(response_data)
    # # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    # new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    # return JsonResponse(response_data)


    # Return the Response
    response_data_COPY = dict(response_data)
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    # return JsonResponse(response_data)
    # Normal response
    #return JsonResponse(response_data)
    return processCallBack(request, json.dumps([-1.0]), "application/json")












# getDataFromRequest
# DESCRIPTION
# URL_LINE
# # USES SCRIPT ACCESS
@csrf_exempt  # POST REQUESTS ONLY
def getDataFromRequest(request):
    response_data = {}
    api_function_name = "getDataFromRequest"
    api_function_code = "A2GDFR"
    additional_request_data_py_obj = {}
    try:
        request_method = request.method

        id = None
        # operationtype (Required)
        try:
            if (request_method == 'POST'):
                id = str(request.POST["id"])
            elif (request_method == 'GET'):
                id = str(request.GET["id"])
            if (id == None):
                raise Exception("Unable to read from request params.  id is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'id'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")

        # Look up the Task ID
        job_data = Task_Log.get_job_data(job_uuid=str(id))
        response_data['job_data'] = str(job_data)

        # Return the response
        response_data_COPY = dict(response_data)
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        return processCallBack(request, json.dumps(job_data), "application/json")

    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
        #
        response_data_COPY = dict(response_data)
        # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        #
        # Legacy Style ERROR return was like this.
        return processCallBack(request, json.dumps(human_readable_error), "application/json")

    # Return the Response
    response_data_COPY = dict(response_data)
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    #return JsonResponse(response_data)
    return processCallBack(request, json.dumps({}), "application/json")












# getFileForJobID
# DESCRIPTION
# URL_LINE
# # USES SCRIPT ACCESS
@csrf_exempt  # POST REQUESTS ONLY
def getFileForJobID(request):
    response_data = {}
    api_function_name = "getFileForJobID"
    api_function_code = "A2GFFJI"
    additional_request_data_py_obj = {}
    try:
        #response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
        #pass
        request_method = request.method

        id = None
        # operationtype (Required)
        try:
            if (request_method == 'POST'):
                id = str(request.POST["id"])
            elif (request_method == 'GET'):
                id = str(request.GET["id"])
            if (id == None):
                raise Exception("Unable to read from request params.  id is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'id'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")

        # Look up the Task ID
        job_progress = Task_Log.get_job_progress(job_uuid=str(id))
        response_data['job_progress'] = str(job_progress)

        if(job_progress != 100):
            sys_error_info = "The User called getFileForJobID for a job which has not finished processing."
            human_readable_error = "Job: " + str(id) + " is not finished processing.  Current progress is at: " + str(job_progress) + ".  Please try again shortly."
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")
        else:

            # Do the file sending stuff here. (to get the zip file)
            # Settings for sending the file
            #expectedFileLocation = "TODO_expectedFileLocation"
            #expectedFileName = "TODO_expectedFileName"
            expectedFileLocation, expectedFileName = Task_Log.get_job_file_info(job_uuid=str(id))
            print("About to send file: expectedFileLocation: " + str(expectedFileLocation))
            print("About to send file: expectedFileName: " + str(expectedFileName))

            # Trying it
            response = FileResponse(open(expectedFileLocation, 'rb'))
            response['Content-Disposition'] = 'attachment; filename=' + str(expectedFileName)  # filename=myfile.zip'

            # The return is down below (so we can log this file download)
            #return response


            # The Old way (Which breaks with this error:        sys_error_info: (<class 'UnicodeDecodeError'>, UnicodeDecodeError('utf-8', b'PK\x03\  ... etc )  )
            # # Sending the file
            # theFileToSend = open(expectedFileLocation)
            # theFileWrapper = FileWrapper(theFileToSend)
            # response = HttpResponse(theFileWrapper, content_type='application/zip')
            # response['Content-Disposition'] = 'attachment; filename=' + str(expectedFileName)  # filename=myfile.zip'

            # Load up this response_data object for logging
            response_data['expectedFileName'] = str(expectedFileName)
            # Return the response (Logging)
            response_data_COPY = dict(response_data)
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #return processCallBack(request, json.dumps([job_progress]), "application/json")

            # Log the data
            # dataThatWasLogged = set_LogRequest(request, get_client_ip(request))

            # Actually sends the file
            return response

            # # Return the response
            # response_data_COPY = dict(response_data)
            # new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            # return processCallBack(request, json.dumps([job_progress]), "application/json")

    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
        #
        response_data_COPY = dict(response_data)
        # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        #
        # Legacy Style ERROR return was like this.
        print("DEBUGGING:  sys_error_info: " + str(sys_error_info))
        return processCallBack(request, json.dumps(human_readable_error), "application/json")

    # Return the Response
    response_data_COPY = dict(response_data)
    #response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    #return JsonResponse(response_data)
    return processCallBack(request, json.dumps({}), "application/json")











# TODO: functions to translate legacy datatypes, operationtypes, and intervaltypes



# submitDataRequest
# DESCRIPTION
# URL_LINE
@csrf_exempt  # MUST SUPPORT GET AND POST REQUESTS
def submitDataRequest(request):
    response_data = {}
    api_function_name = "submitDataRequest"
    api_function_code = "A2SDR"
    additional_request_data_py_obj = {}

    #print("DEBUG/REMINDER: In order to support legacy operations, we must return specific expected data inside of a jsonp with a callback.")
    #print("submitDataRequest: Started")
    try:


        request_method = request.method
        #print("DEBUG/TEST: request_method: " + str(request_method))

        # Hold on to Errors and return them.
        #error = []
        # Update: This part of the legacy code is Not needed - Error handling was updated in cserv2

        # Process inputs

        requester_ip_address = common_views_utils.get_client_ip(request)
        additional_request_data_py_obj['ip_address'] = str(requester_ip_address)
        #print("DEBUG/TEST: requester_ip_address: " + str(requester_ip_address))





        # Current Resolution to this problem:  Clientside must use JSON.stringify around the 'geometry' object, and on the serverside, we load the data with json.loads(request.POST['geometry'])
        #
        # # Figuring out the problem with request.POST['geometry'] with a json object sent (multivalue key dict error)
        # try:
        #     print("DEBUG: Solving django.utils.datastructures.MultiValueDictKeyError")
        #     dir_request_POST = dir(request.POST)
        #     print("DEBUG: dir_request_POST: " + str(dir_request_POST))
        #     request_POST_keys = request.POST.keys()
        #     print("DEBUG: request_POST_keys: " + str(request_POST_keys))
        #
        #     # I don't remember which input scheme the original client used (The question is, were we wrapping the value of the parameter geometry into a JSON string, or just sending it as a JSON object).
        #     # # Either of these can be supported - Chrome tools show a value that looks like it is NOT stringified, so going with support for that one first.
        #     #
        #     # UPDATE: Having problems with this, going to go with clientside doing JSON.stringify and Serverside doing json.loads()
        #     # # https://stackoverflow.com/questions/17201075/how-to-parse-a-nested-json-ajax-object-in-django-views/34579736
        #
        #
        #     # When we wrap the value of 'geometry' inside JSON.stringify we get this:
        #     # # # DEBUG: request_POST_keys: dict_keys(['operationtype', 'datatype', 'begintime', 'endtime', 'geometry'])
        #     # # # NOTE: Doing it this way, requires json.loads(request.POST['geometry']) in order to get at the actual values
        #
        #
        #     # WITHOUT wrapping the value of 'geometry' inside JSON.stringify we get this:
        #     # # DEBUG: request_POST_keys: dict_keys(['operationtype', 'datatype', 'begintime', 'endtime', 'geometry[type]', 'geometry[coordinates][0][0][]', 'geometry[coordinates][0][1][]', 'geometry[coordinates][0][2][]', 'geometry[coordinates][0][3][]', 'geometry[coordinates][0][4][]'])
        #
        #     # When examining the WITHOUT Wrapping
        #     #request_POST_geometry = request.POST['geometry'] # GIVES ERROR:     DEBUG:  sys_error_info: (<class 'django.utils.datastructures.MultiValueDictKeyError'>, MultiValueDictKeyError('geometry'), <traceback object at 0x10f78f9c8>)
        #     #print("DEBUG: request_POST_geometry: " + str(request_POST_geometry))
        #
        #     request_POST_geometry_type = request.POST['geometry[type]']
        #     print("DEBUG: request_POST_geometry_type: " + str(request_POST_geometry_type))
        #     #request_POST_geometry_coordinates = request.POST['geometry[coordinates]'] # GIVES ERROR:   DEBUG:  sys_error_info: (<class 'django.utils.datastructures.MultiValueDictKeyError'>, MultiValueDictKeyError('geometry[coordinates]'), <traceback object at 0x111bb91c8>)
        #     #print("DEBUG: request_POST_geometry_type: " + str(request_POST_geometry_type))
        #     request_POST_geometry_coordinates = request.POST.get('geometry[coordinates]')
        #     print("DEBUG: request_POST_geometry_type: " + str(request_POST_geometry_coordinates))  # PRINTS:    # DEBUG: request_POST_geometry_type: None
        #
        # except:
        #     sys_error_info = sys.exc_info()
        #     print("DEBUG: Solving django.utils.datastructures.MultiValueDictKeyError: ERROR")
        #     print("DEBUG:  sys_error_info: " + str(sys_error_info))
        #



        # Process Params
        #
        #
        # Required PArams
        operationtype   = None # str(5) # Default set to 'mean'  # str(6)  #str(5)                # Operation Guide, (0 == max, 1 == min, 5 == mean, 6 == download)
        datatype        = None # str(2)  # str(99) # str(2)      # str(2) == ndvi east africa
        begintime       = None # Earliest Date # Example: # 01/01/2020
        endtime         = None # Latest Date # Example: # 03/01/2020
        #
        # Geo Inputs
        geometry        = None
        #
        # Checking for features further downstream
        has_featureList = False # (featureList) Flag to determine if we have a list of features
        layerid         = None  # (Optional) Only applies when shapefiles used
        featureids      = []    # Array to hold list of feature ids



        # # DEBUG - Why isn't 'geometry' coming through
        # # UPDATE: Result, Clientside MUST do json.stringify on the 'geometry' object and serverside MUST do json.loads()  # Example: # geometry_TEST = json.loads(request.POST["geometry"])
        # try:
        #     print("")
        #     print("DEBUG - Why isn't 'geometry' coming through.")
        #     print("  request.POST['geometry']: " + str(request.POST["geometry"]))
        #     print("  request.POST['geometry']: " + str(request.POST.get("geometry") ) ) #request.GET.get('number')
        #
        #     # More Tests
        #     #geometry_TEST = request.POST["geometry"]
        #     geometry_TEST = json.loads(request.POST["geometry"])
        #     print("geometry_TEST: " + str(geometry_TEST))
        #     print("geometry_TEST['coordinates']: " + str(geometry_TEST['coordinates']))
        #     #geometry = request.POST["geometry"]
        # except:
        #     sys_error_info = sys.exc_info()
        #     print("Geometry input Debug: sys_error_info: " + str(sys_error_info))



        # operationtype (Required)
        try:
            if (request_method == 'POST'):
                operationtype   = str(int(request.POST["operationtype"]))
            elif (request_method == 'GET'):
                operationtype   = str(int(request.GET["operationtype"]))
            if(operationtype == None):
                raise Exception("Unable to read from request params.  operationtype is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'operationtype'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")


        # datatype (Required)
        try:
            if (request_method == 'POST'):
                datatype = str(int(request.POST["datatype"]))
            elif (request_method == 'GET'):
                datatype = str(int(request.GET["datatype"]))
            if (datatype == None):
                raise Exception("Unable to read from request params.  datatype is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'datatype'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")


        # begintime (Required)
        try:
            if (request_method == 'POST'):
                begintime = str(request.POST["begintime"])
            elif (request_method == 'GET'):
                begintime = str(request.GET["begintime"])
            if (begintime == None):
                raise Exception("Unable to read from request params.  begintime is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'begintime'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")


        # endtime
        try:
            if (request_method == 'POST'):
                endtime = str(request.POST["endtime"])
            elif (request_method == 'GET'):
                endtime = str(request.GET["endtime"])
            if (endtime == None):
                raise Exception("Unable to read from request params.  endtime is still set to None.")
        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing required input parameter 'endtime'"
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")


        # GeoInput - At least one of these is Required
        geoInput_Type = "UNSET" # Supported types, "layerid_and_featureids", and "geometry"
        has_GeoInput = False
        geoInput_Warning = ""

        # Try to parse Layerid and Feature ids
        try:
            if (request_method == 'POST'):
                layerid = str(request.POST["layerid"])
                fids = str(request.POST["featureids"]).split(',')
                featureids = []
                for fid in fids:
                    value, isInt = intTryParse(fid)
                    if (isInt == True):
                        featureids.append(value)
                #has_featureList = True
                ##Go get geometry
                #logger.debug("submitDataRequest: Loaded feature ids, featureids: " + str(featureids))
                has_GeoInput = True
                geoInput_Type = "layerid_and_featureids"

            elif (request_method == 'GET'):
                layerid = str(request.GET["layerid"])
                fids = str(request.GET["featureids"]).split(',')
                featureids = []
                for fid in fids:
                    value, isInt = intTryParse(fid)
                    if (isInt == True):
                        featureids.append(value)
                # has_featureList = True
                ##Go get geometry
                #logger.debug("submitDataRequest: Loaded feature ids, featureids: " + str(featureids))
                has_GeoInput = True
                geoInput_Type = "layerid_and_featureids"
        except:
            # Failed to process layerid, no problem, unless the geometry parsing also fails.
            sys_error_info = sys.exc_info()
            geoInput_Warning = geoInput_Warning + " There was a warning when trying to parse geo input for 'layerid' and 'featureids'.  System message: " + str(sys_error_info)


        # Try to parse Geometry into polygonstring
        try:
            if (request_method == 'POST'):
                geometry = json.loads(request.POST["geometry"])
                #geometry = request.POST["geometry"]
                #print("GEOMETRY: " + str(geometry))
                #polygonstring = request.POST["geometry"]
                #geometry = decodeGeoJSON(polygonstring)

            elif (request_method == 'GET'):
                geometry = json.loads(request.GET["geometry"])
                #geometry = request.GET["geometry"]
                #polygonstring = request.GET["geometry"]
                #geometry = decodeGeoJSON(polygonstring)
            if geometry is None:
                geoInput_Warning = geoInput_Warning + " There was a warning when trying to parse geo input for 'geometry'.  Geometry was still None"
            else:
                has_GeoInput = True
                geoInput_Type = "geometry"
        except:
            # Failed to process 'geometry', no problem, unless the layerid and featureids parsing also failed.
            sys_error_info = sys.exc_info()
            geoInput_Warning = geoInput_Warning + " There was a warning when trying to parse geo input for 'geometry'.  System message: " + str(sys_error_info)

        if(has_GeoInput == False):
            # Must have one of these two sets of params.  Either 'geometry' by itself which can be parsed into a closed polygon or the two params 'layerid' and 'featureids'
            sys_error_info = "Failed to parse either of the two supported GeoInput types (geometry or the pair of layerid and featureids.  Warnings Collected when attempting to parse the geo inputs: " + str(geoInput_Warning) #sys_error_info = sys.exc_info()
            human_readable_error = "There was a problem processing the geoinputs.  You must have at least one of these two sets of parameters.  Either 'geometry' by itself which can be parsed into a closed polygon or the two params 'layerid' and 'featureids'."
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")



        # Proceed as normal - Setup the job, etc
        # Make a new Job ID
        job_uuid = Task_Log.make_new_job_uuid()
        # job_uuid = "25211111" + job_uuid[8:]  # For testing

        # Make the dictionary and submit the New Task Log here.
        dictionary = {}
        try:

            # # ORIGINAL
            #dictionary = {'uniqueid': uniqueid, 'datatype': datatype, 'begintime': begintime, 'endtime': endtime, 'intervaltype': intervaltype, 'operationtype': operationtype}
            dictionary['job_uuid'] = str(job_uuid).strip()  # CSERV 2 Property Name for the job/task uuid
            dictionary['uniqueid'] = str(job_uuid).strip()  # Legacy Property Name for the job uuid
            dictionary['datatype'] = str(datatype).strip()
            dictionary['operationtype'] = str(operationtype).strip()
            dictionary['begintime'] = str(begintime).strip()
            dictionary['endtime'] = str(endtime).strip()
            dictionary['geoInput_Type'] = str(geoInput_Type).strip()
            # Deprecated # dictionary['intervaltype'] = str(intervaltype).strip()
            #
            # Check the GeoInput type and add the correct values
            # # Supported GeoInput Type:    "layerid_and_featureids" and "geometry"
            if (geoInput_Type == "layerid_and_featureids"):
                dictionary['layerid']       = layerid
                dictionary['featureids']    = featureids
            if (geoInput_Type == "geometry"):
                dictionary['geometry']  = geometry


            response_data['job_dictionary'] = dictionary
            response_data['job_uuid'] = str(job_uuid)

            # Create the Task Log now
            #print("DONE: Create Task Log now - with ip address")
            request_params = dictionary
            #
            print("DEBUG (Geometry is missing from dictionary): About to create Task Log with (request_params): " + str(request_params))
            #
            is_task_created, error_message = Task_Log.create_new_task(job_uuid=job_uuid, request_params=request_params, ip_address=str(requester_ip_address))
            #print("DONE: Check for Error when Creating Task Log")
            if(is_task_created == True):
                # Great, do nothing else, this means the Task_Log was created and the Job Processing core will take over and handle this job.
                pass
            else:
                # There was a problem.  This Task_Log was not created, so the job processing core will not pick up this job, send error back to the user.
                sys_error_info = "Failed to Create a Task_Log.  The cause of this could be database connection error or a different database / django related problem."
                human_readable_error = "There was a problem when submitting the Job to the Task_Log.  Unable to create Task_Log Entry for this job id.  This error has been logged in the system."
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
                additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
                additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
                #
                response_data_COPY = dict(response_data)
                # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
                #
                # Legacy Style ERROR return was like this.
                return processCallBack(request, json.dumps(human_readable_error), "application/json")




        except:
            sys_error_info = sys.exc_info()
            human_readable_error = "There was an unexpected problem when submitting the Job to the Task_Log.  This error has been logged in the system."
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
            #
            response_data_COPY = dict(response_data)
            # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
            #
            # Legacy Style ERROR return was like this.
            return processCallBack(request, json.dumps(human_readable_error), "application/json")



        # Legacy Style SUCCESS return was like this.
        # Return the Response
        response_data_COPY = dict(response_data)
        # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        # return JsonResponse(response_data)
        # Normal response
        #return JsonResponse(response_data)
        #
        #return processCallBack(request, json.dumps([uniqueid]), "application/json")
        return processCallBack(request, json.dumps([job_uuid]), "application/json")




        # ALL THIS STUFF BELOW WAS FOR TESTING AND BUILDING
        # ALL THIS STUFF BELOW WAS FOR TESTING AND BUILDING
        # ALL THIS STUFF BELOW WAS FOR TESTING AND BUILDING



        # # DEBUG / BUILDING - TESTING CLIENTSIDE SENDING
        # # Testing
        # # # $.post("http://127.0.0.1:8234/chirps/submitDataRequest/?callback=successCallback", { some_key:"some_value"}, function(data, status) { alert("Data: " + data + "\nStatus: " + status); });
        # #inputValue = str(requestData_PyObj[inputKey_Str]).strip()
        # #
        # #inputValue = str(request["some_key"]).strip()
        # #print("submitDataRequest: inputValue: " + str(inputValue))
        # #
        # inputValue = request.POST["some_key"] # int(request.POST["some_key"])     # str(request["some_key"]).strip()
        # print("submitDataRequest: inputValue: " + str(inputValue))
        #
        # # DEBUG / BUILDING - HARDCODED PARAMS
        #
        # # Legacy Only Datatypes
        # datatype                = str(2)
        # intervaltype            = str(0)
        # operationtype           = str(5)
        # dateType_Category       = "default"
        # # Current (and legacy) Datatypes
        # begintime               = "01/01/2020"
        # endtime                 = "03/01/2020"
        # callback                = "successCallback"
        # isZip_CurrentDataType   = "false" #false
        # geometry                = {"type": "Polygon", "coordinates": [[[29.922637939453143, 17.369644034060244], [34.924163818359375, 16.96026258715051], [35.37734985351563, 13.112917604124647], [29.672698974609382, 13.676678908553882], [29.922637939453143, 17.369644034060244]]]}
        #
        #
        # # Placeholder / Test Response Stuff # Remove me on cleanup
        # response_data['placeholder'] = "Function not yet supported in ClimateSERV 2.0"
        # response_data['debug_data__geometry'] = geometry
        # response_data['debug_data__isZip_CurrentDataType'] = isZip_CurrentDataType
        # response_data['debug_data__operationtype'] = operationtype
        # pass
        #
        #
        # # Problem here, I can't seem to get shapely or xarray to be recognized from inside of python django.
        # # # instead, going to use the database to store any tasks, and then pull in that data from a daemon process which monitors for unresolved tasks.
        # # # # Tasks can have different states, 'ready_for_processing', 'errored', 'inprogress', or 'completed'
        #
        #
        # # Test Select from NetCDF
        # #selectedData = SelectFromNetCDF.test_select_data__From_SubmitDataRequest_Call()
        # #response_data['selectedData'] = selectedData

    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)

        # Report the API Error to the server for tracking and feedback
        # additional_request_data_py_obj['extra_information'] = "none"
        additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
        additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()
        #
        response_data_COPY = dict(response_data)
        # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
        new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
        #
        # Legacy Style ERROR return was like this.
        return processCallBack(request, json.dumps(human_readable_error), "application/json")

    # Return the Response
    response_data_COPY = dict(response_data)
    # response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    # return JsonResponse(response_data)
    # Normal response
    #return JsonResponse(response_data)
    return processCallBack(request, json.dumps([]), "application/json")

    # JSONP wrapped in callback response
    #return processCallBack(request, json.dumps([uniqueid]), "application/json")
    #return JsonResponse(response_data)













# scriptAccess
# DESCRIPTION
# URL_LINE
@csrf_exempt  # POST REQUESTS ONLY
def scriptAccess(request):
    response_data = {}
    api_function_name = "scriptAccess"
    api_function_code = "A2SA"
    additional_request_data_py_obj = {}
    try:
        # TODO - Check and Support API Token System
        # # isKeyValid, keyCheckResponse = isTokenValid(script_API_AccessKey)

        logger__Legacy = ""
        # Legacy Code       START
        try:

            errorMsg = ""
            api_Key_ID = "NOT_SET"

            # Get the API Access Key and check to see if it is in the list AND Active
            try:
                script_API_AccessKey = str(request.GET['t'])
                # return ret_is_Token_Valid, ret_Token_ID, ret_error_message, ret_sys_error_data
                isKeyValid, token_ID, error_message, sys_error_data = isTokenValid(script_API_AccessKey)
                #isKeyValid, keyCheckResponse = isTokenValid(script_API_AccessKey)
                if isKeyValid == False:
                    #keyCheckErrorMessage = keyCheckResponse
                    keyCheckErrorMessage = error_message
                    errObj = {"errorMsg": keyCheckErrorMessage, "request": str(request.GET)}

                    # Catch Errors
                    response_data['Legacy_Object_Returned_To_User'] = json.dumps(errObj)
                    errorMessage    = keyCheckErrorMessage
                    errorData       = sys_error_data
                    #
                    response_data   = common_views_utils.get_Error_Response_JSON(errorMessage=errorMessage, errorCode=api_function_code, errorData=errorData)
                    response_data['Legacy_Object_Returned_To_User'] = json.dumps(errorMsg)
                    response_data['logger__Legacy'] = logger__Legacy
                    # Log the API Call
                    additional_request_data_py_obj['errorMessage'] = errorMessage
                    additional_request_data_py_obj['errorData'] = str(errorData).strip()
                    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)

                    # Legacy Support: Return what Script Clients are expecting
                    return processCallBack(request, json.dumps(errObj), "application/json")
                else:
                    # Key is valid, continue
                    #api_Key_ID = keyCheckResponse
                    api_Key_ID = token_ID
            except:
                errorMsg += "API Access Key Required"

                # Catch Errors
                response_data['Legacy_Object_Returned_To_User'] = json.dumps(errorMsg)
                errorMessage    = errorMsg
                errorData       = ""
                #
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=errorMessage, errorCode=api_function_code, errorData=errorData)
                response_data['Legacy_Object_Returned_To_User'] = json.dumps(errorMsg)
                response_data['logger__Legacy'] = logger__Legacy
                # Log the API Call
                additional_request_data_py_obj['errorMessage'] = errorMessage
                additional_request_data_py_obj['errorData'] = str(errorData).strip()
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)

                # Legacy Support: Return what Script Clients are expecting
                return processCallBack(request, json.dumps(errorMsg), "application/json")



            # Continue with Command Validation and then Params Validation here
            # Get the command, validate the params and execute it with those validated params
            script_Access_Command = str(request.GET['cmd'])
            logger__Legacy += "scriptAccess: script_Access_Command: " + script_Access_Command
            # Put this line before every report_API_Call_Event: # response_data['logger__Legacy'] = logger__Legacy
            #logger.debug("scriptAccess: script_Access_Command: " + script_Access_Command)

            if script_Access_Command == "getDataFromRequest":
                # CATCH API_LOG EVENT (Calling Sub Function)
                response_data_SubFunction = {"about_to_call":"scriptAccess: sub function getDataFromRequest"}
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_SubFunction)
                return getDataFromRequest(request)
            elif script_Access_Command == "getFileForJobID":
                # CATCH API_LOG EVENT (Calling Sub Function)
                response_data_SubFunction = {"about_to_call": "scriptAccess: sub function getFileForJobID"}
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_SubFunction)
                return getFileForJobID(request)
            elif script_Access_Command == "getDataRequestProgress":
                # CATCH API_LOG EVENT (Calling Sub Function)
                response_data_SubFunction = {"about_to_call": "scriptAccess: sub function getDataRequestProgress"}
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_SubFunction)
                return getDataRequestProgress(request)
            elif script_Access_Command == "submitDataRequest":
                # Geometry Validation.. already handled in other part of the script.
                # Params validation
                isValid = scriptAccess_isValidate_Params(request)  # (request.GET['datatype'], request.GET['operationtype'], request.GET['intervaltype'])
                if isValid == True:
                    # CATCH API_LOG EVENT (Calling Sub Function)
                    response_data_SubFunction = {"about_to_call": "scriptAccess: sub function submitDataRequest"}
                    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_SubFunction)
                    return submitDataRequest(request)
                else:
                    errorMsg += "Validation Error submitting new job.  Issue may be with params."

                    # Catch Errors
                    errorMessage = errorMsg
                    errorData = ""
                    #
                    response_data = common_views_utils.get_Error_Response_JSON(errorMessage=errorMessage, errorCode=api_function_code, errorData=errorData)
                    response_data['Legacy_Object_Returned_To_User'] = json.dumps(errorMsg)
                    response_data['logger__Legacy'] = logger__Legacy
                    # Log the API Call
                    additional_request_data_py_obj['errorMessage'] = errorMessage
                    additional_request_data_py_obj['errorData'] = str(errorData).strip()
                    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)

                    # Legacy Support: Return what Script Clients are expecting
                    return processCallBack(request, json.dumps(errorMsg), "application/json")
            # Duplicate?
            #elif script_Access_Command == "getDataFromRequest":
            #    return getDataFromRequest(request)
            else:
                errorMsg += "Command Not found"

                # Catch Errors
                errorMessage = errorMsg
                errorData = ""
                #
                response_data = common_views_utils.get_Error_Response_JSON(errorMessage=errorMessage, errorCode=api_function_code, errorData=errorData)
                response_data['Legacy_Object_Returned_To_User'] = json.dumps(errorMsg)
                response_data['logger__Legacy'] = logger__Legacy
                # Log the API Call
                additional_request_data_py_obj['errorMessage'] = errorMessage
                additional_request_data_py_obj['errorData'] = str(errorData).strip()
                new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)

                # Legacy Support: Return what Script Clients are expecting
                return processCallBack(request, json.dumps(errorMsg), "application/json")

        except:
            # Error message for the system
            e = sys.exc_info()[0]
            logger__Legacy += "Problem with scriptAccess: System Error Message: " + str(e)
            #logger.warn("Problem with scriptAccess: System Error Message: " + str(e))

            # Error message for the user
            errObj = {"errorMsg": "scriptAccess: Error Processing Request", "request": str(request.GET['QUERY_STRING'])}  # "request":str(request)}


            # Catch Errors
            errorMessage = errorMsg['errorMsg']
            errorData = "Problem with scriptAccess: System Error Message: " + str(e)
            #
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=errorMessage, errorCode=api_function_code, errorData=errorData)
            response_data['Legacy_Object_Returned_To_User'] = json.dumps(errObj)
            response_data['logger__Legacy'] = logger__Legacy
            # Log the API Call
            additional_request_data_py_obj['errorMessage'] = errorMessage
            additional_request_data_py_obj['errorData'] = str(errorData).strip()
            new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data)

            # Legacy Support: Return what Script Clients are expecting
            return processCallBack(request, json.dumps(errObj), "application/json")


            # A newer version of an error would go here and look like this.
            #
            #
            # # Uncaught Generic Error - Prep the response
            # sys_error_info = sys.exc_info()
            # human_readable_error = "Legacy Code Support Error.  Please try again shortly"
            # response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)
            #
            # # Report the API Error to the server for tracking and feedback
            # # additional_request_data_py_obj['extra_information'] = "none"
            # additional_request_data_py_obj['errorMessage'] = str(human_readable_error).strip()
            # additional_request_data_py_obj['errorData'] = str(sys_error_info).strip()

        # Legacy Code       END
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
    #response_data_COPY['key_to_remove'] = "Objects_Removed_For_Logging"
    new_API_Log_UUID = views.report_API_Call_Event(request_obj=request, api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj, server_response_json=response_data_COPY)
    return JsonResponse(response_data)







@csrf_exempt  # POST REQUESTS ONLY
def test_zmq(request):
    response_data = {}
    api_function_name = "test_zmq"
    api_function_code = "A2TZMQ"
    additional_request_data_py_obj = {}
    try:
        # Setup the Dictionary to send
        dictionary = {"placeholder":"test content for zmq here"}

        # Get the address of the Queue for ZMQ
        zmq_queue_address = Config_Setting.get_value(setting_name="ZMQ_LOCAL_QUEUE_ADDRESS", default_or_error_return_value="ipc:///tmp/servir/Q1/input") # ZMQ_LOCAL_QUEUE_ADDRESS' // 'ipc:///tmp/servir/Q1/input'

        # Create the ZMQ context and push the dictionary to the address
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.connect(zmq_queue_address)    #("ipc:///tmp/servir/Q1/input")
        sender.send_string(json.dumps(dictionary))

        response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
        response_data['dictionary'] = dictionary
        response_data['zmq_queue_address'] = zmq_queue_address

    except:
        # Uncaught Generic Error - Prep the response
        sys_error_info = sys.exc_info()
        human_readable_error = "An Unknown Error Occurred.  Please try again shortly"
        response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData=sys_error_info)


    return JsonResponse(response_data)








