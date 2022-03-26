import os
from pathlib import Path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
CRICDATA_API_KEY = os.environ.get('CRICDATA_API_KEY')

if not CRICDATA_API_KEY:
    raise Exception('CRICDATA_API_KEY not set in env')

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if not GOOGLE_APPLICATION_CREDENTIALS:
    raise Exception('GOOGLE_APPLICATION_CREDENTIALS not set in env')

def __google_creds():
    creds = None
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
    ]
    gauth_token = Path(GOOGLE_APPLICATION_CREDENTIALS).resolve()
    if gauth_token.exists():
        creds = Credentials.from_service_account_file(str(gauth_token), scopes=SCOPES)
    else:
        raise Exception(f'token not found at {gauth_token}.')

    if not creds:
        raise Exception('credentials not found')

    return creds

google_creds = __google_creds()
