from django import forms
from .models import *


class UserAccountForm(forms.ModelForm):
  class Meta:
    fields=['username','password',]


class RegisterForm(forms.ModelForm):
  class Meta:
    model = Registration
    fields=['username','email','password','phonenumber','otp',]
    


class countriesForm(forms.ModelForm):
  class Meta:
    model = Country
    fields=['country_id','country']


class StateForm(forms.ModelForm):
  class Meta:
    model = State
    fields=['state_id','state']

class DistrictForm(forms.ModelForm):
  class Meta:
    model = District
    fields=['district','district_id']

class MasterplanForm(forms.ModelForm):
  class Meta:
    model = Masterplan
    fields=['masterplan_id','masterplan_name']
    
class LocalbodyForm(forms.ModelForm):
  class Meta:
    model = Localbody
    fields=['localbody_id','localbody_name','localbody_type']

class TalukmasterForm(forms.ModelForm):
  class Meta:
    model = Talukmaster
    fields=['taluk_id','taluk_name']

  
class LanduseForm(forms.ModelForm):
  class Meta:
    model = Landuse
    fields=['landuse_type','polygon_colour']


class VillagemasterForm(forms.ModelForm):
  class Meta:
    model = Villagemaster
    fields=['village_id','village_name']

class villagesurveryForm(forms.ModelForm):
  class Meta:
    model = villagesurverylist
    fields = ['surveyno_from','surveyno_to']


class TownlistForm(forms.ModelForm):
  class Meta:
    model = TownList
    fields = ['wardno','blockno','surveyno_from','surveyno_to']

