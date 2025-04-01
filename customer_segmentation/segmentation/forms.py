from django import forms
from .models import CustomerData

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = CustomerData
        fields = ['file']
        
    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError("Only CSV files are allowed.")
        return file