import datetime
import time
from datetime import timedelta
# from . models import UserAccount
from django.contrib.auth import authenticate, login
import logging
from django.contrib.auth.models import User
from django.db import connection
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
# from myapp import show_data
import math,random
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django_otp.oath import hotp
import pyotp
import psycopg2
from psycopg2 import OperationalError
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import MasterplanForm
import logging
from django.utils import timezone
from .models import Registration
from .models import Country,State,District,Masterplan,Localbody,Talukmaster,Villagemaster
from .forms import RegisterForm,countriesForm,StateForm,DistrictForm
from .forms import VillagemasterForm
from myapp.decorators import login_required
from myapp.custom_auth import custom_logout
from myapp.custom_auth import custom_login, custom_authenticate, show_data
from django.views.decorators.cache import cache_control
from django.shortcuts import redirect
from django.shortcuts import render,redirect, get_object_or_404
from django.shortcuts import get_object_or_404, render
from .forms import TalukmasterForm
from .models import villagesurverylist
from django.db import connection
from .models import TownList


logger = logging.getLogger(__name__)  



@login_required
def aec_main(request):
    print("Inside AEC MAIN")
    return render(request,'myapp/aec_main.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_page(request):
    if request.method == 'POST':
        print("request.POST",request.POST)
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        pwd = urlsafe_base64_encode(force_bytes(pwd))
        print("unameunameunameunameuname",uname,"   :  ",pwd)
        if uname == 'admin':
            print("username")
            return render(request, 'myapp/aec_login.html')
        else:
            print('INSIDE AEC-MAIN PAGE')
            pwd = urlsafe_base64_encode(force_bytes(pwd))
            return redirect('aec-main')
    else:
        print("login page")
        return render(request,'myapp/aec_login.html')


def logout_request(request):
    print("inside logout page",request.method)
    custom_logout(request)
    print("inside logout ")
    return redirect('login-page')


def custom_sql_query():
    with connection.cursor() as cursor:
        cursor.execute("SELECT coordinates FROM aec_db.latlong_tbl;")
        rows = cursor.fetchall()
    return rows

def latlong_json(request):
    latlong_data = custom_sql_query()
    all_coords = []
    for row in latlong_data:
        split_coords = row[0].split('/')
        #print(split_coords)
        for coord in split_coords:
            if coord:
                lat_str, long_str = coord.strip().split(', ')
                lat = float(lat_str)
                long = float(long_str.rstrip(','))
                #strip - rstrip no change in above 
                all_coords.append({"lat": lat, "long": long})
                print(f"################{all_coords}###################")
    # result = {"coordinates": all_coords}
    result = all_coords
    return JsonResponse(result, safe=False)


def encode_password(request):
    print("i'm here here")
    if request.method == 'POST':
        print("=================")
        email = request.POST.get('email')
        password = request.POST.get('password')
        password = urlsafe_base64_encode(force_bytes(password))
        confirmpassword = request.POST.get('confirmpassword')
        confirmpassword = urlsafe_base64_encode(force_bytes(confirmpassword))
        print(email,password, confirmpassword)
        if password == confirmpassword:
            print("CHECK CONDITION BOTH PASSWORDS ARE TRUE OR NOT")
            user = Registration.objects.get(email=email)
            print("i'm here here here")
            password = request.POST.get('password')
            password = urlsafe_base64_encode(force_bytes(password))
            confirmpassword = request.POST.get('confirmpassword')
            confirmpassword = urlsafe_base64_encode(force_bytes(confirmpassword))
            user.password = password
            user.save()
            return redirect('login')
        else:
            print("invalid password")
            user.delete()
            # messages.error(request,'please fill the given password is correct')
            return render(request,'myapp/forgot_password.html')
    else:
      print("incorrect password")
      form = RegisterForm()
      print('changing password is invalid')
    #   messages.error(request,'please fill the correct password')
      return render(request, 'myapp/forgot_password.html')



def reset_password(request):
    return render(request,'myapp/aec_login.html')


def aec_modal(request):
    return render(request,'myapp/aec_modal.html')


def change_password(request):
    return render(request,'myapp/passwordchange.html')


def aec_sweetalarm(request):
    print("Inside sweetalarm")
   
    return render(request,'myapp/aec_sweetalarm.html')

def aec_erroralerm(request):
    return render(request,'myapp/aec_erroralerts.html')

def autogenerateotp(phonenumber):
    secret_key = b'1234567890123467890'
    for counter in range(1):
        print(hotp(key=secret_key,counter=counter,digits=6))
        OTP_Auto = get_random_string(6, allowed_chars='0123456789')
        return (OTP_Auto)


def resend_otp(request, pk):
    print("inside resend otp",request.method)
    obj = Registration.objects.get(id=pk)
    if obj.otp_count <3:
        obj.otp = autogenerateotp(obj.phonenumber)
        obj.otp_count += 1
        obj.otp_time = timezone.now()
        obj.save()
        return redirect("aec_otp", pk=pk)
    else:
        obj.delete()
        print("Maximum tries exceeded. Please try again after 24 hrs")
        return redirect("aec-register")


def aec_register(request):
    if request.method == 'POST':
            print("saving all the data's:")
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmPassword =request.POST.get('confirmPassword')
            confirmPassword = urlsafe_base64_encode(force_bytes(confirmPassword))
            password = urlsafe_base64_encode(force_bytes(password))
            phonenumber = request.POST.get('phonenumber')
            otp = autogenerateotp(phonenumber)
            print(f"username:{username}, Email-ID:{email},Password:{password},confirmPassword:{confirmPassword},phone_number:{phonenumber},otp:{otp}")
            if password == confirmPassword:
                print("i'm here here here")
                password = request.POST.get('password')
                password = urlsafe_base64_encode(force_bytes(password))
                confirmPassword = request.POST.get('confirmPassword')
                confirmPassword = urlsafe_base64_encode(force_bytes(confirmPassword))
                user = Registration.objects.create(username=username,
                email=email,password=password,phonenumber=phonenumber,otp=otp,
                otp_count=1, otp_time=datetime.datetime.now()
                )
                # user.password = password
                user.save()
                return redirect('aec_otp', user.id)
            else:
                print("enter same password")
                error = 'Please Enter A Valid Username And Password' + email
                return JsonResponse({"error":error})
                # print("i'm here here") 
                # return redirect('aec_regerror')
    else:
        form = RegisterForm()
        return render(request, 'myapp/aec_reg.html')


def aec_otp(request,pk):
    print("inside otp screen",request.method )
    obj = Registration.objects.get(id=pk)
    id = obj.id
    id = int(id)
    diff = datetime.datetime.now() - obj.otp_time
    print(30 - int(diff.total_seconds()))
    otp_secs= 30 - int(diff.total_seconds())
    if otp_secs <= 0:
        otp_secs = 0
    if request.method == 'POST':
        otp = request.POST.get('otp')
        print("obj.otp_count:", obj.otp_count)
        otp_count = obj.otp_count
        if obj.otp == int(otp):
            if obj.registered_user == 0:
                user_type = 'new_Registration'
                obj.registered_user = 1
                obj.save()
                return redirect('aec_sweetalarm')
            else:
                return redirect('aec-main')
        else:
            if otp_count<=3:
                # diff = datetime.datetime.now() - obj.otp_time
                print("222222222222222222222222222222222222222222", otp_secs)
                if (diff.total_seconds() > 30):
                    print("total seconds greater than 30 secs")
                    otp = autogenerateotp(obj.phonenumber)
                    print("generate otp for every 30 seconds")
                    print("otp",otp)
                    # user.phonenumber
                    obj.otp = otp
                    obj.otp_count += 1
                    obj.otp_time=datetime.datetime.now()
                    
                    obj.save()
                    return render(request,'myapp/otp.html',context={"user": obj,"otp_secs":otp_secs,"id":id})
                else:
                    print("total seconds LESS than 30 secs")
                   
                    return render(request,'myapp/otp.html',context={"user": obj,"otp_secs":otp_secs,"id":id})
            else:
                print("Your otp limit reached ..kindly reregister after 24 hours",otp_count)
                obj.delete() 
                return redirect("aec-register") 
    else:
        return render(request,'myapp/otp.html', context={"user": obj,"otp_secs":otp_secs,"id":id})


def aec_warningalert(request):
    return render(request,'myapp/aec_warningalert.html')


def aec_regerror(request):
    return render(request,'myapp/aec_regerror.html')



from django.views.decorators.cache import cache_control
def login_view(request):
    print("i'm here @login_view:",request.method)
    if request.method == 'POST':
                post_text = request.POST.get('the_post')
                response_data = {}
                print("saving all the data's:")
                email = request.POST.get('email')
                password = request.POST.get('password')
                password = urlsafe_base64_encode(force_bytes(password))
                print(f"Email-ID:{email},Password:{password}")
                # user = Registration.objects.get(email=email,password=password)
                try:
                    user = Registration.objects.get(email=email,password=password)
                    if user is not None:
                        custom_login(request, user)
                        user = Registration.objects.get(
                            email=email,password=password
                            )
                        print('1232')
                        print("i'm here here")
                        otp = autogenerateotp(user.phonenumber)
                        print("otp",otp)
                        # user.phonenumber
                        user.otp = otp
                        user.otp_count=1
                        user.otp_time=datetime.datetime.now()
                        user.save() 
                        error = 'Login successfully for ' + email
                        print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                        # response = redirect('aec_otp',user.id)
                        # return response
                        # return JsonResponse({"error":error},{"user_id":user.id})
                        return redirect('aec_otp', user.id)   
                    else:
                        print("heyyyy")
                        return render(request, 'myapp/aec_login.html')
                        # error = 'Please Enter A Valid Username And Password' + email
                        # return JsonResponse({"error":error},status=400)
                except Registration.DoesNotExist:
                    user = None
                    print("----^%^45343")
                    return render(request, 'myapp/aec_login.html')
                    # error = 'Please Enter A Valid Username And Password' + email
                    # return JsonResponse({"error":error},status=400)             
    else:
        print("*******insidee login GET view ********")
        print("inside login ",request.method)
       
        # form = RegisterForm()
        return render(request, 'myapp/aec_login.html')


def country_databases(request):
    print("countrydatabase",request.method)
    obj=Country.objects.all()
    print("obj",obj)
    form =countriesForm()

    context={
        "obj":obj,
        "form":form,
    }
    print("context",context)
    return render(request,'myapp/aec_countrydata.html',context)
  


def get_states(request):
    country_id = request.GET.get('country_id')
    country = Country.objects.get(id=country_id)
    states = State.objects.filter(country=country).values('id', 'state')
    data = {
        "data": list(states)
    }
    return JsonResponse(data)

 
def get_districts(request):
    state_id = request.GET.get('state_id')
    print("MMMMMMMMMMMMMMMM",state_id)
    state = State.objects.get(id=state_id)
    print("i'm here here",state)
    districts = District.objects.filter(state=state).values('id', 'district')
    print("heyyyyyyyyyyyyyyyy" ,districts)
    data = {
        'data': list(districts)
    }
    return JsonResponse(data)


def aec_masterscreen(request):
    return render(request,'myapp/aec_masterscreen.html')


def state_databases(request):
    obj=State.objects.all()
    countries = Country.objects.all()
    print("countries",countries)
    context={
        "obj":obj,
        "countries":countries
    }
    return render(request,'myapp/aec_statedata.html',context)


def district_databases(request):
    obj=District.objects.all()
    states = State.objects.all()
    context={
        "obj":obj,
        "states":states
    }
    return render(request,'myapp/aec_districtdata.html',context)


def aec_masterdata(request):
    obj=Masterplan.objects.all()
    district = District.objects.all()

    context={
        "obj":obj,
        "district":district
    }
    return render(request,'myapp/aec_masterplan.html',context)


def aec_localbodydata(request):
    obj=Localbody.objects.all()
    district = District.objects.all()
    masterplan = Masterplan.objects.all()
    context={
        "obj":obj,
        "district":district,
        "masterplan":masterplan
    }   
    return render(request,'myapp/aec_localbody.html',context)

def aec_talukdata(request):
    obj=Talukmaster.objects.all()
    district = District.objects.all()
    masterplan = Masterplan.objects.all()
    context={
        "obj":obj,
        "district":district,
        "masterplan":masterplan,

    }
    return render(request,'myapp/aec_taluk.html',context)

def aec_villagedata(request):
    print("i'm here here",request.method)
    obj=Villagemaster.objects.all()
    print("obj",obj)
    taluk = Talukmaster.objects.all()
    print("taluk",taluk)
    context={
         "obj":obj,
         "taluk":taluk,
    }
    return render(request,'myapp/aec_villagedata.html',context)


def aec_villagesurverylist(request):
    obj = villagesurverylist.objects.all()
    print("obj",obj)
    village_name = Villagemaster.objects.all()
    print("villagemaster",village_name)
    landuse = Landuse.objects.all()
    print("landuse",landuse)
    context ={
        "obj":obj,
        "village_name":village_name,
        "landuse":landuse,
    }
    return render(request,'myapp/aec_villagesurverylist.html',context)


def aec_townlist(request):
    obj = TownList.objects.all()
    print("obj",obj)
    localbody = Localbody.objects.all()
    print("localbody_id",localbody)
    landuse = Landuse.objects.all()
    print("Landuse",landuse)
    context ={
        "obj":obj,
        "localbody":localbody,
        "landuse":landuse,

    }
    return render(request,'myapp/aec_townlist.html',context)


def add_field(request):
    if request.method == 'POST':
            print("saving all the data's:",request.method)
            try:
                country_id = request.POST.get('id')
                print("country_id",country_id)
                country = request.POST.get('country_name')
                print("LLLLLLLLLLLLLLLL",country)
                print(f" country:{country},country_id:{country_id}")
                user = Country.objects.create(country_id=country_id,country=country)
                print("user",user)
                # user.save()
                return JsonResponse({"success": True, "message": "Added successful"})
            except Exception as e:  
                error_message = str(e)
                return JsonResponse({"success": False, "message": error_message}, status=400)

   

def add_statefield(request):
    if request.method == 'POST':
            print("saving all the data's:",request.method)
            try:
                country = request.POST.get('country')
                print("KKKKKKKKKKKK",country)
                state = request.POST.get('state')
                # print("LLLLLLLLLLLLLLLLwqw",state)
                print(f" state:{state}")
                country = Country.objects.get(id=country)
                # print("djkhjdhfjf",country)
                State.objects.create(state=state,country=country)
                return JsonResponse({"success": True, "message": "Added successful"})
            except Exception as e:  
                error_message = str(e)
                return JsonResponse({"success": False, "message": error_message}, status=400)

    

 
def add_districtfield(request):
    if request.method == 'POST':
            print("saving all the data's:",request.method)
          
            district = request.POST.get('district')
            print("LLLLLLLLLLLLLLLLdd",district)
            state = request.POST.get('state')
            print(f" state:{state}")
            state = State.objects.get(id=state)
            District.objects.create(district=district,state=state)
            return JsonResponse({"success": True, "message": "Added successful"})
    data = {
                "message": "success",
                "data": {}
            }
    print(data)
    return JsonResponse(data)
    




def add_masterfield(request):
    if request.method == 'POST':
            print("saving all the data's:",request.method)
            masterplan_id = request.POST.get('masterplan_id')
            print("masterplan_id",masterplan_id)
            district_id = request.POST.get('district_id') 
            print("fggkjg",district_id)   
            masterplan_name = request.POST.get('masterplan_name')
            print("LLLLLLLLLLLLLLxxLL",masterplan_name) 
            Masterplan.objects.create(masterplan_name=masterplan_name,district_id=district_id)
            return JsonResponse({"success": True, "message": "Added successful"})
    return JsonResponse({'message': 'failed to add'}, status=405)


def add_villagefields(request):
    if request.method == 'POST':
        print("saving all the data's:",request.method)
        taluk_id = request.POST.get('taluk_id')
        print("hhhhhhhhhhhhhhh",taluk_id)
        village_name = request.POST.get('village_name')
        print("ggggggggggggggg",village_name)
        Villagemaster.objects.create(taluk_id=taluk_id,village_name=village_name)
        return JsonResponse({"success": True, "message": "Added successful"})


def delete_item(request, country_id):
    country = Country.objects.filter(pk=country_id)
    print("=====================",country)
    country.delete()
    return redirect('country_databases')



def delete_stateitem(request, state_id):
    state = State.objects.filter(pk=state_id)
    print("=====================",state)
    state.delete()
    return redirect('state_databases')


def delete_districtitem(request,district_id):
    district = District.objects.filter(district_id=district_id)
    district.delete()
    return redirect('district_databases')

def delete_masteritem(request,master_id):
    masterplan = Masterplan.objects.filter(pk=master_id)
    masterplan.delete()
    return redirect('aec_masterdata')

def delete_localbodyitem(request,localbody_id):
    localbody = Localbody.objects.filter(pk=localbody_id)
    localbody.delete()
    return redirect('aec_localbodydata')

def delete_talukitem(request,taluk_id):
    talukmaster = Talukmaster.objects.filter(pk=taluk_id)
    talukmaster.delete()
    return redirect('aec_talukdata')


def delete_villageitem(request,village_id):
    villagemaster = Villagemaster.objects.filter(pk=village_id)
    villagemaster.delete()
    return redirect('aec_villagedata')


# def aec_data(request):
#     print("============",request.method)
#     obj=Country.objects.all()
   
#     context={
#         "obj":obj,
#     }
#     return render(request,'myapp/aec_data.html',context)
  
def check_district(id):
    district = None
    try:
        district = District.objects.get(id=id)
    except District.DoesNotExist as e:
        print(e)
        return JsonResponse({})
    return district

def check_master(id):
    masterplan_name = None
    try:
        masterplan_name = Masterplan.objects.get(id=id)
    except masterplan_name.DoesNotExist as e:
        print(e)
        return JsonResponse({})
    return masterplan_name

def check_localbody(id):
    localbody = None
    try:
        localbody_name = Localbody.objects.get(id=id)
    except localbody_name.DoesNotExist as e:
        print(e)
        return JsonResponse({})
    return localbody_name


def check_village(id):
    village_name = None
    try:
        village_name=Villagemaster.objects.get(id=id)
    except village_name.DoesNotExist as e:
        print(e)
        return JsonResponse({})

def check_landuse(id):
    landuse =   None
    try:
        landuse_type = Landuse.objects.get(id=id)
        print("landuse",landuse_type)
    except landuse_type.DoesNotExist as e:
        print(e)
        return JsonResponse({})

def check_taluk(id):
    taluk = None
    try:
        taluk_name = Talukmaster.objects.get(id=id)
    except taluk_name.DoesNotExist as e:
        print(e)
        return JsonResponse({})
    return taluk_name

def check_villagesurvery(id):
    villagesurvery = None
    try:
        surveyno_from = villagesurverylist.objects.get(id=id)
        print("surveyno_from",surveyno_from)
    except surveyno_from.DoesNotExist as e:
        print(e)
        return JsonResponse({})
    return surveyno_from
   


def add_localbodyfield(request):
    print("i'm here here add_localbodyfield " ,request.method,request.FILES)
    if request.method == 'POST':
        district = request.POST.get('district')
        print("district",district)
        localbody_name = request.POST.get('localbody_name')
        print("localbody_name",localbody_name)
        localbody_type = request.POST.get('localbody_type')
        print('localbody_type',localbody_type)
        masterplan = request.POST.get("masterplan_name")
        print("masterplan",masterplan)

        # masterplan = Masterplan.objects.filter(district=district).values('id')
       
        district = check_district(district)
        masterplan = check_master(masterplan)
        localbody=Localbody.objects.create(
            district=district,
            masterplan=masterplan,
            localbody_name=localbody_name,
            localbody_type=localbody_type
        )
        print("localbody created : ",localbody)
        data = {
                "message": "success",
                "data": {}
            }
        print(data)
        return JsonResponse(data)
        # if localbody:
        #     return JsonResponse({"success": True, "message": "Added Successfully"})
    else:
        if request.method == 'GET':
            print("add_localbodyfield :", request.method )
            district_id = request.GET.get("district_id")
            print("district",district_id)
            # district = District.objects.get(id = district_id)
            masterplans = Masterplan.objects.filter(district=district_id).values('id', 'masterplan_name')
            print("masterplans",masterplans)
            data = {
                'data': list(masterplans)
            }
            return JsonResponse(data)


def add_talukfields(request):
    print("i'm here here add_masterplan " ,request.method,request.FILES)
    if request.method == 'POST':
        district = request.POST.get('district')
        print("district",district)
        taluk_name = request.POST.get('taluk_name')
        print("taluk_name",taluk_name)
        masterplan = request.POST.get("masterplan_name")
        print("masterplan",masterplan)
        district = check_district(district)
        print("district",district)
        masterplan = check_master(masterplan)
        print("masterplan",masterplan)
        talukmaster=Talukmaster.objects.create(
            district=district,
            masterplan=masterplan,
            taluk_name=taluk_name,
           
        )
        print("talukmasterplan",talukmaster)
        data = {
                "message": "success",
                "data": {}
            }
        print(data)
        return JsonResponse(data)
    else:
        if request.method == 'GET':
            print("add_masterplanfield :", request.method )
            district_id = request.GET.get("district_id")
            print("district",district_id)
            # district = District.objects.get(id = district_id)
            masterplans = Masterplan.objects.filter(district=district_id).values('id', 'masterplan_name')
            print("masterplans",masterplans)
            data = {
                'data': list(masterplans)
            }
            return JsonResponse(data)

def aec_base(request):
     print("INSIDE NAV")
     return render(request,'myapp/aec_base.html')


# def aec_countrydata1(request):
#     return render(request,'myapp/aec_countrydata1.html')


def edit_country1(request, country_id):
    print("country_id",country_id)
    print("i'm here here", request.method)
    obj = Country.objects.get(country_id=country_id)
    print("obj",obj)
    if request.method == 'POST':
        form = countriesForm(request.POST, instance=obj)
        print("form", form)
        if form.is_valid():
            form.save()  
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
        else:
            print(form.errors)  
            data = {
                'message': 'Failed to update data',
                'errors': form.errors, 
            }
            print("data",data)
            return JsonResponse(data, status=400)
    print("DDDDDDDDDDDD", request.method)
    form = countriesForm(instance=obj)
    return render(request, 'myapp/aec_countrydata.html', {'form': form, 'obj': obj})


def edit_state1(request, state_id):
    print("request",state_id)
    try:
        if request.method == 'POST':
            state_id = request.POST.get("state_id")
            print("state_id",state_id)
            country = request.POST.get('country')
            print("KKKKKKKKKKKK",country)
          
            state = request.POST.get('state')
            print(f" state:{state}")
            obj = Country.objects.get(id=country)
            obj = State.objects.get(id=state_id)  
            print("obj", obj)
            obj.state = state
            obj.country = country 
            form = StateForm(request.POST, instance=obj)
            print("form", form)
            if form.is_valid():
                form.save()  
                data = {
                    'message': 'Data updated successfully',
                }
                return JsonResponse(data)
            else:
                print(form.errors)  
                data = {
                    'message': 'Failed to update data',
                    'errors': form.errors, 
                }
                print("data",data)
        else:
            return JsonResponse({'message': 'Invalid Request'}, status=400)
    except State.DoesNotExist as e:
        return JsonResponse({'message': 'State does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'message': 'An error occurred'}, status=500)


def edit_village(request, taluk_id):
    print("taluk_id",taluk_id)
    print("i'm here here", request.method)
    obj = Talukmaster.objects.get(taluk_id=taluk_id)
    print("obj",obj)
    if request.method == 'POST':
        form = VillagemasterForm(request.POST, instance=obj)
        print("form", form)
        if form.is_valid():
            form.save()  
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
        else:
            print(form.errors)  
            data = {
                'message': 'Failed to update data',
                'errors': form.errors, 
            }
            print("data",data)
            return JsonResponse(data, status=400)
    print("DDDDDDDDDDDD", request.method)
    form = VillagemasterForm(instance=obj)
    return render(request, 'myapp/aec_villagedata.html', {'form': form, 'obj': obj})



def edit_district(request, district_id):
    print("district_id",district_id)
    print("i'm here here", request.method)
    obj = District.objects.get(district_id=district_id)
    print("obj",obj)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=obj)
        print("form", form)
        if form.is_valid():
            form.save()  
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
        else:
            print(form.errors)  
            data = {
                'message': 'Failed to update data',
                'errors': form.errors, 
            }
            print("data",data)
            return JsonResponse(data, status=400)
    print("DDDDDDDDDDDD", request.method)
    form = DistrictForm(instance=obj)
    return render(request, 'myapp/aec_districtdata.html', {'form': form, 'obj': obj})



# def edit_state(request, state_id):
#     try:
#         obj = State.objects.get(id=state_id)
#         print("state", obj)
#         if request.method == 'POST':
#             form = StateForm(request.POST, instance=obj)
#             if form.is_valid():
#                 form.save()
#                 data = {
#                     'message': 'Data updated successfully',
#                 }
#                 return JsonResponse(data)
#             else:
#                 data = {
#                     'message': 'Failed to update data',
#                     'errors': form.errors,
#                 }
#                 return JsonResponse(data, status=400)

#         form = StateForm(instance=obj)
#         return render(request, 'myapp/aec_statedata.html', {'form': form, 'obj': obj})
#     except State.DoesNotExist as e:
#         return JsonResponse({'message': 'State does not exist'}, status=404)
#     except Exception as e:
#         return JsonResponse({'message': 'An error occurred'}, status=500)


def edit_country(request, country_id):
    obj = Country.objects.get(country_id=country_id)
    if request.method == 'POST':
        form = countriesForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            data = {
                    'message': 'Data updated successfully',
                }
            return JsonResponse(data)
    else:
        errors = form.errors.as_json()
        data = {
                'message': 'Failed to update data',
                'errors': errors,
            }
        return JsonResponse(data, status=400)
    context = {
        'form': form,
        'country': obj,
    }
    return render(request, 'myapp/aec_countrydata.html', context)




def edit_district(request, district_id):
    print("hey",request.method,district_id)
    obj = District.objects.get(id=district_id)
    print("obj",obj)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = DistrictForm(instance=obj)
    context = {
        'form': form,
        'state': obj,
    }
    return render(request, 'myapp/aec_districtdata.html', context)


def edit_state(request, state_id):
    print("hey",request.method,state_id)
    obj = State.objects.get(id=state_id)
    print("obj",obj)
    if request.method == 'POST':
        form = StateForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            # return redirect('state_databases')
            # render redirect("state_databases")
            return JsonResponse(data)
    else:
        form = StateForm(instance=obj)
    context = {
        'form': form,
        'country': obj,
    }
    return render(request, 'myapp/aec_statedata.html', context)


def edit_master(request, masterplan_id):
    print("hey",request.method)
    obj = Masterplan.objects.get(id=masterplan_id)
    print("obj",obj)
    if request.method == 'POST':
        form = MasterplanForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            print("data",data)
            return JsonResponse(data)
    else:

        form = MasterplanForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'district': obj,
    }
    print("context",context)
    return render(request, 'myapp/aec_masterplan.html', context)



from .forms import LocalbodyForm

def edit_localbody(request, localbody_id):
    print("hey",request.method,localbody_id)
    obj = Localbody.objects.get(id=localbody_id)
    print("obj",obj)
    if request.method == 'POST':
        form = LocalbodyForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = LocalbodyForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'masterplan': obj,
        'district':obj,
    }
    print("context",context)
    return render(request, 'myapp/aec_localbody.html', context)



