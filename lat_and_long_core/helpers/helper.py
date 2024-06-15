import logging, json,socket
from django.contrib.auth import get_user_model
from django.core.files import File
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from apps.user.models import GeneratedAccessToken
from django.conf import settings
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


def calculate_distances(df):
    distances = []
    for i in range(1, len(df)):
        coord1 = (df.loc[i-1, 'latitude'], df.loc[i-1, 'longitude'])
        coord2 = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
        distances.append(geodesic(coord1, coord2).meters)
    return distances

def calculate_distance_terrain(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    



    
def get_all_tokens_for_user(user):
    return OutstandingToken.objects.filter(user=user)


def get_all_tokens_for_multiple_users(users):
    return OutstandingToken.objects.filter(user__in=users)


def get_user_access_tokens(user):
    return GeneratedAccessToken.objects.filter(user=user)

# def update_last_logout(sender, user, **kwargs):
#     """
#     A signal receiver which updates the last_logout date for
#     the user logging out.
#     """
#     user.last_logout = timezone.now()
#     user.last_active = timezone.now()
#     user.is_logged_in = False
#     user.save(update_fields=["last_logout","is_logged_in","last_active"])




def get_token_user_or_none(request):
    User = get_user_model()
    try:
        instance = User.objects.get(id=request.user.id)
    except Exception:
        instance = None
    finally:
        return instance


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
    
    
def get_value_or_empty(value):
    
    return value if value is not None else ""


    
def get_value_or_dash(value):
    
    return value if value is not None and value !='' else "-"


def handle_index_error(key, content):
    try:
        return content[key]
    except IndexError:
        return ''
    except:
        return ''
    
    
    


def login_authorization(request):
    if request.user.is_authenticated:
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "req_body":json.loads(request.body.decode("utf-8")) if request.body else {},
        }  

        if ('req_body' in log_data):
            if ('password' in log_data['req_body']):
                del log_data['req_body']['password']

        index='unauthorized_login'

        return False   
    else:
        return True


def convert_to_datetime_format(input_string):
    format_string = ''
    format_codes = {'M': '%m', 'D': '%d', 'Y': '%Y'}
    separators = set('-/')
    processed_letters = []
    
    for char in input_string:
        if char in format_codes and char not in processed_letters:
            format_string += format_codes[char]
            processed_letters.append(char)
        elif char in separators:
            format_string += char
    
    return format_string








