from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

from .models import Document,UserData

from django.forms.widgets import PasswordInput, TextInput

from django import forms


class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('associate', 'Associate'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    passcode = forms.CharField(max_length=50, required=False, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        passcode = cleaned_data.get("passcode")

        if role == 'manager' and passcode != '123ABC':
            raise forms.ValidationError("Invalid passcode for Manager.")
        return cleaned_data


class NewAccountForm(UserCreationForm):

    class Meta:

        model = User 
        fields = ['username' ,'password1', 'password2']

#User Login

class LoginPageForm(AuthenticationForm):

    username = forms.CharField(widget = TextInput())
    password = forms.CharField(widget = PasswordInput())


#Record Creation

class AddRecord(forms.ModelForm):
    class Meta:

        model = UserData
        fields = ['first_name' ,'last_name', 'email', 'phone', 'address', 'city', 'state', 'country']

#Record Updation
class UpdateRecord(forms.ModelForm):
    class Meta:

        model = UserData
        fields = ['first_name' ,'last_name', 'email', 'phone', 'address', 'city', 'state', 'country']

# UploadForms

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document  
        fields = ('file',) 