def edit_taluk(request, taluk_id):
    print("hey",request.method,taluk_id)
    obj = Talukmaster.objects.get(id=taluk_id)
    print("obj",obj)
    if request.method == 'POST':
        form = TalukmasterForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = TalukmasterForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'masterplan': obj,
        'district':obj,
    }
    print("context",context)
  


def edit_village(request, village_id):
    print("hey",request.method)
    print("------",village_id)
    obj = Villagemaster.objects.get(id=village_id)
    print("obj",obj)
    if request.method == 'POST':
        form = VillagemasterForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = VillagemasterForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'taluk':obj,
       
    }
    print("context",context)
    return render(request, 'myapp/aec_villagedata.html', context)


def show_districts(request):
    district = District.objects.filter()
    print("district",district)
    data={
        'districts':district
    }
    return JsonResponse(data)

   

# def get_district(request):
#     print("get_district function called")
    
#     db_connection=mysqlconnect()
#     if db_connection == 0 :
#         print("unable to connect to DB")
#     else:
#         # Making Cursor Object For Query Execution
#         get_all_district="select district_name from aec_db.district_mtbl"
#         cursor=db_connection.cursor()
#         cursor.execute(get_all_district)
#         result = cursor.fetchall()
#         for i in range(0,len(result)):
#             print(result[i])
#         cursor.close()
#         db_connection.close()
#         return JsonResponse(result, safe=False)


