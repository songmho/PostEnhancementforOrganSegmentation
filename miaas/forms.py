# Django Multiupload Required: pip install django-multiupload
from django import forms

from multiupload.fields import MultiFileField

class UploadForm(forms.Form):
    attachments = MultiFileField(min_num=1)
    # attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)


# References
# https://github.com/Chive/django-multiupload
# https://www.chicagodjango.com/blog/multiple-file-uploads-django/