# external_call_test_1.py

# Testing that an internal python django command can be called from the hosting server's commandline.

# Reference
# https://docs.djangoproject.com/en/3.0/howto/custom-management-commands/

# Call this custom command using
# # # python manage.py external_call_test_1 <any_string_params>.

# Includes
from django.core.management.base import BaseCommand, CommandError
#from api_v2.models import a_model_name as a_model_name

class Command(BaseCommand):
    help = 'Just makes sure we can call a custom command from the shell AND perform some operation with parameters.'

    # Parsing a list of arguments (more than 1 string can be passed in but only 1 is required)
    def add_arguments(self, parser):
        parser.add_argument('any_string_params', nargs='+', type=str)

    # Function Handler
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully called handle().  About to iterate through each param.'))

        # Iterate each param
        for current_string_param in options['any_string_params']:
            # Can put model logic in here (Example: load a model record by id, do something to it, then save it)
            self.stdout.write(self.style.SUCCESS('Successfully called handle() and iterated to param: "%s"' % current_string_param))



# # Running Test:
# python manage.py external_call_test_1 hello world
#
# # Output from Test:
# Successfully called handle().  About to iterate through each param.
# Successfully called handle() and iterated to param: "hello"
# Successfully called handle() and iterated to param: "world"
