# 2. forms.py
from django import forms
from .models import NationalIDVerification

class NationalIDVerificationForm(forms.ModelForm):
    class Meta:
        model = NationalIDVerification
        fields = ['front_image', 'back_image']

