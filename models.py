from django.db import models
from django_countries.fields import CountryField
from django.utils import timezone
from datetime import datetime 
from django.utils import timezone
from django.contrib.auth.models import User


#Registration Model
class Registration(models.Model):
    username = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255) # In real-world use cases, always use hashed passwords!
    phonenumber = models.CharField(max_length=300)
    otp = models.IntegerField(default= 000000)
    otp_count = models.IntegerField(default=0)
    otp_time = models.DateTimeField(null=True, blank=True)
    registered_user = models.IntegerField(default= 0)
    def __str__(self):
        return self.username

#Country Model
class Country(models.Model):
    country_id = models.IntegerField(default=0000)
    country=models.CharField(max_length=200,null=True,unique=True)
    def __str__(self):
        return self.country
    
#State Model
class State(models.Model):
    country=models.ForeignKey(Country,on_delete=models.CASCADE, null=True)
    state_id = models.IntegerField(default=0000)
    state=models.CharField(max_length=200,null=True,unique=True)
  
    def __str__(self):
        return self.state

#District Model
class District(models.Model):
    district_id = models.IntegerField(default=0000)
    district=models.CharField(max_length=200,null=True,unique=True)
    state=models.ForeignKey(State,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.district
    
#masterplan Model
class Masterplan(models.Model):
    masterplan_id=models.IntegerField(default=0000)
    masterplan_name = models.CharField(max_length=200,null=True,unique=True)
    district = models.ForeignKey(District,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.masterplan_name
    
#Localbody Model
class Localbody(models.Model):
    localbody_id=models.IntegerField(default=0000)
    localbody_name = models.CharField(max_length=200,null = True,unique=True)
    localbody_type = models.CharField(max_length=200,null = True)
    district = models.ForeignKey(District,on_delete=models.CASCADE, null=True)
    masterplan = models.ForeignKey(Masterplan,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.localbody_name
    
#Taluk Model
class Talukmaster(models.Model):
    taluk_id=models.IntegerField(default=0000)
    taluk_name = models.CharField(max_length=200,null = True,unique=True)
    district = models.ForeignKey(District,on_delete=models.CASCADE, null=True)
    masterplan = models.ForeignKey(Masterplan,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.taluk_name
    

#Village Model
class Villagemaster(models.Model):
    village_id=models.IntegerField(default=0000)
    village_name = models.CharField(max_length=200,null = True,unique=True)
    taluk = models.ForeignKey(Talukmaster,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.village_name
    
#landuse Model
class Landuse(models.Model):
    landuse_id = models.AutoField(primary_key=True)
    landuse_type = models.CharField(max_length=100,unique=True)
    polygon_colour = models.CharField(max_length =50)
    def __str__(self):
        return self.landuse_type
 


#villagesurverylist MOdel
class villagesurverylist(models.Model):
    village_name = models.ForeignKey(Villagemaster,on_delete=models.CASCADE, null=True)
    landuse_type = models.ForeignKey(Landuse,on_delete=models.CASCADE, null=True)
    villagesurvey_id = models.AutoField(primary_key=True)
    surveyno_from = models.CharField(max_length=100,null = False)
    surveyno_to = models.CharField(max_length=100, null=True, blank=True)
    # landuse_detail = models.CharField(max_length=200)
    def __str__(self):
        return self.surveyno_from


class TownList(models.Model):
    townlist_id = models.AutoField(primary_key=True)
    wardno = models.CharField(max_length=10)
    blockno = models.CharField(max_length=10)
    surveyno_from = models.CharField(max_length=50)
    surveyno_to = models.CharField(max_length=70)
    landuse_type = models.ForeignKey(Landuse,on_delete=models.CASCADE, null=True)
    localbody_name=models.ForeignKey(Localbody,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.wardno
  
