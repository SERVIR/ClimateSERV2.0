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


import sys
import json

# Custom stuff
from common_utils import utils as common_utils
from common_utils import views as common_views_utils


from django.contrib.auth import authenticate

from api_v2.app_models.model_User import User as api_v2__user




# admin_create_user
# Signing User in - Process a signin request (requires a username and password)
# url(r'admin_create_user/',  views_Admin_ManageUsers.admin_create_user,  name='admin_create_user'),
@csrf_exempt  # POST REQUESTS ONLY
def admin_create_user(request):
    response_data = {}
    api_function_name = "admin_create_user"
    api_function_code = "A2ACU"
    additional_request_data_py_obj = {}
    try:
        # Gather filtered request here.
        filteredRequest = common_views_utils.filter_And_Validate_Request(request=request)
        theData_PyObj   = common_views_utils.extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest)

        # Report Incoming API Request
        additional_request_data_py_obj['raw_httpbody_POST_params'] = theData_PyObj
        #views.report_API_Call_Event(api_function_name=api_function_name, api_function_code=api_function_code, additional_request_data_py_obj=additional_request_data_py_obj)

        # Process Input Params
        paramsInfo = {}
        paramsInfo['items'] = [
            {'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'username', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'firstname', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'lastname', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'email', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'password', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            {'inputKey_Str': 'password_confirm', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},

            #{'inputKey_Str': 'session_info', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},


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
        username            = processed_RequestParams['username']
        firstname           = processed_RequestParams['firstname']
        lastname            = processed_RequestParams['lastname']
        email               = processed_RequestParams['email']
        password            = processed_RequestParams['password']
        password_confirm    = processed_RequestParams['password_confirm']

        # (1) Validate (Session ID has admin permission)
        cserv_user_info_obj, auth_user_info_obj = views.get_cserv_user_and_auth_user_from_Session(sid=session_info)
        created_by__username = auth_user_info_obj['username']
        print("(cserv_user_info_obj): " + str(cserv_user_info_obj))
        print("(auth_user_info_obj): " + str(auth_user_info_obj))

        current_user__has_permissions = False
        try:
            current_user__is_admin = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=cserv_user_info_obj['is_admin'], defaultBoolValue=False)
            if(current_user__is_admin == True):
                current_user__has_permissions = True
        except:
            pass
        if(current_user__has_permissions == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "You do not have permission to create a new user.  "

        # (2) Validate (username is unique (no record found with exact username)) - Do this for email also
        is_username_available = api_v2__user.auth_user__is_username_avalaible(input__username=username)
        if(is_username_available == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "Username, " + str(username) + " is not available.  Try a different username.  "

        is_email_available = api_v2__user.auth_user__is_email_avalaible(input__email=email)
        if (is_email_available == False):
            is_Pass_Biz_Validation = False
            validation_error_message += "Email, " + str(email) + " is not available.  Try a different email.  "


        # (3) Validate (password and password_confirm match)
        if(password != password_confirm):
            is_Pass_Biz_Validation = False
            validation_error_message += "Password and Confirm Password do not match.  They must be the same.  "


        # Catch Biz Validation errors and return to user here
        if (is_Pass_Biz_Validation == False):
            human_readable_error = validation_error_message
            response_data = common_views_utils.get_Error_Response_JSON(errorMessage=human_readable_error, errorCode=api_function_code, errorData="")
            response_data['validation_error_message'] = str(validation_error_message).strip()
        else:
            # Did Passed Biz Validation - Create the Users


            # (4) Create the Auth User (Setting all the props)
            new_auth_user_id = api_v2__user.auth_user__create_user(input__username=username, input__firstname=firstname, input__lastname=lastname, input__email=email, input__password=password)


            # (5) Create the API User, setting is_admin to true, return user's json - So clientside can say, 'user XYZ' has been created.
            # api_v2__user
            new__api_v2__user = api_v2__user()
            new__api_v2__user.is_admin = True
            new__api_v2__user.created_by = str(created_by__username).strip()
            new__api_v2__user.auth_id = str(new_auth_user_id).strip()
            new__api_v2__user.save()


            # Load up the new user info and send the response back to the client
            new_user_info = {}
            new_user_info['username'] = username
            new_user_info['email'] = email
            new_user_info['cserv_user_info'] = new__api_v2__user.to_JSONable_Object()

            # Get the success response data
            response_data = common_views_utils.get_Success_Response_JSON(original_request_data={})
            response_data['new_user_info'] = new_user_info


        #
        # TODO: (0) Validate that this user actually has the permissions to "Manage Users" (By checking their session info)
        # TODO: (1) Create an Auth User, (Setting all the props)
        # TODO: (2) Create a api_v2.User (Passing in the AuthUser's ID) --- This should be a new function on model_User called: create_new_user__ForAdminCreateUser(auth_user_id, created_by=This_Users_UUID):
        # TODO: (3) Return the new User's JSON info (So the clientside can say, 'user XYZ' has been created'





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
    return JsonResponse(response_data)