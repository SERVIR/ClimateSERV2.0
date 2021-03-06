# Generated by Django 3.0.7 on 2020-07-26 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v2', '0003_etl_dataset_dataset_subtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='etl_granule',
            name='etl_pipeline_run_uuid',
            field=models.CharField(default='UNSET_DATASET_UUID', help_text='Each time the ETL Pipeline runs, there is a unique ID generated, this field operates like a way to tag which pipeline this row is attached to', max_length=40, verbose_name='ETL Pipeline Run UUID'),
        ),
        migrations.AddField(
            model_name='etl_granule',
            name='granule_pipeline_state',
            field=models.CharField(default='UNSET_ATTEMPTED', help_text='Each Individual Granule has a pipeline state.  This lets us easily understand if the Granule succeeded or failed', max_length=20, verbose_name='Granule Pipeline State'),
        ),
        migrations.AddField(
            model_name='etl_log',
            name='etl_pipeline_run_uuid',
            field=models.CharField(default='UNSET_DATASET_UUID', help_text='Each time the ETL Pipeline runs, there is a unique ID generated, this field operates like a way to tag which pipeline this row is attached to.', max_length=40, verbose_name='ETL Pipeline Run UUID'),
        ),
    ]
