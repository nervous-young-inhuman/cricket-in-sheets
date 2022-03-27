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


class SpreadsheetSecrets(object):
    def __init__(self, id, sheet_id, sheet_name):
        self.ID = id
        self.SHEET_ID = sheet_id
        self.SHEET_NAME = sheet_name
        self.__classname = type(self).__name__

    def __str__(self):
        return f"{self.__classname}(ID={self.ID}, SHEET_ID={self.SHEET_ID}, SHEET_NAME={self.SHEET_NAME})"

    def __repr__(self):
        return f"{self.__classname}({self.ID},{self.SHEET_ID},{self.SHEET_NAME})"



DEFAULT_SPREADSHEET = SpreadsheetSecrets(
    os.environ.get('SPREADSHEET_ID'),
    os.environ.get('SPREADSHEET_SHEET_ID'),
    os.environ.get('SPREADSHEET_SHEET_NAME'),
)

if not DEFAULT_SPREADSHEET.ID:
    raise Exception('SPREADSHEET_ID not set in env')
if not DEFAULT_SPREADSHEET.SHEET_NAME and not DEFAULT_SPREADSHEET.SHEET_ID:
    raise Exception('SPREADSHEET_SHEET_ID not set in env')

if DEFAULT_SPREADSHEET.SHEET_ID:
    try:
        DEFAULT_SPREADSHEET.SHEET_ID = int(DEFAULT_SPREADSHEET.SHEET_ID)
    except ValueError:
        raise ValueError('SPREADSHEET_SHEET_ID should be an integer')


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
