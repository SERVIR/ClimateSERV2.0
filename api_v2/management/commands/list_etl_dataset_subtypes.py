# list_etl_dataset_uuids.py
# Command function for outputting all the UUIDs and Dataset Names


# Call this custom command using
# # # python manage.py list_etl_dataset_subtypes

# Includes
from django.core.management.base import BaseCommand, CommandError
from api_v2.app_models.model_ETL_Dataset import ETL_Dataset


class Command(BaseCommand):
    help = 'List all of the possible ETL Dataset Subtypes that are currently supported by the ETL Pipeline.'

    # Function Handler
    def handle(self, *args, **options):
        # Debug
        #self.stdout.write(self.style.SUCCESS('list_etl_dataset_uuids.py: Successfully called handle()'))

        etl_subtypes_array = ETL_Dataset.get_all_subtypes_as_string_array()
        self.stdout.write(self.style.SUCCESS('ETL Dataset Subtypes: ' + str(etl_subtypes_array)))
        self.stdout.write(self.style.SUCCESS(''))

        return




# # Running Test:
# python manage.py list_etl_dataset_subtypes
#
# # Output from Test:
# ETL Dataset Subtypes: ['chrip', 'chrips', 'chrips_gefs', 'emodis', 'esi_4week', 'esi_12week', 'imerg_early', 'imerg_late']





