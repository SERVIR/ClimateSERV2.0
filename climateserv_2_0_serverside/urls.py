
"""climateserv_2_0_serverside URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
#from django.conf.urls import include, url
#url(r'^signin_authenticated/',  views_Auth.process_signin,  name='process_signin'),


# Legacy Support (Legacy ClimateSERV 1.0 Support)
from django.conf.urls import url
from api_v2.app_views import views_Legacy_Endpoints



urlpatterns = [
    #path('admin/', admin.site.urls),
    path('cserv_system_admin/', admin.site.urls),               # Django System/Super User Admin Section

    # TODO: # path('cserv_admin/', ROUTE_TO_ADMIN_CLIENT),      # ClimateSERV 2.0 Admin Application Support.
    # TODO: # path('pub/', ROUTE_TO_PUBLIC_USER_CLIENT),        # After Deployment, Browsing to "https://climateserv.servirglobal.net/" should autoforward to this route.
    # TODO: Provide Routing for Legacy API Request URLs         # (Automation and Scripting support)

    # Linking up to other modules
    path('api_v2/', include('api_v2.urls')),            	   # API V2, the entry point into the latest, API for this platform.
    #path('tests/',     include('tests_module.urls')),         # Tests is for running tests (but exposing this to the outside world)  - This should be behind a kind of protection or only output something very simple (Maybe just for Integration tests)
    

    # ##############################################################################
    # # Legacy Support Endpoints (Taken from Active Endpoints of ClimateSERV 1.0)
    # ##############################################################################

    # Routing all of these to api_v2
    #url(r'process_signin/',  views_Auth.process_signin,  name='process_signin'),
    url(r'^chirps/admin/doc/',  views_Legacy_Endpoints.admin_doc,  name='admin_doc'),
    url(r'^chirps/pydash/',  views_Legacy_Endpoints.pydash,  name='pydash'),
    url(r'^chirps/metrics/',  views_Legacy_Endpoints.metrics,  name='metrics'),
    url(r'^chirps/getParameterTypes/',  views_Legacy_Endpoints.getParameterTypes,  name='getParameterTypes'),
    url(r'^chirps/getRequiredElements/',  views_Legacy_Endpoints.getRequiredElements,  name='getRequiredElements'),

    url(r'^chirps/submitDataRequest/',  views_Legacy_Endpoints.submitDataRequest,  name='submitDataRequest'),
    url(r'^chirps/getDataRequestProgress/',  views_Legacy_Endpoints.getDataRequestProgress,  name='getDataRequestProgress'),
    url(r'^chirps/getDataFromRequest/',  views_Legacy_Endpoints.getDataFromRequest,  name='getDataFromRequest'),
    url(r'^chirps/getFeatureLayers/',  views_Legacy_Endpoints.getFeatureLayers,  name='getFeatureLayers'),
    url(r'^chirps/getCapabilitiesForDataset/',  views_Legacy_Endpoints.getCapabilitiesForDataset,  name='getCapabilitiesForDataset'),
    url(r'^chirps/getClimateScenarioInfo/',  views_Legacy_Endpoints.getClimateScenarioInfo,  name='getClimateScenarioInfo'),
    url(r'^chirps/getRequestLogs/',  views_Legacy_Endpoints.getRequestLogs,  name='getRequestLogs'),
    url(r'^chirps/getFileForJobID/',  views_Legacy_Endpoints.getFileForJobID,  name='getFileForJobID'),
    url(r'^chirps/submitMonthlyGEFSRainfallAnalysisRequest/',  views_Legacy_Endpoints.submitMonthlyGEFSRainfallAnalysisRequest,  name='submitMonthlyGEFSRainfallAnalysisRequest'),

    url(r'^chirps/scriptAccess/',  views_Legacy_Endpoints.scriptAccess,  name='scriptAccess'),
    url(r'^chirps/submitMonthlyRainfallAnalysisRequest/',  views_Legacy_Endpoints.submitMonthlyRainfallAnalysisRequest,  name='submitMonthlyRainfallAnalysisRequest'),


    # Test Endpoints
    url(r'^test_zmq/',  views_Legacy_Endpoints.test_zmq,  name='test_zmq'),


    # Original ClimateSERV 1.0 endpoints
        # ROUTED: url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        # Uncomment the next line to enable the admin:
        # NEW_ADDRESS IS: (cserv_system_admin) url(r'^admin/', include(admin.site.urls)),
        # ROUTED: url(r'^pydash/', include('pydash.urls')),
        # ROUTED: url(r'^metrics/', include('servirmetrics.urls')),
        # ROUTED: url(r'^getParameterTypes/',getParameterTypes),
        # ROUTED: url(r'^getRequiredElements/', getRequiredElements),
        # SKIPPED - WAS COMMENTED OUT - #url(r'^getDataTypes/','servirchirps.views.getDataTypes'),
        # ROUTED: url(r'^submitDataRequest/',submitDataRequest),
        # ROUTED: url(r'^getDataRequestProgress/',getDataRequestProgress),
        # ROUTED: url(r'^getDataFromRequest/',getDataFromRequest),
        # ROUTED: url(r'^getFeatureLayers/',getFeatureLayers),
        # ROUTED: url(r'^getCapabilitiesForDataset/',getCapabilitiesForDataset),
        # ROUTED: url(r'^getClimateScenarioInfo/',getClimateScenarioInfo),    # ks refactor 2015 // New API Hook getClimateScenarioInfo
        # ROUTED: url(r'^getRequestLogs/',getRequestLogs),    # ks refactor 2015 // New API Hook getRequestLogs
        # ROUTED: url(r'^getFileForJobID/',getFileForJobID),
        # ROUTED: url(r'^submitMonthlyGEFSRainfallAnalysisRequest/',submitMonthlyGEFSRainfallAnalysisRequest),
        # SKIPPED - WAS COMMENTED OUT - #url(r'^getFileURLForJobID/','servirchirps.views.getFileURLForJobID'),  # ks refactor 2015 // New API Hook for downloading files from completed jobs.
        # ROUTED: url(r'^scriptAccess/',scriptAccess),  # New path for Serverside Script access.
        # ROUTED: url(r'^submitMonthlyRainfallAnalysisRequest/',submitMonthlyRainfallAnalysisRequest)


]
