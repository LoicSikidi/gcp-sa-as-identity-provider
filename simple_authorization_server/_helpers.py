import calendar
import datetime
import math
import os
import urllib.request
import base64
import json
import six

def get_sa_email() -> str:
    if 'SIGNING_SERVICE_ACCOUNT' in os.environ:
        return os.environ['SIGNING_SERVICE_ACCOUNT']
        
    sa_email_metadata_endpoint = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email"
    req = urllib.request.Request(sa_email_metadata_endpoint)
    req.add_header("Metadata-Flavor", "Google")
    return urllib.request.urlopen(req).read().decode()

def get_service_account_key_path() -> str:
    return os.getenv('SIGNING_SERVICE_ACCOUNT_KEY_PATH', None)

def diff_in_seconds_between_now_and_timestamp(d:datetime) -> int:
    now = datetime.datetime.now()
    return int(math.floor((d-now).total_seconds()))

def unpadded_urlsafe_b64encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=")

def padded_urlsafe_b64decode(value):
    b64string = value.encode('utf-8')
    padded = b64string + b"=" * (-len(b64string) % 4)
    return base64.urlsafe_b64decode(padded)
    
def get_exp_from_encoded_jwt(jwt: str) -> int:
    payload = json.loads(padded_urlsafe_b64decode(jwt.split(".")[1]))
    return payload.get('exp')

def utcnow():
    return datetime.datetime.utcnow()


def datetime_to_secs(value):
    return calendar.timegm(value.utctimetuple())
