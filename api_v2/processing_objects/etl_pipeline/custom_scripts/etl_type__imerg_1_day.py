# etl_type__imerg_1_day.py

# Imports

# Common Functions
from api_v2.processing_objects.etl_pipeline.custom_scripts.common import common
# Usage common.get_function_response_object(class_name="", function_name="", is_error=False, event_description="",
# error_description="", detail_state_info={})

# Other Imports
from api_v2.app_models.model_Config_Setting import Config_Setting
from collections import OrderedDict
import datetime
import ftplib
import numpy as np
import os
import pandas as pd
from shutil import copyfile, rmtree
import sys
import time
import xarray as xr


# Description Create an instance of the subtype class - this class must implement each of the pipeline functions for
# this to work properly.

class ImergOneDay:
    class_name = "ImergOneDay"
    etl_parent_pipeline_instance = None  # def log_etl_error(self, activity_event_type="default_error",
    # activity_description="an error occurred", etl_granule_uuid="", is_alert=True, additional_json={}):

    # Imerg Has more than 1 mode which refer to sub datasets (Early and Late)
    imerg_mode = "LATE"  # Choices at this time are "LATE" and "EARLY" // Controlled by setter functions. // Default
    # is "LATE"

    # Input Settings
    YYYY__Year__Start = 2020  # 2019
    YYYY__Year__End = 2020
    MM__Month__Start = 1  # 12    # 2 #1
    MM__Month__End = 1  # 4 #6
    DD__Day__Start = 1  # 30    # 23
    DD__Day__End = 1  # 2     # 9
    NN__30MinIncrement__Start = 22  # 0     # 0
    NN__30MinIncrement__End = 24  # 48    # 0

    relative_dir_path__WorkingDir = 'working_dir'

    # DRAFTING - Suggestions
    _expected_remote_full_file_paths = []  # Place to store a list of remote file paths (URLs) that the script will
    # need to download.
    _expected_granules = []  # Place to store granules
    #
    # TODO: Other Props used by the script

    _remote_connection__Username = ""
    _remote_connection__Password = ""

    # init (Passing a reference from the calling class, so we can callback the error handler)
    def __init__(self, etl_parent_pipeline_instance):
        self.etl_parent_pipeline_instance = etl_parent_pipeline_instance

    def set_imerg_mode__To__Late(self):
        self.imerg_mode = "LATE"

    def set_imerg_mode__To__Early(self):
        self.imerg_mode = "EARLY"

    # Validate type or use existing default for each
    def set_imerg_params(self, YYYY__Year__Start, YYYY__Year__End, MM__Month__Start, MM__Month__End, DD__Day__Start,
                         DD__Day__End, NN__30MinIncrement__Start, NN__30MinIncrement__End):
        try:
            self.YYYY__Year__Start = int(YYYY__Year__Start)
        except:
            pass
        try:
            self.YYYY__Year__End = int(YYYY__Year__End)
        except:
            pass
        try:
            self.MM__Month__Start = int(MM__Month__Start)
        except:
            pass
        try:
            self.MM__Month__End = int(MM__Month__End)
        except:
            pass
        try:
            self.DD__Day__Start = int(DD__Day__Start)
        except:
            pass
        try:
            self.DD__Day__End = int(DD__Day__End)
        except:
            pass
        try:
            self.NN__30MinIncrement__Start = int(NN__30MinIncrement__Start)
        except:
            pass
        try:
            self.NN__30MinIncrement__End = int(NN__30MinIncrement__End)
        except:
            pass

    # Get the credentials from the settings for connecting to the IMERG Data Source, and then set them to the
    # Instance Vars.
    def get_credentials_and_set_to_class(self):
        self._remote_connection__Username = Config_Setting.get_value(setting_name="FTP_CREDENTIAL_IMERG__USER",
                                                                     default_or_error_return_value="")
        self._remote_connection__Password = Config_Setting.get_value(setting_name="FTP_CREDENTIAL_IMERG__PASS",
                                                                     default_or_error_return_value="")

    # Months between two dates
    def diff_month(self, latest_datetime, earliest_datetime):
        return (latest_datetime.year - earliest_datetime.year) * 12 + latest_datetime.month - earliest_datetime.month

    # Get the local filesystem place to store data
    @staticmethod
    def get_root_local_temp_working_dir(subtype_filter):  # , year):
        # Type Specific Settings
        imerg__EARLY__rootoutputworkingdir = Config_Setting.get_value(
            setting_name="PATH__TEMP_WORKING_DIR__IMERG__EARLY",
            default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/early/'
        # With a year (20xx/) appended
        imerg__LATE__rootoutputworkingdir = Config_Setting.get_value(setting_name="PATH__TEMP_WORKING_DIR__IMERG__LATE",
                                                                     default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/temp_etl_data/imerg/late/'
        # With a year (20xx/) appended

        # ret_rootlocal_working_dir = settings.PATH__TEMP_WORKING_DIR__DEFAULT
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/data/image/input/UNKNOWN/'
        ret_rootlocal_working_dir = Config_Setting.get_value(setting_name="PATH__TEMP_WORKING_DIR__DEFAULT",
                                                             default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/data/image/input/UNKNOWN/'
        subtype_filter = str(subtype_filter).strip()
        if subtype_filter == 'EARLY':
            ret_rootlocal_working_dir = imerg__EARLY__rootoutputworkingdir
        if subtype_filter == 'LATE':
            ret_rootlocal_working_dir = imerg__LATE__rootoutputworkingdir

        # # Add the Year as a string.
        # year = str(year).strip()    # Expecting 'year' to be something like 2019 or "2019"
        # year_dir_name_to_append = year + "/"
        # ret_rootlocal_working_dir = ret_rootlocal_working_dir + year_dir_name_to_append

        return ret_rootlocal_working_dir

    # Get the local filesystem place to store the final NC4 files (The THREDDS monitored Directory location)
    @staticmethod
    def get_final_load_dir(subtype_filter):  # , year):
        imerg__EARLY__finalloaddir = Config_Setting.get_value(setting_name="PATH__THREDDS_MONITORING_DIR__IMERG__EARLY",
                                                              default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/
        # nasa-imerg-early/global/0.1deg/30min/'
        imerg__LATE__finalloaddir = Config_Setting.get_value(setting_name="PATH__THREDDS_MONITORING_DIR__IMERG__LATE",
                                                             default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/
        # nasa-imerg-late/global/0.1deg/30min/'
        ret_dir = Config_Setting.get_value(setting_name="PATH__THREDDS_MONITORING_DIR__DEFAULT",
                                           default_or_error_return_value="")
        # '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/UNKNOWN/'
        subtype_filter = str(subtype_filter).strip()
        if subtype_filter == 'EARLY':
            ret_dir = imerg__EARLY__finalloaddir
        if subtype_filter == 'LATE':
            ret_dir = imerg__LATE__finalloaddir

        # # Add the Year as a string.
        # year = str(year).strip()  # Expecting 'year' to be something like 2019 or "2019"
        # year_dir_name_to_append = year + "/"
        # ret_dir = ret_dir + year_dir_name_to_append

        return ret_dir

    # Get the Remote Locations for each of the subtypes
    @staticmethod
    def get_roothttp_for_subtype(subtype_filter):
        imerg__EARLY__roothttp = Config_Setting.get_value(setting_name="REMOTE_PATH__ROOT_HTTP__IMERG__EARLY",
                                                          default_or_error_return_value="")  # 'ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/early/'        # Early # Note: EARLY from here only requires /yyyy/mm/ appended to path
        imerg__LATE__roothttp = Config_Setting.get_value(setting_name="REMOTE_PATH__ROOT_HTTP__IMERG__LATE",
                                                         default_or_error_return_value="")  # 'ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/'              # Late # Note: LATE, from here only requires /yyyy/mm/ appended to path
        # ret_roothttp = settings.REMOTE_PATH__ROOT_HTTP__DEFAULT #'localhost://UNKNOWN_URL'
        ret_roothttp = Config_Setting.get_value(setting_name="REMOTE_PATH__ROOT_HTTP__DEFAULT",
                                                default_or_error_return_value="")  # ret_roothttp = settings.REMOTE_PATH__ROOT_HTTP__DEFAULT #'localhost://UNKNOWN_URL'
        subtype_filter = str(subtype_filter).strip()
        if subtype_filter == 'EARLY':
            ret_roothttp = imerg__EARLY__roothttp
        if subtype_filter == 'LATE':
            ret_roothttp = imerg__LATE__roothttp

        return ret_roothttp

    @staticmethod
    def append_YEAR_to_dir_path(dirPath, year_int):
        # # Add the Year as a string.
        # year_YYYY = str(year_YYYY).strip()    # Expecting 'year' to be something like 2019 or "2019"
        year_YYYY = "{:0>4d}".format(year_int)
        year_dir_name_to_append = year_YYYY + "/"
        dirPath = dirPath + year_dir_name_to_append
        return dirPath

    @staticmethod
    def append_YEAR_and_MONTH_to_dir_path(dirPath, year_int, month_int):
        # # Add the Year as a string.
        year_YYYY = "{:0>4d}".format(
            year_int)  # year_YYYY = str(year_YYYY).strip()  # Expecting 'year' to be something like 2019 or "2019"
        year_dir_name_to_append = year_YYYY + "/"
        month_MM = "{:02d}".format(month_int)
        month_dir_name_to_append = month_MM + "/"
        dirPath = dirPath + year_dir_name_to_append + month_dir_name_to_append
        return dirPath

    def execute__Step__Pre_ETL_Custom(self):
        ret__function_name = "execute__Step__Pre_ETL_Custom"
        ret__is_error = False
        ret__event_description = ""
        ret__error_description = ""

        # Get the root http path based on the region.
        # current_root_http_path = self.get_roothttp_for_subtype(subtype_filter=self.imerg_mode)
        root_file_download_path = os.path.join(self.get_root_local_temp_working_dir(subtype_filter=self.imerg_mode),
                                               self.relative_dir_path__WorkingDir)
        final_load_dir_path = self.get_final_load_dir(subtype_filter=self.imerg_mode)

        self.temp_working_dir = str(root_file_download_path).strip()
        self._expected_granules = []
        # expected_granules = []

        # (1) Generate Expected remote file paths
        try:

            # Create the list of Days (From start time to end time)
            start_Date = datetime.datetime(year=self.YYYY__Year__Start, month=self.MM__Month__Start,
                                           day=self.DD__Day__Start)
            end_Date = datetime.datetime(year=self.YYYY__Year__End, month=self.MM__Month__End, day=self.DD__Day__End)

            first_day__Start_30Min_Increment = self.NN__30MinIncrement__Start  # = 0  # 0
            last_day__End_30Min_Increment = self.NN__30MinIncrement__End  # = 48  # 0

            delta = end_Date - start_Date
            # print("DELTA: " + str(delta))

            for i in range(delta.days + 1):
                # print start_Date + datetime.timedelta(days=i)
                currentDate = start_Date + datetime.timedelta(days=i)
                current_year__YYYY_str = "{:0>4d}".format(currentDate.year)
                current_month__MM_str = "{:02d}".format(currentDate.month)
                current_day__DD_str = "{:02d}".format(currentDate.day)

                # Debug (making sure we got the right date ranges)
                # print(currentDate)
                # #print("i: " + str(i) + ":   (currentDate.year) " + str(currentDate.year))
                # print("i: " + str(i) + ":   (current_year__YYYY_str) " + str(current_year__YYYY_str))
                # print("i: " + str(i) + ":   (current_month__MM_str) " + str(current_month__MM_str))
                # print("i: " + str(i) + ":   (current_day__DD_str) " + str(current_day__DD_str))

                # Get the Current Day, Start '30 min' increment
                start_30min_increment = 0
                end_30min_increment = 24 * 2

                if i == 0:
                    # We are on the FIRST day, check the start and end 30 min increments
                    start_30min_increment = first_day__Start_30Min_Increment
                    # print("FIRST DAY Loop: (i): " + str(i) + ", (start_30min_increment): " + str(
                    # start_30min_increment))

                if i == delta.days:
                    # We are on the LAST day, check the start and end 30 min increments
                    end_30min_increment = last_day__End_30Min_Increment
                    # print("LAST DAY Loop: (i): " + str(i) + ", (end_30min_increment): " + str(end_30min_increment))

                # Analyzing the Dates
                #
                # # April 2nd, 2020, FIRST 30 min item of the day
                # # # 3B-HHR-L.MS.MRG.3IMERG.20200402-S000000-E002959.0000.V06B.30min.tfw
                #
                #
                # # April 2nd, 2020, LAST 30 min item of the day
                # # # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.1410.V06B.30min.tfw

                # Now we must divide the entire day into 30 minute increments. intraday_filename_helpers_list = []  #
                # List of objects that have the parts of the file name in them, including the final file tif and tfw
                # names

                # minutes_array = []   # Result of the for loop gives us something like this:  [0, 30, 60, 90, 120,
                # 150, 180, 210, 240, 270, 300, 330, .... 1410] //, 1440] for j in range((24*2) + 1):  # There is no
                # 1440, so removing the '+ 1' part for j in range(24 * 2):
                for j in range(start_30min_increment, end_30min_increment):
                    increment_minute_value = j * 30  # 1410
                    increment_minute_value_4Char_Str = "{:0>4d}".format(
                        increment_minute_value)  # "1410"    # Note: A number like 0 gets turned into "0000"
                    increment_minute_value__Div_60 = float(increment_minute_value / 60)  # 23.5
                    both_hh_str = "{:0>2d}".format(
                        int(increment_minute_value__Div_60))  # "23"      # Note: A number like 0 gets turned into "00"
                    hh_remainder = float(increment_minute_value__Div_60 - int(increment_minute_value__Div_60))  # 0.5
                    start_mm_str = "00"  # Correct if hh_remainder is NOT 0.5
                    end_mm_str = "29"  # Correct if hh_remainder is NOT 0.5
                    if hh_remainder == 0.5:
                        start_mm_str = "30"
                        end_mm_str = "59"
                    start_ss_str = "00"
                    end_ss_str = "59"

                    # minutes_array.append(increment_minute_value)
                    # unused variables
                    # start_hour_calc = int(increment_minute_value / 60)  # 0, 1, 2 ... 23
                    # start_hour_HH = "00"

                    base_filename = ''
                    base_filename += '3B-HHR-'  # 3B-HHR-
                    if self.imerg_mode == "LATE":
                        base_filename += 'L'  # 3B-HHR-L
                    if self.imerg_mode == "EARLY":
                        base_filename += 'E'  # 3B-HHR-E
                    base_filename += '.MS.MRG.3IMERG.'  # 3B-HHR-L.MS.MRG.3IMERG.
                    base_filename += current_year__YYYY_str  # 3B-HHR-L.MS.MRG.3IMERG.2020
                    base_filename += current_month__MM_str  # 3B-HHR-L.MS.MRG.3IMERG.202004
                    base_filename += current_day__DD_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402
                    base_filename += '-'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-
                    base_filename += 'S'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S
                    base_filename += both_hh_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S23
                    base_filename += start_mm_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S2330
                    base_filename += start_ss_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000
                    base_filename += '-'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-
                    base_filename += 'E'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E
                    base_filename += both_hh_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E23
                    base_filename += end_mm_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E2359
                    base_filename += end_ss_str  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959
                    base_filename += '.'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.
                    base_filename += str(
                        increment_minute_value_4Char_Str)  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.1410
                    base_filename += '.V06B.30min.'  # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.1410.V06B.30min.
                    tfw_filename = base_filename + 'tfw'
                    # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.1410.V06B.30min.tfw
                    tif_filename = base_filename + 'tif'
                    # 3B-HHR-L.MS.MRG.3IMERG.20200402-S233000-E235959.1410.V06B.30min.tif
                    # .1410.V06B.30min.tfw

                    # print("i,j: " + str(j) + ":   delta date:  delta[i]")

                    # 20200402-S233000-E235959.1410.V06B.30min.tfw

                    # Building the Common NC4 Filename
                    # # Example filename (IMERG Late:   # nasa-imerg-late.20190101T033000Z.global.nc4
                    # expected_file_path_object['final_nc4_filename'] = final_nc4_filename
                    final_nc4_filename = ''
                    final_nc4_filename += 'nasa-imerg-'  # nasa-imerg-
                    if self.imerg_mode == "LATE":
                        final_nc4_filename += 'late'  # nasa-imerg-late
                    if self.imerg_mode == "EARLY":
                        final_nc4_filename += 'early'  # nasa-imerg-early
                    final_nc4_filename += '.'  # nasa-imerg-late.
                    final_nc4_filename += current_year__YYYY_str  # nasa-imerg-late.2020
                    final_nc4_filename += current_month__MM_str  # nasa-imerg-late.202001
                    final_nc4_filename += current_day__DD_str  # nasa-imerg-late.20200130
                    final_nc4_filename += 'T'  # nasa-imerg-late.20200130T
                    final_nc4_filename += both_hh_str  # nasa-imerg-late.20200130T23
                    final_nc4_filename += start_mm_str  # nasa-imerg-late.20200130T2330
                    final_nc4_filename += start_ss_str  # nasa-imerg-late.20200130T233000
                    final_nc4_filename += 'Z.global.nc4'  # nasa-imerg-late.20200130T233000Z.global.nc4

                    # Now get the remote File Paths (Directory) based on the date infos.
                    # current_remote_dir_path
                    # REMOTE_PATH__ROOT_HTTP__IMERG__LATE   // ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/
                    # REMOTE_PATH__ROOT_HTTP__IMERG__EARLY  // ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/gis/early/
                    # Remote DIR Patterns are like this
                    # Late      ...path_to_gis_dir/YYYY/MM/<files_here>
                    # // All of the files for the whole month are in here
                    # Early     ...path_to_gis_early_dir/YYYY/MM/<files_here>
                    # // All of the files for the whole month are in here
                    remote_directory_path = "UNSET/"
                    if self.imerg_mode == "LATE":
                        remote_directory_path = Config_Setting.get_value(
                            setting_name="REMOTE_PATH__ROOT_HTTP__IMERG__LATE",
                            default_or_error_return_value="ERROR_GETTING_DIR_FOR_LATE/")
                    if self.imerg_mode == "EARLY":
                        remote_directory_path = Config_Setting.get_value(
                            setting_name="REMOTE_PATH__ROOT_HTTP__IMERG__EARLY",
                            default_or_error_return_value="ERROR_GETTING_DIR_FOR_EARLY/")

                    # Add the Year and Month to the directory path.
                    remote_directory_path += current_year__YYYY_str
                    remote_directory_path += '/'
                    remote_directory_path += current_month__MM_str
                    remote_directory_path += '/'

                    # Getting full paths
                    remote_full_filepath_tif = str(os.path.join(remote_directory_path, tif_filename)).strip()
                    remote_full_filepath_tfw = str(os.path.join(remote_directory_path, tfw_filename)).strip()

                    local_full_filepath_tif = os.path.join(self.temp_working_dir, tif_filename)
                    local_full_filepath_tfw = os.path.join(self.temp_working_dir, tfw_filename)

                    local_full_filepath_final_nc4_file = os.path.join(final_load_dir_path, final_nc4_filename)

                    current_obj = {}

                    # Loop and Filename building info
                    current_obj['j'] = j
                    current_obj['increment_minute_value'] = increment_minute_value
                    current_obj['increment_minute_value_4Char_Str'] = increment_minute_value_4Char_Str
                    current_obj['increment_minute_value__Div_60'] = increment_minute_value__Div_60
                    current_obj['both_hh_str'] = both_hh_str
                    current_obj['start_mm_str'] = start_mm_str
                    current_obj['end_mm_str'] = end_mm_str
                    current_obj['start_ss_str'] = start_ss_str
                    current_obj['end_ss_str'] = end_ss_str

                    # Date Info (Which Day Is it?)
                    current_obj['date_YYYY'] = current_year__YYYY_str
                    current_obj['date_MM'] = current_month__MM_str
                    current_obj['date_DD'] = current_day__DD_str

                    # Filename and Granule Name info
                    local_extract_path = self.temp_working_dir
                    # There is no extract step, so just using the working directory as the local extract path.
                    local_final_load_path = final_load_dir_path
                    current_obj['local_extract_path'] = local_extract_path  # Download path
                    current_obj[
                        'local_final_load_path'] = local_final_load_path
                    # The path where the final output granule file goes.
                    current_obj['remote_directory_path'] = remote_directory_path
                    current_obj['base_filename'] = base_filename
                    current_obj['tfw_filename'] = tfw_filename
                    current_obj['tif_filename'] = tif_filename
                    current_obj['final_nc4_filename'] = final_nc4_filename
                    current_obj['granule_name'] = final_nc4_filename

                    # Full Paths
                    current_obj['remote_full_filepath_tif'] = remote_full_filepath_tif
                    current_obj['remote_full_filepath_tfw'] = remote_full_filepath_tfw
                    current_obj['local_full_filepath_tif'] = local_full_filepath_tif
                    current_obj['local_full_filepath_tfw'] = local_full_filepath_tfw
                    current_obj['local_full_filepath_final_nc4_file'] = local_full_filepath_final_nc4_file

                    #
                    # Create a new Granule Entry - The first function 'log_etl_granule' is the one that actually
                    # creates a new ETL Granule Attempt (There is one granule per dataset per pipeline attempt run in
                    # the ETL Granule Table) # Granule Helpers # # def log_etl_granule(self,
                    # granule_name="unknown_etl_granule_file_or_object_name", granule_contextual_information="",
                    # granule_pipeline_state=settings.GRANULE_PIPELINE_STATE__ATTEMPTING, additional_json={}): # #
                    # def etl_granule__Update__granule_pipeline_state(self, granule_uuid,
                    # new__granule_pipeline_state, is_error): # # def etl_granule__Update__is_missing_bool_val(self,
                    # granule_uuid, new__is_missing__Bool_Val): # # def etl_granule__Append_JSON_To_Additional_JSON(
                    # self, granule_uuid, new_json_key_to_append, sub_jsonable_object):
                    granule_name = final_nc4_filename
                    granule_contextual_information = ""
                    # granule_pipeline_state = settings.GRANULE_PIPELINE_STATE__ATTEMPTING  # At the start of
                    # creating a new Granule, it starts off as 'attempting' - So we can see Active Granules in the
                    # database while the system is running.
                    granule_pipeline_state = Config_Setting.get_value(setting_name="GRANULE_PIPELINE_STATE__ATTEMPTING",
                                                                      default_or_error_return_value="Attempting")
                    # settings.GRANULE_PIPELINE_STATE__ATTEMPTING
                    additional_json = current_obj  # {}
                    new_Granule_UUID = self.etl_parent_pipeline_instance.log_etl_granule(
                        granule_name=granule_name,
                        granule_contextual_information=granule_contextual_information,
                        granule_pipeline_state=granule_pipeline_state,
                        additional_json=additional_json)
                    #
                    # Save the Granule's UUID for reference in later steps
                    current_obj['Granule_UUID'] = str(new_Granule_UUID).strip()

                    # Add to the granules list
                    self._expected_granules.append(current_obj)

                    # print("DEBUG: JUST DO ONE GRANULE - BREAKING THIS FOR LOOP AFTER 1 ITERATION... BREAKING NOW.")
                    # break

            # End Loop for getting all the granules for each of the days.

            # DEBUG
            # print("len(expected_granules): " + str(len(self._expected_granules)))
            # print("First Granule: str(expected_granules[0]): " + str(self._expected_granules[0]))

        except:
            error_message = "Error: There was an error when generating the expected remote filepaths.  "
            "See the additional data for details on which expected file caused the "
            "error.  System Error Message: " + str(sys.exc_info())
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name, is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "error": error_message,
                                                           "is_error": True,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Pre_ETL_Custom"
                                                       })

        # Make sure the directories exist
        #
        if self.etl_parent_pipeline_instance.create_dir_if_not_exist(self.temp_working_dir):
            error_message = "Error: There was an error when the pipeline tried to create a new directory on " \
                            "the filesystem.  The path that the pipeline tried to create was: " \
                            + str(self.temp_working_dir) + ".  There should be another error logged " \
                                                           "just before this one that contains " \
                                                           "system error info.  That info should give " \
                                                           "clues to why the directory was not able to be created. "
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name,
                                                       is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "error": error_message,
                                                           "is_error": True,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Pre_ETL_Custom"
                                                       })

        # final_load_dir_path
        if self.etl_parent_pipeline_instance.create_dir_if_not_exist(final_load_dir_path):
            error_message = "Error: There was an error when the pipeline tried to create a new directory on the " \
                            "filesystem.  The path that the pipeline tried to create was: " \
                            + str(final_load_dir_path) + ".  There should be another error logged " \
                                                         "just before this one that contains " \
                                                         "system error info.  That info should give clues to " \
                                                         "why the directory was not able to be created. "
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name,
                                                       is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "error": error_message,
                                                           "is_error": True,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Pre_ETL_Custom"
                                                       })

        # Ended, now for reporting

        ret__event_description = "Success.  Completed Step execute__Step__Pre_ETL_Custom by generating " + str(
            len(self._expected_remote_full_file_paths)).strip() + " expected full file paths to download and " + str(
            len(self._expected_granules)).strip() + " expected granules to process."

        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=ret__is_error,
                                                   event_description=ret__event_description,
                                                   error_description=ret__error_description,
                                                   detail_state_info={
                                                       "class_name": self.__class__.__name__,
                                                       "number_of_expected_granules": str(
                                                           len(self._expected_granules)).strip()
                                                   })

    def getErrorObject(self, error_message, function_name, ret__event_description, ret__function_name):
        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=True,
                                                   event_description=ret__event_description,
                                                   error_description=error_message + str(sys.exc_info()),
                                                   detail_state_info={
                                                       "error": error_message + str(sys.exc_info()),
                                                       "is_error": True,
                                                       "class_name": self.__class__.__name__,
                                                       "function_name": function_name
                                                   })

    def execute__Step__Download(self):
        ret__function_name = "execute__Step__Download"
        ret__is_error = False
        ret__error_description = ""
        #
        # TODO: Subtype Specific Logic Here TODO - Iterate each expected granule, attempt to download the file(s)
        #  attached to it to the correct expected location (the working directory). # TODO - Log errors as warnings (
        #   not show stoppers) - Add indexes to allow skipping over items (so the ETL job can continue in an
        #   automated way). - Need to think this through very carefully, so that the clientside can know about these
        #   errors and skip over them as well (and allow the clientside to handle random missing granules - which
        #   happens sometimes).
        #

        # Note: In imerg, each granule has 2 files associated with it
        # # A 'tif' (image) file and a 'tfw' (world metadata file)

        download_counter = 0
        loop_counter = 0
        error_counter = 0
        detail_errors = []

        # # expected_granule Has these properties (and possibly more)
        #             current_obj['j'] = j
        #             current_obj['increment_minute_value']           = increment_minute_value
        #             current_obj['increment_minute_value_4Char_Str'] = increment_minute_value_4Char_Str
        #             current_obj['increment_minute_value__Div_60']   = increment_minute_value__Div_60
        #             current_obj['both_hh_str']                      = both_hh_str
        #             current_obj['start_mm_str']                     = start_mm_str
        #             current_obj['end_mm_str']                       = end_mm_str
        #             current_obj['start_ss_str']                     = start_ss_str
        #             current_obj['end_ss_str']                       = end_ss_str
        #
        #             # Date Info (Which Day Is it?)
        #             current_obj['date_YYYY']    = current_year__YYYY_str
        #             current_obj['date_MM']      = current_month__MM_str
        #             current_obj['date_DD']      = current_day__DD_str
        #
        #             # Filename and Granule Name info
        #             current_obj['base_filename']                    = base_filename
        #             current_obj['remote_directory_path']            = remote_directory_path
        #             current_obj['tfw_filename']                     = tfw_filename
        #             current_obj['tif_filename']                     = tif_filename
        #             current_obj['final_nc4_filename']               = final_nc4_filename
        #             current_obj['granule_name']                     = final_nc4_filename
        #
        #             #
        #             current_obj['remote_full_filepath_tif']             = remote_full_filepath_tif
        #             current_obj['remote_full_filepath_tfw']             = remote_full_filepath_tfw
        #             current_obj['local_full_filepath_tif']              = local_full_filepath_tif
        #             current_obj['local_full_filepath_tfw']              = local_full_filepath_tfw
        #             current_obj['local_full_filepath_final_nc4_file']   = local_full_filepath_final_nc4_file
        #
        #             current_obj['Granule_UUID']                         = str(new_Granule_UUID).strip()
        expected_granules = self._expected_granules
        num_of_objects_to_process = len(expected_granules)
        num_of_download_activity_events = 4
        modulus_size = int(num_of_objects_to_process / num_of_download_activity_events)
        if modulus_size < 1:
            modulus_size = 1

        # Connect to FTP
        FTP_Host = Config_Setting.get_value(setting_name="FTP_CREDENTIAL_IMERG__HOST",
                                            default_or_error_return_value="error.getting.ftp-host.nasa.gov")
        FTP_UserName = Config_Setting.get_value(setting_name="FTP_CREDENTIAL_IMERG__USER",
                                                default_or_error_return_value="error_getting_user_name")
        FTP_UserPass = Config_Setting.get_value(setting_name="FTP_CREDENTIAL_IMERG__PASS",
                                                default_or_error_return_value="error_getting_user_password")
        # unused variable
        # FTP_SubFolderPath = ""  # Set in granule['remote_directory_path']

        # Attempt Making FTP Connection here (if fail, then exit this function with an error
        # unused variable
        # ftp_Connection = None
        # Connect to the FTP Server and download all of the files in the list.
        try:
            ftp_Connection = ftplib.FTP_TLS(host=FTP_Host, user=FTP_UserName, passwd=FTP_UserPass)
            ftp_Connection.prot_p()

            time.sleep(1)

        except:
            error_counter = error_counter + 1
            error_message = "imerg.execute__Step__Download: Error Connecting to FTP.  There was an error when " \
                            "attempting to connect to the Remote FTP Server.  System Error Message: " \
                            + str(sys.exc_info())
            detail_errors.append(error_message)
            print(error_message)

            # Ended, now for reporting
            ret__event_description = "Error During Step execute__Step__Download by downloading " + str(
                download_counter).strip() + " files."
            #
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name, is_error=ret__is_error,
                                                       event_description=ret__event_description,
                                                       error_description=ret__error_description,
                                                       detail_state_info={
                                                           "class_name": self.__class__.__name__,
                                                           "download_counter": download_counter,
                                                           "error_counter": error_counter,
                                                           "loop_counter": loop_counter,
                                                           "detail_errors": detail_errors
                                                       })

        for expected_granule in expected_granules:

            try:
                if ((loop_counter + 1) % modulus_size) == 0:
                    # print("Output a log, (and send pipeline activity log) saying, --- about to download file: " +
                    # str(loop_counter + 1) + " out of " + str(num_of_objects_to_process)) print(" - Output a log,
                    # (and send pipeline activity log) saying, --- about to download file: " + str(loop_counter + 1)
                    # + " out of " + str(num_of_objects_to_process))
                    event_message = "About to download file: " + str(loop_counter + 1) + " out of " + str(
                        num_of_objects_to_process)
                    print(event_message)
                    # activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__DOWNLOAD_PROGRESS
                    activity_event_type = Config_Setting.get_value(
                        setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__DOWNLOAD_PROGRESS",
                        default_or_error_return_value="ETL Download Progress")
                    # settings.ETL_LOG_ACTIVITY_EVENT_TYPE__DOWNLOAD_PROGRESS
                    activity_description = event_message
                    additional_json = self.etl_parent_pipeline_instance.to_JSONable_Object()
                    self.etl_parent_pipeline_instance.log_etl_event(activity_event_type=activity_event_type,
                                                                    activity_description=activity_description,
                                                                    etl_granule_uuid="", is_alert=False,
                                                                    additional_json=additional_json)

                # Current Granule to download
                remote_directory_path = expected_granule['remote_directory_path']
                # remote_full_filepath_tif    = expected_granule['remote_full_filepath_tif']
                # remote_full_filepath_tfw    = expected_granule['remote_full_filepath_tfw']
                tfw_filename = expected_granule['tfw_filename']
                tif_filename = expected_granule['tif_filename']
                local_full_filepath_tif = expected_granule['local_full_filepath_tif']
                local_full_filepath_tfw = expected_granule['local_full_filepath_tfw']
                #
                # Granule info
                Granule_UUID = expected_granule['Granule_UUID']
                # unused variable
                # granule_name = expected_granule['granule_name']

                # FTP Processes
                # # 1 - Change Directory to the directory path
                ftp_Connection.cwd(remote_directory_path)

                # TODO - Fix the problems with checking if a file exists        START
                # # 2 - Check to see if the files exists
                hasFiles = False
                filelist = []  # to store all files
                ftp_Connection.retrlines('LIST', filelist.append)  # append to list
                file_found_count = 0
                # Looking for two specific file matches out of the whole list of files in the current remote directory
                for f in filelist:
                    if tfw_filename in f:
                        file_found_count = file_found_count + 1
                    if tif_filename in f:
                        file_found_count = file_found_count + 1

                # # # DEBUG
                # # print("filelist: " + str(filelist))  # Are we in the right dir?
                # print("remote_directory_path: " + str(remote_directory_path))
                # print("tfw_filename: " + str(tfw_filename))
                # print("tif_filename: " + str(tif_filename))
                # print("local_full_filepath_tif: " + str(local_full_filepath_tif))
                # print("local_full_filepath_tfw: " + str(local_full_filepath_tfw))

                if file_found_count == 2:
                    hasFiles = True

                # Validation
                if not hasFiles:
                    print("Could not find both TIF and TFW files in the directory.  - TODO - Granule Error Recording "
                          "here.")

                    # print("DEBUG: EXITING NOW.  Remove me to continue working on IMERG")
                    # return
                # TODO - Fix the problems with checking if a file exists        END

                # # Let's assume the files DO exist on the remote server - until we can get the rest of the stuff
                # working. hasFiles = True

                # print("DEBUG OUTS")
                # print("remote_directory_path: " + str(remote_directory_path))
                # print("tfw_filename: " + str(tfw_filename))
                # print("tif_filename: " + str(tif_filename))
                # print("local_full_filepath_tif: " + str(local_full_filepath_tif))
                # print("local_full_filepath_tfw: " + str(local_full_filepath_tfw))
                # # print("DEBUG RETURN")
                # # return {}

                if hasFiles:
                    # Both files were found, so let's now download them.

                    # Backwards compatibility
                    # # Remote paths (where the files are coming from)
                    ftp_PathTo_TIF = tif_filename
                    ftp_PathTo_TWF = tfw_filename
                    # # Local Paths (Where the files are being saved)
                    local_FullFilePath_ToSave_Tif = local_full_filepath_tif
                    local_FullFilePath_ToSave_Twf = local_full_filepath_tfw

                    try:
                        # Download the Tif
                        fx = open(local_FullFilePath_ToSave_Tif, "wb")
                        fx.close()
                        os.chmod(local_FullFilePath_ToSave_Tif, 0o0777)  # 0777

                        try:
                            with open(local_FullFilePath_ToSave_Tif, "wb") as f:
                                ftp_Connection.retrbinary("RETR " + ftp_PathTo_TIF,
                                                          f.write)  # "RETR %s" % ftp_PathTo_TIF
                        except:
                            os.remove(local_FullFilePath_ToSave_Tif)
                            local_FullFilePath_ToSave_Tif = local_FullFilePath_ToSave_Tif.replace("03E", "04A")
                            ftp_PathTo_TIF = ftp_PathTo_TIF.replace("03E", "04A")
                            fx = open(local_FullFilePath_ToSave_Tif, "wb")
                            fx.close()
                            os.chmod(local_FullFilePath_ToSave_Tif, 0o0777)  # 0777
                            try:
                                with open(local_FullFilePath_ToSave_Tif, "wb") as f:
                                    ftp_Connection.retrbinary("RETR " + ftp_PathTo_TIF,
                                                              f.write)  # "RETR %s" % ftp_PathTo_TIF
                            except:
                                os.remove(local_FullFilePath_ToSave_Tif)
                                ftp_PathTo_TIF = ftp_PathTo_TIF.replace("04A", "04B")
                                local_FullFilePath_ToSave_Tif = local_FullFilePath_ToSave_Tif.replace("04A", "04B")
                                fx = open(local_FullFilePath_ToSave_Tif, "wb")
                                fx.close()
                                os.chmod(local_FullFilePath_ToSave_Tif, 0o0777)  # 0777
                                try:
                                    with open(local_FullFilePath_ToSave_Tif, "wb") as f:
                                        ftp_Connection.retrbinary("RETR " + ftp_PathTo_TIF,
                                                                  f.write)  # "RETR %s" % ftp_PathTo_TIF
                                except:
                                    error_counter = error_counter + 1
                                    activity_event_type = Config_Setting.get_value(
                                        setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING",
                                        default_or_error_return_value="ETL Warning")
                                    activity_description = "Warning: There was an error when downloading tif file: " \
                                                           + str(tif_filename) + " from FTP directory: " \
                                                           + str(remote_directory_path) + ".  If the System Error " \
                                                                                          "message says something " \
                                                                                          "like 'nodename nor " \
                                                                                          "servname provided, or " \
                                                                                          "not known', then one " \
                                                                                          "common cause of that " \
                                                                                          "error is an unstable " \
                                                                                          "or disconnected " \
                                                                                          "internet connection.  " \
                                                                                          "Double check that the " \
                                                                                          "internet connection is" \
                                                                                          " working and try again." \
                                                                                          "  System Error Message: " \
                                                           + str(str(sys.exc_info()))
                                    self.etl_parent_pipeline_instance.log_etl_error(
                                        activity_event_type=activity_event_type,
                                        activity_description=activity_description, etl_granule_uuid=Granule_UUID,
                                        is_alert=True, additional_json={
                                            "warning": activity_description,
                                            "is_error": True,
                                            "class_name": self.__class__.__name__,
                                            "function_name": "execute__Step__Download",
                                            "current_object_info": expected_granule
                                        })

                                    # Give the FTP Connection a short break (Server spam protection mitigation)
                        time.sleep(3)

                        # Download the Tfw
                        fx = open(local_FullFilePath_ToSave_Twf, "wb")
                        fx.close()
                        os.chmod(local_FullFilePath_ToSave_Twf, 0o0777)  # 0777
                        try:
                            with open(local_FullFilePath_ToSave_Twf, "wb") as f:
                                ftp_Connection.retrbinary("RETR " + ftp_PathTo_TWF,
                                                          f.write)  # "RETR %s" % ftp_PathTo_TIF
                        except:
                            os.remove(local_FullFilePath_ToSave_Twf)
                            local_FullFilePath_ToSave_Twf = local_FullFilePath_ToSave_Twf.replace("03E", "04A")
                            ftp_PathTo_TWF = ftp_PathTo_TWF.replace("03E", "04A")
                            fx = open(local_FullFilePath_ToSave_Twf, "wb")
                            fx.close()
                            os.chmod(local_FullFilePath_ToSave_Twf, 0o0777)  # 0777
                            try:
                                with open(local_FullFilePath_ToSave_Twf, "wb") as f:
                                    ftp_Connection.retrbinary("RETR " + ftp_PathTo_TWF,
                                                              f.write)  # "RETR %s" % ftp_PathTo_TIF
                            except:
                                os.remove(local_FullFilePath_ToSave_Twf)
                                ftp_PathTo_TWF = ftp_PathTo_TWF.replace("04A", "04B")
                                local_FullFilePath_ToSave_Twf = local_FullFilePath_ToSave_Twf.replace("04A", "04B")
                                fx = open(local_FullFilePath_ToSave_Twf, "wb")
                                fx.close()
                                os.chmod(local_FullFilePath_ToSave_Twf, 0o0777)  # 0777
                                try:
                                    with open(local_FullFilePath_ToSave_Twf, "wb") as f:
                                        ftp_Connection.retrbinary("RETR " + ftp_PathTo_TWF,
                                                                  f.write)  # "RETR %s" % ftp_PathTo_TIF
                                except:
                                    error_counter = error_counter + 1
                                    # print("DEBUG Warn: (WARN LEVEL) (File can not be downloaded).

                                    warning_message = "Warning: There was an error when downloading tfw file: " + str(
                                        tfw_filename) + " from FTP directory: " + str(
                                        remote_directory_path) + ".  If the System Error message says something " \
                                                                 "like 'nodename nor servname provided, or not " \
                                                                 "known', then one common cause of that error is " \
                                                                 "an unstable or disconnected internet connection.  " \
                                                                 "Double check that the internet connection is " \
                                                                 "working and try again.  System Error Message: " \
                                                      + str(str(sys.exc_info()))
                                    # Call Error handler right here to send a warning message to ETL log. - Note this
                                    # warning will not make it back up to the overall pipeline, it is being sent here
                                    # so admin can still be aware of it and handle it. activity_event_type         =
                                    # settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING

                                    self.etl_parent_pipeline_instance.log_etl_error(
                                        activity_event_type=Config_Setting.get_value(
                                            setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING",
                                            default_or_error_return_value="ETL Warning"),
                                        activity_description=warning_message, etl_granule_uuid=Granule_UUID,
                                        is_alert=True, additional_json={
                                            "warning": warning_message,
                                            "is_error": True,
                                            "class_name": self.__class__.__name__,
                                            "function_name": "execute__Step__Download",
                                            "current_object_info": expected_granule
                                        })

                        # Give the FTP Connection a short break (Server spam protection mitigation)
                        time.sleep(3)

                        # Counting Granule downloads, not individual files (in this case, 1 granule is made up from
                        # two files)
                        download_counter = download_counter + 1
                        # print("At the end, no errors....  maybe... download_counter: " + str(download_counter))

                    except:
                        # print("There was some kind of error when trying to download IMERG Files (Tif and/or Tfw files).  TODO - Add the Granule Error here.")

                        # remote_directory_path, tfw_filename, tif_filename

                        error_counter = error_counter + 1
                        # print("DEBUG Warn: (WARN LEVEL) (File can not be downloaded).
                        warning_message = "Warning: There was an uncaught error when attempting to download 1 of " \
                                          "these files (tif or tfw), " + str(
                            tif_filename) + ", or " + str(tfw_filename) + " from FTP directory: " + str(
                            remote_directory_path) + ".  If the System Error message says something like 'nodename " \
                                                     "nor servname provided, or not known', then one common cause of " \
                                                     "that error is an unstable or disconnected internet connection." \
                                                     "  Double check that the internet connection is working and try " \
                                                     "again.  System Error Message: " + str(
                            str(sys.exc_info()))
                        # Call Error handler right here to send a warning message to ETL log. - Note this warning
                        # will not make it back up to the overall pipeline, it is being sent here so admin can still
                        # be aware of it and handle it. activity_event_type         =
                        # settings.ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING
                        activity_event_type = Config_Setting.get_value(
                            setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__ERROR_LEVEL_WARNING",
                            default_or_error_return_value="ETL Warning")
                        activity_description = warning_message
                        self.etl_parent_pipeline_instance.log_etl_error(activity_event_type=activity_event_type,
                                                                        activity_description=activity_description,
                                                                        etl_granule_uuid=Granule_UUID, is_alert=True,
                                                                        additional_json={
                                                                            "warning": warning_message,
                                                                            "is_error": True,
                                                                            "class_name": self.__class__.__name__,
                                                                            "function_name": "execute__Step__Download",
                                                                            "current_object_info": expected_granule
                                                                        })

                    # END   try:    Where the file downloads happen
                # END   if (hasFiles == True):

                # # Will at least 1 download work?
                # print("DEBUG OUTS")
                # print("remote_directory_path: " + str(remote_directory_path))
                # print("tfw_filename: " + str(tfw_filename))
                # print("tif_filename: " + str(tif_filename))
                # print("local_full_filepath_tif: " + str(local_full_filepath_tif))
                # print("local_full_filepath_tfw: " + str(local_full_filepath_tfw))
                # print("DEBUG RETURN")
                # return {}

            except:
                error_counter = error_counter + 1
                error_message = "imerg.execute__Step__Download: Generic Uncaught Error.  At least 1 download failed.  " \
                                "System Error Message: " + str(sys.exc_info())
                detail_errors.append(error_message)
                print(error_message)

                # Maybe in here is an error with sending the warning in an earlier step?
            loop_counter = loop_counter + 1

        # Ended, now for reporting
        ret__event_description = "Success.  Completed Step execute__Step__Download by downloading " + str(
            download_counter).strip() + " files."
        #
        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=ret__is_error,
                                                   event_description=ret__event_description,
                                                   error_description=ret__error_description,
                                                   detail_state_info={
                                                       "class_name": self.__class__.__name__,
                                                       "download_counter": download_counter,
                                                       "error_counter": error_counter,
                                                       "loop_counter": loop_counter,
                                                       "detail_errors": detail_errors
                                                   })

    def execute__Step__Extract(self):
        ret__function_name = "execute__Step__Extract"
        ret__is_error = False
        ret__event_description = ""
        ret__error_description = ""
        #
        # TODO: Subtype Specific Logic Here
        #

        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=ret__is_error,
                                                   event_description=ret__event_description,
                                                   error_description=ret__error_description,
                                                   detail_state_info={
                                                       "class_name": self.__class__.__name__,
                                                       "custom_message": "Imerg types do not need to be extracted.  "
                                                                         "The source files are non-compressed Tif "
                                                                         "and Tfw files. "
                                                   })

    def execute__Step__Transform(self):
        ret__function_name = "execute__Step__Transform"
        ret__is_error = False
        ret__event_description = ""
        ret__error_description = ""
        #
        # TODO: Subtype Specific Logic Here
        #

        # error_counter, detail_errors
        error_counter = 0
        detail_errors = []

        try:
            expected_granules = self._expected_granules
            for expected_granules_object in expected_granules:
                try:

                    # Getting info ready for the current granule.
                    local_extract_path = expected_granules_object['local_extract_path']
                    tif_filename = expected_granules_object['tif_filename']
                    final_nc4_filename = expected_granules_object['final_nc4_filename']
                    expected_full_path_to_local_extracted_tif_file = os.path.join(local_extract_path, tif_filename)

                    geotiffFile_FullPath = expected_full_path_to_local_extracted_tif_file

                    # Matching to the other script
                    # geotiffFile = tif_filename   # Use Tif Filename for doing string split stuff  # tif_filename
                    # geotiffFile_FullPath
                    # geotiffFile Sometimes is tif_filename
                    # geotiffFile Sometimes is geotiffFile_FullPath

                    ############################################################
                    # Start extracting data and creating output netcdf file.
                    ############################################################

                    # !/usr/bin/env python Program: Convert NASA IMERG Early 30-min rainfall accumulation geoTiff
                    # files into netCDF-4 for storage on the ClimateSERV 2.0 thredds data server. Calling:
                    # imergEarly2netcdf.py geotiffFile geotiffFile: The inputfile to be processed.
                    #
                    # General Flow: Determine the date associated with the geoTiff file. 1) Use  xarray+rasterio to
                    # read the geotiff data from a file into a data array. 2) Convert to a dataset and add an
                    # appropriate time dimension 3) Clean up the dataset: Rename and add dimensions, attributes,
                    # and scaling factors as appropriate. 4) Dump the dataset to a netCDF-4 file with a filename
                    # conforming to the ClimateSERV 2.0 TDS conventions.

                    # Set region ID
                    regionID = 'Global'

                    # Based on the geotiffFile name, determine the time string elements.
                    # Split elements by period
                    TimeStrSplit = tif_filename.split('.')  # TimeStrSplit = geotiffFile.split('.')
                    TimeStr = TimeStrSplit[4].split('-')
                    yyyymmdd = TimeStr[0]
                    hhmmss = TimeStr[1]
                    # Set versionID
                    versionID = TimeStrSplit[6]
                    # Determine the timestamp for the data.

                    # Determine starting and ending times. # Error with pandas.Timestamp function (Solution,
                    # just use Datetime to parse this) startTime = pd.Timestamp.strptime(yyyymmdd + hhmmss,
                    # '%Y%m%dS%H%M%S')   # pandas can't seem to use datetime to parse timestrings...
                    startTime = datetime.datetime.strptime(yyyymmdd + hhmmss, '%Y%m%dS%H%M%S')
                    endTime = startTime + pd.Timedelta('29M') + pd.Timedelta('59S')  # 4 weeks (i.e. 28 days)

                    ############################################################
                    # Beging extracting data and creating output netcdf file.
                    ############################################################

                    # 1) Read the geotiff data into an xarray data array
                    tiffData = xr.open_rasterio(geotiffFile_FullPath)  # tiffData = xr.open_rasterio(geotiffFile)
                    # Rescale to accumulated precipitation amount
                    tiffData = tiffData / 10.0
                    # 2) Convert to a dataset.  (need to assign a name to the data array)
                    imerg = tiffData.rename('precipitation_amount').to_dataset()
                    # Handle selecting/adding the dimesions
                    imerg = imerg.isel(band=0).reset_coords('band', drop=True)
                    # select the singleton band dimension and drop out the associated coordinate.
                    # Add the time dimension as a new coordinate.
                    imerg = imerg.assign_coords(time=startTime).expand_dims(dim='time', axis=0)
                    # Add an additional variable "time_bnds" for the time boundaries.
                    imerg['time_bnds'] = xr.DataArray(np.array([startTime, endTime]).reshape((1, 2)),
                                                      dims=['time', 'nbnds'])

                    # 3) Rename and add attributes to this dataset.
                    # # Error, 'inplace' has been removed from xarray.
                    # imerg.rename({'y': 'latitude', 'x': 'longitude'}, inplace=True)  # rename lat/lon
                    # Now making the assignment (look like the above ones)
                    imerg = imerg.rename({'y': 'latitude', 'x': 'longitude'})  # rename lat/lon

                    # Lat/Lon/Time dictionaries.
                    # Use Ordered dict
                    latAttr = OrderedDict([('long_name', 'latitude'), ('units', 'degrees_north'), ('axis', 'Y')])
                    lonAttr = OrderedDict([('long_name', 'longitude'), ('units', 'degrees_east'), ('axis', 'X')])
                    timeAttr = OrderedDict([('long_name', 'time'), ('axis', 'T'), ('bounds', 'time_bnds')])
                    timeBoundsAttr = OrderedDict([('long_name', 'time_bounds')])
                    precipAttr = OrderedDict(
                        [('long_name', 'precipitation_amount'), ('units', 'mm'), ('accumulation_interval', '30 minute'),
                         ('comment', 'IMERG 30-minute accumulated rainfall, Early Run')])
                    fileAttr = OrderedDict(
                        [('Description',
                          'NASA Integrated Multi-satellitE Retrievals for GPM (IMERG) data product, Early Run.'),
                         ('DateCreated', pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%SZ')),
                         ('Contact', 'Lance Gilliland, lance.gilliland@nasa.gov'),
                         ('Source', 'NASA GPM Precipitation Processing System; '
                                    'https://gpm.nasa.gov/data-access/downloads/gpm; '
                                    'ftp://jsimpson.pps.eosdis.nasa.gov:/data/imerg/gis/early'),
                         ('Version', versionID),
                         ('Reference', 'G. Huffman, D. Bolvin, D. Braithwaite, K. Hsu, R. Joyce, P. Xie, '
                                       '2014: Integrated Multi-satellitE Retrievals for GPM (IMERG), version 4.4. '
                                       'NASAs Precipitation Processing Center.'),
                         ('RangeStartTime', startTime.strftime('%Y-%m-%dT%H:%M:%SZ')),
                         ('RangeEndTime', endTime.strftime('%Y-%m-%dT%H:%M:%SZ')),
                         ('SouthernmostLatitude', np.min(imerg.latitude.values)),
                         ('NorthernmostLatitude', np.max(imerg.latitude.values)),
                         ('WesternmostLongitude', np.min(imerg.longitude.values)),
                         ('EasternmostLongitude', np.max(imerg.longitude.values)),
                         ('TemporalResolution', '30-minute'), ('SpatialResolution', '0.1deg')])

                    # missing_data/_FillValue , relative time units etc. are handled as
                    # part of the encoding dictionary used in to_netcdf() call.
                    # 'zlib' and 'complevel' are added to generate compression and reduce file size
                    precipEncoding = {'_FillValue': np.uint16(29999), 'missing_value': np.uint16(29999),
                                      'dtype': np.dtype('uint16'), 'scale_factor': 0.1, 'add_offset': 0.0, 'zlib': True,
                                      'complevel': 7}
                    timeEncoding = {'units': 'seconds since 1970-01-01T00:00:00Z', 'dtype': np.dtype('int32')}
                    timeBoundsEncoding = {'units': 'seconds since 1970-01-01T00:00:00Z', 'dtype': np.dtype('int32')}
                    # Set the Attributes
                    imerg.latitude.attrs = latAttr
                    imerg.longitude.attrs = lonAttr
                    imerg.time.attrs = timeAttr
                    imerg.time_bnds.attrs = timeBoundsAttr
                    imerg.precipitation_amount.attrs = precipAttr
                    imerg.attrs = fileAttr
                    # Set the Endcodings
                    imerg.precipitation_amount.encoding = precipEncoding
                    imerg.time.encoding = timeEncoding
                    imerg.time_bnds.encoding = timeBoundsEncoding

                    # 5) Output File outputFile_name_ORIG_SCRIPT = 'NASA-IMERG_EARLY.' + startTime.strftime(
                    # '%Y%m%dT%H%M%SZ') + '.' + regionID + '.nc4' print("READY FOR OUTPUT FILE!: (
                    # outputFile_name_ORIG_SCRIPT): " + str(outputFile_name_ORIG_SCRIPT)) outputFile =
                    # 'NASA-IMERG_EARLY.' + startTime.strftime('%Y%m%dT%H%M%SZ') + '.' + regionID + '.nc4'
                    # imerg.to_netcdf(outputFile, unlimited_dims='time')
                    outputFile_FullPath = os.path.join(local_extract_path, final_nc4_filename)
                    imerg.to_netcdf(outputFile_FullPath, unlimited_dims='time')

                    pass

                except:
                    Granule_UUID = expected_granules_object['Granule_UUID']

                    error_message = "imerg.execute__Step__Transform: An Error occurred during the Transform step " \
                                    "with ETL_Granule UUID: " + str(
                        Granule_UUID) + ".  System Error Message: " + str(sys.exc_info())

                    # print("DEBUG: PRINT ERROR HERE: (error_message) " + str(error_message))

                    # Individual Transform Granule Error
                    error_counter = error_counter + 1
                    detail_errors.append(error_message)

                    # Update this Granule for Failure (store the error info in the granule also) Granule_UUID =
                    # expected_granules_object['Granule_UUID'] new__granule_pipeline_state =
                    # settings.GRANULE_PIPELINE_STATE__FAILED  # When a granule has a NC4 file in the correct
                    # location, this counts as a Success.
                    new__granule_pipeline_state = Config_Setting.get_value(
                        setting_name="GRANULE_PIPELINE_STATE__FAILED", default_or_error_return_value="FAILED")  #
                    is_error = True
                    is_update_succeed = self.etl_parent_pipeline_instance.etl_granule__Update__granule_pipeline_state(
                        granule_uuid=Granule_UUID, new__granule_pipeline_state=new__granule_pipeline_state,
                        is_error=is_error)
                    new_json_key_to_append = "execute__Step__Transform"
                    self.etl_parent_pipeline_instance.etl_granule__Append_JSON_To_Additional_JSON(
                        granule_uuid=Granule_UUID, new_json_key_to_append=new_json_key_to_append,
                        sub_jsonable_object={
                            "error_message": error_message,
                            "is_update_succeed": is_update_succeed,
                            "is_update_succeed_2": "Current process"
                        })

                pass

        except:
            error_message = "Error: There was an uncaught error when processing the Transform step on all of the " \
                            "expected Granules.  See the additional data and system error message for details on " \
                            "what caused this error.  System Error Message: " + str(
                str(sys.exc_info()))
            # Exit Here With Error info loaded up
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name, is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "error": error_message,
                                                           "is_error": True,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Transform"
                                                       })

        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=ret__is_error,
                                                   event_description=ret__event_description,
                                                   error_description=ret__error_description,
                                                   detail_state_info={
                                                       "class_name": self.__class__.__name__,
                                                       "error_counter": error_counter,
                                                       "detail_errors": detail_errors
                                                   })

    def execute__Step__Load(self):
        ret__function_name = "execute__Step__Load"
        ret__is_error = False
        ret__event_description = ""
        ret__error_description = ""
        #
        # TODO: Subtype Specific Logic Here
        #
        try:
            expected_granules = self._expected_granules
            for expected_granules_object in expected_granules:

                expected_full_path_to_local_working_nc4_file = "UNSET"
                expected_full_path_to_local_final_nc4_file = "UNSET"

                # local_extract_path      = expected_granules_object['local_extract_path'] local_final_load_path   =
                # expected_granules_object['local_final_load_path'] final_nc4_filename      =
                # expected_granules_object['final_nc4_filename'] expected_full_path_to_local_working_nc4_file =
                # os.path.join(local_extract_path, final_nc4_filename)  # Where the NC4 file was generated during the
                # Transform Step expected_full_path_to_local_final_nc4_file = os.path.join(local_final_load_path,
                # final_nc4_filename)  # Where the final NC4 file should be placed for THREDDS Server monitoring

                try:
                    local_extract_path = expected_granules_object['local_extract_path']
                    local_final_load_path = expected_granules_object['local_final_load_path']
                    final_nc4_filename = expected_granules_object['final_nc4_filename']
                    expected_full_path_to_local_working_nc4_file = os.path.join(local_extract_path,
                                                                                final_nc4_filename)
                    # Where the NC4 file was generated during the Transform Step
                    expected_full_path_to_local_final_nc4_file = os.path.join(local_final_load_path,
                                                                              final_nc4_filename)
                    # Where the final NC4 file should be placed for THREDDS Server monitoring

                    # Copy the file from the working directory over to the final location for it.  (Where THREDDS
                    # Monitors for it)
                    copyfile(expected_full_path_to_local_working_nc4_file,
                             expected_full_path_to_local_final_nc4_file)  # (src, dst)

                    # Create a new Granule Entry - The first function 'log_etl_granule' is the one that actually
                    # creates a new ETL Granule Attempt (There is one granule per dataset per pipeline attempt run in
                    # the ETL Granule Table) # Granule Helpers # # def log_etl_granule(self,
                    # granule_name="unknown_etl_granule_file_or_object_name", granule_contextual_information="",
                    # granule_pipeline_state=settings.GRANULE_PIPELINE_STATE__ATTEMPTING, additional_json={}): # #
                    # def etl_granule__Update__granule_pipeline_state(self, granule_uuid,
                    # new__granule_pipeline_state, is_error): # # def etl_granule__Update__is_missing_bool_val(self,
                    # granule_uuid, new__is_missing__Bool_Val): # # def etl_granule__Append_JSON_To_Additional_JSON(
                    # self, granule_uuid, new_json_key_to_append, sub_jsonable_object):
                    Granule_UUID = expected_granules_object['Granule_UUID']
                    # new__granule_pipeline_state = settings.GRANULE_PIPELINE_STATE__SUCCESS # When a granule has a
                    # NC4 file in the correct location, this counts as a Success.
                    new__granule_pipeline_state = Config_Setting.get_value(
                        setting_name="GRANULE_PIPELINE_STATE__SUCCESS", default_or_error_return_value="SUCCESS")  #
                    is_error = False
                    is_update_succeed = self.etl_parent_pipeline_instance.etl_granule__Update__granule_pipeline_state(
                        granule_uuid=Granule_UUID, new__granule_pipeline_state=new__granule_pipeline_state,
                        is_error=is_error)
                    #

                    # Now that the granule is in it's destination location, we can do a create_or_update 'Available
                    # Granule' so that the database knows this granule exists in the system (so the client side will
                    # know it is available)
                    #
                    # # TODO - Possible Parameter updates needed here.  (As we learn more about what the specific
                    #  client side needs are) # def create_or_update_Available_Granule(self, granule_name,
                    #  granule_contextual_information, etl_pipeline_run_uuid, etl_dataset_uuid, created_by,
                    #  additional_json):
                    granule_name = final_nc4_filename
                    granule_contextual_information = ""
                    self.etl_parent_pipeline_instance.create_or_update_Available_Granule(
                        granule_name=granule_name,
                        granule_contextual_information=granule_contextual_information,
                        additional_json={
                            "MostRecent__ETL_Granule_UUID": str(Granule_UUID).strip()
                        })

                except:
                    error_message = "Error: There was an error when attempting to copy the current nc4 file to it's " \
                                    "final directory location.  See the additional data and system error message for " \
                                    "details on what caused this error.  System Error Message: " + str(
                        str(sys.exc_info()))
                    # Update this Granule for Failure (store the error info in the granule also)
                    Granule_UUID = expected_granules_object['Granule_UUID']
                    # new__granule_pipeline_state = settings.GRANULE_PIPELINE_STATE__FAILED  # When a granule has a
                    # NC4 file in the correct location, this counts as a Success.
                    new__granule_pipeline_state = Config_Setting.get_value(
                        setting_name="GRANULE_PIPELINE_STATE__FAILED", default_or_error_return_value="FAILED")
                    self.etl_parent_pipeline_instance.etl_granule__Update__granule_pipeline_state(
                        granule_uuid=Granule_UUID, new__granule_pipeline_state=new__granule_pipeline_state,
                        is_error=True)
                    self.etl_parent_pipeline_instance.etl_granule__Append_JSON_To_Additional_JSON(
                        granule_uuid=Granule_UUID, new_json_key_to_append="execute__Step__Load",
                        sub_jsonable_object={
                            "error": error_message,
                            "is_error": True,
                            "class_name": self.__class__.__name__,
                            "function_name": "execute__Step__Load",
                            "expected_full_path_to_local_working_nc4_file": str(
                                expected_full_path_to_local_working_nc4_file).strip(),
                            "expected_full_path_to_local_final_nc4_file": str(
                                expected_full_path_to_local_final_nc4_file).strip()
                        })

            pass
        except:
            error_message = "Error: There was an uncaught error when processing the Load step on all of the expected " \
                            "Granules.  See the additional data and system error message for details on what caused " \
                            "this error.  System Error Message: " + str(
                str(sys.exc_info()))
            # Exit Here With Error info loaded up
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name, is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "is_error": True,
                                                           "error": error_message,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Load"
                                                       })

        return common.get_function_response_object(class_name=self.__class__.__name__,
                                                   function_name=ret__function_name, is_error=ret__is_error,
                                                   event_description=ret__event_description,
                                                   error_description=ret__error_description,
                                                   detail_state_info={
                                                       "class_name": self.__class__.__name__,
                                                       "is_error": False,
                                                       "function_name": "execute__Step__Load"
                                                   })

    def execute__Step__Post_ETL_Custom(self):
        #
        # TODO: Subtype Specific Logic Here
        #
        retObj = common.get_function_response_object(class_name=self.__class__.__name__,
                                                     function_name="execute__Step__Post_ETL_Custom", is_error=False,
                                                     event_description="",
                                                     error_description="",
                                                     detail_state_info={
                                                         "custom_message": "No logic was written here",
                                                         "function_name": "execute__Step__Post_ETL_Custom"
                                                     })
        return retObj

    def execute__Step__Clean_Up(self):
        ret__function_name = "execute__Step__Clean_Up"
        ret__is_error = False
        ret__event_description = ""
        ret__error_description = ""
        #
        # TODO: Subtype Specific Logic Here
        #
        try:
            temp_working_dir = str(self.temp_working_dir).strip()
            if temp_working_dir == "":

                # Log an ETL Activity that says that the value of the temp_working_dir was blank.
                # activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_BLANK
                activity_event_type = Config_Setting.get_value(
                    setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_BLANK",
                    default_or_error_return_value="Temp Working Dir Blank")  #
                activity_description = "Could not remove the temporary working directory.  The value for " \
                                       "self.temp_working_dir was blank. "
                additional_json = self.etl_parent_pipeline_instance.to_JSONable_Object()
                additional_json['subclass'] = "imerg"
                self.etl_parent_pipeline_instance.log_etl_event(activity_event_type=activity_event_type,
                                                                activity_description=activity_description,
                                                                etl_granule_uuid="", is_alert=False,
                                                                additional_json=additional_json)

            else:
                # shutil.rmtree
                rmtree(temp_working_dir)

                # Log an ETL Activity that says that the value of the temp_working_dir was blank.
                # activity_event_type = settings.ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_REMOVED
                activity_event_type = Config_Setting.get_value(
                    setting_name="ETL_LOG_ACTIVITY_EVENT_TYPE__TEMP_WORKING_DIR_REMOVED",
                    default_or_error_return_value="Temp Working Dir Removed")  #
                activity_description = "Temp Working Directory, " + str(
                    self.temp_working_dir).strip() + ", was removed."
                additional_json = self.etl_parent_pipeline_instance.to_JSONable_Object()
                additional_json['subclass'] = "imerg"
                additional_json['temp_working_dir'] = str(temp_working_dir).strip()
                self.etl_parent_pipeline_instance.log_etl_event(activity_event_type=activity_event_type,
                                                                activity_description=activity_description,
                                                                etl_granule_uuid="", is_alert=False,
                                                                additional_json=additional_json)

            # print("execute__Step__Clean_Up: Cleanup is finished.")

        except:
            error_message = "Error: There was an uncaught error when processing the Clean Up step.  This function is " \
                            "supposed to simply remove the working directory.  This means the working directory was " \
                            "not removed.  See the additional data and system error message for details on what " \
                            "caused this error.  System Error Message: " + str(
                str(sys.exc_info()))
            # Exit Here With Error info loaded up
            return common.get_function_response_object(class_name=self.__class__.__name__,
                                                       function_name=ret__function_name, is_error=True,
                                                       event_description=ret__event_description,
                                                       error_description=error_message,
                                                       detail_state_info={
                                                           "error": error_message,
                                                           "is_error": True,
                                                           "class_name": self.__class__.__name__,
                                                           "function_name": "execute__Step__Clean_Up",
                                                           "self__temp_working_dir": str(self.temp_working_dir).strip()
                                                       })

        retObj = common.get_function_response_object(class_name=self.__class__.__name__,
                                                     function_name=ret__function_name, is_error=ret__is_error,
                                                     event_description=ret__event_description,
                                                     error_description=ret__error_description,
                                                     detail_state_info={
                                                         "class_name": self.__class__.__name__,
                                                         "function_name": "execute__Step__Clean_Up",
                                                         "is_error": False
                                                     })
        return retObj

    def test_class_instance(self):
        print("imerg.test_class_instance: Reached the end.")