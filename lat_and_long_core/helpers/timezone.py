# from django.utils import timezone
from rest_framework import serializers
from lat_and_long_core.helpers.helper import get_object_or_none, get_token_user_or_none
from pytz import timezone, utc
import sys, os, pytz
from datetime import datetime, timedelta
from django.conf import settings


class LocalizedDateTimeField(serializers.DateTimeField):
    
    def to_representation(self, value):
        try:

            if value is None:
                return None
            
            request         = self.context.get('request')
            user_instance   = get_token_user_or_none(request=request)
            if user_instance is  None:
                return super().to_representation(value)
            
            if user_instance.timezone is None:
                return super().to_representation(value)

            user_timezone = user_instance.timezone.timezones
            
            if user_timezone is None:
                return super().to_representation(value)
            
            default_timezone    = settings.DEFAULT_TIMEZONE

            original_timezone   = pytz.timezone(default_timezone)
            
            date_time           = original_timezone.localize(value)

            local_time          = date_time.astimezone(timezone(user_timezone))

            

            # user_timezone = timezone(user_timezone)

            # local_time = value.astimezone(user_timezone)

            return local_time.strftime(self.format)
        
        
        except Exception as e:
            return super().to_representation(value)
        














#---For date field---#
class LocalizedDateField(serializers.DateField):
    
    def to_representation(self, value):
        try:

            if value is None:
                return None
            
            print("value",value)
            
            request         = self.context.get('request')
            user_instance   = get_token_user_or_none(request=request)

            print("user_instance",user_instance)

            if user_instance is  None:
                return super().to_representation(value)
            
            if user_instance.timezone is None:
                return super().to_representation(value)

            user_timezone = user_instance.timezone.timezones
            
            if user_timezone is None:
                return super().to_representation(value)
            

            user_timezone = timezone(user_timezone)

            local_time = value.astimezone(user_timezone)

            return local_time.strftime(self.format)
        
        
        except Exception as e:
            return super().to_representation(value)
        
        

def simpleLocalizeTimeZone(value, request):
    
    format = "%m-%d-%Y %H:%M"
    try:

        if value is None:
            return None

        user_instance = get_token_user_or_none(request=request)


        if user_instance is  None:
            return value
        
            
        if user_instance.timezone is None:
            return value
            
        user_timezone = user_instance.timezone.timezones

        if user_timezone is None:
            return value
        
        user_timezone = timezone(user_timezone)
        
        local_time = value.astimezone(user_timezone)
        
        return local_time.strftime(format)
    
    
    except Exception as e:
        return value
    

def simpleLocalizeTimeZoneFormat(value, request,format):
    
    try:

        if value is None:
            return None

        user_instance = get_token_user_or_none(request=request)

        if user_instance is  None:
            return value.strftime(format)
        
        if user_instance.timezone is None:
            return value.strftime(format)
            
        user_timezone = user_instance.timezone.timezones

        if user_timezone is None:
            return value
        
        user_timezone = timezone(user_timezone)
        
        local_time = value.astimezone(user_timezone)

        return local_time.strftime(format)
    
    
    except Exception as e:
        return value
    

    
def timezoneUTCdifference(timezone):
    
    try:

        utc_time   = datetime.now(pytz.utc) # current UTC time
        tz         = pytz.timezone(timezone)
        local_time = utc_time.astimezone(tz)
        utc_offset = local_time.strftime('%z')
        
        return f"UTC{utc_offset} - {timezone}"
    
    except Exception as es:
        print(es)
        
    return ""


        

class ManualLocalizedDateTimeField():

        def __init__(self, date, date_format, request):
            self.date = date
            self.format = date_format
            self.request  = request
    
        def processed_date(self):
            try:
                if self.date is None:
                    return ''
                
                user_instance = get_token_user_or_none(request=self.request)
                
                if user_instance is  None:
                    return ''
                
                user_timezone = user_instance.timezone.timezones

                if user_timezone is None:
                    return ''
                
                default_timezone    = settings.DEFAULT_TIMEZONE

                original_timezone   = pytz.timezone(default_timezone)
                
                date_time           = original_timezone.localize(self.date)

                local_time          = date_time.astimezone(timezone(user_timezone))

                
                
                return local_time.strftime(self.format)
            
            
            except Exception as e:
                print(e)
                return ""
            
            




class ManualLocalizedTimezoneToUTC():

        def __init__(self, date, request, date_format= None):
            self.date       = date
            self.format     = date_format
            self.request    = request
    
        def processed_date(self):
            try:

                if self.date is None:
                    return ''
                

                user_instance = get_token_user_or_none(request=self.request)

                if user_instance is None or user_instance.timezone is None:
                    return self.date.strftime('%Y-%m-%d %H:%M:%S')

                user_timezone = user_instance.timezone.timezones 

                original_timezone = pytz.timezone(user_timezone)
                
                default_timezone = settings.DEFAULT_TIMEZONE
                
                self.date = self.date.strftime('%Y-%m-%d %H:%M:%S')

                date_time = datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')

                date_time = original_timezone.localize(date_time)

                local_time = date_time.astimezone(timezone(default_timezone))

                return local_time
            
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                return None
            



#---Email time field updates---#
class ManualEmailTimezoneToEST():

        def __init__(self, date, date_format= None):
            self.date = date
            self.format = date_format
    
        def datetoEST(self):
            try:
                if self.date is None:
                    return ''
                
                default_timezone = 'America/New_York'
                
                print('self.date :>>>>> ', self.date)
                
                
                date_time = datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
                
                local_time = date_time.astimezone(timezone(default_timezone))
                return local_time.strftime('%H:%M:%S')
                
            
            except Exception as e:
                print(">>>>>",str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                return None