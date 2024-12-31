from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Fields to include


class CSVUploadForm(forms.Form):
    file = forms.FileField()

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Upload Excel File')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')