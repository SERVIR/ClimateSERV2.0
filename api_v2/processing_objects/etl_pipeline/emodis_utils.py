# TODO - Remove me (Make sure this file is not referenced anywhere else)
# # TODO - Note: This is part of the main 'etl_pipeline.py' cleanup process..

# emodis_utils.py

import urllib
import re
import os.path as path
import gzip
import os
import sys
import zipfile


# # Console Test
# from api_v2.processing_objects.etl_pipeline import emodis_utils
# emodis_utils.test__emodis_utils__by_example()



def get_expected_files_list(self, THE_PARAMS_HERE):
    pass


def get_expected_granules():

    pass


# Emodis has their months split into 3rds
# # month_fraction_index is how we can tell those section apart.  month_fraction_index can be 0, 1, or 2
# region_str can be one of these: ["ea", "wa", "sa", "cta"]  // EastAfrica, WestAfrica, SouthernAfrica, CentralAsia
def get_expected_filename(region_str, year_YYYY, month_MM, month_fraction_index):
    ret_filename_str = ""
    ret_filename_str += region_str
    ret_filename_str += year_YYYY[2:4]

    # Handling the dakad parts
    month_multiplier = int(month_MM)
    dekad_position = month_fraction_index + 1       # converts 0 or 1 or 2  into    a 1, or 2 or 3
    filename_dekad_part = month_multiplier * dekad_position
    filename_dekad_part = '{:02d}'.format(filename_dekad_part)  # Force into 2 digit string
    ret_filename_str += filename_dekad_part

    ret_filename_str += '.zip'

    return ret_filename_str




def test__emodis_utils__by_example():
    print("test__emodis_utils__by_example: Has Started")

    print("test__emodis_utils__by_example: Get Expected File Name for West Africa Region, 2020, Feb, Index 2 (3rd position)")
    month_MM = '{:02d}'.format(2)       # 2 is Feb, and this line turns it into a string "02"
    year_YYYY = '{:04d}'.format(2020)
    get_expected_filename__TEST1 = get_expected_filename(region_str="wa", year_YYYY=year_YYYY, month_MM=month_MM, month_fraction_index=2)
    get_expected_filename__TEST2 = get_expected_filename(region_str="wa", year_YYYY='{:04d}'.format(2020), month_MM='{:02d}'.format(1), month_fraction_index=1)
    print("test__emodis_utils__by_example: (get_expected_filename__TEST1): " + str(get_expected_filename__TEST1))
    print("test__emodis_utils__by_example: (get_expected_filename__TEST2): " + str(get_expected_filename__TEST2))

    print("test__emodis_utils__by_example: Has Reached the End")
