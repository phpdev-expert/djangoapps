
from django.db import models
STATUS_CHOICES = (
   ('1', 'Active'),
   ('0', 'Suspended')
)
class Ais(models.Model):
    ai_id=models.IntegerField()
    ai_code = models.CharField(max_length=20)
    ai_no  = models.CharField(max_length=20)
    email = models.CharField(max_length=500, null=True, blank=True,default="")
    status = models.BooleanField(default=False)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)
    class Meta:
       managed = False
       db_table = 'ai_participating'


class AisSettings(models.Model):
    return_type = models.CharField(max_length=3)
    deadline = models.DateField(null=True, blank=True)
    created_by=models.CharField(max_length=50, blank=True, editable=False)
    last_modified_by=models.CharField(max_length=50, blank=True, editable=False)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'return_deadline'



class GdrSubmissionControl(models.Model):
    ai_code = models.CharField(max_length=6, primary_key=True)
    position_date = models.DateField(primary_key=True)
    return_name = models.CharField(max_length=3, primary_key=True)
    submission_type = models.CharField(max_length=1, primary_key=True)
    zip_file_name = models.CharField(max_length=55, primary_key=True)
    csv_file_name = models.CharField(max_length=70, primary_key=True)
    block_code = models.CharField(max_length=10, primary_key=True)
    job_uuid = models.CharField(max_length=40, primary_key=True)
    zip_file_timestamp = models.DateTimeField()
    tot_csv_rows = models.IntegerField()
    staging_failed = models.IntegerField()
    staging_rows = models.IntegerField()
    staging_good = models.IntegerField()
    staging_warn = models.IntegerField()
    staging_error = models.IntegerField()
    gdr_good = models.IntegerField()
    gdr_warn = models.IntegerField()
    status = models.CharField(max_length=2)
    download_timestamp = models.DateTimeField()
    process_timestamp = models.DateTimeField()
    by_user = models.CharField(max_length=6)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)

    class Meta:
       managed = False
       db_table = 'gdr_submission_control'
       unique_together = ('ai_code', 'position_date', 'return_name','submission_type', 'zip_file_name', 'csv_file_name','block_code','job_uuid')

class GdrValidationLog(models.Model):
    job_uuid = models.CharField(max_length=40, primary_key=True)
    event_id = models.CharField(max_length=36, primary_key=True)
    ai_code = models.CharField(max_length=6, primary_key=True)
    position_date = models.CharField(max_length=6, primary_key=True)
    return_name = models.CharField(max_length=3, primary_key=True)
    submission_type = models.CharField(max_length=1, primary_key=True)
    zip_file_name = models.CharField(max_length=55, primary_key=True)
    zip_file_timestamp = models.DateTimeField(primary_key=True)
    block_code= models.CharField(max_length=10, primary_key=True)
    field_label = models.CharField(max_length=30, primary_key=True)
    validation_rule = models.CharField(max_length=10, primary_key=True)
    row_key = models.CharField(max_length=100)
    result = models.CharField(max_length=1)
    remark = models.CharField(max_length=100,null=True, blank=True)
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)
    class Meta:
       managed = False
       db_table = 'gdr_validation_log'
       unique_together = ('event_id', 'ai_code', 'position_date', 'return_name', 'submission_type', 'zip_file_name', 'zip_file_timestamp', 'block_code', 'validation_rule', 'field_label')


class UddAIDimension(models.Model):
    ai_no = models.CharField(max_length=6)
    ai_code = models.CharField(max_length=6, primary_key=True)
    start_month = models.DateField(primary_key=True)
    end_month = models.DateField(primary_key=True)
    ai_name = models.CharField(max_length=70)
    ai_bkg_group = models.CharField(max_length=10)
    ai_bkg_group_name = models.CharField(max_length=70)
    ai_retail_group = models.CharField(max_length=10)
    ai_retail_group_name =  models.CharField(max_length=70)
    ai_large_retail_group = models.CharField(max_length=10)
    ai_large_retail_group_name = models.CharField(max_length=70)
    ai_ri_flag= models.CharField(max_length=1)
    ai_ri_name = models.CharField(max_length=50)
    ai_retail_bk_bus_group = models.CharField(max_length=10)
    ai_retail_bk_bus_group_name = models.CharField(max_length=70)
    ai_mpf_flag = models.CharField(max_length=1)
    ai_mpf_name = models.CharField(max_length=50,null=True, blank=True)
    ai_insurance_group =models.CharField(max_length=10,null=True, blank=True)
    ai_insurance_group_name =models.CharField(max_length=70,null=True, blank=True)
    ai_private_group =models.CharField(max_length=10,null=True, blank=True)
    ai_private_group_name = models.CharField(max_length=70,null=True, blank=True)
    ai_excl_flag = models.CharField(max_length=1,null=True, blank=True)
    ai_no_name = models.CharField(max_length=80,null=True, blank=True)
    custom_field = models.CharField(max_length=76,null=True, blank=True)
    ai_type = models.CharField(max_length=3,null=True, blank=True)
    ai_type_name = models.CharField(max_length=50,null=True, blank=True)
    ai_inc_place = models.CharField(max_length=3,null=True, blank=True)
    ai_inc_place_name = models.CharField(max_length=50,null=True, blank=True)
    ai_inc_place_region = models.CharField(max_length=3,null=True, blank=True)
    ai_bo_place = models.CharField(max_length=3,null=True, blank=True)
    ai_bo_place_name = models.CharField(max_length=50,null=True, blank=True)
    ai_bo_place_region = models.CharField(max_length=3,null=True, blank=True)
    div_description = models.CharField(max_length=100,null=True, blank=True)
    co_user_name = models.CharField(max_length=30,null=True, blank=True)
    sm_user_name = models.CharField(max_length=30,null=True, blank=True)
    ai_parent_ai_name = models.CharField(max_length=70,null=True, blank=True)
    ai_parent_ai_no = models.CharField(max_length=6,null=True, blank=True)
    ai_merge_ai_name = models.CharField(max_length=70,null=True, blank=True)
    ai_merge_ai_no = models.CharField(max_length=6,null=True, blank=True)
    ai_app_date =models.DateField(null=True, blank=True)
    ai_open_date = models.DateField(null=True, blank=True)
    ai_revoke_date = models.DateField(null=True, blank=True)
    ai_id =models.IntegerField()
    create_dtm=models.DateTimeField(auto_now_add=True)
    last_modified_dtm=models.DateTimeField(auto_now=True)
    class Meta:
       managed = False
       db_table = 'udd_ai_dimensions'



       # Create your models here.
