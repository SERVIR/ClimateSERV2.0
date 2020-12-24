# select_from_netcdf.py

import json
import os
import shutil
import sys
import uuid
import time
import random

#print("select_from_netcdf: sys.path: " + str(sys.path))

import shapely
import shapely.geometry
from shapely.geometry import Polygon
import xarray
import calendar
from datetime import datetime
import rasterio
import rasterio.mask
import rasterio.crs as rasterio_crs
from rasterio.transform import Affine
import numpy as np
#from rasterstats import zonal_stats
#import rioxarray



# # External Django Setup (Giving access to django models and database from a script that does not use manage.py)
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "climateserv_2_0_serverside.settings")
# import django
# django.setup()
#
#
#from climateserv_2_0_serverside import settings as climateserv_2_0_serverside__settings
#from django.core.management import settings
#
# Now access any django models
from api_v2.app_models.model_ETL_Dataset import ETL_Dataset
from api_v2.app_models.model_Task_Log import Task_Log
from api_v2.app_models.model_WorkerProcess import WorkerProcess
from api_v2.app_models.model_Config_Setting import Config_Setting


# select_polygon_from_netcdf_from_params

# TESTS
#
# # Can we read from the database?
# # # python console
# # # # from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf as SelectFromNetCDF
# # # # SelectFromNetCDF.test__CanReadFromDjangoDB()



# Usage
# # from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf as SelectFromNetCDF
# # SelectFromNetCDF.test_select_data__From_SubmitDataRequest_Call(params)

