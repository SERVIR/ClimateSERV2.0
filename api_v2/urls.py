
from django.conf.urls import url
from . import views
#from . import draft_views
from .app_views import views_Auth
from .app_views import views_Admin_ManageUsers
from .app_views import views_Admin_Generic


# from .app_views_subdirectory import views_SubFile   # Example of how to import a sub views file from a views subdirectory.

# The URLs for this Module (api_v2)
# Overall Pattern leading to this module: domainRoot.com/api_v2/<ItemBelow>

urlpatterns = [

url(r'^get_server_versions/', views.get_server_versions, name='get_server_versions'),



# # ###########################################################################################################################
# # // AUTHENTICATION (Signin and Signout)
# # ###########################################################################################################################
#

# Signing User in - Process a signin request (requires a username and password)
url(r'process_signin/',  views_Auth.process_signin,  name='process_signin'),
#
# Signing User Out - Process a request to signout a user (requires their session id)
url(r'^process_signout/', views_Auth.process_signout, name='process_signout'),
#
#
#
# # Debug Endpoints # MaybeNotNeeded - Make these real
url(r'^session_output_test/',               	views_Auth.session_output_test, 				name='session_output_test'),
# url(r'^process_signin_as_test_user_1/',      	views_Auth.process_signin_as_test_user_1, 		name='process_signin_as_test_user_1'),
# url(r'^process_signin_as_test_user_2/',      	views_Auth.process_signin_as_test_user_2, 		name='process_signin_as_test_user_2'),
# url(r'^process_signin_as_test_admin_user_1/', views_Auth.process_signin_as_test_admin_user_1, name='process_signin_as_test_admin_user_1'),


# # ###########################################################################################################################
# # // Admin ManageUsers (Create User and Set Properties)
# # ###########################################################################################################################
#
# When an Admin User Creates a new User
url(r'admin_create_user/',  views_Admin_ManageUsers.admin_create_user,  name='admin_create_user'),


# # ###########################################################################################################################
# # // Admin Generic Functions    # views_Admin_Generic
# # ###########################################################################################################################
#
# Generic Getter for any specific white listed database object by type and id.  // object_type, object_uuid
# # /api_v2/admin_get_db_item  // the_uuid, the_type // (WHITE LIST THE TYPES WITH IF STATEMENTS - ALWAYS RETURN JSON-ABLE VERSION OF THE ITEM, IF IT WAS FOUND)
url(r'admin_get_db_item/',  views_Admin_Generic.admin_get_db_item,  name='admin_get_db_item'),

# List Types - Support paging and Custom Param Sorting
# # /api_v2/admin_get_api_logs  //
url(r'admin_get_api_logs/',  views_Admin_Generic.admin_get_api_logs,  name='admin_get_api_logs'),               # # /api_v2/admin_get_api_logs  //
url(r'admin_get_etl_logs/',  views_Admin_Generic.admin_get_etl_logs,  name='admin_get_etl_logs'),               # # /api_v2/admin_get_etl_logs  //
url(r'admin_get_server_logs/',  views_Admin_Generic.admin_get_server_logs,  name='admin_get_server_logs'),      # # /api_v2/admin_get_server_logs  //

# admin_get_stats_for_type // Types are: "APILog", "ETLLog", "ServerLog"
url(r'admin_get_stats_for_type/',  views_Admin_Generic.admin_get_stats_for_type,  name='admin_get_stats_for_type'),      # # /api_v2/admin_get_stats_for_type  //

# A single function for the Dashboard page to call and get data for display. (Stats, lists and other data)
url(r'admin_get_dashboard_data/',  views_Admin_Generic.admin_get_dashboard_data,  name='admin_get_dashboard_data'),      # # /api_v2/admin_get_dashboard_data  //


]  # END of urlpatterns


# NOTES:



# Garbage 