from django.http import JsonResponse
from django.db import connection

def get_district(request):
    print("inside district view")
    try:
        with connection.cursor() as cursor:
            print("inside district select query")
            cursor.execute("SELECT district_id, district FROM myapp_district;")
            # print("cursor.execute",cursor.execute)
            result = cursor.fetchall()
            print("result",result)
            district_list = [{'district_id': row[0], 'district': row[1]} for row in result]
            print("district_result",district_list)
            return JsonResponse(district_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while fetching the districts.'})



def get_masterplan(request, district_id):
    print("get_masterplan function called")
    try:
        print("inside masterplan query")

        sql_query = "SELECT masterplan_name FROM public.myapp_masterplan WHERE district_id = %s;"
        with connection.cursor() as cursor:
            print("inside db connection")
            cursor.execute(sql_query, [district_id])
            result = cursor.fetchone()
            if result:
                masterplan_name = result[0]
                return JsonResponse({'masterplan_name': masterplan_name})
            else:
                print("========")
                return JsonResponse({'error': 'Masterplan not found for this district.'})
    except Exception as e:
        print(f"Error in get_masterplan: {str(e)}")
        return JsonResponse({'error': 'An error occurred while fetching the masterplan.'})


from .models import Landuse
def add_landusedata(request):
    if request.method == 'POST':
            print("saving all the data's:",request.method)
            try:
                landuse_type = request.POST.get('landuse_type')
                print("landuse_type",landuse_type)
                polygon_colour = request.POST.get('polygon_colour')
                print("hhhhhhhhhhh",polygon_colour)
                print(f" landuse_type:{landuse_type},polygon_colour:{polygon_colour}")
                user = Landuse.objects.create(landuse_type=landuse_type,polygon_colour=polygon_colour)
                print("user",user)
                # user.save()
                return JsonResponse({"success": True, "message": "Added successful"})
            except Exception as e:  
                error_message = str(e)
                return JsonResponse({"success": False, "message": error_message}, status=400)
            
from .forms import LanduseForm

def edit_landusedata(request, landuse_id):
    obj = Landuse.objects.get(landuse_id=landuse_id)
    if request.method == 'POST':
        form = LanduseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            data = {
                    'message': 'Data updated successfully',
                }
            return JsonResponse(data)
    else:
        errors = form.errors.as_json()
        data = {
                'message': 'Failed to update data',
                'errors': errors,
            }
        return JsonResponse(data, status=400)
    context = {
        'form': form,  
    }
    return render(request, 'myapp/aec_landuse.html', context)

def delete_landuse(request,landuse_id):
    landuse = Landuse.objects.filter(pk=landuse_id)
    landuse.delete()
    return redirect('aec_landusedata')


def delete_villagesurvery(request,villagesurvery_id):
    villagesurvery = villagesurverylist.objects.filter(pk=villagesurvery_id)
    villagesurvery.delete()
    return redirect('aec_villagesurveydata')

from .models import Landuse
from .models import villagesurverylist

def aec_landusedata(request):
    print("i;m here here",request.method)
    obj = Landuse.objects.all()
    print("obj",obj)
    context={
        "obj":obj,
    }
    return render(request,'myapp/aec_landuse.html',context)


from django.http import JsonResponse
from .models import Villagemaster, Landuse, villagesurverylist

def add_villagesurvery(request):
    if request.method == 'POST':
        try:
            village_id = request.POST.get('village_name')
            print("village_id",village_id)
            surveyno_from = request.POST.get('surveyno_from')
            print("surveyno_from",surveyno_from)
            surveyno_to = request.POST.get('surveyno_to')
            landuse_id = request.POST.get('landuse_type')

            village_name = Villagemaster.objects.get(village_id=village_id)
            landuse_type = Landuse.objects.get(landuse_id=landuse_id)

            villagesurvery = villagesurverylist.objects.create(
                village_name=village_name,
                landuse_type=landuse_type,
                surveyno_from=surveyno_from,
                surveyno_to=surveyno_to
            )

            return JsonResponse({"success": True, "message": "Added successfully"})
        except Villagemaster.DoesNotExist:
            return JsonResponse({"success": False, "message": "Village does not exist"}, status=400)
        except Landuse.DoesNotExist:
            return JsonResponse({"success": False, "message": "Landuse type does not exist"}, status=400)
        except Exception as e:
            error_message = str(e)
            return JsonResponse({"success": False, "message": error_message}, status=400)

    elif request.method == 'GET':
        village_id = request.GET.get("village_id")
        landuse_type = list(Landuse.objects.filter(village_name__village_id=village_id).values('id', 'landuse_type'))
        data = {'data': landuse_type}
        return JsonResponse(data)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)
   
