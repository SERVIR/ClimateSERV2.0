
from django.conf import settings


# Utils 
from common_utils import utils



# For Downloading and also Testing if a URL has an error
import urllib
#import urllib2

# For reading a file object
import io

# For getting my current working directory // dirspot = os.getcwd()   // print dirspot
import os

# This lib is used A LOT!!
import json

import datetime

# For Error tracking
import sys

import time  # for time.sleep(1)
import random

# Simple way to make requests!
import requests

# Import a model item for testing
from api_v2.app_models.model_Widget import Widget



# Called from Terminal  // python common_utils/dev_tools.py
if __name__ == "__main__":
    print("common_utils.dev_tools: has reached the end!")


# Called from Python Console
# # import common_utils.dev_tools as devTools
# # devTools.TEST_From_PythonConsole()
def TEST_From_PythonConsole():
    print("common_utils.dev_tools.TEST_From_PythonConsole(): has reached the end!")


# BUSINESS LOGIC CLASSES HERE

# ############################################################
# # CONTENT GENERATORS.
# ############################################################

# TODO: Create a random <Data_Object> - if there is a specific testing need

# import common_utils.dev_tools as devTools
# devTools.GENERATOR__Get_Random__DataObject()
def GENERATOR__Get_Random__DataObject():
	# # Placeholder for a content Generator function - Used in testing.
	retObj = {}
	
	try:
		retObj['some_property_key'] = 'some_generated_value'
	except:
		sysErrorData = sys.exc_info()
        human_error_Message = "dev_tools.GENERATOR__Get_Random__DataObject: Generic Error.  Error Message: " + str(sysErrorData)
        print(human_error_Message)

	print("dev_tools.GENERATOR__Get_Random__DataObject: Has Reached the End!")
	return retObj
	



# END OF FILE
