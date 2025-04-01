from django.db import models
from django.core.files.storage import FileSystemStorage

upload_storage = FileSystemStorage(location='/tmp')

class CustomerData(models.Model):
    file = models.FileField(storage=upload_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    cluster_count = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Data uploaded at {self.uploaded_at}"