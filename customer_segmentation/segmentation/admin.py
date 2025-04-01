from django.contrib import admin
from .models import CustomerData

@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'cluster_count')
    readonly_fields = ('uploaded_at',)