from .forms import villagesurveryForm

def edit_villagesurvery1(request, village_id):
    print("hey",request.method,village_id)
    obj = villagesurverylist.objects.get(id=village_id)
    print("obj",obj)
    if request.method == 'POST':
        form = villagesurveryForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = villagesurveryForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'village_name': obj,
        'land_use':obj,
    }
    print("context",context)
    return render(request, 'myapp/aec_villagesurverylist.html', context)


def edit_villagesurvery(request, villagesurvey_id):
    print("hey",request.method,villagesurvey_id)
    obj = villagesurverylist.objects.get(villagesurvey_id=villagesurvey_id)
    print("obj",obj)
    if request.method == 'POST':
        form = villagesurveryForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = villagesurveryForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
       'village_name': obj,
        'land_use':obj,
    }
    print("context",context)
    return render(request, 'myapp/aec_villagesurverylist.html', context)


def delete_villagesurvey(request,villagesurvey_id ):
    villagesurvey = villagesurverylist.objects.filter(villagesurvey_id=villagesurvey_id)
    print("=====================",villagesurvey)
    villagesurvey.delete()
    return redirect('aec_villagesurverylist')


def add_townlist(request):
    print("***************************",request.method)
    if request.method == 'POST':
        print("----------------------------",request.method)
        try:
            localbody_name = request.POST.get('localbody_name')
            print("localbody_name",localbody_name)
            landuse_type = request.POST.get('landuse_type')
            print("landuse_type",landuse_type)
            wardno = request.POST.get('wardno')
            blockno = request.POST.get('wardno')
            surveyno_from = request.POST.get('surveyno_from')
            print("surve=======",surveyno_from)
            surveyno_to = request.POST.get('surveyno_to')  # Correct the field name
            print("surveyno_to",surveyno_to)
            localbody_name = Localbody.objects.get(localbody_id=localbody_name)
            print("village_instance",localbody_name)
            landuse_type = Landuse.objects.get(landuse_id=landuse_type)
            print("landuse_instance",landuse_type)
            townlist = TownList.objects.create(
                localbody_name=localbody_name,
                landuse_type=landuse_type,
                wardno=wardno,
                blockno=blockno,
                surveyno_from=surveyno_from,
                surveyno_to=surveyno_to  # Use the correct field name
            )
            print("townlist",townlist)

            return JsonResponse({"success": True, "message": "Added successfully"})
        except Exception as e:
            error_message = str(e)
            return JsonResponse({"success": False, "message": error_message}, status=400)
    else:
        if request.method == 'GET':
            print("add_townlist :", request.method )
            localbody_id = request.GET.get("localbody_id")
            print("localbody_id",localbody_id)
            #district = District.objects.get(id = district_id)
            landuse_type = Landuse.objects.filter(localbody_name=localbody_id).values('id', 'landuse_type')
            print("masterplans",landuse_type)
            data = {
                'data': list(landuse_type)
            }
            return JsonResponse(data)
     
from .forms import TownlistForm

def edit_townlist(request, townlist_id):
    print("hey",request.method,townlist_id)
    obj = TownList.objects.get(townlist_id=townlist_id)
    print("obj",obj)
    if request.method == 'POST':
        form = TownlistForm(request.POST, instance=obj)
        print("form",form)
        if form.is_valid():
            form.save()
            data = {
                'message': 'Data updated successfully',
            }
            return JsonResponse(data)
    else:
        form = TownlistForm(instance=obj)
        print("form",form)
    context = {
        'form': form,
        'localbody_name': obj,
        'land_use':obj,
    }
    print("context",context)
    return render(request, 'myapp/aec_townlist.html', context)


def delete_townlist(request,townlist_id ):
    print("----------",request.method)
    townlist = TownList.objects.filter(townlist_id=townlist_id)
    print("=====================",townlist)
    townlist.delete()
    return redirect('aec_townlist')
