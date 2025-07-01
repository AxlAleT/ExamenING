from django.db import models
from django.core.files.storage import default_storage
import os


class ETLJob(models.Model):
    """Model to track ETL job executions."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    records_processed = models.IntegerField(default=0)
    records_inserted = models.IntegerField(default=0)
    records_updated = models.IntegerField(default=0)
    records_skipped = models.IntegerField(default=0)
    records_errored = models.IntegerField(default=0)
    
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'etl_jobs'
        ordering = ['-created_at']
        app_label = 'etl'
    
    def __str__(self):
        return f"ETL Job: {self.name} - {self.status}"


class DataUpload(models.Model):
    """Model to handle file uploads for ETL processing."""
    
    file = models.FileField(upload_to='etl_uploads/')
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    etl_job = models.ForeignKey(ETLJob, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'data_uploads'
        ordering = ['-uploaded_at']
        app_label = 'etl'
    
    def __str__(self):
        return f"Upload: {self.original_filename}"
    
    def get_file_path(self):
        """Get the full file path."""
        if self.file:
            return self.file.path
        return None
    
    def delete_file(self):
        """Delete the uploaded file."""
        if self.file:
            if default_storage.exists(self.file.name):
                default_storage.delete(self.file.name)
