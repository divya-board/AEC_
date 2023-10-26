from django.contrib import admin
from .models import Registration,State,District,Masterplan,Localbody,Talukmaster,Villagemaster,Country,villagesurverylist,Landuse,TownList

# Register your models here.

admin.site.register(Registration)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(District)
admin.site.register(Masterplan)
admin.site.register(Localbody)
admin.site.register(Talukmaster)
admin.site.register(Villagemaster)
admin.site.register(villagesurverylist)
admin.site.register(Landuse)
admin.site.register(TownList)



