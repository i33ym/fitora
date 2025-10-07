import os
import random
import requests
from requests.auth import HTTPBasicAuth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def generate_otp():
    return str(random.randint(100000, 999999))

def send_sms(phone_number, otp_code):
    request_url = os.getenv('SMS_API_URL')
    username = os.getenv('SMS_USERNAME')
    password = os.getenv('SMS_PASSWORD')
    originator = os.getenv('SMS_ORIGINATOR')
    
    auth = HTTPBasicAuth(username, password)
    
    try:
        request_data = {
            "messages": [
                {
                    "recipient": phone_number,
                    "message-id": random.randint(111111111, 999999999),
                    "sms": {
                        "originator": originator,
                        "content": {
                            "text": f"Your code is {otp_code}",
                        },
                    },
                }
            ]
        }
        response = requests.post(
            request_url,
            auth=auth,
            json=request_data,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

def verify_google_token(token):
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            client_id
        )
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', '')
        }
    except Exception as e:
        print(f"Google token verification error: {e}")
        return None