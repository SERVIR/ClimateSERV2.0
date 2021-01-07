


# Came with Django
from django.shortcuts import render

from common_utils import utils as common_utils
import json
import sys



# TODO: Check and see if the system for 'showing error data in dev but NOT in production' is functioning properly.  If it is, then remove this.
print("views_utils:: WARNING: SHOW_ERROR_DATA is set to True, this means that the API will return system level error information to any client that throws random stuff at it.  It is extremely useful during debugging but extremely risky during stage or production.")
SHOW_ERROR_DATA = True






# Filter and Validate entire request object.. not sure if django or python has an easy way of doing this but if it does, put that code in here.
# Called at the start of EVERY input received
def filter_And_Validate_Request(request):
    # Is there a way to safely filter EVERY incoming post request?? If so, do it here!
    #print("VERY IMPORTANT TODO: FILTER ENTIRE INCOMING REQUEST AND RETURN FILTERED REQUEST")
    return request




# #############################################
# # extract_raw_httpbody_POST_Request_To_PyObj(postRequest=filteredRequest) 	// RETURNS: 	theData_PyObj
# #############################################

# Standard way of converting the post requests with JSON in the raw body into a usable json object
# This also serves as a way to validate
def extract_raw_httpbody_POST_Request_To_PyObj(postRequest):
    theData = postRequest.body              # theData = postRequest.body.decode('utf-8')  # adding the .decode('utf-8')
    theData_PyObj = json.loads(theData)     # Because the data coming in is expected to be a JSON string already
    return theData_PyObj




# #############################################
# # get_Error_Response_JSON(errorMessage=authErrorMsg, errorCode=errorCode, errorData=authSysErrorMsg) 		// RETURNS:		response_data
# # get_Success_Response_JSON(original_request_data=original_request_data) 		                            // RETURNS: 	response_data
# #############################################

# Standard way of reporting errors back to the client device.
# errorMessage is the place for a message that is ok to send back to a client device
# errorCode is the way to tell developers where to find the part that broke in the code without giving away exploitable information about the system
# errorData is the way to add system information for trouble shooting complex issues (but should be disabled on the production machine)
def get_Error_Response_JSON(errorMessage, errorCode, errorData):
    retObj = {}
    retObj['result'] = "error"
    retObj['ErrorMessage'] = str(errorMessage)
    retObj['ErrorCode'] = str(errorCode)
    try:
        if SHOW_ERROR_DATA == True:
            print("views_utils::API.get_Error_Response_JSON: YET ANOTHER WARNING ABOUT 'SHOW_ERROR_DATA': About to load up system level Error Data into a response object.  If we are seeing this on production or Public Stage server, we have a problem and this should not be happening.  To fix this, look into how the variable 'SHOW_ERROR_DATA' or 'Settings.API_SHOW_ERROR_DATA' is being set and fix it!")
            retObj['ErrorData'] = str(errorData)  # Type/Context:   errorData, Usually comes from: sysErrorData = sys.exc_info()[0]
        else:
            retObj['ErrorData'] = ""
    except:
        retObj['ErrorData'] = ""
    return retObj

# Standard way of reporting success back to the client machine.
def get_Success_Response_JSON(original_request_data):
    retObj = {}
    retObj['result'] = "success"

    # When debug/show_error_data is turned on, we want / or need to see the original request data.
    try:
        if SHOW_ERROR_DATA == True:
            print("views_utils::API.get_Error_Response_JSON: YET ANOTHER WARNING ABOUT 'SHOW_ERROR_DATA': About to load up system level Error Data into a response object.  If we are seeing this on production or Public Stage server, we have a problem and this should not be happening.  To fix this, look into how the variable 'SHOW_ERROR_DATA' or 'Settings.API_SHOW_ERROR_DATA' is being set and fix it!")
            retObj['request_data'] = original_request_data # NOT JSON
        else:
            # Not appending the key means that it just won't exist in the output.  We really only want this key if the error data is turned on...
            #retObj['request_data'] = {}
            pass
    except:
        retObj['request_data'] = {}

    return retObj







