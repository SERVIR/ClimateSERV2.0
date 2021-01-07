
# Admin Import
from django.contrib import admin

# Import your models here.
#from .app_models.model_Widget                 import Widget
from .app_models.model_User                 import User
from .app_models.model_ETL_PipelineRun      import ETL_PipelineRun
from .app_models.model_ETL_Dataset          import ETL_Dataset
from .app_models.model_ETL_Log              import ETL_Log
from .app_models.model_ETL_Granule          import ETL_Granule
from .app_models.model_Available_Granule    import Available_Granule
from .app_models.model_API_Log              import API_Log
from .app_models.model_Config_Setting       import Config_Setting
from .app_models.model_Task_Log             import Task_Log
from .app_models.model_WorkerProcess        import WorkerProcess


# Register your models here.
#admin.site.register(Widget)
admin.site.register(User)
admin.site.register(ETL_PipelineRun)
admin.site.register(ETL_Dataset)
admin.site.register(ETL_Log)
admin.site.register(ETL_Granule)
admin.site.register(Available_Granule)
admin.site.register(API_Log)
admin.site.register(Config_Setting)
admin.site.register(Task_Log)
admin.site.register(WorkerProcess)



