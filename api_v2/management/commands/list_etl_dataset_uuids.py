# list_etl_dataset_uuids.py
# Command function for outputting all the UUIDs and Dataset Names


# Call this custom command using
# # # python manage.py list_etl_dataset_uuids

# Includes
from django.core.management.base import BaseCommand, CommandError
from api_v2.app_models.model_ETL_Dataset import ETL_Dataset


class Command(BaseCommand):
    help = 'List all the Dataset IDs along with their respective human-readable (human defined) names.'

    # Function Handler
    def handle(self, *args, **options):
        # Debug
        #self.stdout.write(self.style.SUCCESS('list_etl_dataset_uuids.py: Successfully called handle()'))

        etl_datasets = ETL_Dataset.get_all_etl_datasets_preview_list()

        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('UUID,    Dataset Name'))
        for current_etl_dataset in etl_datasets:
            current_uuid            = str(current_etl_dataset['uuid']).strip()
            current_dataset_name    = str(current_etl_dataset['dataset_name']).strip()

            self.stdout.write(self.style.SUCCESS(current_uuid + ',    ' + current_dataset_name))
        self.stdout.write(self.style.SUCCESS(''))

        return




# # Running Test:
# python manage.py list_etl_dataset_uuids
#
# # Output from Test:
# UUID,    Dataset Name
# fRjduT9v4jHyazGBMEJe,    CSERV-TEST_PIPELINE_DATASET