class Select_From_Netcdf():



    # Main Core Code to process a job.
    @staticmethod
    def process_job(job_uuid):
        returnData = {}
        errors = []
        warnings = []

        try:
            # Pull in params from the task_log for this job uuid
            # operationtype, datatype, etc

            # Get the job info and extract the request params from it.
            task_log__job_info__obj                     = Task_Log.objects.filter(job_uuid=str(job_uuid))[0].to_JSONable_Object()
            task_log__job_info__obj_additional_json     = task_log__job_info__obj["additional_json"]
            job__request_params                         = task_log__job_info__obj_additional_json['request_params']

            operationtype   = str(job__request_params['operationtype']).strip()     # Operation Guide, (0 == max, 1 == min, 5 == mean, 6 == download)
            datatype        = str(job__request_params['datatype']).strip()          # str(99) # str(2)      # str(2) == ndvi east africa
            begintime       = str(job__request_params['begintime']).strip()         # "01/01/2020"
            endtime         = str(job__request_params['endtime']).strip()           # "03/01/2020"  # "05/01/2020"
            geometry = None
            try:
                #geometry = str(job__request_params['geometry']).strip()           #
                geometry = job__request_params['geometry']
            except:
                pass


            # print("Debuging: (operationtype): " + str(operationtype))
            # print("Debuging: (datatype): " + str(datatype))
            # print("Debuging: (begintime): " + str(begintime))
            # print("Debuging: (endtime): " + str(endtime))
            # print("Debuging: (geometry): " + str(geometry))


            # Init State
            has_errors = False
            out_json_data = {}

            # Operation Type (What Operation to perform on the data)
            # operation_enum = "mean"  # min, max, mean, download   # DONE - Look this up by 'operationtype'
            operationtype = int(operationtype)
            operation_enum = Task_Log.get_operation_type_from_legacy_operation_int(operation_int=operationtype)

            # Dataset type (Which dataset are we performing on)
            # def get_dataset_by_legacy_datatype(legacy_datatype="0"):  // return existing_dataset_json, is_error, error_message
            dataset_json, is_error_getting_dataset, error_message_getting_dataset = ETL_Dataset.get_dataset_by_legacy_datatype(legacy_datatype=datatype)
            nc4_variable_name = "UNSET"

            if (is_error_getting_dataset == True):
                errors.append("Error Looking up a matching Dataset for parameter 'datatype' " + str(datatype) + " : " + str(error_message_getting_dataset))
                has_errors = True

            # Get the NC4 Variable Name from the Dataset object.
            if (has_errors == False):
                try:
                    nc4_variable_name = str(dataset_json['dataset_nc4_variable_name'])  # ['nc4_variable_name'])
                except:
                    sysErrorData = str(sys.exc_info())
                    error_message = "Error getting the nc4 variable name from the dataset object.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True

            # Defaults
            is_lat_order_reversed = 'False'
            is_lat_order_reversed_BOOL = False
            if (has_errors == False):
                try:
                    # Make sure each dataset type's 'is_lat_order_reversed' is set to True or False
                    is_lat_order_reversed = str(dataset_json['is_lat_order_reversed'])
                    is_lat_order_reversed_BOOL = False
                    if (is_lat_order_reversed == 'True'):
                        is_lat_order_reversed_BOOL = True
                    else:
                        is_lat_order_reversed_BOOL = False
                except:
                    sysErrorData = str(sys.exc_info())
                    error_message = "Error getting the is_lat_order_reversed flag from the dataset object.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True

            dataset_base_directory_path = "/UNSET/"
            if (has_errors == False):
                try:
                    dataset_base_directory_path = str(dataset_json['dataset_base_directory_path'])
                except:
                    sysErrorData = str(sys.exc_info())
                    error_message = "Error getting the dataset_base_directory_path from the dataset object.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True

            # Earliest Datetime
            earliest_datetime = ""
            if (has_errors == False):
                try:
                    earliest_datetime = datetime.strptime(begintime, "%m/%d/%Y")  # ("01/01/2020", "%m/%d/%Y")
                except:
                    sysErrorData = str(sys.exc_info())
                    error_message = "Error processing input parameter: 'begintime' " + str(begintime) + ".  Expected date format is: %m/%d/%Y.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True

            # Latest Datetime
            latest_datetime = ""
            if (has_errors == False):
                try:
                    latest_datetime = datetime.strptime(endtime, "%m/%d/%Y")  # ("03/01/2020", "%m/%d/%Y")
                except:
                    sysErrorData = str(sys.exc_info())
                    error_message = "Error processing input parameter: 'endtime' " + str(endtime) + ".  Expected date format is: %m/%d/%Y.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True

            # If we don't have any errors at this point, we now proceed to setting up working directory and processing the job itself (processing the geometry happens down stream in here)
            if (has_errors == False):
                try:

                    # Set up the directories and filenames
                    base_working_dir = Config_Setting.get_value(setting_name="PATH__BASE_TEMP_WORKING_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/temp_tasks_processing/")  # Append   "<Job_UUID>/"
                    base_output_dir = Config_Setting.get_value(setting_name="PATH__BASE_DATA_OUTPUT_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/")  # Append   "<Job_UUID>/"

                    job_working_dir = os.path.join(base_working_dir, str(job_uuid))
                    job_output_dir = os.path.join(base_output_dir, str(job_uuid))

                    raw_tif_dir = os.path.join(job_working_dir, "raw")
                    cropped_tif_dir = os.path.join(job_working_dir, "cropped")

                    # Using the job uuid as the base file name.
                    output_base_file_name = str(job_uuid)
                    # output_zip_file_name = str(new_job_uuid) + '.zip'

                    json_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.json')  # ../job_data/tasks_data_out/<job_id>/<job_id>.json  # // Contains json data clientside expects
                    zip_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.zip')  # ../job_data/tasks_data_out/<job_id>/<job_id>.zip  # // Contains collection of tif files zipped up that an end user expects
                    zip_file_output_fullpath_NoExtension = os.path.join(job_output_dir, output_base_file_name)  # shutil.make_archive gives us an extra .zip at the end, so we need a version of this filename without the .zip on it.

                    # operation_enum = "mean"  # min, max, mean, download   # DONE - Look this up by 'operationtype'
                    is_download_data = False  # Is this a job to setup a zip file for data downloading?
                    if (operation_enum == "download"):
                        is_download_data = True


                    # Setup Temp Directory Paths (all of them)
                    had_error__CreatingDirectory_Raw, error_data = Task_Log.create_dir_if_not_exist(dir_path=raw_tif_dir)
                    had_error__CreatingDirectory_Cropped, error_data = Task_Log.create_dir_if_not_exist(dir_path=cropped_tif_dir)
                    had_error__CreatingDirectory_Output, error_data = Task_Log.create_dir_if_not_exist(dir_path=job_output_dir)

                    if (had_error__CreatingDirectory_Raw == True):
                        error_message = "There was an error when creating the raw tif directory: " + str(raw_tif_dir)
                        errors.append(error_message)
                        has_errors = True
                    if (had_error__CreatingDirectory_Cropped == True):
                        error_message = "There was an error when creating the cropped tif directory: " + str(cropped_tif_dir)
                        errors.append(error_message)
                        has_errors = True
                    if (had_error__CreatingDirectory_Output == True):
                        error_message = "There was an error when creating the data output directory: " + str(job_output_dir)
                        errors.append(error_message)
                        has_errors = True

                    #print("C")

                    #print("??? GOING TO HAVE TO DEAL WITH SHAPEFILES ????")

                    # Process the input geometry into a Shapely Polygon (Lat/Longs)
                    # geom_data__Control  = json.dumps( [[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]])
                    # Note, the json.dumps and json.loads provides a way for us to validate the JSON
                    geom_data = json.dumps(geometry['coordinates'][0])
                    geom_data_json = json.loads(geom_data)
                    poly_geojson = Polygon(geom_data_json)
                    # poly_geojson        = Polygon(json.loads(geom_data))
                    bounds = poly_geojson.bounds

                    #print("D")

                    # Get the Bounds and min/max lat/longs
                    # bounds = poly_geojson.bounds
                    min_Lat = float(bounds[0])  # miny
                    min_Long = float(bounds[1])  # minx
                    max_Lat = float(bounds[2])  # maxy
                    max_Long = float(bounds[3])  # maxx

                    # Code to reach into the 'dataset_base_directory_path' and read all the files, check their ranges and load up the file infos of any nc4 files we will need to read data from.

                    # Make a list of all the files found in the dataset_base_directory_path location
                    list_of_file_infos = []
                    for file in os.listdir(dataset_base_directory_path):
                        if file.endswith(".nc4"):
                            filename = str(file)

                            filename_parts = filename.split('.')
                            filename_time_part_index = -1
                            for idx, filename_part in enumerate(filename_parts):
                                # Looking for the T and Z in something like: '20200211T000000Z'
                                if (filename_part[-1].lower() == 'z'):
                                    if (filename_part[8].lower() == 't'):
                                        # Compare our time ranges to see if we are within the range we want
                                        iso_time_str = filename_part
                                        iso_time_datetime = datetime.strptime(iso_time_str, "%Y%m%dT%H%M%SZ")

                                        is_in_range = True
                                        if (iso_time_datetime >= earliest_datetime):
                                            # We are still in the range, nothing changes
                                            pass
                                        else:
                                            # We are not in the range, set the flag to false
                                            is_in_range = False

                                        if (iso_time_datetime <= latest_datetime):
                                            # We are still in the range, nothing changes
                                            pass
                                        else:
                                            # We are not in the range, set the flag to false
                                            is_in_range = False

                                        if (is_in_range == True):
                                            # Finally, set the index, setting this index value indicates this ia a file we want to keep in the list.
                                            filename_time_part_index = idx

                            if (filename_time_part_index == -1):
                                # Do nothing here,
                                pass
                            else:
                                file_info = {}
                                file_info['filename'] = filename
                                file_info['fullpath'] = str(os.path.join(dataset_base_directory_path, filename))
                                file_info['iso_time'] = str(filename_parts[filename_time_part_index])
                                list_of_file_infos.append(file_info)

                                # print(file)
                                # filename_only = str(file)
                                # fullpath = os.path.join(dataset_base_directory_path, file)

                        # END OF        if file.endswith(".nc4"):
                    # END OF        for file in os.listdir(dataset_base_directory_path):

                    # This is the output results for non-download types.
                    # This eventually gets written to a .json file
                    operation_calculations_Objects = []  # Store the array of each time slice calculation

                    # Things needed inside the loop but that don't need to be calculated on every single pass in the loop..
                    height_Lat_in_cords = max_Lat - min_Lat
                    width_Long_in_cords = max_Long - min_Long

                    # Protection from dividing by zero in later step
                    if (height_Lat_in_cords == 0):
                        height_Lat_in_cords = 0.01
                    if (width_Long_in_cords == 0):
                        width_Long_in_cords = 0.01

                    # Updated to correct values on First Dataset Pass
                    height_in_Pixels = 1  # arr.data.shape[1]
                    width_in_Pixels = 1  # arr.data.shape[2]
                    geom_data_json__ReProjected = []
                    shapes_list = []

                    # Data set Processing
                    # Since only the time indexes change (and the geometry does not), Some elements inside of this loop can be calculated once (on the first pass) and then reused for each subsequent time index selection.
                    has_processed_atleast_1_dataset = False

                    # For tracking and updating progress
                    dataset_file_info__Counter = 0
                    total_number_of_file_infos = len(list_of_file_infos)
                    if(total_number_of_file_infos < 1):
                        total_number_of_file_infos = 1
                    num_of_tracking_activity_events = 10  # How many times we update progress during this job.
                    modulus_size = int(total_number_of_file_infos / num_of_tracking_activity_events)
                    if (modulus_size < 1):
                        modulus_size = 1
                    # print("DEBUG: SETUP JobProgress Update: (dataset_file_info__Counter): " + str(dataset_file_info__Counter))
                    # print("DEBUG: SETUP JobProgress Update: (total_number_of_file_infos): " + str(total_number_of_file_infos))
                    # print("DEBUG: SETUP JobProgress Update: (num_of_tracking_activity_events): " + str(num_of_tracking_activity_events))
                    # print("DEBUG: SETUP JobProgress Update: (modulus_size): " + str(modulus_size))

                    for dataset_file_info in list_of_file_infos:

                        # For Updating the progress
                        if (((dataset_file_info__Counter + 1) % modulus_size) == 0):
                            #current_progress = int( dataset_file_info__Counter / total_number_of_file_infos )
                            current_progress = int((dataset_file_info__Counter / total_number_of_file_infos) * 100)
                            Task_Log.set_JobProgress_To(job_uuid=job_uuid, current_progress_int=current_progress)
                            # print("DEBUG: INPROGRESS: JobProgress Update: (dataset_file_info__Counter): " + str(dataset_file_info__Counter))
                            # print("DEBUG: INPROGRESS: JobProgress Update: (modulus_size): " + str(modulus_size))
                            # print("DEBUG: INPROGRESS: JobProgress Update: (((dataset_file_info__Counter + 1) % modulus_size)): " + str(((dataset_file_info__Counter + 1) % modulus_size)))
                            # print("DEBUG: Counter: "+str(dataset_file_info__Counter)+".  Just set job progress to: (current_progress): " + str(current_progress))

                        dataset_file_location = dataset_file_info['fullpath']
                        dataset_file_location_FilenameOnly = dataset_file_info['filename']

                        # Select the dataset

                        # Name of the Variable inside the netcdf file
                        # var_to_select = "ndvi"
                        var_to_select = nc4_variable_name

                        # Opening the NC4 dataset file with xarray
                        nc4_data_set = xarray.open_dataset(dataset_file_location)

                        # Select data from the NC4 file, based on the selection
                        arr = ""
                        if (is_lat_order_reversed_BOOL == True):
                            arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(max_Lat, min_Lat))  # Remember, Lat is switched here
                        else:
                            arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(min_Lat, max_Lat))

                        # only do the following on the first pass through the loop.
                        if (has_processed_atleast_1_dataset == False):

                            height_in_Pixels = arr.data.shape[1]
                            width_in_Pixels = arr.data.shape[2]

                            geom_data_json__ReProjected = []
                            for cord_pair in geom_data_json:
                                lat = cord_pair[0]
                                long = cord_pair[1]

                                lat_partial = lat - min_Lat
                                lat_Pixel_Reproj = (lat_partial / height_Lat_in_cords) * height_in_Pixels

                                long_partial = long - min_Long
                                long_Pixel_Reproj = (long_partial / width_Long_in_cords) * width_in_Pixels

                                # CORRECT
                                cord_Pixel_Reproj = [lat_Pixel_Reproj, long_Pixel_Reproj]

                                # WRONG
                                # cord_Pixel_Reproj = [long_Pixel_Reproj, lat_Pixel_Reproj]

                                geom_data_json__ReProjected.append(cord_Pixel_Reproj)

                            # Create a new shapely polygon
                            shapely_poly_geojson_reprojected = Polygon(geom_data_json__ReProjected)
                            shapes_list = []
                            shapes_list.append(shapely_poly_geojson_reprojected)  # Crop operates on a list of shapes, it is ok if we have a list with 1 shape...

                        # END OF        if(has_processed_atleast_1_dataset == False):


                        # This block catches individual dataset granule errors.  Any errors here are recorded as warnings and do not halt the execution of the job.
                        try:
                            # Create the temp raw tiff file
                            raw_width = arr.shape[2]
                            raw_height = arr.shape[1]

                            # Checkpoint, if the width is 0 here, everything below will fail (it likely means that no data was selected)
                            # print("DEBUG: Value of (raw_width): " + str(raw_width))
                            if (raw_width == 0):
                                warning_message = "Generic Warning, no data found to select for dataset granule: " + str(dataset_file_location_FilenameOnly) + " .  Detail Warning: raw_width is equal to 0.  This will cause the next steps in this processing pipeline to fail.  The most likely cause of this error is that there was no data to select in the given range."
                                warnings.append(warning_message)
                                # error_message = "Generic Error, no data found to select.  Detail Error: raw_width is equal to 0.  This will cause the next steps in this processing pipeline to fail.  The most likely cause of this error is that there was no data to select in the given range."
                                # errors.append(error_message)
                                # print(error_message)
                                # has_errors = True

                            # Create the raw transform from the width of the original dataset
                            raw_Transform = Affine(raw_height / raw_width, 0.0, 0.0, 0.0, 1.0, 0.0)

                            # At this point in the code, it is safe to set this to True (All single pass processses should be calculated before this point)
                            has_processed_atleast_1_dataset = True

                            # Now process each time slice
                            # MOVED TO OUTER LOOP # operation_calculations_Objects = []  # Store the array of each time slice calculation
                            num_of_time_steps = arr.shape[0]
                            for arr_time_idx in range(0, num_of_time_steps):

                                # Get the xarray object for the single lat/long time slice
                                arr_single_LatLong_Time_Slice = arr[arr_time_idx]

                                # Epoch Time
                                epoch_time = arr_single_LatLong_Time_Slice.time.data.tolist() / 1000000000
                                epoch_time = int(epoch_time)  # Force to int to remove the <number>.0

                                datetime_time_string_for_file_name = datetime.fromtimestamp(epoch_time).strftime("%Y%m%dT%H%M%SZ")
                                datetime_time_string_for_json = datetime.fromtimestamp(epoch_time).strftime("%m/%d/%Y")

                                # Likely need to put this into a loop so we can name each tif file differently, after each granule
                                # tif_file_name_raw = "ZZ_ndvi_test_raw.tif"
                                # tif_file_name_cropped = "ZZ_ndvi_test_cropped.tif"
                                tif_file_name_raw = str(datetime_time_string_for_file_name) + "_raw.tif"
                                tif_file_name_cropped = str(datetime_time_string_for_file_name) + ".tif"  # Removed the 'cropped' part of the file name because this data gets zipped up.
                                tif_full_file_path__Raw = os.path.join(raw_tif_dir, tif_file_name_raw)  # Working_directory_path/<job_id>/raw/tif_file_name.tif
                                tif_full_file_path__Cropped = os.path.join(cropped_tif_dir, tif_file_name_cropped)  # Working_directory_path/<job_id>/cropped/tif_file_name.tif

                                temp_data_writing_array = np.zeros((1, arr.shape[1], arr.shape[2]), dtype=arr_single_LatLong_Time_Slice.dtype)

                                # Index 0 on 'temp_data_writing_array' is the single value time dimension
                                # # Rasterio needs this to be a 3d Array for the write functions to work.
                                temp_data_writing_array[0] = arr_single_LatLong_Time_Slice.data

                                # raw_rasterio_dataset = rasterio.open('ZZ_ndvi_test_raw.tif', 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                                raw_rasterio_dataset = rasterio.open(tif_full_file_path__Raw, 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                                # raw_rasterio_dataset.write(arr.data)  # // raw_rasterio_dataset.write(arr.data, 0)
                                raw_rasterio_dataset.write(temp_data_writing_array)
                                # crs = rasterio.crs.CRS({"init": "epsg:4326"})
                                crs = rasterio_crs.CRS({"init": "epsg:4326"})
                                raw_rasterio_dataset.crs = crs
                                raw_rasterio_dataset.close()

                                # Now load the tiff file and process it with a mask
                                # src_img = rasterio.open('ZZ_ndvi_test_raw.tif', 'r')  # raw_rasterio_dataset
                                src_img = rasterio.open(tif_full_file_path__Raw, 'r')  # raw_rasterio_dataset

                                # Crop by mask - grab the shapely list from up above and use it to crop out an image
                                # AND Create a new Tiff file from this result.
                                cropped_out_image, cropped_out_transform = rasterio.mask.mask(src_img, shapes_list)
                                cropped_out_meta = src_img.meta
                                cropped_out_meta.update({"driver": "GTiff", "height": arr.data.shape[1], "width": arr.data.shape[2], "transform": cropped_out_transform, "nodata": 0.0})
                                # cropped__rasterio_dataset = rasterio.open("test_CROPPED.tif", "w", **cropped_out_meta)
                                cropped__rasterio_dataset = rasterio.open(tif_full_file_path__Cropped, "w", **cropped_out_meta)
                                cropped__rasterio_dataset.write(cropped_out_image)
                                cropped__rasterio_dataset.close()

                                # DONE - INSIDE THIS BLOCK, WE NEED TO BUILD THE OBJECTS THAT GET SAVED TO JSON
                                # print("LOAD UP (operation_calculations_Objects) MAKE SURE TO BUILD THE JSON FILE HERE BY APPENDING EACH STAT VALUE AND PROPERLY ADDING THE EXPECTED PROPERTIES.  MAKE SURE TO SAVE THAT FILE AS WELL.")
                                ## Calculate the correct stats
                                # tif_file = "test_CROPPED.tif"
                                # stats_result = zonal_stats(tif_file, stats=['mean'])
                                # cropped_data_readonly = rasterio.open('test_CROPPED.tif', 'r')
                                cropped_data_readonly = rasterio.open(tif_full_file_path__Cropped, 'r')
                                stat_value = float(0.0)
                                operation_key_name = "default"
                                if (operation_enum == "mean"):  # min, max, mean
                                    operation_key_name = "avg"
                                    stat_value = float(cropped_data_readonly.read().mean())
                                #
                                if (operation_enum == "min"):  # min, max, mean
                                    operation_key_name = "min"
                                    stat_value = float(cropped_data_readonly.read().min())
                                #
                                if (operation_enum == "max"):  # min, max, mean
                                    operation_key_name = "max"
                                    stat_value = float(cropped_data_readonly.read().max())
                                #
                                if (operation_enum == "download"):
                                    operation_key_name = "download"
                                    stat_value = float(1.0)

                                # Example fragment of output
                                # # Example output from CSERV 1 (Legacy Support) # successCallback({"data": [{"date": "11/10/2019", "workid": "d4e240e7-8131-4c29-960b-1cca2d37b87d", "epochTime": "1573344000", "value": {"avg": 0.6790033448131554}}, {"date": "11/20/2019", "workid": "7bff39a4-6691-41ec-ae7d-e3a8a2228010", "epochTime": "1574208000", "value": {"avg": 0.6646363897534401}}, {"date": "11/30/2019", "workid": "dde2771c-8701-49c7-b99d-8968b95a0593", "epochTime": "1575072000", "value": {"avg": 0.6453001141912953}}]})
                                # # We can append new json fields/properties, but do not remove old ones.
                                #  DONE - Fix '"value": {"avg": 0.6790033448131554}' so that it also does ' "value": {"avg": 0.6790033448131554, "val": 0.6790033448131554} '

                                # DONE - Update: All of them - work out which of these lines below that we need..
                                new_calc_obj = {}
                                new_calc_obj["date"] = str(datetime_time_string_for_json)
                                new_calc_obj["workid"] = str(job_uuid)
                                new_calc_obj["epochTime"] = str(epoch_time)
                                value_object = {}
                                value_object[operation_key_name] = stat_value
                                value_object["val"] = stat_value
                                new_calc_obj["value"] = value_object
                                operation_calculations_Objects.append(new_calc_obj)

                            # END OF        for arr_time_idx in range(0, num_of_time_steps):

                        except:
                            sysErrorData = str(sys.exc_info())
                            warning_message = "Generic Warning, There was an uncaught error when processing dataset granule: " + str(dataset_file_location_FilenameOnly) + " .  System Error Message: " + str(sysErrorData)
                            warnings.append(warning_message)

                        # Increment the counter
                        dataset_file_info__Counter = dataset_file_info__Counter + 1
                        pass

                    # END OF    for dataset_file_info in list_of_file_infos:
                    pass

                    # OUTSIDE LOOP (After all stats have been processed)
                    # Write a JSON file here - remember, if this is a download data type, we still write a json file.
                    job_output_json = {}
                    job_output_json["data"] = operation_calculations_Objects
                    # with open('data.json', 'w') as f:
                    with open(json_file_output_fullpath, 'w') as f:
                        json.dump(job_output_json, f)
                    returnData['job_result_json'] = json.dumps(job_output_json)

                    # OUTSIDE LOOP (After all tif files have been generated for the whole timeseries)
                    if (is_download_data == True):
                        # This line zips up the entire <cropped_tif_dir> directory and places it into a zip archive located at <zip_file_output_fullpath>
                        did_zip_files = False
                        try:
                            shutil.make_archive(zip_file_output_fullpath_NoExtension, 'zip', cropped_tif_dir)  # Gives us, <job_id>.zip
                            did_zip_files = True
                        except:
                            did_zip_files = False
                            sysErrorData = str(sys.exc_info())
                            error_message = "There was an error when creating the zip archive of the group of output data files:  System Error Message: " + str(sysErrorData)
                            errors.append(error_message)
                            has_errors = True

                        if (did_zip_files == False):
                            # at this point, This Job Errored, make sure to store that in the database.
                            error_message = "There was an unknown error when creating the zip archive of the group of output data files."
                            errors.append(error_message)
                            has_errors = True
                            pass
                    # TODO - CONTINUE HERE!
                    # TODO - CONTINUE HERE!


                except:
                    # END OF BIG TRY
                    sysErrorData = str(sys.exc_info())
                    error_message = "Uncaught Error when processing job: " + str(job_uuid) + ".  This error occurred after processing job input params.  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)
                    has_errors = True
            # END OF    if (has_errors == False):


        except:
            # END OF BIGGEST TRY block
            sysErrorData = str(sys.exc_info())
            error_message = "Uncaught Error when processing job: " + str(job_uuid) + ".  System Error Message: " + str(sysErrorData)
            errors.append(error_message)
            has_errors = True
        # END OF:   Trye:  - Outer Try / Except block

        returnData['errors']    = errors
        returnData['warnings']  = warnings
        return returnData, has_errors






    # Endless loop stuff
    # did_find_available_job, job_uuid, total_jobs_available = Task_Log.get_job_uuid_for_a_waiting_job()

    @staticmethod
    def worker_process_endless_loop(worker_db_uuid):

        if(worker_db_uuid == ""):
            print("worker_process_endless_loop:  There was a problem starting the worker.  worker_db_uuid was blank.  check start_worker.py to find out why this function is being called with a blank uuid!  Exiting now.")
            return

        # Stagger the sleep time so jobs don't run at the exact same moments (0.8 seconds to 3.5 second rest intervals)
        sleep_seconds = float(random.randint(800, 3500) / 1000)
        max_idle_checks = 20
        is_worker_running = True
        test_checkpoint_counter = 0
        print("******************************************************************************************************************************")
        print("*   Worker Id: "+str(worker_db_uuid)+": About to Enter the Endless Loop")
        print("******************************************************************************************************************************")
        while (is_worker_running == True):
            #print("worker_process_endless_loop: Starting a run through the loop at: (test_checkpoint_counter): " + str(test_checkpoint_counter) + " out of (max_idle_checks): " + str(max_idle_checks))
            #print("worker_process_endless_loop: Worker Id: "+str(worker_db_uuid)+":  Starting a run through the loop at: (test_checkpoint_counter): " + str(test_checkpoint_counter))

            # Check for a job to process - This gives us a single job_uuid to process
            did_find_available_job, waiting_to_process_job_uuid, total_jobs_available = Task_Log.get_job_uuid_for_a_waiting_job()
            if (did_find_available_job == True):
                # Found a job to process
                print(" Worker Id: "+str(worker_db_uuid)+".  Found a Job to process.  About to start processing it. (job_uuid): " + str(waiting_to_process_job_uuid) + ".  Note, Including this job, there are " + str(total_jobs_available) + " jobs still in the queue.")

                # Tell the database that this worker is currently processing a job.
                WorkerProcess.set_is_processing_job(worker_uuid=str(worker_db_uuid).strip(), is_processing_job_value=True)
                #
                # Do the work to process the job (all in this functioncall)
                returnData, has_errors = Select_From_Netcdf.process_job(job_uuid=waiting_to_process_job_uuid)
                #
                # Tell the database that this worker is NOT currently processing a job.
                WorkerProcess.set_is_processing_job(worker_uuid=str(worker_db_uuid).strip(), is_processing_job_value=False)

                if (has_errors == True):
                    # Sets the error flag on the task_log for this job
                    Task_Log.flag_Job_As__Is_Errored(job_uuid=waiting_to_process_job_uuid)
                    #print("DEBUG: worker_process_endless_loop: Job: " + str(waiting_to_process_job_uuid) + " had an error.  It has been flagged in the database.")
                    print(" Worker Id: " + str(worker_db_uuid) + ": had en error when processing job_uuid: " + str(waiting_to_process_job_uuid) + ".  This error has been flagged in the Task_Log table for this job uuid.")

                # Inject this worker's db uuid (in case we need to track which worker did the job).
                returnData['worker_db_uuid'] = str(worker_db_uuid).strip()

                # Job Processing is complete, send the returnData over to the Task Log to be stored with this job info.
                Task_Log.set_JobStatus_To__Processing_Complete(job_uuid=waiting_to_process_job_uuid, job_result_info=returnData)
                #print("DEBUG: worker_process_endless_loop: Completed Processing complete for Job: " + str(waiting_to_process_job_uuid))
                #print("DEBUG: worker_process_endless_loop: Completed Processing complete for Job: " + str(waiting_to_process_job_uuid))
                print(" Worker Id: " + str(worker_db_uuid) + ": Completed Processing Job: " + str(waiting_to_process_job_uuid))

                pass
            else:
                # No jobs are waiting to process, do nothing else
                pass

            # Sleep and then increment the counter, then check for exit conditions
            time.sleep(sleep_seconds)
            #print("worker_process_endless_loop: Tick")
            #if ((test_checkpoint_counter % 5) == 0):
            # every 5000 cycles through the loop, output something so we know the workers are still alive!
            if ((test_checkpoint_counter % 5000) == 0):
                print("worker_process_endless_loop: Periodic Tick: (test_checkpoint_counter): " + str(test_checkpoint_counter))

            #
            test_checkpoint_counter = test_checkpoint_counter + 1
            WorkerProcess.increment_worker_idle_count(worker_uuid=str(worker_db_uuid).strip())
            # # Debug, Check for max_idle_checks before turning off
            # if (test_checkpoint_counter > max_idle_checks):
            #     is_worker_running = False

            # Check the database for a stop signal, if there is a stop signal, exit the loop.
            should_worker_still_be_running = WorkerProcess.is_worker_still_running(worker_uuid=str(worker_db_uuid).strip())
            if (should_worker_still_be_running == False):
                is_worker_running = False

            #print("")

        print("")
        print("******************************************************************************************************************************")
        print("*   Worker Id: " + str(worker_db_uuid) + ": Received a stop signal: (test_checkpoint_counter): " + str(test_checkpoint_counter))
        print("*  Exiting now")
        print("******************************************************************************************************************************")
        pass



    # DONE - Endless Loop for workers
    # DONE - Code to reach into the task log model and get the next task to process (and set that task to 'inprogress')
    # DONE -- Code on the Task Log Model to hold ALL props (including list of params) AND a way to retrieve task data (some other json value after the job is done)
    # DONE - Code to Lookup Datatypes (Legacy Datatypes)
    # DONE - Code to Lookup Operationtypes (Legacy OperationTypes)


    # Next Up
    # # Write the submit data request input function (API) that will ACTUALLY create a job and save it in the database.
    # # Write the endless loop where the worker checks every few seconds for a job to process (by selecting from the jobs whose status are still set to 'waiting_to_start', and then calls the core function to do the work. - periodically output as they wait and work
    # # Write the Core function to actually take in a job_uuid input and then do all the work (and update the job status/ etc)


    @staticmethod
    def test__almostEndlessLoop_for_worker():
        # Runs for 'max_idle_checks' loop checks

        # Datamodel
        # # Is Worker processing a job?             Bool       // When a worker starts processing a job, this should be set to True, when a worker finishes processing a job, this should be set to False
        # # Should_Worker_Be_Stopped                Bool       // When we disable a worker from the database level, this gets set to True, when a worker starts / initializes, this should be set to False
        # # current_run_idle_check_counter          BigInt     // How many times has this worker done it's idle checkpoint since the last time it has been turned on?  Reset this to 0 when the worker is first initialized

        worker_db_uuid = "abcdefg"

        # Stagger the sleep time so jobs don't run at the exact same moments (0.8 seconds to 3.5 second rest intervals)
        sleep_seconds = float(random.randint(800, 3500) / 1000)
        max_idle_checks = 20
        is_worker_running = True
        test_checkpoint_counter = 0
        print("******************************************************************************************************************************")
        print("*  About to Enter the Loop")
        print("******************************************************************************************************************************")
        while(is_worker_running == True):
            print("test__almostEndlessLoop_for_worker: Starting a run through the loop at: (test_checkpoint_counter): " + str(test_checkpoint_counter) + " out of (max_idle_checks): " + str(max_idle_checks))

            # Check for a job to process - This gives us a single job_uuid to process
            did_find_available_job, waiting_to_process_job_uuid, total_jobs_available = Task_Log.get_job_uuid_for_a_waiting_job()
            if(did_find_available_job == True):
                # Found a job to process
                print("Found a Job to process.  About to start processing it. (job_uuid): " + str(waiting_to_process_job_uuid) + ".  Note, Including this job, there are " + str(total_jobs_available) + " jobs still in the queue.")

                returnData, has_errors = Select_From_Netcdf.process_job(job_uuid=waiting_to_process_job_uuid)
                if(has_errors == True):
                    # Sets the error flag on the task_log for this job
                    Task_Log.flag_Job_As__Is_Errored(job_uuid=waiting_to_process_job_uuid)
                    print("DEBUG: test__almostEndlessLoop_for_worker: Job: " + str(waiting_to_process_job_uuid) + " had an error.  It has been flagged in the database.")

                # Inject this worker's db uuid (in case we need to track which worker did the job).
                returnData['worker_db_uuid'] = str(worker_db_uuid).strip()

                # Job Processing is complete, send the returnData over to the Task Log to be stored with this job info.
                Task_Log.set_JobStatus_To__Processing_Complete(job_uuid=waiting_to_process_job_uuid, job_result_info=returnData)
                print("DEBUG: test__almostEndlessLoop_for_worker: Completed Processing complete for Job: " + str(waiting_to_process_job_uuid))

                pass
            else:
                # No jobs are waiting to process, do nothing else
                pass


            # Sleep and then increment the counter, then check for exit conditions
            time.sleep(sleep_seconds)
            #
            test_checkpoint_counter = test_checkpoint_counter + 1
            # Debug, Check for max_idle_checks before turning off
            if(test_checkpoint_counter > max_idle_checks):
                is_worker_running = False
            # Check the database for a stop signal, if there is a stop signal, exit the loop.
            # # TODO!

            print("")
        print("")
        print("******************************************************************************************************************************")
        print("*  test_checkpoint_counter: Completed ALL cycles through the loop: (test_checkpoint_counter): " + str(test_checkpoint_counter))
        print("*  Exiting now")
        print("******************************************************************************************************************************")
        pass

    @staticmethod
    def test__Create_New_TaskLog__and_Modify_TaskLog():

        ip_address = "0.0.0.1"

        # # Test 1 - Just create a new job with a new uuid
        # job_uuid = Task_Log.make_new_job_uuid()
        # request_params = {}
        # request_params['some_param_here'] = "some value here"
        # is_task_created, error_message = Task_Log.create_new_task(job_uuid=job_uuid, request_params=request_params, ip_address=ip_address)
        #
        # print("test__Create_New_TaskLog: (is_task_created): " + str(is_task_created))
        # print("test__Create_New_TaskLog: (error_message): " + str(error_message))
        # print("test__Create_New_TaskLog: (job_uuid): " + str(job_uuid))


        # # Test 2 - Set a created job to inprogress and set the processing progress to 40%,
        # Task_Log.set_JobStatus_To__In_Progress(job_uuid=job_uuid)
        # Task_Log.set_JobProgress_To(job_uuid=job_uuid, current_progress_int=40)
        # print("test__Create_New_TaskLog: test 2 is complete, go check and see if we have an in_progress job")

        # # Test 3 - Set a job to complete (progress should automatically get set to 100%
        # job_result_info = {}
        # job_result_info['some_finished_result_param'] = "A value that appears after a job is done"
        # Task_Log.set_JobStatus_To__Processing_Complete(job_uuid=job_uuid, job_result_info=job_result_info)
        # print("test__Create_New_TaskLog: test 3 is complete, go check and see if we have a completed job with result info in it's json")

        # # Test 4 - Set the error flag
        # Task_Log.set_JobStatus_To__In_Progress(job_uuid=job_uuid)
        # Task_Log.set_JobProgress_To(job_uuid=job_uuid, current_progress_int=80)
        # Task_Log.flag_Job_As__Is_Errored(job_uuid=job_uuid)
        # job_result_info = {}
        # job_result_info['some_finished_result_param'] = "There should be some other errors here, maybe collected and dumped from an error collecting array."
        # Task_Log.set_JobStatus_To__Processing_Complete(job_uuid=job_uuid, job_result_info=job_result_info)
        # print("test__Create_New_TaskLog: test 4 is complete, go check and see if we have a completed job with result info in it's json, AND that it's error flag is set to True")

        # Test 5 - Select a job id for a task that is 'Waiting_To_Start'
        did_find_available_job, waiting_to_process_job_uuid, total_jobs_available = Task_Log.get_job_uuid_for_a_waiting_job()
        print("test__Create_New_TaskLog: (did_find_available_job): " + str(did_find_available_job))
        print("test__Create_New_TaskLog: (waiting_to_process_job_uuid): " + str(waiting_to_process_job_uuid))
        print("test__Create_New_TaskLog: (total_jobs_available): " + str(total_jobs_available))

    # The Process Job code is at the core of Climateserv.  Writing this function in steps.  Each iteration of the 'test' functions gets further and further along until it runs as expected.


    @staticmethod
    def test_Process_Job_Test_1():
        returnData = {}
        errors = []
        warnings = []

        # # Simulated Inputs
        # job_uuid = str(uuid.uuid4())
        # job_uuid = "16811111" + job_uuid[8:]        # Simulated ID, so replacing the first 8 chars with 1's so that tests can be easily identified when examining the output.
        # operationtype   = str(6) #str(6)  #str(5)                # Operation Guide, (0 == max, 1 == min, 5 == mean, 6 == download)
        # datatype        = str(221) #str(99) # str(2)      # str(2) == ndvi east africa,  str(202) == imerg_early, str(221) == ESI 4wk
        # begintime       = "04/29/2020"      # NDVI_East_Africa: # "01/01/2020"
        # endtime         = "05/27/2020"      # NDVI_East_Africa: # "05/01/2020"
        # callback        = "successCallback"
        # #
        # # Geometry for ESI test
        # geometry = {"type": "Polygon", "coordinates": [[[34.992345835892738, 33.51888205432572], [34.8175587553681805, 40.766317125846676], [25.13264042444045324, 40.36063619076476], [25.17436096751475016, 31.47951303201745], [34.992345835892738, 33.51888205432572]]]}


        #
        # Larger Geometry for IMERG Tests
        #geometry = {"type": "Polygon", "coordinates": [[[44.992345835892738, 33.51888205432572], [44.8175587553681805, 60.766317125846676], [-0.13264042444045324, 60.36063619076476], [0.17436096751475016, 31.47951303201745], [44.992345835892738, 33.51888205432572]]]}
        #
        # Decent Geometry for NDV East Africa
        #geometry        = {"type": "Polygon", "coordinates": [[[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]]]}
        #
        #geometry = {"type": "Polygon", "coordinates": [[[34.992345835892738, 63.51888205432572], [34.8175587553681805, 70.766317125846676], [29.13264042444045324, 70.36063619076476], [34.992345835892738, 63.51888205432572]]]}
        # Deprecating List
        # intervaltype = str(0)
        # dateType_Category = "default"
        # isZip_CurrentDataType = "false"  # false


        # Imerg Input Tests
        # # Simulated Inputs
        # job_uuid = str(uuid.uuid4())
        # job_uuid = "16011111" + job_uuid[8:]  # Simulated ID, so replacing the first 8 chars with 1's so that tests can be easily identified when examining the output.
        # operationtype = str(6)  # str(6)  #str(5)                # Operation Guide, (0 == max, 1 == min, 5 == mean, 6 == download)
        # datatype = str(202)  # str(99) # str(2)      # str(2) == ndvi east africa,  str(202) == imerg_early
        # begintime = "12/31/2019"  # NDVI_East_Africa: # "01/01/2020"
        # endtime = "01/02/2020"  # NDVI_East_Africa: # "05/01/2020"
        # callback = "successCallback"
        # #
        # # Larger Geometry for IMERG Tests
        # geometry = {"type": "Polygon", "coordinates": [[[44.992345835892738, 33.51888205432572], [44.8175587553681805, 60.766317125846676], [-0.13264042444045324, 60.36063619076476], [0.17436096751475016, 31.47951303201745], [44.992345835892738, 33.51888205432572]]]}


        # The Standard Parameters used for the NDVI Test.  This one was used for much of the initial development/debugging
        # Simulated Inputs
        job_uuid = str(uuid.uuid4())
        job_uuid = "15211111" + job_uuid[8:]  # Simulated ID, so replacing the first 8 chars with 1's so that tests can be easily identified when examining the output.
        operationtype = str(5)  # str(6)  #str(5)                # Operation Guide, (0 == max, 1 == min, 5 == mean, 6 == download)
        datatype = str(2)  # str(99) # str(2)      # str(2) == ndvi east africa
        begintime = "1/1/2020" #"01/01/2020"
        endtime = "3/1/2020" #"03/01/2020"  # "05/01/2020"
        callback = "successCallback"
        geometry = {"type": "Polygon", "coordinates": [[[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]]]}



        print("test_Process_Job_Test_1: Starting Job Processing Test for SIMULATED (job_uuid): " + str(job_uuid))
        has_errors = False
        out_json_data = {}  # Example output from CSERV 1 (Legacy Support) # successCallback({"data": [{"date": "11/10/2019", "workid": "d4e240e7-8131-4c29-960b-1cca2d37b87d", "epochTime": "1573344000", "value": {"avg": 0.6790033448131554}}, {"date": "11/20/2019", "workid": "7bff39a4-6691-41ec-ae7d-e3a8a2228010", "epochTime": "1574208000", "value": {"avg": 0.6646363897534401}}, {"date": "11/30/2019", "workid": "dde2771c-8701-49c7-b99d-8968b95a0593", "epochTime": "1575072000", "value": {"avg": 0.6453001141912953}}]})
        # We can append new json fields/properties, but do not remove old ones.  # TODO - Fix '"value": {"avg": 0.6790033448131554}' so that it also does ' "value": {"avg": 0.6790033448131554, "val": 0.6790033448131554} '

        # Processing Each Input
        #

        # Operation Type (What Operation to perform on the data)
        #operation_enum = "mean"  # min, max, mean, download   # DONE - Look this up by 'operationtype'
        operationtype = int(operationtype)
        operation_enum = Task_Log.get_operation_type_from_legacy_operation_int(operation_int=operationtype)

        # Dataset type (Which dataset are we performing on)
        # def get_dataset_by_legacy_datatype(legacy_datatype="0"):  // return existing_dataset_json, is_error, error_message
        dataset_json, is_error_getting_dataset, error_message_getting_dataset = ETL_Dataset.get_dataset_by_legacy_datatype(legacy_datatype=datatype)
        nc4_variable_name = "UNSET"

        if(is_error_getting_dataset == True):
            errors.append("Error Looking up a matching Dataset for parameter 'datatype' "+str(datatype)+" : " + str(error_message_getting_dataset))
            has_errors = True

        # Get the NC4 Variable Name from the Dataset object.
        if (has_errors == False):
            try:
                nc4_variable_name = str(dataset_json['dataset_nc4_variable_name']) # ['nc4_variable_name'])
            except:
                sysErrorData = str(sys.exc_info())
                error_message = "Error getting the nc4 variable name from the dataset object.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True


        # Defaults
        is_lat_order_reversed = 'False'
        is_lat_order_reversed_BOOL = False
        if (has_errors == False):
            try:
                # Make sure each dataset type's 'is_lat_order_reversed' is set to True or False
                is_lat_order_reversed = str(dataset_json['is_lat_order_reversed'])
                is_lat_order_reversed_BOOL = False
                if (is_lat_order_reversed == 'True'):
                    is_lat_order_reversed_BOOL = True
                else:
                    is_lat_order_reversed_BOOL = False
            except:
                sysErrorData = str(sys.exc_info())
                error_message = "Error getting the is_lat_order_reversed flag from the dataset object.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True


        dataset_base_directory_path = "/UNSET/"
        if (has_errors == False):
            try:
                dataset_base_directory_path = str(dataset_json['dataset_base_directory_path'])
            except:
                sysErrorData = str(sys.exc_info())
                error_message = "Error getting the dataset_base_directory_path from the dataset object.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True


        # Earliest Datetime
        earliest_datetime = ""
        if(has_errors == False):
            try:
                earliest_datetime = datetime.strptime(begintime, "%m/%d/%Y")  # ("01/01/2020", "%m/%d/%Y")
            except:
                sysErrorData = str(sys.exc_info())
                error_message = "Error processing input parameter: 'begintime' "+str(begintime)+".  Expected date format is: %m/%d/%Y.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True

        # Latest Datetime
        latest_datetime = ""
        if (has_errors == False):
            try:
                latest_datetime = datetime.strptime(endtime, "%m/%d/%Y")  # ("03/01/2020", "%m/%d/%Y")
            except:
                sysErrorData = str(sys.exc_info())
                error_message = "Error processing input parameter: 'endtime' "+str(endtime)+".  Expected date format is: %m/%d/%Y.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True

        # If we don't have any errors at this point, we now proceed to setting up working directory and processing the job itself (processing the geometry happens down stream in here)
        if (has_errors == False):
            try:

                # Set up the directories and filenames
                base_working_dir    = Config_Setting.get_value(setting_name="PATH__BASE_TEMP_WORKING_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/temp_tasks_processing/")  # Append   "<Job_UUID>/"
                base_output_dir     = Config_Setting.get_value(setting_name="PATH__BASE_DATA_OUTPUT_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/")  # Append   "<Job_UUID>/"

                job_working_dir     = os.path.join(base_working_dir, str(job_uuid))
                job_output_dir      = os.path.join(base_output_dir, str(job_uuid))

                raw_tif_dir         = os.path.join(job_working_dir, "raw")
                cropped_tif_dir     = os.path.join(job_working_dir, "cropped")

                # Using the job uuid as the base file name.
                output_base_file_name   = str(job_uuid)
                # output_zip_file_name = str(new_job_uuid) + '.zip'

                json_file_output_fullpath               = os.path.join(job_output_dir, output_base_file_name + '.json')     # ../job_data/tasks_data_out/<job_id>/<job_id>.json  # // Contains json data clientside expects
                zip_file_output_fullpath                = os.path.join(job_output_dir, output_base_file_name + '.zip')      # ../job_data/tasks_data_out/<job_id>/<job_id>.zip  # // Contains collection of tif files zipped up that an end user expects
                zip_file_output_fullpath_NoExtension    = os.path.join(job_output_dir, output_base_file_name)               # shutil.make_archive gives us an extra .zip at the end, so we need a version of this filename without the .zip on it.

                #operation_enum = "mean"  # min, max, mean, download   # DONE - Look this up by 'operationtype'
                is_download_data = False    # Is this a job to setup a zip file for data downloading?
                if(operation_enum == "download"):
                    is_download_data = True

                # Setup Temp Directory Paths (all of them)
                had_error__CreatingDirectory_Raw,       error_data      = Task_Log.create_dir_if_not_exist(dir_path=raw_tif_dir)
                had_error__CreatingDirectory_Cropped,   error_data      = Task_Log.create_dir_if_not_exist(dir_path=cropped_tif_dir)
                had_error__CreatingDirectory_Output,    error_data      = Task_Log.create_dir_if_not_exist(dir_path=job_output_dir)

                if (had_error__CreatingDirectory_Raw == True):
                    error_message = "There was an error when creating the raw tif directory: " + str(raw_tif_dir)
                    errors.append(error_message)
                    has_errors = True
                if (had_error__CreatingDirectory_Cropped == True):
                    error_message = "There was an error when creating the cropped tif directory: " + str(cropped_tif_dir)
                    errors.append(error_message)
                    has_errors = True
                if (had_error__CreatingDirectory_Output == True):
                    error_message = "There was an error when creating the data output directory: " + str(job_output_dir)
                    errors.append(error_message)
                    has_errors = True


                print("GOING TO HAVE TO DEAL WITH SHAPEFILES")
                # Process the input geometry into a Shapely Polygon (Lat/Longs)
                # geom_data__Control  = json.dumps( [[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]])
                # Note, the json.dumps and json.loads provides a way for us to validate the JSON
                geom_data = json.dumps(geometry['coordinates'][0])
                geom_data_json = json.loads(geom_data)
                poly_geojson = Polygon(geom_data_json)
                # poly_geojson        = Polygon(json.loads(geom_data))
                bounds = poly_geojson.bounds

                # Get the Bounds and min/max lat/longs
                # bounds = poly_geojson.bounds
                min_Lat = float(bounds[0])  # miny
                min_Long = float(bounds[1])  # minx
                max_Lat = float(bounds[2])  # maxy
                max_Long = float(bounds[3])  # maxx



                # UPDATE: This won't tell us if the lats are reversed or not, the problem is within the NC4 file with how the axis is set, that is independant of the bounding box inputs.
                # DEBUG
                # try:
                #     print("")
                #     print("DEBUG: Attempting to check and see if we can tell if the lats are reversed by ONLY looking at the bounding box")
                #     print("DEBUG: (dataset_name): " + str(dataset_json["dataset_name"]))
                #     print("DEBUG: (nc4_variable_name): " + str(nc4_variable_name))
                #     print("DEBUG: (min_Lat): " + str(min_Lat))
                #     print("DEBUG: (max_Lat): " + str(max_Lat))
                #     print("")
                # except:
                #     sysErrorData = str(sys.exc_info())
                #     print("DEBUG:  UNCAUGHT ERROR WHEN ATTEMPTING TO DEBUG THE LATS_REVERSED SITUATION.  System Error Message: " + str(sysErrorData))
                #     print("")


                # DONE - WRITE CODE THAT LOOKS INTO THE DATASET_EXPECTED_DIRECTORY AND FINDS ALL FILES,

                # Code to reach into the 'dataset_base_directory_path' and read all the files, check their ranges and load up the file infos of any nc4 files we will need to read data from.

                # Make a list of all the files found in the dataset_base_directory_path location
                list_of_file_infos = []
                for file in os.listdir(dataset_base_directory_path):
                    if file.endswith(".nc4"):
                        filename = str(file)

                        filename_parts = filename.split('.')
                        filename_time_part_index = -1
                        for idx, filename_part in enumerate(filename_parts):
                            # Looking for the T and Z in something like: '20200211T000000Z'
                            if (filename_part[-1].lower() == 'z'):
                                if (filename_part[8].lower() == 't'):
                                    # Compare our time ranges to see if we are within the range we want
                                    iso_time_str = filename_part
                                    iso_time_datetime = datetime.strptime(iso_time_str, "%Y%m%dT%H%M%SZ")

                                    is_in_range = True
                                    if (iso_time_datetime >= earliest_datetime):
                                        # We are still in the range, nothing changes
                                        pass
                                    else:
                                        # We are not in the range, set the flag to false
                                        is_in_range = False

                                    if (iso_time_datetime <= latest_datetime):
                                        # We are still in the range, nothing changes
                                        pass
                                    else:
                                        # We are not in the range, set the flag to false
                                        is_in_range = False

                                    if (is_in_range == True):
                                        # Finally, set the index, setting this index value indicates this ia a file we want to keep in the list.
                                        filename_time_part_index = idx


                        if (filename_time_part_index == -1):
                            # Do nothing here,
                            pass
                        else:
                            file_info = {}
                            file_info['filename'] = filename
                            file_info['fullpath'] = str(os.path.join(dataset_base_directory_path, filename))
                            file_info['iso_time'] = str(filename_parts[filename_time_part_index])
                            list_of_file_infos.append(file_info)

                            # print(file)
                            # filename_only = str(file)
                            # fullpath = os.path.join(dataset_base_directory_path, file)

                    # END OF        if file.endswith(".nc4"):
                # END OF        for file in os.listdir(dataset_base_directory_path):


                # End of Directory name processing.
                # list_of_file_infos
                # list_of_file_infos['filename']        // filename The Filename ONLY
                # list_of_file_infos['fullpath']        // fullpath Full local path to a specific NetCDF file
                # list_of_file_infos['iso_time']        // iso_time The part of the filename that contains time, iso time format. (with T and Z in it)




                # DONE - WRAP THIS WHOLE CHUNK INTO A LOOP THAT ITERATES THROUGH DATASET_LOCATIONS - MAKE SURE THAT WE ONLY OPEN AND SELECT DATA FROM THE FILES THAT FALL WITHIN THE PROPER TIME RANGES - WHICH MEANS WE HAVE TO PARSE EACH FILE NAME FOR IT'S DATETIME AND COMPARE IT TO OUR DATETIME RANGE




                # This is the output results for non-download types.
                # This eventually gets written to a .json file
                operation_calculations_Objects = []  # Store the array of each time slice calculation




                # Things needed inside the loop but that don't need to be calculated on every single pass in the loop..
                height_Lat_in_cords = max_Lat - min_Lat
                width_Long_in_cords = max_Long - min_Long

                # Protection from dividing by zero in later step
                if (height_Lat_in_cords == 0):
                    height_Lat_in_cords = 0.01
                if (width_Long_in_cords == 0):
                    width_Long_in_cords = 0.01

                # Updated to correct values on First Dataset Pass
                height_in_Pixels    = 1 #arr.data.shape[1]
                width_in_Pixels     = 1 #arr.data.shape[2]
                geom_data_json__ReProjected = []
                shapes_list = []

                # Data set Processing
                # Since only the time indexes change (and the geometry does not), Some elements inside of this loop can be calculated once (on the first pass) and then reused for each subsequent time index selection.
                has_processed_atleast_1_dataset = False
                for dataset_file_info in list_of_file_infos:
                    dataset_file_location = dataset_file_info['fullpath']
                    dataset_file_location_FilenameOnly = dataset_file_info['filename']





                    # Select the dataset
                    # The Location of an NDVI nc4 file

                    # print("UPDATE THIS CODE SO THAT THERE IS A LIST OF DATASET FILE LOCATIONS AND THEY CAN HANDLE SELECTING (OR TRYING TO SELECT) EACH ONE.  IF ANY OF THEM FAIL, THEN WE SIMPLY GET A WARNING AND THAT DATE/TIME GETS IGNORED. (AND APPENDED TO AN EXPECTED_BUT_MISSING DATE_TIME LIST WHICH GOES BACK WITH THE JSON")
                    # print(" THE CODE TO GET THE DIRECTORY FOR A DATASET SHOULD HAPPEN OUTSIDE OF THE LOOP (AT THE SAME TIME WE LOAD A DATASET'S INFO")
                    # print("  NOTE THAT EVEN DOWNLOAD JOBS HAVE A JSON FILE ASSOCIATED WITH THEM, THE JSON FOR A DOWNLOAD JOB IS VERY BASIC AND JUST CONTAINS A FILE NAME FOR THE ZIP FILE")
                    # dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"
                    # # TODO - WRITE A FUNCTION ON THE ETL_DATASET MODEL SO THAT WE CAN LOOK UP THE CORRECT DATASET FILE LOCATION (THIS SHOULD RETURN A DIRECTORY AT FIRST)
                    # # TODO - MOVE THE BELOW CODE INSIDE THE LOOP (SO SELECTING THE NETCDF FILE IS IN A LOOP NOW, WITH EACH NC4 FILE BEING THE OUTER LOOP AND THEN EACH TIME STEP BEING THE INNER LOOP)




                    # Name of the Variable inside the netcdf file
                    #var_to_select = "ndvi"
                    var_to_select = nc4_variable_name

                    # Opening the NC4 dataset file with xarray
                    nc4_data_set = xarray.open_dataset(dataset_file_location)

                    # Select data from the NC4 file, based on the selection
                    arr = ""
                    if(is_lat_order_reversed_BOOL == True):
                        arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(max_Lat, min_Lat))  # Remember, Lat is switched here
                    else:
                        arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(min_Lat, max_Lat))






                    # only do the following on the first pass through the loop.
                    if(has_processed_atleast_1_dataset == False):

                        height_in_Pixels = arr.data.shape[1]
                        width_in_Pixels = arr.data.shape[2]

                        geom_data_json__ReProjected = []
                        for cord_pair in geom_data_json:
                            lat = cord_pair[0]
                            long = cord_pair[1]

                            lat_partial = lat - min_Lat
                            lat_Pixel_Reproj = (lat_partial / height_Lat_in_cords) * height_in_Pixels

                            long_partial = long - min_Long
                            long_Pixel_Reproj = (long_partial / width_Long_in_cords) * width_in_Pixels

                            # CORRECT
                            cord_Pixel_Reproj = [lat_Pixel_Reproj, long_Pixel_Reproj]

                            # WRONG
                            # cord_Pixel_Reproj = [long_Pixel_Reproj, lat_Pixel_Reproj]

                            geom_data_json__ReProjected.append(cord_Pixel_Reproj)

                        # Create a new shapely polygon
                        shapely_poly_geojson_reprojected = Polygon(geom_data_json__ReProjected)
                        shapes_list = []
                        shapes_list.append(shapely_poly_geojson_reprojected)  # Crop operates on a list of shapes, it is ok if we have a list with 1 shape...

                    # END OF        if(has_processed_atleast_1_dataset == False):




                    # DONE - WRAP ALL SINGLE DATASET TIME FRAME STUFF INTO THIS TRY/EXCEPT, IF ANYTHING IN HERE FAILS, IT IS ONLY WARNINGS, IT DOES NOT PREVENT THE PROCESSING OF OTHER FILES.
                    # This block catches individual dataset granule errors.  Any errors here are recorded as warnings and do not halt the execution of the job.
                    try:
                        # Create the temp raw tiff file
                        raw_width = arr.shape[2]
                        raw_height = arr.shape[1]

                        # Checkpoint, if the width is 0 here, everything below will fail (it likely means that no data was selected)
                        # print("DEBUG: Value of (raw_width): " + str(raw_width))
                        if (raw_width == 0):
                            warning_message = "Generic Warning, no data found to select for dataset granule: " + str(dataset_file_location_FilenameOnly) + " .  Detail Warning: raw_width is equal to 0.  This will cause the next steps in this processing pipeline to fail.  The most likely cause of this error is that there was no data to select in the given range."
                            warnings.append(warning_message)
                            #error_message = "Generic Error, no data found to select.  Detail Error: raw_width is equal to 0.  This will cause the next steps in this processing pipeline to fail.  The most likely cause of this error is that there was no data to select in the given range."
                            #errors.append(error_message)
                            #print(error_message)
                            #has_errors = True

                        # Create the raw transform from the width of the original dataset
                        raw_Transform = Affine(raw_height / raw_width, 0.0, 0.0, 0.0, 1.0, 0.0)


                        # At this point in the code, it is safe to set this to True (All single pass processses should be calculated before this point)
                        has_processed_atleast_1_dataset = True

                        # Now process each time slice
                        # MOVED TO OUTER LOOP # operation_calculations_Objects = []  # Store the array of each time slice calculation
                        num_of_time_steps = arr.shape[0]
                        for arr_time_idx in range(0, num_of_time_steps):

                            # Get the xarray object for the single lat/long time slice
                            arr_single_LatLong_Time_Slice = arr[arr_time_idx]

                            # Epoch Time
                            epoch_time = arr_single_LatLong_Time_Slice.time.data.tolist() / 1000000000
                            epoch_time = int(epoch_time) # Force to int to remove the <number>.0

                            datetime_time_string_for_file_name = datetime.fromtimestamp(epoch_time).strftime("%Y%m%dT%H%M%SZ")
                            datetime_time_string_for_json = datetime.fromtimestamp(epoch_time).strftime("%m/%d/%Y")

                            # Likely need to put this into a loop so we can name each tif file differently, after each granule
                            # TODO - Use that same etl code to build the time parts of the tiff file names.
                            # tif_file_name_raw = "ZZ_ndvi_test_raw.tif"
                            # tif_file_name_cropped = "ZZ_ndvi_test_cropped.tif"
                            tif_file_name_raw = str(datetime_time_string_for_file_name) + "_raw.tif"
                            tif_file_name_cropped = str(datetime_time_string_for_file_name) + ".tif"  # Removed the 'cropped' part of the file name because this data gets zipped up.
                            tif_full_file_path__Raw = os.path.join(raw_tif_dir, tif_file_name_raw)  # Working_directory_path/<job_id>/raw/tif_file_name.tif
                            tif_full_file_path__Cropped = os.path.join(cropped_tif_dir, tif_file_name_cropped)  # Working_directory_path/<job_id>/cropped/tif_file_name.tif

                            temp_data_writing_array = np.zeros((1, arr.shape[1], arr.shape[2]), dtype=arr_single_LatLong_Time_Slice.dtype)

                            # Index 0 on 'temp_data_writing_array' is the single value time dimension
                            # # Rasterio needs this to be a 3d Array for the write functions to work.
                            temp_data_writing_array[0] = arr_single_LatLong_Time_Slice.data

                            # raw_rasterio_dataset = rasterio.open('ZZ_ndvi_test_raw.tif', 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                            raw_rasterio_dataset = rasterio.open(tif_full_file_path__Raw, 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                            # raw_rasterio_dataset.write(arr.data)  # // raw_rasterio_dataset.write(arr.data, 0)
                            raw_rasterio_dataset.write(temp_data_writing_array)
                            # crs = rasterio.crs.CRS({"init": "epsg:4326"})
                            crs = rasterio_crs.CRS({"init": "epsg:4326"})
                            raw_rasterio_dataset.crs = crs
                            raw_rasterio_dataset.close()

                            # Now load the tiff file and process it with a mask
                            # src_img = rasterio.open('ZZ_ndvi_test_raw.tif', 'r')  # raw_rasterio_dataset
                            src_img = rasterio.open(tif_full_file_path__Raw, 'r')  # raw_rasterio_dataset

                            # Crop by mask - grab the shapely list from up above and use it to crop out an image
                            # AND Create a new Tiff file from this result.
                            cropped_out_image, cropped_out_transform = rasterio.mask.mask(src_img, shapes_list)
                            cropped_out_meta = src_img.meta
                            cropped_out_meta.update({"driver": "GTiff", "height": arr.data.shape[1], "width": arr.data.shape[2], "transform": cropped_out_transform, "nodata": 0.0})
                            # cropped__rasterio_dataset = rasterio.open("test_CROPPED.tif", "w", **cropped_out_meta)
                            cropped__rasterio_dataset = rasterio.open(tif_full_file_path__Cropped, "w", **cropped_out_meta)
                            cropped__rasterio_dataset.write(cropped_out_image)
                            cropped__rasterio_dataset.close()



                            # DONE - INSIDE THIS BLOCK, WE NEED TO BUILD THE OBJECTS THAT GET SAVED TO JSON
                            #print("LOAD UP (operation_calculations_Objects) MAKE SURE TO BUILD THE JSON FILE HERE BY APPENDING EACH STAT VALUE AND PROPERLY ADDING THE EXPECTED PROPERTIES.  MAKE SURE TO SAVE THAT FILE AS WELL.")
                            ## Calculate the correct stats
                            # tif_file = "test_CROPPED.tif"
                            # stats_result = zonal_stats(tif_file, stats=['mean'])
                            # cropped_data_readonly = rasterio.open('test_CROPPED.tif', 'r')
                            cropped_data_readonly = rasterio.open(tif_full_file_path__Cropped, 'r')
                            stat_value = float(0.0)
                            operation_key_name = "default"
                            if (operation_enum == "mean"):  # min, max, mean
                                operation_key_name = "avg"
                                stat_value = float(cropped_data_readonly.read().mean())
                            #
                            if (operation_enum == "min"):  # min, max, mean
                                operation_key_name = "min"
                                stat_value = float(cropped_data_readonly.read().min())
                            #
                            if (operation_enum == "max"):  # min, max, mean
                                operation_key_name = "max"
                                stat_value = float(cropped_data_readonly.read().max())
                            #
                            if (operation_enum == "download"):
                                operation_key_name = "download"
                                stat_value = float(1.0)

                            # Example fragment of output
                            # # Example output from CSERV 1 (Legacy Support) # successCallback({"data": [{"date": "11/10/2019", "workid": "d4e240e7-8131-4c29-960b-1cca2d37b87d", "epochTime": "1573344000", "value": {"avg": 0.6790033448131554}}, {"date": "11/20/2019", "workid": "7bff39a4-6691-41ec-ae7d-e3a8a2228010", "epochTime": "1574208000", "value": {"avg": 0.6646363897534401}}, {"date": "11/30/2019", "workid": "dde2771c-8701-49c7-b99d-8968b95a0593", "epochTime": "1575072000", "value": {"avg": 0.6453001141912953}}]})
                            # # We can append new json fields/properties, but do not remove old ones.
                            #  DONE - Fix '"value": {"avg": 0.6790033448131554}' so that it also does ' "value": {"avg": 0.6790033448131554, "val": 0.6790033448131554} '

                            # DONE - Update: All of them - work out which of these lines below that we need..
                            new_calc_obj = {}
                            new_calc_obj["date"] = str(datetime_time_string_for_json)
                            new_calc_obj["workid"] = str(job_uuid)
                            new_calc_obj["epochTime"] = str(epoch_time)
                            value_object = {}
                            value_object[operation_key_name] = stat_value
                            value_object["val"] = stat_value
                            new_calc_obj["value"] = value_object
                            operation_calculations_Objects.append(new_calc_obj)

                        # END OF        for arr_time_idx in range(0, num_of_time_steps):

                    except:
                        sysErrorData = str(sys.exc_info())
                        warning_message = "Generic Warning, There was an uncaught error when processing dataset granule: " + str(dataset_file_location_FilenameOnly) + " .  System Error Message: " + str(sysErrorData)
                        warnings.append(warning_message)


                # END OF    for dataset_file_info in list_of_file_infos:
                # DONE - WRAP THIS WHOLE CHUNK INTO A LOOP --- END








                # OUTSIDE LOOP (After all stats have been processed)
                # TODO - Write a JSON file here - remember, if this is a download data type, the json file will be much simpler, and just include the destination filename for the archive (maybe a path too?)
                job_output_json = {}
                job_output_json["data"] = operation_calculations_Objects
                #with open('data.json', 'w') as f:
                with open(json_file_output_fullpath, 'w') as f:
                    json.dump(job_output_json, f)
                returnData['job_result_json'] = json.dumps(job_output_json)



                # OUTSIDE LOOP (After all tif files have been generated for the whole timeseries)
                if (is_download_data == True):
                    # This line zips up the entire <cropped_tif_dir> directory and places it into a zip archive located at <zip_file_output_fullpath>
                    did_zip_files = False
                    try:
                        shutil.make_archive(zip_file_output_fullpath_NoExtension, 'zip', cropped_tif_dir)  # Gives us, <job_id>.zip
                        did_zip_files = True
                    except:
                        did_zip_files = False
                        sysErrorData = str(sys.exc_info())
                        error_message = "There was an error when creating the zip archive of the group of output data files:  System Error Message: " + str(sysErrorData)
                        errors.append(error_message)

                    if (did_zip_files == False):
                        # TODO - at this point, This Job Errored, make sure to store that in the database.
                        pass

            except:
                # END OF BIG TRY
                sysErrorData = str(sys.exc_info())
                error_message = "Uncaught Error when processing job: "+str(job_uuid)+".  This error occurred after processing job input params.  System Error Message: " + str(sysErrorData)
                errors.append(error_message)
                has_errors = True
        # END OF        if (has_errors == False):       // Main Job Processing Pipeline


        returnData['errors'] = errors
        returnData['warnings'] = warnings

        return returnData





    @staticmethod
    def test_select_data__From_SubmitDataRequest_Call():
        returnData = {}
        errors = []



        # Receive Input params
        # Legacy Only Datatypes
        datatype = str(2)
        intervaltype = str(0)
        operationtype = str(5)
        dateType_Category = "default"
        # Current (and legacy) Datatypes
        begintime = "01/01/2020"
        endtime = "03/01/2020"
        callback = "successCallback"
        isZip_CurrentDataType = "false"  # false
        #geometry = {"type": "Polygon", "coordinates": [ [[29.922637939453143, 17.369644034060244], [34.924163818359375, 16.96026258715051], [35.37734985351563, 13.112917604124647], [29.672698974609382, 13.676678908553882], [29.922637939453143, 17.369644034060244]] ]}
        geometry = {"type": "Polygon", "coordinates": [ [[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]]]}


        try:
            pass


            # (TESTING ONLY) Get new Job ID
            new_job_uuid = Task_Log.make_new_job_uuid()  # '37928bc5-75a2-4142-acab-599af5e5854d'
            base_working_dir     = Config_Setting.get_value(setting_name="PATH__BASE_TEMP_WORKING_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/temp_tasks_processing/")     # Append   "<Job_UUID>/"
            base_output_dir      = Config_Setting.get_value(setting_name="PATH__BASE_DATA_OUTPUT_DIR__TASKS", default_or_error_return_value="/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/job_data/tasks_data_out/")             # Append   "<Job_UUID>/"

            job_working_dir = os.path.join(base_working_dir, str(new_job_uuid))
            job_output_dir = os.path.join(base_output_dir, str(new_job_uuid))

            raw_tif_dir = os.path.join(job_working_dir, "raw")
            cropped_tif_dir = os.path.join(job_working_dir, "cropped")

            # Using the job uuid as the base file name.
            output_base_file_name = str(new_job_uuid)
            #output_zip_file_name = str(new_job_uuid) + '.zip'

            json_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name +'.json')         # ../job_data/tasks_data_out/<job_id>/<job_id>.json  # // Contains json data clientside expects
            zip_file_output_fullpath = os.path.join(job_output_dir, output_base_file_name + '.zip')         # ../job_data/tasks_data_out/<job_id>/<job_id>.zip  # // Contains collection of tif files zipped up that an end user expects
            zip_file_output_fullpath_NoExtension = os.path.join(job_output_dir, output_base_file_name)  # shutil.make_archive gives us an extra .zip at the end, so we need a version of this filename without the .zip on it.


            operation_enum = "mean"  # min, max, mean, download   # DONE - Look this up by 'operationtype'
            is_download_data = True # Is this a job to setup a zip file for data downloading?

            # Setup Temp Directory Paths (all of them)
            had_error__CreatingDirectory_Raw, error_data        = Task_Log.create_dir_if_not_exist(dir_path=raw_tif_dir)
            had_error__CreatingDirectory_Cropped, error_data    = Task_Log.create_dir_if_not_exist(dir_path=cropped_tif_dir)
            had_error__CreatingDirectory_Output, error_data     = Task_Log.create_dir_if_not_exist(dir_path=job_output_dir)

            if(had_error__CreatingDirectory_Raw == True):
                error_message = "There was an error when creating the raw tif directory: " + str(raw_tif_dir)
                errors.append(error_message)
            if (had_error__CreatingDirectory_Cropped == True):
                error_message = "There was an error when creating the cropped tif directory: " + str(cropped_tif_dir)
                errors.append(error_message)
            if (had_error__CreatingDirectory_Output == True):
                error_message = "There was an error when creating the data output directory: " + str(job_output_dir)
                errors.append(error_message)



            # Process the input geometry into a Shapely Polygon (Lat/Longs)
            #geom_data__Control  = json.dumps( [[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]])
            # Note, the json.dumps and json.loads provides a way for us to validate the JSON
            geom_data           = json.dumps( geometry['coordinates'][0] )
            geom_data_json      = json.loads(geom_data)
            poly_geojson        = Polygon(geom_data_json)
            # poly_geojson        = Polygon(json.loads(geom_data))
            bounds              = poly_geojson.bounds

            # Get the Bounds and min/max lat/longs
            #bounds = poly_geojson.bounds
            min_Lat = float(bounds[0])  # miny
            min_Long = float(bounds[1])  # minx
            max_Lat = float(bounds[2])  # maxy
            max_Long = float(bounds[3])  # maxx

            # Select the dataset
            # The Location of an NDVI nc4 file
            dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"

            # Name of the Variable inside the netcdf file
            var_to_select = "ndvi"

            # Opening the NC4 dataset file with xarray
            nc4_data_set = xarray.open_dataset(dataset_file_location)



            # TOOD - Put this part into an iteration

            # Select the dataset from the netcdf by using the lat/long
            # This selects the superset (the entire area of interest by bounding box)
            #
            # Geo Selection Note
            # For Longitude, it is: slice(min_Long, max_Long)
            # For Latitude, it is switched: slice(max_Lat, min_Lat)
            # TODO - Test to see if we need to switch the Lat order (min_Lat, max_Lat) VS (max_Lat, min_Lat) - This requires checking to see which result actually returns data or not first
            # # arr_LatTest = nc4_data_set[var_to_select].sel(latitude=slice(min_Lat, max_Lat))
            # # arr_LatTest ..... # TODO Check for Data, If no data came out, then execute the call the Other way
            arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(max_Lat, min_Lat))  # Remember, Lat is switched here



            # Reproject from Lat/Longs
            height_Lat_in_cords = max_Lat - min_Lat
            width_Long_in_cords = max_Long - min_Long

            # Protection from dividing by zero in later step
            if (height_Lat_in_cords == 0):
                height_Lat_in_cords = 0.01
            if (width_Long_in_cords == 0):
                width_Long_in_cords = 0.01

            height_in_Pixels = arr.data.shape[1]
            width_in_Pixels = arr.data.shape[2]

            geom_data_json__ReProjected = []
            for cord_pair in geom_data_json:
                lat = cord_pair[0]
                long = cord_pair[1]

                lat_partial = lat - min_Lat
                lat_Pixel_Reproj = (lat_partial / height_Lat_in_cords) * height_in_Pixels

                long_partial = long - min_Long
                long_Pixel_Reproj = (long_partial / width_Long_in_cords) * width_in_Pixels

                # CORRECT
                cord_Pixel_Reproj = [lat_Pixel_Reproj, long_Pixel_Reproj]

                # WRONG
                # cord_Pixel_Reproj = [long_Pixel_Reproj, lat_Pixel_Reproj]

                geom_data_json__ReProjected.append(cord_Pixel_Reproj)

            # Create a new shapely polygon
            shapely_poly_geojson_reprojected = Polygon(geom_data_json__ReProjected)
            shapes_list = []
            shapes_list.append(shapely_poly_geojson_reprojected)  # Crop operates on a list of shapes, it is ok if we have a list with 1 shape...







            # Create the temp raw tiff file
            raw_width = arr.shape[2]
            raw_height = arr.shape[1]

            # Checkpoint, if the width is 0 here, everything below will fail (it likely means that no data was selected)
            #print("DEBUG: Value of (raw_width): " + str(raw_width))
            if(raw_width == 0):
                error_message = "Error: raw_width is equal to 0.  This will cause the next steps to fail.  The most likely cause of this error is that there was no data to select in the given range.  Generic Error, no data found to select."
                errors.append(error_message)
                print(error_message)


            # Create the raw transform from the width of the original dataset
            raw_Transform = Affine(raw_height / raw_width, 0.0, 0.0, 0.0, 1.0, 0.0)





            # Now iterate over time dimensions
            # for arr_single_frame in arr:
            #    pass
            # UPDATE (SOLVED) - Solve this problem when dealing with an xarray object that has a time dimension. (Read comments on next line)
            #
            # This line works just fine when there is only 1 time dimension
            # # raw_rasterio_dataset.write(arr.data)
            # Not sure how to properly iterate through a netcdf file along the time dimension and still do the convert to raster..


            # Now process each time slice
            operation_calculations_Objects = []         # Store the array of each time slice calculation
            num_of_time_steps = arr.shape[0]
            for arr_time_idx in range(0, num_of_time_steps):

                # Get the xarray object for the single lat/long time slice
                arr_single_LatLong_Time_Slice = arr[arr_time_idx]

                # Epoch Time
                epoch_time = arr_single_LatLong_Time_Slice.time.data.tolist() / 1000000000

                datetime_time_string_for_file_name = datetime.fromtimestamp(epoch_time).strftime("%Y%m%dT%H%M%SZ")


                # Likely need to put this into a loop so we can name each tif file differently, after each granule
                # TODO - Use that same etl code to build the time parts of the tiff file names.
                #tif_file_name_raw = "ZZ_ndvi_test_raw.tif"
                #tif_file_name_cropped = "ZZ_ndvi_test_cropped.tif"
                tif_file_name_raw = str(datetime_time_string_for_file_name) + "_raw.tif"
                tif_file_name_cropped = str(datetime_time_string_for_file_name) + ".tif"  # Removed the 'cropped' part of the file name because this data gets zipped up.
                tif_full_file_path__Raw = os.path.join(raw_tif_dir, tif_file_name_raw)  # Working_directory_path/<job_id>/raw/tif_file_name.tif
                tif_full_file_path__Cropped = os.path.join(cropped_tif_dir, tif_file_name_cropped)  # Working_directory_path/<job_id>/cropped/tif_file_name.tif




                temp_data_writing_array = np.zeros((1, arr.shape[1], arr.shape[2]), dtype=arr_single_LatLong_Time_Slice.dtype)

                # Index 0 on 'temp_data_writing_array' is the single value time dimension
                # # Rasterio needs this to be a 3d Array for the write functions to work.
                temp_data_writing_array[0] = arr_single_LatLong_Time_Slice.data


                #raw_rasterio_dataset = rasterio.open('ZZ_ndvi_test_raw.tif', 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                raw_rasterio_dataset = rasterio.open(tif_full_file_path__Raw, 'w', driver='GTiff', height=arr.data.shape[1], width=arr.data.shape[2], count=1, dtype=arr.data.dtype, crs='EPSG:4326', transform=raw_Transform)
                #raw_rasterio_dataset.write(arr.data)  # // raw_rasterio_dataset.write(arr.data, 0)
                raw_rasterio_dataset.write(temp_data_writing_array)
                #crs = rasterio.crs.CRS({"init": "epsg:4326"})
                crs = rasterio_crs.CRS({"init": "epsg:4326"})
                raw_rasterio_dataset.crs = crs
                raw_rasterio_dataset.close()

                # Now load the tiff file and process it with a mask
                #src_img = rasterio.open('ZZ_ndvi_test_raw.tif', 'r')  # raw_rasterio_dataset
                src_img = rasterio.open(tif_full_file_path__Raw, 'r')  # raw_rasterio_dataset


                # Crop by mask - grab the shapely list from up above and use it to crop out an image
                # AND Create a new Tiff file from this result.
                cropped_out_image, cropped_out_transform = rasterio.mask.mask(src_img, shapes_list)
                cropped_out_meta = src_img.meta
                cropped_out_meta.update({"driver": "GTiff", "height": arr.data.shape[1], "width": arr.data.shape[2], "transform": cropped_out_transform, "nodata": 0.0})
                #cropped__rasterio_dataset = rasterio.open("test_CROPPED.tif", "w", **cropped_out_meta)
                cropped__rasterio_dataset = rasterio.open(tif_full_file_path__Cropped, "w", **cropped_out_meta)
                cropped__rasterio_dataset.write(cropped_out_image)
                cropped__rasterio_dataset.close()


                ## Calculate the correct stats
                #tif_file = "test_CROPPED.tif"
                #stats_result = zonal_stats(tif_file, stats=['mean'])
                #cropped_data_readonly = rasterio.open('test_CROPPED.tif', 'r')
                cropped_data_readonly = rasterio.open(tif_full_file_path__Cropped, 'r')
                stat_value = 0
                if(operation_enum == "mean"):  # min, max, mean
                    stat_value = cropped_data_readonly.read().mean()
                if (operation_enum == "min"):  # min, max, mean
                    stat_value = cropped_data_readonly.read().min()
                if (operation_enum == "max"):  # min, max, mean
                    stat_value = cropped_data_readonly.read().max()







            # OUTSIDE LOOP (After all tif files have been generated for the whole timeseries)
            if (is_download_data == True):
                # This line zips up the entire <cropped_tif_dir> directory and places it into a zip archive located at <zip_file_output_fullpath>
                did_zip_files = False
                try:
                    shutil.make_archive(zip_file_output_fullpath_NoExtension, 'zip', cropped_tif_dir)  # Gives us, <job_id>.zip
                    did_zip_files = True
                except:
                    did_zip_files = False
                    sysErrorData = str(sys.exc_info())
                    error_message = "There was an error when creating the zip archive of the group of output data files:  System Error Message: " + str(sysErrorData)
                    errors.append(error_message)


                if(did_zip_files == False):
                    # TODO - at this point, This Job Errored, make sure to store that in the database.
                    pass

            print("test_select_data__From_SubmitDataRequest_Call: Reached the end of Zipping up data... go check and see if it worked (validate the result)!")

            # TODO - Update database to signal that this job is done, make sure to save any needed data to the job record so that a get data reqeust will know how to get to the actual data.







            # TODO - Open with rasterio (not xarray)
            # TODO - Use Shapely to make a shape to apply to the selection?
            # TODO -- Figure out how to mask by selection (I think shapely does this in the step described above)
            # TODO - Make Tiff with rasterio
            # TODO - Calculate Stats (maybe with rasterstats and zonal_statistics?)

            #
            #
            #

            # TODO -- Try this https://corteva.github.io/rioxarray/stable/examples/clip_geom.html
            # TODO --- Open with rioxarray.open_rasterio
            # TODO -- Use Bounds to select data from

            #dir__nc4_data_set = str(dir(nc4_data_set))

            # https://gis.stackexchange.com/questions/328128/extracting-data-within-geometry-shape
            #geometries = [{'type': 'Polygon', 'coordinates': [[[425499.18381405267, 4615331.540546387], [425499.18381405267, 4615478.540546387], [425526.18381405267, 4615478.540546387], [425526.18381405267, 4615331.540546387], [425499.18381405267, 4615331.540546387]]]}]
            #xds.rio.set_crs("epsg:4326")
            #clipped = xds.rio.clip(geometries, xds.rio.crs)


            # Trying something - terminal
            # # import rioxarray
            # #


            # TODO - Continue here with bounds selection and TIFF generation



            returnData['PLACEHOLDER']   = "TODO: Finish returnData for Select_From_Netcdf.test_select_data__From_SubmitDataRequest_Call"
            returnData['geometry']      = geometry
            #returnData['geom_data__Control'] = geom_data__Control
            returnData['geom_data']     = geom_data
            returnData['bounds']        = bounds
            #returnData['dir__nc4_data_set'] = dir__nc4_data_set


        except:
            sysErrorData = str(sys.exc_info())
            error_message = "There was a generic uncaught error when processing the job for input params.  System Error Message: " + str(sysErrorData)
            errors.append(error_message)


        returnData['errors'] = errors

        return returnData

    @staticmethod
    def test__CanReadFromDjangoDB():
        test_configSetting_Value = Config_Setting.get_value(setting_name="REMOTE_PATH__ROOT_HTTP__CHIRP", default_or_error_return_value="SOME_ERROR_GETTING_CONFIG_SETTING")
        print("test__CanReadFromDjangoDB: (test_configSetting_Value): " + str(test_configSetting_Value))


    # Testing and understanding netcdf selections within the context of climateserv, the operators, and all the different dataset types.
    @staticmethod
    def test_select_data__NDVI():

        # The Location of an NDVI nc4 file
        dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"

        # Name of the Variable inside the netcdf file
        var_to_select = "ndvi"

        # Opening the NC4 dataset file with xarray
        nc4_data_set = xarray.open_dataset(dataset_file_location)

        # Time Selection Parameter
        # # (Not needed since each file is already coded properly - Each NC4 is equivalent to a single Tif slice in time (and it's max coverage region)

        # Geographic Selection
        # SouthernmostLatitude:  -12.500846850184978    # nc4_data_set.SouthernmostLatitude
        # NorthernmostLatitude:  22.999209149815027     # nc4_data_set.NorthernmostLatitude
        # WesternmostLongitude:  21.000489500000022     # nc4_data_set.WesternmostLongitude
        # EasternmostLongitude:  51.997887500000026     # nc4_data_set.EasternmostLongitude
        #
        # # [ [lat, lon], [lat, lon], .... [lat, lon] ]  # First and last lon, lat pairs have to be the same (to close the polygon)
        geom_data = json.dumps([[4.992345835892738, 33.51888205432572], [4.8175587553681805, 40.766317125846676], [-0.13264042444045324, 40.36063619076476], [0.17436096751475016, 31.47951303201745], [4.992345835892738, 33.51888205432572]])
        geom_data_json = json.loads(geom_data)
        poly_geojson = Polygon(geom_data_json)
        #poly_geojson = Polygon(json.loads(geom_data))

        # Get the Bounds
        bounds = poly_geojson.bounds
        min_Lat     = float(bounds[0])     # miny
        min_Long    = float(bounds[1])     # minx
        max_Lat     = float(bounds[2])     # maxy
        max_Long    = float(bounds[3])     # maxx


        # Geo Selection Note
        # For Longitude, it is: slice(min_Long, max_Long)
        # For Latitude, it is switched: slice(max_Lat, min_Lat)
        arr = nc4_data_set[var_to_select].sel(longitude=slice(min_Long, max_Long), latitude=slice(max_Lat, min_Lat))  # Remember, Lat is switched here


        # At this point, arr is the geo-coded ndvi data, now we need to perform operations on it?  and/or return it?



        # Get the values of the array # Maybe not needed this step -
        #vals = arr.values.tolist()

        # Geo Selection - SCRATCH
        #
        # arr = nc4_data_set.sel(longitude=slice(min_Long, max_Long), latitude=slice(max_Lat, min_Lat))  # Remember, Lat is switched here
        #arr = nc4_data_set.sel(longitude=slice(nc4_data_set.WesternmostLongitude, nc4_data_set.EasternmostLongitude), latitude=slice(nc4_data_set.SouthernmostLatitude, nc4_data_set.NorthernmostLatitude))
        #
        #arr = nc4_data_set.sel(longitude=slice(nc4_data_set.WesternmostLongitude, nc4_data_set.EasternmostLongitude), latitude=slice(nc4_data_set.SouthernmostLatitude, nc4_data_set.NorthernmostLatitude))
        #arr = nc4_data_set.sel(longitude=slice(miny, maxy), latitude=slice(minx, maxx))
        #arr_ndvi = nc4_data_set[var_to_select]
        #arr = nc4_data_set[var_to_select].sel(longitude=slice(miny, maxy), latitude=slice(minx, maxx))
        #arr = nc4_data_set[var_to_select].sel(longitude=slice(miny, maxy), latitude=slice(minx, maxx)).mean(dim=['latitude', 'longitude'])
        #
        # nc4_data_set['ndvi'].sel(longitude=slice(minx, maxx))
        # nc4_data_set['ndvi'].sel(latitude=slice(miny, maxy))      nc4_data_set['ndvi'].sel(latitude=slice(nc4_data_set.SouthernmostLatitude, nc4_data_set.NorthernmostLatitude))


        # Garbage
        #
        #
        # # The below is wrong, it needs to be, [lat, long], or [y, x]
        # # [ [lon, lat], [lon, lat], .... [lon, lat] ]  # First and last lon, lat pairs have to be the same (to close the polygon)
        #geom_data = json.dumps([[33.51888205432572, 4.992345835892738], [40.766317125846676, 4.8175587553681805], [40.36063619076476, -0.13264042444045324], [31.47951303201745, 0.17436096751475016], [33.51888205432572, 4.992345835892738]])
        #poly_geojson = Polygon(json.loads(geom_data))

    # END       def test_select_data__NDVI():


    hc_address = '/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy'

    # from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf
    # selected_data = Select_From_Netcdf.test_select_data()
    @staticmethod
    def test_select_data():


        # Hard Coded Examples
        # NDVI
        dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"
        #dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200111T000000Z.eastafrica.nc4"
        #dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200121T000000Z.eastafrica.nc4"

        var_to_select = "ndvi"      # Variable to Select
        sd = "2020-01-01T00:00:00"  # "%Y-%m-%dT%H:%M:%S"   #"%Y-%m-%d %H:%M:%S"
        ed = "2020-01-31T23:59:59"  # "%Y-%m-%dT%H:%M:%S"   #"%Y-%m-%d %H:%M:%S"

        # A Hard Coded Polygon (Within range of the data)
        # # Long, Lat (which is x, y)
        geom_data = json.dumps( [ [33.51888205432572, 4.992345835892738], [40.766317125846676, 4.8175587553681805], [40.36063619076476, -0.13264042444045324], [31.47951303201745, 0.17436096751475016], [33.51888205432572, 4.992345835892738] ] )
        sd = "2020-01-01T00:00:00" #"%Y-%m-%dT%H:%M:%S"   #"%Y-%m-%d %H:%M:%S"
        ed = "2020-01-31T23:59:59" #"%Y-%m-%dT%H:%M:%S"   #"%Y-%m-%d %H:%M:%S"


        # cfg
        #cfg_data_path = dataset_file_location


        json_obj = {}
        # Defining the lat and lon from the coords string
        poly_geojson = Polygon(json.loads(geom_data))

        shape_obj = shapely.geometry.asShape(poly_geojson)
        bounds = poly_geojson.bounds
        miny = float(bounds[0])
        minx = float(bounds[1])
        maxy = float(bounds[2])
        maxx = float(bounds[3])
        #nc4_data_set = xarray.open_dataset(os.path.join(cfg.data['path'], var_to_select + "_final.nc"))
        #nc4_data_set = xarray.open_dataset(os.path.join(dataset_file_location, var_to_select + "_final.nc"))
        nc4_data_set = xarray.open_dataset(dataset_file_location)
        print(nc4_data_set)  # Prints a lot of useful stuff

        #arr = nc4_data_set[var_to_select].sel(time=slice(sd, ed)).sel(lon=slice(miny, maxy), lat=slice(minx, maxx)).mean(dim=['lat', 'lon'])
        #arr = nc4_data_set[var_to_select].sel(time=slice(sd, ed)).sel(longitude=slice(miny, maxy), latitude=slice(minx, maxx)).mean(dim=['latitude', 'longitude'])
        arr = nc4_data_set[var_to_select].sel(longitude=slice(miny, maxy), latitude=slice(minx, maxx)).mean(dim=['latitude', 'longitude'])
        # print(arr.time.values)
        # print(arr.values)
        vals = arr.values.tolist()
        values = [0 if ((var_to_select == 'prec' or var_to_select == 'evap') and float(val) < 0) else round(float(val), 3) for val in vals]
        times2 = arr['time'].dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist()
        times1 = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in times2]
        times = [(calendar.timegm(st.utctimetuple()) * 1000) for st in times1]
        ts_plot = [[i, j] for i, j in zip(times, values)]
        return ts_plot



    # from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf
    # nc4_xarray_dataset_object = Select_From_Netcdf.test_understand_nc4__get_dataset()
    @staticmethod
    def test_understand_nc4__get_dataset():
        dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"
        nc4_data_set = xarray.open_dataset(dataset_file_location)
        #print(nc4_data_set)  # Prints a lot of useful stuff
        return nc4_data_set

    # from api_v2.processing_objects.select_data.select_from_netcdf import Select_From_Netcdf
    # result = Select_From_Netcdf.test_understand_nc4__ndvi_generic_processing()
    @staticmethod
    def test_understand_nc4__ndvi_generic_processing():
        dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"
        nc4_data_set = xarray.open_dataset(dataset_file_location)
        # print(nc4_data_set)  # Prints a lot of useful stuff
        return nc4_data_set



    # nc4_xarray_dataset_object.attrs


