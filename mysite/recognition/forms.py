from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
import re
from django.core.exceptions import ValidationError


class RecognitionForm(forms.Form):
    photo = forms.ImageField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super(RecognitionForm, self).__init__(*args, **kwargs)
    #     self.photo.required = False