# #############################################
# # validate_extract_process_requestParams(requestData_PyObj=theData_PyObj, paramsInfo=paramsInfo) 			// RETURNS:		processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData 		// paramsInfo example (Array of complex objects):	[   {'inputKey_Str': 'uuid', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'isValidate_JSONLoadsObj': 'False', 'defaultReturnValue': ''},		{'inputKey_Str': 'DataPackageJSONSTR',      'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True',  'isValidate_JSONLoadsObj': 'True',  'defaultReturnValue': '{}'} 		]
#
# # # And Companion dependent function
# # # # validate_and_extract_request_param__As_Type(requestData_PyObj, inputKey_Str, inputType_ClassName, isParamOptional, isValidate_ForNotEmpty, isValidate_JSONLoadsObj, defaultReturnValue=""): # isValidate_Required
# #############################################

# This is really just a custom validator mechanism.
def validate_extract_process_requestParams(requestData_PyObj, paramsInfo):

    # Example of the Return:
    # processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData = validate_extract_process_requestParams()

    # Example of the paramsInfo object
    #paramsInfo['items'] = [{'inputKey_Str': 'NewEntityName', 'inputType_ClassName': 'str', 'isParamOptional': 'False', 'isValidate_ForNotEmpty': 'True', 'defaultReturnValue': ''}]
    # # Array full of objects that get used for validation.
    # # # Note: the objects such as 'inputType_ClassName' and 'isParamOptional' are processed as strings (rather than bool or classname) for portability (in case we one day want to configure this by JSON - so this object is easily JSONable in it's current form.).
    # # # Note: The return object is each of the input_keys and their values..  and any error info associated with specific request params.


    # Default
    processed_RequestParams = {}
    #processed_RequestParams['results'] = {}#[]
    isValidationError = False
    validationErrorMessages = ""        # Only the most recent message goes back in this return value (details are in the object that gets returned)
    validationSysErrorData = ""         # Only the most recent message goes back in this return value (details are in the object that gets returned)

    # Does paramsInfo have a key called, 'items' (which is supposed to be an array of param info objects).
    if('items' in paramsInfo):

        # Yes, paramsInfo['items'] does exist.

        # Array that will be added to the return object as params are loaded into it.
        processed_RequestParams_Results = []

        # Iterate through each of the 'items' objects found in the paramsInfo['items'] array.
        for paramItem in paramsInfo['items']:

            # Process a single paramItem object (Validate and extract the value)

            # Defaults to each input param (so function execution will not fail).
            function__Input__Param___requestedData_PyObj        = requestData_PyObj
            function__Input__Param___inputKey_Str               = ""        # // NewEntityName
            function__Input__Param___inputType_ClassName        = str
            function__Input__Param___isParamOptional            = True
            function__Input__Param___isValidate_ForNotEmpty     = False
            function__Input__Param___isValidate_JSONLoadsObj    = False
            function__Input__Param___defaultReturnValue         = ""


            # ########################
            # # Unpack the paramItem
            # ########################

            # function__Input__Param___requestedData_PyObj
            # # No action necessary, this param gets passed as is.

            # function__Input__Param___inputKey_Str
            if('inputKey_Str' in paramItem):
                function__Input__Param___inputKey_Str = paramItem['inputKey_Str']

            # function__Input__Param___inputType_ClassName  # // str, int, bool     // JSON types are supported by setting 'str' and then turning on the JSON Flag.
            if('inputType_ClassName' in paramItem):
                inputType_ClassName__String = paramItem['inputType_ClassName']
                if (inputType_ClassName__String == 'str'):
                    function__Input__Param___inputType_ClassName = str
                elif (inputType_ClassName__String == 'int'):
                    function__Input__Param___inputType_ClassName = int
                elif (inputType_ClassName__String == 'bool'):
                    function__Input__Param___inputType_ClassName = bool
                else:
                    # default
                    function__Input__Param___inputType_ClassName = str

            # function__Input__Param___isParamOptional
            if('isParamOptional' in paramItem):
                function__Input__Param___isParamOptional = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=paramItem['isParamOptional'], defaultBoolValue=False)

            # function__Input__Param___isValidate_ForNotEmpty
            if ('isValidate_ForNotEmpty' in paramItem):
                function__Input__Param___isValidate_ForNotEmpty = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=paramItem['isValidate_ForNotEmpty'], defaultBoolValue=True)

            # function__Input__Param___isValidate_JSONLoadsObj
            if ('isValidate_JSONLoadsObj' in paramItem):
                function__Input__Param___isValidate_JSONLoadsObj = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=paramItem['isValidate_JSONLoadsObj'], defaultBoolValue=True)

            # function__Input__Param___defaultReturnValue
            if ('defaultReturnValue' in paramItem):
                function__Input__Param___defaultReturnValue = paramItem['defaultReturnValue']


            # ########################
            # # Validate and Extract the request param.
            # ########################

            paramExtractedValue, isValidationError__Param, errorMessage__Param, sysErrorData__Param = validate_and_extract_request_param__As_Type(requestData_PyObj=function__Input__Param___requestedData_PyObj,
                                                                                                                                                inputKey_Str=function__Input__Param___inputKey_Str,
                                                                                                                                                inputType_ClassName=function__Input__Param___inputType_ClassName,
                                                                                                                                                isParamOptional=function__Input__Param___isParamOptional,
                                                                                                                                                isValidate_ForNotEmpty=function__Input__Param___isValidate_ForNotEmpty,
                                                                                                                                                isValidate_JSONLoadsObj=function__Input__Param___isValidate_JSONLoadsObj,
                                                                                                                                                defaultReturnValue=function__Input__Param___defaultReturnValue)

            # In short, if we ever have a validation error (any of the times while in this loop) then the overall isValidationError gets set to True (which prevents further api action on the calling function)
            if (isValidationError__Param == True):
                isValidationError = True
                validationErrorMessages = errorMessage__Param
                validationSysErrorData = sysErrorData__Param


            # ########################
            # # Load up the object
            # ########################
            currentParam_ResultObj = {}
            currentParam_ResultObj[function__Input__Param___inputKey_Str]   = paramExtractedValue
            currentParam_ResultObj['inputKey_Str']                          = function__Input__Param___inputKey_Str
            currentParam_ResultObj['paramExtractedValue']                   = paramExtractedValue
            currentParam_ResultObj['isValidationError__Param']              = isValidationError__Param
            currentParam_ResultObj['errorMessage__Param']                   = errorMessage__Param
            currentParam_ResultObj['sysErrorData__Param']                   = sysErrorData__Param
            #processed_RequestParams_Results.append(currentParam_ResultObj)
            #processed_RequestParams_Results[function__Input__Param___inputKey_Str] = currentParam_ResultObj #.append(currentParam_ResultObj)
            processed_RequestParams[function__Input__Param___inputKey_Str] = paramExtractedValue
            processed_RequestParams[function__Input__Param___inputKey_Str+'__ResultObject'] = currentParam_ResultObj



            # DEBUGGING
            #print("DEBUG: create_new_entity_page: (input__NewEntityName): " + str(input__NewEntityName))
            #print("DEBUG: create_new_entity_page: (isValidationError__NewEntityName): " + str(isValidationError__NewEntityName))
            #print("DEBUG: create_new_entity_page: (validationErrorMessages): " + str(validationErrorMessages))
            #print("DEBUG: create_new_entity_page: (validationSysErrorData): " + str(validationSysErrorData))
            #print("DEBUG: create_new_entity_page: (isValidationError): " + str(isValidationError))



        # Return
        #processed_RequestParams['results'] = processed_RequestParams_Results
        return processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData  # EXITING THIS FUNCTION HERE
    else:
        # The paramsInfo object was in the improper format - If there are no params, we should at least pass in a blank array.
        processed_RequestParams = {}
        isValidationError = True
        validationErrorMessages = ""
        validationSysErrorData = ""
        return processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData          # EXITING THIS FUNCTION HERE



    return processed_RequestParams, isValidationError, validationErrorMessages, validationSysErrorData          # EXITING THIS FUNCTION HERE