# Access from terminal:

# python
print("About to call test__CanReadFromDjangoDB()")
SelectFromNetCDF = Select_From_Netcdf()
SelectFromNetCDF.test__CanReadFromDjangoDB()

# Other Notes

# # NDVI
#
# dataset_file_location = "/Volumes/TestData/Data/SERVIR/ClimateSERV_2_0/data/THREDDS/thredds/catalog/climateserv/emodis-ndvi/eastafrica/250m/10dy/emodis-ndvi.20200101T000000Z.eastafrica.nc4"
# nc4_data_set = xarray.open_dataset(dataset_file_location)
# print(nc4_data_set)  # Prints a lot of useful stuff
#
# # Attributes:
#     Description:           EMODIS NDVI C6 at 250m resolution
#     DateCreated:           2020-11-16T17:35:17Z
#     Contact:               Lance Gilliland, lance.gilliland@nasa.gov
#     Source:                EMODIS NDVI C6, https://earlywarning.usgs.gov/fews...
#     Version:               C6
#     RangeStartTime:        2020-01-01T00:00:00Z
#     RangeEndTime:          2020-01-10T23:59:59Z
#     SouthernmostLatitude:  -12.500846850184978
#     NorthernmostLatitude:  22.999209149815027
#     WesternmostLongitude:  21.000489500000022
#     EasternmostLongitude:  51.997887500000026
#     TemporalResolution:    dekad
#     SpatialResolution:     250m


