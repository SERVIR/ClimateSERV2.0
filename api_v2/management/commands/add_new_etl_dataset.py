# add_new_etl_dataset.py
# Command function for adding a new dataset (with only a name)


# Call this custom command using
# # # python manage.py add_new_etl_dataset <etl_dataset_name>.

# Includes
from django.core.management.base import BaseCommand, CommandError
from api_v2.app_models.model_ETL_Dataset import ETL_Dataset


class Command(BaseCommand):
    help = 'Create a new Dataset from an input name with default parameters.'

    # Parsing params
    def add_arguments(self, parser):
        parser.add_argument('etl_dataset_name', type=str)

    # Function Handler
    def handle(self, *args, **options):
        # Get the input param
        etl_dataset_name = ""
        try:
            etl_dataset_name = options['etl_dataset_name']
        except:
            self.stdout.write(self.style.ERROR('add_new_etl_dataset.handle(): Could not read required input param: <etl_dataset_name>'))
            return

        # Filter down to a forced string that is not empty.
        etl_dataset_name = str(etl_dataset_name).strip()

        # Debug
        # self.stdout.write(self.style.SUCCESS('add_new_etl_dataset.py: Successfully called handle(): with param: (etl_dataset_name) ' + str(etl_dataset_name)))

        # Check and see if dataset name is already taken
        is_dataset_name_available = ETL_Dataset.is_datasetname_avalaible(input__datasetname=etl_dataset_name)
        if(is_dataset_name_available == False):
            self.stdout.write(self.style.ERROR('add_new_etl_dataset.handle(): Dataset name is not available.  Try another name for this dataset.'))
            return

        # Create the new Dataset
        did_create_dataset, new_etl_dataset_uuid = ETL_Dataset.create_etl_dataset_from_datasetname_only(input__datasetname=etl_dataset_name, created_by="terminal_manage_py_command__add_new_etl_dataset")

        # Check to see if this was created and then output to the console.
        if(did_create_dataset == True):
            self.stdout.write(self.style.SUCCESS('add_new_etl_dataset.py: Successfully created new dataset, ' + str(etl_dataset_name) + ', with UUID: ' + str(new_etl_dataset_uuid)))
        else:
            self.stdout.write(self.style.ERROR('add_new_etl_dataset.handle(): Unknown Error.  Dataset was not created.'))

        return



# # Running Test:
# python manage.py add_new_etl_dataset CSERV-TEST_PIPELINE_DATASET
#
# # Output from Test:
# add_new_etl_dataset.py: Successfully created new dataset, CSERV-TEST_PIPELINE_DATASET, with UUID: fRjduT9v4jHyazGBMEJe


# # Running again: (to make sure duplicate name checking works properly)
# python manage.py add_new_etl_dataset CSERV-TEST_PIPELINE_DATASET
#
# # Output from Test:
# add_new_etl_dataset.handle(): Dataset name is not available.  Try another name for this dataset.