# Validate Various Input Types


def validate_and_extract_request_param__As_Type(requestData_PyObj, inputKey_Str, inputType_ClassName, isParamOptional, isValidate_ForNotEmpty, isValidate_JSONLoadsObj, defaultReturnValue=""): # isValidate_Required
    # Default will be to just check if it is a string.

    # # # https://stackoverflow.com/questions/2225038/determine-the-type-of-an-object
    # >>> type([]) is list
    # True
    # >>> type({}) is dict
    # True
    # >>> type('') is str
    # True
    # >>> type(0) is int
    # True
    # >>> type({})
    # <type 'dict'>
    # >>> type([])
    # <type 'list'>

    retValue = defaultReturnValue
    isError = False
    errorMessage = ""
    sysErrorData = ""



    try:

        # Check to see if the Key exists
        if(inputKey_Str in requestData_PyObj):

            # Key Exists (Time to do stuff with it)

            # All Request Items come in as Strings at first..
            inputValue = str(requestData_PyObj[inputKey_Str]).strip()

            is_ok_to_proceed = True
            fail_reason = "" #"Unknown Validation Error"

            # Check to see if this value is empty or missing (only if this loop is configured to check for that.)
            if (isValidate_ForNotEmpty == True):
                if (len(inputValue.strip()) == 0):
                    is_ok_to_proceed = False
                    fail_reason = "" + str(inputKey_Str) + " must not be empty or only blank spaces."


            # For Types that need to be extracted as a String...
            if (inputType_ClassName == str):

                # # Check to see if this value is empty or missing
                # if (isValidate_ForNotEmpty == True):
                #     if (len(inputValue.strip()) == 0):
                #         is_ok_to_proceed = False
                #         fail_reason = "" + str(inputKey_Str) + " must not be empty or blank spaces."

                # Are we validating this string to see if it loads properly as a JSON object?
                if(isValidate_JSONLoadsObj == True):
                    try:
                        inputValue__AS_JSON = json.loads(inputValue)
                    except:
                        sysErrorData = sys.exc_info()
                        is_ok_to_proceed = False
                        fail_reason = "Unable to read Object.  Ensure the input is in the correct JSON String format."

            # For Types that need to be extracted as an Int
            elif (inputType_ClassName == int):
                try:
                    inputValue = int(inputValue)
                except:
                    sysErrorData = sys.exc_info()
                    is_ok_to_proceed = False
                    fail_reason = "Unable to read Object.  Ensure the input can be converted to an integer (round number)"

            # For Types that need to be extracted as a Boolean  # Note, this can't fail at this step, it simply sets defaultValue... the only fail condition is if the checkpoint for empty or not changed the fail flag already
            elif (inputType_ClassName == bool):
                inputValue = common_utils.get_True_or_False_from_boolish_string(bool_ish_str_value=inputValue,defaultBoolValue=defaultReturnValue)



            # Validations done, now check to see if it is ok to proceed.
            if (is_ok_to_proceed == False):

                # One of the validations failed..
                retValue = defaultReturnValue
                isError = True
                errorMessage = fail_reason
                ret_sysErrorData = sysErrorData
                return retValue, isError, errorMessage, ret_sysErrorData  # EXITING THIS FUNCTION HERE

            else:
                # No Errors here and param is extracted.
                retValue = inputValue
                isError = False
                errorMessage = ""
                ret_sysErrorData = sysErrorData #sysErrorData = ""
                return retValue, isError, errorMessage, ret_sysErrorData  # EXITING THIS FUNCTION HERE


            # FUTURE!!
            #
            # For Types that need to be extracted as an Integer...
            #if (inputType_ClassName == int):
            #    pass

        else:

            # Key does NOT exist... was this param optional?
            if (isParamOptional == True):

                # in this situation, the param was optional and we failed to actually get the param, so returning default without error.
                retValue = defaultReturnValue
                isError = False
                errorMessage = ""
                sysErrorData = ""
                return retValue, isError, errorMessage, sysErrorData  # EXITING THIS FUNCTION HERE

            else:

                # Param was missing.. so unable to get it from the request object. # Param is NOT optional.. so Error.
                retValue = defaultReturnValue
                isError = True
                errorMessage = "Validate and Extract Request Param Error:  They parameter key, " + str(inputKey_Str) + ", was missing and is a required param."  #: System Message: " + str(sysErrorData)
                sysErrorData = ""
                return retValue, isError, errorMessage, sysErrorData  # EXITING THIS FUNCTION HERE

    except:
        # Generic, uncaught exception/error.
        sysErrorInfo = sys.exc_info()
        retValue = defaultReturnValue
        isError = True
        errorMessage = "Validate and Extract Request Param Error:  Generic error when attempting to validate parameter, " + str(inputKey_Str) + "."  #: System Message: " + str(sysErrorData)
        sysErrorData = sysErrorInfo
        return retValue, isError, errorMessage, sysErrorData  # EXITING THIS FUNCTION HERE


















# ############################################################
# # Additional Utils
# ############################################################

# Utility - # Get Client IP address
# https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip









# # END OF FILE