# https://github.com/SERVIR/Rheas-Viewer-Option2/blob/master/tethysapp/rheasvieweroption2/model.py

# @csrf_exempt
# def get_vic_polygon(s_var,geom_data,sd,ed):
#     json_obj = {}
#     # Defining the lat and lon from the coords string
#     poly_geojson = Polygon(json.loads(geom_data))
#     shape_obj = shapely.geometry.asShape(poly_geojson)
#     bounds = poly_geojson.bounds
#     miny = float(bounds[0])
#     minx = float(bounds[1])
#     maxy = float(bounds[2])
#     maxx = float(bounds[3])
#     ks_sat3=xarray.open_dataset(os.path.join(cfg.data['path'], s_var+"_final.nc"))
#     arr=ks_sat3[s_var].sel(time=slice(sd,ed)).sel(lon=slice(miny,maxy),lat=slice(minx,maxx)).mean(dim=['lat','lon'])
#     # print(arr.time.values)
#     # print(arr.values)
#     vals=arr.values.tolist()
#     values=[0 if ((s_var == 'prec' or s_var == 'evap') and float(val) < 0) else round(float(val), 3) for val in vals]
#     times2=arr['time'].dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist()
#     times1=[datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in times2]
#     times=[(calendar.timegm(st.utctimetuple()) * 1000) for st in times1]
#     ts_plot = [ [i , j] for i,j in zip(times,values) ]
#     return ts_plot



# Console Tests
# # import json
# # from shapely.geometry import Polygon
# # geom_data = json.dumps([[33.51888205432572, 4.992345835892738], [40.766317125846676, 4.8175587553681805], [40.36063619076476, -0.13264042444045324], [31.47951303201745, 0.17436096751475016], [33.51888205432572, 4.992345835892738]])

